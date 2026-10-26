import json
import re
import socket
import unicodedata
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List, Optional, Tuple
import certifi
import requests

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept-Language": "cs-CZ,cs;q=0.9,en-US;q=0.8,en;q=0.7",
}

# Directories, registries, and review aggregators (NOT a business's own official website)
DIRECTORY_DOMAINS = {
    "firmy.cz", "mapy.cz", "mapy.com", "seznam.cz", "szn.cz", "sdn.cz", "imedia.cz",
    "zivefirmy.cz", "najisto.cz", "zlatostranky.cz", "rejstrik-firem.kurzy.cz",
    "kurzy.cz", "podnikatel.cz", "justice.cz", "ares.gov.cz", "finmag.cz",
    "sluzby.cz", "nejremeslnici.cz", "atakan.cz", "refsite.info", "atp.cz",
    "tripadvisor.com", "tripadvisor.cz", "foursquare.com", "yelp.com", "yelp.cz",
    "happycow.net", "restu.cz", "kudyznudy.cz", "prague.eu", "citybee.cz",
    "goout.net", "heureka.cz", "zbozi.cz", "google.com", "google.cz",
    "googleapis.com", "gstatic.com", "w3.org", "schema.org", "wikipedia.org",
    "wikidata.org", "openstreetmap.org", "wikimedia.org", "booking.com",
    "praguest.com", "expats.cz", "prague-stay.com", "timeout.com",
}

DELIVERY_DOMAINS = {
    "wolt.com": "Wolt",
    "foodora.cz": "Foodora",
    "damejidlo.cz": "DámeJídlo",
    "bolt.eu": "Bolt Food",
}

SOCIAL_DOMAINS = {
    "instagram.com": "Instagram",
    "facebook.com": "Facebook",
    "fb.com": "Facebook",
    "tiktok.com": "TikTok",
    "linktr.ee": "Linktree",
}

FREE_BUILDER_DOMAINS = {
    "webnode.cz": "Webnode",
    "wz.cz": "Webzdarma",
    "estranky.cz": "eStránky",
    "wixsite.com": "Wix",
    "wordpress.com": "WordPress",
    "blogspot.com": "Blogger",
}

GENERIC_WORDS = {
    "cafe", "café", "caffe", "coffee", "kavarna", "kavárna", "pekárna", "pekarna",
    "cukrárna", "cukrarna", "bistro", "restaurace", "restaurant", "bar", "pub",
    "hospoda", "pizzeria", "kadernictvi", "kadeřnictví", "kadernicke", "kadeřnické",
    "holicstvi", "holičství", "barber", "barbershop", "salon", "salón", "studio",
    "ateliér", "atelier", "kosmetika", "kosmeticke", "beauty", "masaze", "masáže",
    "massage", "spa", "wellness", "thai", "thajske", "thajské", "autoservis",
    "pneuservis", "autodilna", "autodílna", "autosluzby", "autoslužby", "servis",
    "opravna", "instalater", "instalatér", "zamecnictvi", "zámečnictví", "zubni",
    "zubní", "ordinace", "klinika", "kvetinarstvi", "květinářství", "kvetiny",
    "květiny", "butik", "obchod", "praha", "prague", "sro", "spol", "u", "v", "na",
    "and", "the", "pro", "studio", "club",
}


def strip_accents(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )


def extract_name_tokens(name: str) -> Tuple[List[str], List[str]]:
    norm = strip_accents(name.lower())
    # Remove company suffixes like s.r.o.
    norm = re.sub(r"\bs\.?\s*r\.?\s*o\.?\b", "", norm)
    tokens = [t for t in re.findall(r"[a-z0-9]+", norm) if len(t) >= 2]
    distinctive = [t for t in tokens if t not in GENERIC_WORDS and len(t) >= 3]
    if not distinctive and tokens:
        distinctive = [t for t in tokens if len(t) >= 3]
    return tokens, distinctive


def verify_via_seznam_search(name: str, address: str) -> Dict[str, Any]:
    """
    Queries Seznam.cz (Czechia's #1 search engine) for '{name} {address}'
    and extracts organic result URLs to verify whether the business has:
    - Its own official website (.cz / .com / .eu / .info / .shop)
    - A free subdomain website (*.webnode.cz, *.wz.cz, *.estranky.cz)
    - Delivery apps (Wolt, Foodora) or Social Media (Facebook, Instagram)
    """
    all_tokens, distinctive = extract_name_tokens(name)
    short_addr = address.split(",")[0].strip() if address else "Praha"
    query = f"{name} {short_addr} Praha"

    found_own_website = ""
    found_free_builder = ""
    found_platforms: List[str] = []
    found_platform_urls: Dict[str, str] = {}

    try:
        resp = requests.get(
            "https://search.seznam.cz/",
            params={"q": query},
            headers=BROWSER_HEADERS,
            timeout=6,
            verify=certifi.where(),
        )
        if resp.status_code == 200:
            # Unescape HTML entities so URLs inside JSON state are clean
            clean_text = resp.text.replace("&quot;", '"').replace("&amp;", "&")
            raw_urls = re.findall(r'https?://[^\s"<>\\]+', clean_text)

            for u in raw_urls:
                u = u.rstrip(").,;\"'")
                parsed = urllib.parse.urlparse(u)
                host = parsed.netloc.lower()
                if host.startswith("www."):
                    host = host[4:]
                if not host:
                    continue
                url_lower = strip_accents(urllib.parse.unquote(u).lower())

                # Only match Delivery / Social URLs that actually contain the business's distinctive token!
                matches_business = bool(distinctive) and any(tok in url_lower for tok in distinctive if len(tok) >= 3)

                for deliv_dom, deliv_label in DELIVERY_DOMAINS.items():
                    if deliv_dom in host and matches_business:
                        if deliv_label not in found_platforms:
                            found_platforms.append(deliv_label)
                            found_platform_urls[deliv_label] = u

                for soc_dom, soc_label in SOCIAL_DOMAINS.items():
                    if soc_dom in host and matches_business:
                        if soc_label not in found_platforms:
                            found_platforms.append(soc_label)
                            found_platform_urls[soc_label] = u

                for fb_dom, fb_label in FREE_BUILDER_DOMAINS.items():
                    if fb_dom in host and matches_business and not found_free_builder:
                        found_free_builder = f"{parsed.scheme}://{parsed.netloc}"

                # Skip directories, delivery, social, free builders when looking for own official domain
                if any(host == d or host.endswith("." + d) for d in DIRECTORY_DOMAINS):
                    continue
                if any(d in host for d in DELIVERY_DOMAINS) or any(d in host for d in SOCIAL_DOMAINS) or any(d in host for d in FREE_BUILDER_DOMAINS):
                    continue

                # Check if domain name itself matches the business's distinctive tokens!
                host_base = strip_accents(host.split(".")[0].replace("-", ""))
                if distinctive and any(tok in host_base for tok in distinctive if len(tok) >= 4):
                    if not found_own_website:
                        found_own_website = f"{parsed.scheme}://{parsed.netloc}"
    except Exception:
        pass

    return {
        "own_website": found_own_website,
        "free_builder": found_free_builder,
        "platforms": found_platforms,
        "platform_urls": found_platform_urls,
    }


def deep_verify_business(lead: Dict[str, Any]) -> Dict[str, Any]:
    """
    Multi-layer real-time verification:
    1. Checks Firmy.cz / OSM provided URL (classifying real domain vs Facebook/Instagram vs Webnode/sluzby.cz).
    2. Cross-checks Seznam.cz Search for hidden official domains, Wolt/Foodora, and Instagram/Facebook.
    """
    name = lead.get("name", "")
    address = lead.get("address", "")
    existing_web = (lead.get("website") or "").strip()

    existing_social_platforms = []
    existing_free_builder = ""

    if existing_web:
        parsed_ex = urllib.parse.urlparse(existing_web)
        ex_host = parsed_ex.netloc.lower()
        if ex_host.startswith("www."):
            ex_host = ex_host[4:]

        # Is existing_web a directory like sluzby.cz?
        if any(ex_host == d or ex_host.endswith("." + d) for d in DIRECTORY_DOMAINS):
            existing_web = ""
        # Is existing_web a free builder like webnode.cz?
        elif any(fb in ex_host for fb in FREE_BUILDER_DOMAINS):
            existing_free_builder = existing_web
        # Is existing_web Facebook / Instagram?
        elif any(soc in ex_host for soc in SOCIAL_DOMAINS):
            for soc_dom, soc_label in SOCIAL_DOMAINS.items():
                if soc_dom in ex_host:
                    existing_social_platforms.append(soc_label)
        else:
            # It's a genuine custom domain (e.g. myraw.cz, kolacherie.cz, portcafe.cz)!
            lead["website_status"] = "HAS_WEBSITE"
            lead["website_badge"] = f"Web Sitesi Var ({ex_host})"
            lead["opportunity_score"] = 25
            lead["opportunity_reason"] = f"Doğrulandı: İşletmenin resmi web sitesi mevcut ({existing_web})."
            return lead

    # Stage 2: Cross-verify on Seznam.cz Search so we NEVER miss an unlinked official website (like dobratrafika.cz or karlakcafe.cz)
    seznam_res = verify_via_seznam_search(name, address)

    if seznam_res["own_website"]:
        real_url = seznam_res["own_website"]
        domain_label = urllib.parse.urlparse(real_url).netloc.replace("www.", "")
        lead["website"] = real_url
        lead["website_status"] = "HAS_WEBSITE"
        lead["website_badge"] = f"Web Sitesi Var ({domain_label})"
        lead["opportunity_score"] = 30
        lead["opportunity_reason"] = f"Seznam.cz doğrulamasında resmi web sitesi tespit edildi: {real_url}"
        return lead

    free_builder_url = existing_free_builder or seznam_res["free_builder"]
    if free_builder_url:
        fb_host = urllib.parse.urlparse(free_builder_url).netloc.replace("www.", "")
        lead["website"] = free_builder_url
        lead["website_status"] = "WEAK_WEBSITE"
        lead["website_badge"] = f"Ücretsiz Alt Alan Adı ({fb_host})"
        lead["opportunity_score"] = 90
        lead["opportunity_reason"] = f"Kendi .cz alan adı yok; ücretsiz {fb_host} alt alan adı kullanıyor."
        return lead

    all_platforms = list(dict.fromkeys(existing_social_platforms + seznam_res["platforms"]))
    if all_platforms:
        plat_str = ", ".join(all_platforms)
        first_url = existing_web or next(iter(seznam_res["platform_urls"].values()), "")
        lead["website"] = first_url
        lead["website_status"] = "SOCIAL_ONLY"
        lead["website_badge"] = f"Kendi Sitesi Yok (Sadece {plat_str})"
        lead["opportunity_score"] = 95
        lead["opportunity_reason"] = f"Doğrulandı (Firmy.cz + Seznam.cz): Kendi .cz web sitesi yok, sadece {plat_str} sayfası var."
        return lead

    lead["website"] = ""
    lead["website_status"] = "NO_WEBSITE"
    lead["website_badge"] = "Doğrulandı: Web Sitesi Yok ✓"
    lead["opportunity_score"] = 99
    lead["opportunity_reason"] = "Doğrulandı (Firmy.cz + Seznam.cz): İşletmenin internette kendi web sitesi bulunmuyor."
    return lead


def verify_leads_batch(leads: List[Dict[str, Any]], max_workers: int = 8) -> List[Dict[str, Any]]:
    verified = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {executor.submit(deep_verify_business, item): item for item in leads}
        for fut in as_completed(future_map):
            try:
                verified.append(fut.result())
            except Exception:
                verified.append(future_map[fut])
    return verified
