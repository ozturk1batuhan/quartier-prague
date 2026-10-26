# Quartier Prague — Yerel İşletme Web Stüdyosu 🇨🇿

Prag'daki (`Praha 1` – `Praha 10`) yerel işletmeleri **Firmy.cz** ve **Seznam.cz** üzerinden çift aşamalı doğrulamayla tarayan, **web sitesi olmayan** veya **sadece sosyal medya / ücretsiz alt domain kullanan** işletmeleri tespit edip her sektöre uygun **Çekçe (`CZ`) & İngilizce (`EN`) çift dilli editoryal web sitesi** üreten otomasyon sistemi.

---

## 💻 Windows'ta Çalıştırma (Tek Tıkla)

1. Bilgisayarınızda **Python 3.10+** kurulu olduğundan emin olun.
2. Projeyi indirin:
   ```bash
   git clone <REPO_URL>
   cd quartier_prague
   ```
3. Klasör içindeki **`start_windows.bat`** dosyasına çift tıklayın (veya terminalden çalıştırın):
   ```powershell
   pip install -r requirements.txt
   python server.py
   ```
4. Tarayıcınızda otomatik olarak **[http://127.0.0.1:8765](http://127.0.0.1:8765)** açılacaktır.

---

## 🍎 macOS / Linux'ta Çalıştırma

```bash
pip3 install -r requirements.txt
python3 server.py
```
Ardından tarayıcıda `http://127.0.0.1:8765` adresini açın.

---

## ✨ Temel Özellikler

* **Çift Katmanlı Canlı Doğrulama (`scraper.py` + `verifier.py`):**
  * **1. Aşama:** Çekya'nın resmi ticari rehberi `Firmy.cz` üzerinden aktif işletmeleri (telefon, adres, koordinat, mevcut web sitesi) çeker.
  * **2. Aşama:** Sadece sitesiz görünen adayları Çekya'nın arama motoru `Seznam.cz` üzerinden canlı sorgulayarak gizli `.cz` / `.com` siteleri eler; yalnızca gerçekten web sitesi olmayanları (`Doğrulandı: Web Sitesi Yok ✓`), sadece sosyal medya/Wolt kullananları veya ücretsiz alt domain (`*.webnode.cz`) kullananları listeler.
* **Her Sektöre Uygun Editoryal Web Stüdyosu (`site_generator.py`):**
  * Kafe/Fırın, Restoran/Bistro, Berber/Kuaför, Güzellik Salonu, Masaj/Spa, Oto Servis, Tesisat/Usta, Diş/Klinik ve Butik/Çiçekçi sektörlerine özel 2026/2027 yalın tasarım paletleri (`Nordic Alabaster`, `Botanical Sage`, `Warm Cashmere`, `Mineral Slate`, `Soft Pearl`).
  * Canlı **CZ / EN dil değiştirici**, Prag piyasasına uygun **Kč** fiyat listesi, online rezervasyon penceresi ve interaktif harita.
* **Hazır Satış & İletişim Kiti:**
  * Her işletmeye özel Çekçe ve İngilizce WhatsApp / Instagram DM / E-posta teklif metinleri.
