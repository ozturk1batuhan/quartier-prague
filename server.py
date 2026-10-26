import json
import os
import re
import sqlite3
import time
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Dict, Any, Optional

from scraper import (
    PRAGUE_DISTRICTS,
    scrape_osm_prague,
    scrape_google_places_api,
    get_curated_prague_starter_leads,
    infer_industry_from_tags,
    classify_website_status,
)
from site_generator import (
    COLOR_THEMES,
    generate_business_website_html,
    generate_prague_outreach_pitches,
)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "quartier_prague.db"
SITES_DIR = BASE_DIR / "generated_sites"
STATIC_DIR = BASE_DIR / "static"

SITES_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)


def slugify(text: str) -> str:
    s = text.lower().strip()
    replacements = {
        "á": "a", "č": "c", "ď": "d", "é": "e", "ě": "e", "í": "i",
        "ň": "n", "ó": "o", "ř": "r", "š": "s", "ť": "t", "ú": "u",
        "ů": "u", "ý": "y", "ž": "z", "ğ": "g", "ü": "u", "ş": "s",
        "ı": "i", "ö": "o", "ç": "c",
    }
    for k, v in replacements.items():
        s = s.replace(k, v)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "prague-business"


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            external_id TEXT UNIQUE,
            name TEXT NOT NULL,
            slug TEXT,
            district TEXT,
            address TEXT,
            phone TEXT,
            email TEXT,
            website TEXT,
            website_status TEXT,
            website_badge TEXT,
            opportunity_score INTEGER DEFAULT 90,
            opportunity_reason TEXT,
            industry TEXT,
            sub_type TEXT,
            category_label_tr TEXT,
            category_label_cz TEXT,
            category_label_en TEXT,
            opening_hours TEXT,
            rating REAL DEFAULT 4.8,
            reviews_count INTEGER DEFAULT 50,
            lat REAL DEFAULT 50.0755,
            lon REAL DEFAULT 14.4378,
            google_maps_url TEXT,
            source TEXT,
            crm_status TEXT DEFAULT 'NEW',
            site_generated INTEGER DEFAULT 0,
            site_theme TEXT DEFAULT '',
            site_url TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()

    # Seed starter Prague leads if DB is empty
    cur.execute("SELECT COUNT(*) as cnt FROM leads")
    count = cur.fetchone()["cnt"]
    if count == 0:
        starters = get_curated_prague_starter_leads()
        for item in starters:
            slug = slugify(item["name"])
            cur.execute(
                """
                INSERT OR IGNORE INTO leads (
                    external_id, name, slug, district, address, phone, email,
                    website, website_status, website_badge, opportunity_score,
                    opportunity_reason, industry, sub_type, category_label_tr,
                    category_label_cz, category_label_en, opening_hours,
                    rating, reviews_count, lat, lon, google_maps_url, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item["external_id"], item["name"], slug, item["district"],
                    item["address"], item["phone"], item["email"], item["website"],
                    item["website_status"], item["website_badge"], item["opportunity_score"],
                    item["opportunity_reason"], item["industry"], item["sub_type"],
                    item["category_label_tr"], item["category_label_cz"], item["category_label_en"],
                    item["opening_hours"], item["rating"], item["reviews_count"],
                    item["lat"], item["lon"], item["google_maps_url"], item["source"],
                ),
            )
        conn.commit()

        # Pre-generate the first 2 starter websites so user can see instant live demos!
        cur.execute("SELECT * FROM leads ORDER BY id ASC LIMIT 2")
        first_leads = [dict(r) for r in cur.fetchall()]
        for ld in first_leads:
            build_and_save_site_for_lead(conn, ld)

    conn.close()


def get_setting(conn: sqlite3.Connection, key: str, default: str = "") -> str:
    cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cur.fetchone()
    return row["value"] if row else default


def set_setting(conn: sqlite3.Connection, key: str, value: str) -> None:
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )
    conn.commit()


def build_and_save_site_for_lead(
    conn: sqlite3.Connection,
    lead: Dict[str, Any],
    theme_override: Optional[str] = None,
) -> Dict[str, Any]:
    slug = lead.get("slug") or slugify(lead["name"])
    slug_folder = f"{slug}-{lead['id']}"
    site_dir = SITES_DIR / slug_folder
    site_dir.mkdir(parents=True, exist_ok=True)

    gemini_key = get_setting(conn, "gemini_api_key", os.environ.get("GEMINI_API_KEY", ""))
    html = generate_business_website_html(lead, theme_override=theme_override, gemini_api_key=gemini_key)

    index_file = site_dir / "index.html"
    index_file.write_text(html, encoding="utf-8")

    site_url = f"/sites/{slug_folder}/index.html"
    new_crm = lead.get("crm_status", "NEW")
    if new_crm == "NEW":
        new_crm = "SITE_READY"

    cur = conn.cursor()
    cur.execute(
        """
        UPDATE leads
        SET slug = ?, site_generated = 1, site_theme = ?, site_url = ?, crm_status = ?
        WHERE id = ?
        """,
        (slug, theme_override or "", site_url, new_crm, lead["id"]),
    )
    conn.commit()

    cur.execute("SELECT * FROM leads WHERE id = ?", (lead["id"],))
    updated_lead = dict(cur.fetchone())
    return updated_lead


class QuartierRequestHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        pass

    def _send_json(self, data: Any, status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> Dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw) if raw else {}

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # Serve generated sites
        if path.startswith("/sites/"):
            rel_path = path[len("/sites/"):]
            target_file = (SITES_DIR / rel_path).resolve()
            if str(target_file).startswith(str(SITES_DIR)) and target_file.is_file():
                content = target_file.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return
            self._send_json({"error": "Site not found"}, 404)
            return

        # API: Config
        if path == "/api/config":
            conn = get_db()
            gemini_key = get_setting(conn, "gemini_api_key", "")
            gplaces_key = get_setting(conn, "google_places_api_key", "")
            conn.close()
            self._send_json({
                "districts": PRAGUE_DISTRICTS,
                "themes": {k: v["name"] for k, v in COLOR_THEMES.items()},
                "has_gemini_key": bool(gemini_key),
                "has_google_places_key": bool(gplaces_key),
            })
            return

        # API: Leads List
        if path == "/api/leads":
            qs = urllib.parse.parse_qs(parsed.query)
            filter_web = (qs.get("website_filter", ["ALL"])[0] or "ALL").upper()
            filter_crm = (qs.get("crm_status", ["ALL"])[0] or "ALL").upper()
            search_q = (qs.get("q", [""])[0] or "").strip().lower()

            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT * FROM leads ORDER BY id DESC")
            rows = [dict(r) for r in cur.fetchall()]
            conn.close()

            filtered = []
            for r in rows:
                if filter_web == "NO_WEBSITE" and r["website_status"] not in ["NO_WEBSITE", "SOCIAL_ONLY", "WEAK_WEBSITE"]:
                    continue
                if filter_web == "ONLY_NONE" and r["website_status"] != "NO_WEBSITE":
                    continue
                if filter_crm != "ALL" and r["crm_status"] != filter_crm:
                    continue
                if search_q:
                    haystack = f"{r['name']} {r['district']} {r['category_label_tr']} {r['category_label_cz']} {r['address']}".lower()
                    if search_q not in haystack:
                        continue
                filtered.append(r)

            stats = {
                "total": len(rows),
                "no_website": sum(1 for x in rows if x["website_status"] in ["NO_WEBSITE", "SOCIAL_ONLY", "WEAK_WEBSITE"]),
                "sites_generated": sum(1 for x in rows if x["site_generated"] == 1),
                "contacted": sum(1 for x in rows if x["crm_status"] in ["CONTACTED", "WON"]),
                "won": sum(1 for x in rows if x["crm_status"] == "WON"),
            }
            self._send_json({"leads": filtered, "stats": stats})
            return

        # API: Lead Pitch & Details
        match_pitch = re.match(r"^/api/leads/(\d+)/pitch$", path)
        if match_pitch:
            lead_id = int(match_pitch.group(1))
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
            row = cur.fetchone()
            conn.close()
            if not row:
                self._send_json({"error": "Bulunamadı"}, 404)
                return
            lead = dict(row)
            host = self.headers.get("Host", "localhost:8765")
            preview_url = f"http://{host}{lead['site_url']}" if lead.get("site_url") else f"http://{host}"
            pitches = generate_prague_outreach_pitches(lead, preview_url)
            self._send_json({"lead": lead, "pitches": pitches})
            return

        # Serve Dashboard UI
        if path in ["/", "/index.html"]:
            index_html = (STATIC_DIR / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(index_html)))
            self.end_headers()
            self.wfile.write(index_html)
            return

        self._send_json({"error": "Not found"}, 404)

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        body = self._read_json_body()

        # Save API Settings
        if path == "/api/config":
            conn = get_db()
            if "gemini_api_key" in body:
                set_setting(conn, "gemini_api_key", body["gemini_api_key"].strip())
            if "google_places_api_key" in body:
                set_setting(conn, "google_places_api_key", body["google_places_api_key"].strip())
            conn.close()
            self._send_json({"ok": True})
            return

        # Scrape Prague Businesses (Hybrid: Free OSM Overpass or Google Places API)
        if path == "/api/scrape":
            district_key = body.get("district", "praha_2")
            query = body.get("query", "").strip()
            only_no_website = bool(body.get("only_no_website", False))

            conn = get_db()
            gplaces_key = get_setting(conn, "google_places_api_key", "")
            try:
                if gplaces_key:
                    scraped = scrape_google_places_api(district_key, query, gplaces_key, limit=30)
                else:
                    scraped = scrape_osm_prague(district_key, query, limit=45)
            except Exception as e:
                conn.close()
                self._send_json({"error": str(e)}, 500)
                return

            cur = conn.cursor()
            added_count = 0
            for item in scraped:
                if only_no_website and item["website_status"] not in ["NO_WEBSITE", "SOCIAL_ONLY"]:
                    continue
                slug = slugify(item["name"])
                cur.execute(
                    """
                    INSERT OR IGNORE INTO leads (
                        external_id, name, slug, district, address, phone, email,
                        website, website_status, website_badge, opportunity_score,
                        opportunity_reason, industry, sub_type, category_label_tr,
                        category_label_cz, category_label_en, opening_hours,
                        rating, reviews_count, lat, lon, google_maps_url, source
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        item["external_id"], item["name"], slug, item["district"],
                        item["address"], item["phone"], item["email"], item["website"],
                        item["website_status"], item["website_badge"], item["opportunity_score"],
                        item["opportunity_reason"], item["industry"], item["sub_type"],
                        item["category_label_tr"], item["category_label_cz"], item["category_label_en"],
                        item["opening_hours"], item["rating"], item["reviews_count"],
                        item["lat"], item["lon"], item["google_maps_url"], item["source"],
                    ),
                )
                if cur.rowcount > 0:
                    added_count += 1
            conn.commit()
            conn.close()
            self._send_json({
                "ok": True,
                "scraped_total": len(scraped),
                "added_new": added_count,
            })
            return

        # Add Custom Business & Auto-Generate Site
        if path == "/api/leads/custom":
            name = (body.get("name") or "").strip()
            if not name:
                self._send_json({"error": "İşletme adı gerekli"}, 400)
                return
            category_text = (body.get("category") or "Genel İşletme").strip()
            district_key = body.get("district", "praha_2")
            district_obj = PRAGUE_DISTRICTS.get(district_key, PRAGUE_DISTRICTS["praha_2"])
            address = (body.get("address") or district_obj["czech_name"]).strip()
            phone = (body.get("phone") or "+420 777 000 000").strip()

            ind_info = infer_industry_from_tags({"name": f"{name} {category_text}"}, category_text)
            web_info = classify_website_status("")
            slug = slugify(name)
            ext_id = f"custom_{slug}_{int(time.time() * 1000)}"
            gmaps_url = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(name + ' ' + address)}"

            conn = get_db()
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO leads (
                    external_id, name, slug, district, address, phone, email,
                    website, website_status, website_badge, opportunity_score,
                    opportunity_reason, industry, sub_type, category_label_tr,
                    category_label_cz, category_label_en, opening_hours,
                    rating, reviews_count, lat, lon, google_maps_url, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ext_id, name, slug, district_obj["czech_name"], address, phone, "",
                    "", web_info["status"], web_info["badge_tr"], 99,
                    "Manuel eklendi — Özel demo site üretildi.",
                    ind_info["industry"], ind_info["sub_type"],
                    ind_info["label_tr"], ind_info["label_cz"], ind_info["label_en"],
                    "Po-Pá 09:00-19:00, So 10:00-17:00", 4.9, 85,
                    district_obj["lat"], district_obj["lon"], gmaps_url, "Özel Eklendi",
                ),
            )
            new_id = cur.lastrowid
            conn.commit()

            cur.execute("SELECT * FROM leads WHERE id = ?", (new_id,))
            lead = dict(cur.fetchone())
            updated_lead = build_and_save_site_for_lead(conn, lead, theme_override=body.get("theme"))
            conn.close()
            self._send_json({"ok": True, "lead": updated_lead})
            return

        # Generate / Regenerate Website for a Lead
        match_gen = re.match(r"^/api/leads/(\d+)/generate$", path)
        if match_gen:
            lead_id = int(match_gen.group(1))
            theme_override = body.get("theme") or None
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
            row = cur.fetchone()
            if not row:
                conn.close()
                self._send_json({"error": "İşletme bulunamadı"}, 404)
                return
            lead = dict(row)
            updated_lead = build_and_save_site_for_lead(conn, lead, theme_override=theme_override)
            conn.close()

            host = self.headers.get("Host", "localhost:8765")
            preview_url = f"http://{host}{updated_lead['site_url']}"
            pitches = generate_prague_outreach_pitches(updated_lead, preview_url)
            self._send_json({"ok": True, "lead": updated_lead, "pitches": pitches})
            return

        # Update CRM Status
        match_status = re.match(r"^/api/leads/(\d+)/status$", path)
        if match_status:
            lead_id = int(match_status.group(1))
            new_status = body.get("crm_status", "NEW")
            conn = get_db()
            cur = conn.cursor()
            cur.execute("UPDATE leads SET crm_status = ? WHERE id = ?", (new_status, lead_id))
            conn.commit()
            cur.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
            updated_lead = dict(cur.fetchone())
            conn.close()
            self._send_json({"ok": True, "lead": updated_lead})
            return

        self._send_json({"error": "Unknown endpoint"}, 404)


def run_server(port: int = 8765) -> None:
    init_db()
    server = HTTPServer(("127.0.0.1", port), QuartierRequestHandler)
    print(f"🚀 Quartier Prague Agency Paneli çalışıyor: http://127.0.0.1:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server(8765)
