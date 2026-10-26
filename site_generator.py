import json
import os
import re
from typing import Dict, Any, List, Optional

# 2026-2027 Awwwards / Editorial Minimalist Color Palettes (No harsh black/orange!)
COLOR_THEMES = {
    "nordic": {
        "name": "Nordic Alabaster (Yalın Monokrom & Keten)",
        "page_bg": "bg-[#FAF9F5] text-[#141413]",
        "nav_bg": "bg-[#FAF9F5]/85 border-[#E6E4DD]",
        "hero_badge": "bg-[#EFECE6] text-[#4A4945] border-[#E0DDD5]",
        "primary_btn": "bg-[#141413] hover:bg-[#2C2C2A] text-white",
        "secondary_btn": "bg-white hover:bg-[#F2F0EA] text-[#141413] border-[#E2DFD7]",
        "section_alt": "bg-[#F2F0EA]",
        "card_bg": "bg-white border-[#E6E4DD]",
        "accent_text": "text-[#141413]",
        "muted_text": "text-[#686662]",
        "pill_bg": "bg-[#F2F0EA] text-[#141413]",
    },
    "sage": {
        "name": "Botanical Sage (Okaliptüs Yeşili & Fildişi)",
        "page_bg": "bg-[#F7F9F7] text-[#13221B]",
        "nav_bg": "bg-[#F7F9F7]/85 border-[#E1E8E3]",
        "hero_badge": "bg-[#E6F0EA] text-[#1F4B38] border-[#CFE2D7]",
        "primary_btn": "bg-[#1B4332] hover:bg-[#23533F] text-white",
        "secondary_btn": "bg-white hover:bg-[#EDF3EF] text-[#13221B] border-[#DCE5DF]",
        "section_alt": "bg-[#EDF3EF]",
        "card_bg": "bg-white border-[#E1E8E3]",
        "accent_text": "text-[#1B4332]",
        "muted_text": "text-[#56695F]",
        "pill_bg": "bg-[#E6F0EA] text-[#1B4332]",
    },
    "sand": {
        "name": "Warm Cashmere (Kaşmir Kumu & Toprak)",
        "page_bg": "bg-[#FBF9F5] text-[#231F1D]",
        "nav_bg": "bg-[#FBF9F5]/85 border-[#EBE5DC]",
        "hero_badge": "bg-[#F2ECE1] text-[#5C4938] border-[#E4DACB]",
        "primary_btn": "bg-[#3E2F26] hover:bg-[#523F34] text-white",
        "secondary_btn": "bg-white hover:bg-[#F5EFE6] text-[#231F1D] border-[#E6DFD5]",
        "section_alt": "bg-[#F4EFE6]",
        "card_bg": "bg-white border-[#EBE5DC]",
        "accent_text": "text-[#5C4033]",
        "muted_text": "text-[#6E655F]",
        "pill_bg": "bg-[#F2ECE1] text-[#3E2F26]",
    },
    "ocean": {
        "name": "Mineral Slate (Buz Mavisi & Derin İndigo)",
        "page_bg": "bg-[#F8FAFC] text-[#0F172A]",
        "nav_bg": "bg-[#F8FAFC]/85 border-[#E2E8F0]",
        "hero_badge": "bg-[#EEF2FF] text-[#3730A3] border-[#E0E7FF]",
        "primary_btn": "bg-[#1E293B] hover:bg-[#334155] text-white",
        "secondary_btn": "bg-white hover:bg-[#F1F5F9] text-[#0F172A] border-[#E2E8F0]",
        "section_alt": "bg-[#F1F5F9]",
        "card_bg": "bg-white border-[#E2E8F0]",
        "accent_text": "text-[#3730A3]",
        "muted_text": "text-[#64748B]",
        "pill_bg": "bg-[#EEF2FF] text-[#3730A3]",
    },
    "pearl": {
        "name": "Soft Pearl (İnci Beyazı & Pudra Mürdüm)",
        "page_bg": "bg-[#FCF9FA] text-[#241920]",
        "nav_bg": "bg-[#FCF9FA]/85 border-[#EFE6EA]",
        "hero_badge": "bg-[#F7EDF2] text-[#6B3B53] border-[#EBD8E1]",
        "primary_btn": "bg-[#3D2632] hover:bg-[#523444] text-white",
        "secondary_btn": "bg-white hover:bg-[#F7EFF3] text-[#241920] border-[#EADEE3]",
        "section_alt": "bg-[#F6EEF2]",
        "card_bg": "bg-white border-[#EFE6EA]",
        "accent_text": "text-[#6B3B53]",
        "muted_text": "text-[#73626A]",
        "pill_bg": "bg-[#F7EDF2] text-[#3D2632]",
    },
}

INDUSTRY_PRESETS: Dict[str, Dict[str, Any]] = {
    "cafe": {
        "theme": "sand",
        "hero_img": "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?auto=format&fit=crop&w=1400&q=85",
        "gallery": [
            "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1555507036-ab1f4038808a?auto=format&fit=crop&w=800&q=80",
        ],
        "badge_cz": "Výběrová káva & Řemeslná pekárna",
        "badge_en": "Specialty Coffee & Artisan Bakery",
        "headline_cz": "Klidné místo pro skvělou kávu v srdci čtvrti {district}",
        "headline_en": "A Calm Sanctuary for Specialty Coffee in {district}",
        "subheadline_cz": "Čerstvě pražená výběrová káva, domácí kváskové pečivo a vzdušný prostor pro vaše ráno i odpolední setkání.",
        "subheadline_en": "Single-origin specialty coffee, warm sourdough pastries, and a light-filled space designed for slow mornings.",
        "cta_primary_cz": "Rezervovat stůl",
        "cta_primary_en": "Reserve a Table",
        "cta_secondary_cz": "Prohlédnout nabídku",
        "cta_secondary_en": "Explore Menu",
        "features": [
            {"icon": "coffee", "title_cz": "Výběrová pražírna", "title_en": "Specialty Roast", "desc_cz": "Spolupracujeme s lokálními pražírnami pro čistou a vyváženou chuť.", "desc_en": "Sourced from independent micro-roasters and brewed with precision."},
            {"icon": "croissant", "title_cz": "Pečeme každé ráno", "title_en": "Baked Fresh Daily", "desc_cz": "Máslové croissanty, kváskový chléb a sezónní dezerty přímo z pece.", "desc_en": "Artisan pastries, sourdough toasts, and seasonal cakes made in-house."},
            {"icon": "sun", "title_cz": "Světlý a klidný interiér", "title_en": "Calm & Minimal Space", "desc_cz": "Příjemná atmosféra s rychlou Wi-Fi a zahrádkou ve vnitrobloku.", "desc_en": "Thoughtfully designed seating, fast Wi-Fi, and a quiet courtyard."},
        ],
        "services": [
            {"name_cz": "Espresso / Double Espresso", "name_en": "Espresso / Double Shot", "desc_cz": "100% výběrová Arabica s tóny hořké čokolády", "desc_en": "Single-origin specialty espresso", "price": "65 / 78 Kč"},
            {"name_cz": "Cappuccino / Flat White", "name_en": "Cappuccino / Flat White", "desc_cz": "Plnotučné farmářské mléko nebo ovesná alternativa", "desc_en": "Organic farm milk or Minor Figures oat milk", "price": "85 / 95 Kč"},
            {"name_cz": "Máslový croissant & Káva", "name_en": "Artisan Croissant & Coffee", "desc_cz": "Čerstvě upečený croissant + káva dle výběru", "desc_en": "Warm flaky pastry paired with your morning coffee", "price": "145 Kč"},
            {"name_cz": "Avokádový kváskový chléb", "name_en": "Sourdough Avocado Toast", "desc_cz": "Zastřené bio vejce, pražená semínka, mikrobyllinky", "desc_en": "Poached organic egg, toasted seeds & microgreens", "price": "215 Kč"},
            {"name_cz": "Domácí koláč / Dezert dne", "name_en": "Seasonal Tart of the Day", "desc_cz": "Pečeme denně z čerstvého ovoce a tvarohu", "desc_en": "Prepared daily with fresh seasonal fruits", "price": "115 Kč"},
            {"name_cz": "Ceremoniální Matcha Latte", "name_en": "Ceremonial Organic Matcha", "desc_cz": "Japonská bio matcha šlehaná za tepla nebo na ledu", "desc_en": "Whisked ceremonial grade Uji matcha, hot or iced", "price": "105 Kč"},
        ],
        "reviews": [
            {"author": "Markéta Svobodová", "text_cz": "Krásný, čistý prostor a suverénně nejlepší flat white v celé čtvrti.", "text_en": "Beautiful, calm space and hands-down the best flat white in the neighborhood."},
            {"author": "Liam O'Connor", "text_cz": "Skvělé místo na klidnou snídani v Praze. Pečivo bylo čerstvé a káva perfektní.", "text_en": "Wonderful spot for a peaceful breakfast in Prague. Pastries and coffee were 10/10."},
        ],
    },
    "restaurant": {
        "theme": "sand",
        "hero_img": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=1400&q=85",
        "gallery": [
            "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1559339352-11d035aa65de?auto=format&fit=crop&w=800&q=80",
        ],
        "badge_cz": "Moderní bistro & Sezónní kuchyně",
        "badge_en": "Modern Bistro & Seasonal Dining",
        "headline_cz": "Poctivá sezónní kuchyně v příjemné atmosféře čtvrti {district}",
        "headline_en": "Thoughtful Seasonal Dining in the Heart of {district}",
        "subheadline_cz": "Vaříme z čerstvých surovin od lokálních farmářů. Zastavte se na polední menu, sklenku naturálního vína nebo večeři.",
        "subheadline_en": "Crafted daily with fresh ingredients from local Czech producers. Join us for weekday lunch, natural wines, and relaxed dinners.",
        "cta_primary_cz": "Rezervovat stůl",
        "cta_primary_en": "Book a Table",
        "cta_secondary_cz": "Aktuální menu",
        "cta_secondary_en": "View Menu",
        "features": [
            {"icon": "utensils", "title_cz": "Sezónní suroviny", "title_en": "Farm-to-Table Ingredients", "desc_cz": "Jídelní lístek obměňujeme podle čerstvé nabídky lokálních pěstitelů.", "desc_en": "Our menu evolves with the seasons and local harvest."},
            {"icon": "wine", "title_cz": "Vína & Řemeslné pivo", "title_en": "Curated Wines & Craft Beer", "desc_cz": "Pečlivě vybraná moravská i evropská vína a skvěle ošetřený ležák.", "desc_en": "Moravian natural wines and crisp Czech draft beer."},
            {"icon": "calendar", "title_cz": "Snadná online rezervace", "title_en": "Seamless Table Booking", "desc_cz": "Rezervujte si stůl online během několika vteřin bez čekání.", "desc_en": "Reserve your table online in seconds for lunch or dinner."},
        ],
        "services": [
            {"name_cz": "Polední menu (Polévka + Hlavní chod)", "name_en": "Weekday Lunch Menu (Soup + Main)", "desc_cz": "Podáváme Po–Pá 11:00–14:30 z čerstvých surovin", "desc_en": "Served Mon–Fri 11:00–14:30", "price": "195 Kč"},
            {"name_cz": "Pomalu tažená hovězí líčka na víně", "name_en": "Slow-Braised Beef Cheeks", "desc_cz": "Jemné bramborové pyré, kořenová zelenina, silný demi-glace", "desc_en": "Creamy potato purée, roasted root vegetables & rich jus", "price": "325 Kč"},
            {"name_cz": "Grilovaný filet ze pstruha / Ryba dne", "name_en": "Pan-Seared Local Trout Fillet", "desc_cz": "Máslová emulze, pečené grenaille a sezónní zelenina", "desc_en": "Herb butter emulsion, roasted baby potatoes & greens", "price": "345 Kč"},
            {"name_cz": "Domácí těstoviny s lanýžovým krémem", "name_en": "Handmade Truffle Tagliatelle", "desc_cz": "Čerstvé těstoviny, lesní houby, parmezán 24m", "desc_en": "Fresh pasta, wild mushrooms & 24-month aged Parmesan", "price": "275 Kč"},
            {"name_cz": "Čepovaný ležák 0,5l / Domácí limonáda", "name_en": "Draft Czech Lager / House Lemonade", "desc_cz": "Tradičně čepované pivo nebo sezónní ovocný sirup", "desc_en": "Crisp local lager or house-made fruit cordial", "price": "69 Kč"},
            {"name_cz": "Dezert šéfkuchaře", "name_en": "Chef's Seasonal Dessert", "desc_cz": "Sladká tečka dle denní nabídky", "desc_en": "Prepared fresh each morning by our pastry chef", "price": "135 Kč"},
        ],
        "reviews": [
            {"author": "Tomáš Dvořák", "text_cz": "Krásný vzdušný interiér, vynikající jídlo a velmi pozorná obsluha.", "text_en": "Light, airy interior, outstanding food, and very attentive service."},
            {"author": "Elena Rossi", "text_cz": "Jedno z nejlepších bister v Praze! Skvělý poměr ceny a kvality.", "text_en": "One of the finest neighborhood bistros in Prague. Truly memorable meal."},
        ],
    },
    "barber_hair": {
        "theme": "nordic",
        "hero_img": "https://images.unsplash.com/photo-1585747860715-2ba37e788b70?auto=format&fit=crop&w=1400&q=85",
        "gallery": [
            "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1622286342621-4bd786c2447c?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=800&q=80",
        ],
        "badge_cz": "Kadeřnický & Barber Ateliér",
        "badge_en": "Minimalist Hair & Grooming Studio",
        "headline_cz": "Nadčasový střih a osobní péče v lokalitě {district}",
        "headline_en": "Timeless Haircuts & Tailored Grooming in {district}",
        "subheadline_cz": "Klidné prostředí bez spěchu, detailní konzultace a přírodní vlasová kosmetika. Mluvíme česky i anglicky.",
        "subheadline_en": "An unhurried studio experience, detailed style consultation, and natural hair care. Czech and English speaking stylists.",
        "cta_primary_cz": "Rezervovat termín",
        "cta_primary_en": "Book Appointment",
        "cta_secondary_cz": "Ceník služeb",
        "cta_secondary_en": "Service Menu",
        "features": [
            {"icon": "scissors", "title_cz": "Střih na míru", "title_en": "Bespoke Precision Cut", "desc_cz": "Každý střih začíná pečlivou konzultací podle tvaru obličeje a typu vlasů.", "desc_en": "Every visit begins with a personal consultation tailored to your features."},
            {"icon": "sparkles", "title_cz": "Šetrná přírodní kosmetika", "title_en": "Clean Botanical Products", "desc_cz": "Používáme špičkovou udržitelnou kosmetiku šetrnou k pokožce.", "desc_en": "Formulated with organic botanicals for healthy hair and scalp."},
            {"icon": "globe", "title_cz": "Česky & English Friendly", "title_en": "Bilingual Stylists", "desc_cz": "Pohodlná komunikace v češtině i angličtině a online rezervace.", "desc_en": "Effortless communication in Czech and English with instant booking."},
        ],
        "services": [
            {"name_cz": "Pánský střih & Styling", "name_en": "Men's Tailored Cut & Styling", "desc_cz": "Konzultace, mytí, masáž hlavy, precizní střih a finální úprava (45 min)", "desc_en": "Consultation, wash, scalp massage, precision cut & finish (45 min)", "price": "590 Kč"},
            {"name_cz": "Úprava vousů & Hot Towel rituál", "name_en": "Beard Sculpting & Hot Towel Ritual", "desc_cz": "Tvarování vousů, napaření horkým ručníkem a výživný olej (30 min)", "desc_en": "Beard shaping, aromatic hot towel steam & organic oil (30 min)", "price": "450 Kč"},
            {"name_cz": "Kompletní péče (Vlasy + Vousy)", "name_en": "Complete Studio Ritual (Hair + Beard)", "desc_cz": "Střih vlasů, úprava vousů, masáž hlavy a výběrová káva (75 min)", "desc_en": "Full haircut, beard ritual, relaxing massage & specialty coffee (75 min)", "price": "890 Kč"},
            {"name_cz": "Dámský střih, mytí & foukaná", "name_en": "Women's Cut, Wash & Signature Blowout", "desc_cz": "Regenerační lázeň, střih na míru a přirozený styling (60 min)", "desc_en": "Deep hydration bath, tailored cut & effortless styling (60 min)", "price": "950 Kč"},
            {"name_cz": "Barvení / Balayage / Tónování", "name_en": "Natural Balayage & Glossing", "desc_cz": "Šetrné zesvětlení a tónování pro přirozený lesk vlasů", "desc_en": "Gentle hand-painted highlights and bond-building gloss", "price": "od 1 690 Kč"},
            {"name_cz": "Studentský střih", "name_en": "Student Haircut", "desc_cz": "Kompletní střih a mytí se studentskou slevou", "desc_en": "Full wash, cut, and style for students", "price": "450 Kč"},
        ],
        "reviews": [
            {"author": "Jakub Novotný", "text_cz": "Čistý minimalistický salon, žádný hluk a naprosto precizní střih.", "text_en": "Clean minimalist studio, calm vibe, and the most precise haircut I've had in Prague."},
            {"author": "David Miller", "text_cz": "Skvělá domluva anglicky i česky. Odcházel jsem maximálně spokojený.", "text_en": "Seamless consultation in English and top-tier attention to detail."},
        ],
    },
    "beauty_salon": {
        "theme": "pearl",
        "hero_img": "https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=1400&q=85",
        "gallery": [
            "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1487412947147-5cebf100ffc2?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1519014816548-bf5fe059798b?auto=format&fit=crop&w=800&q=80",
        ],
        "badge_cz": "Estetické & Kosmetické Studio",
        "badge_en": "Holistic Beauty & Nail Sanctuary",
        "headline_cz": "Jemná péče o pleť a přirozená krása v lokalitě {district}",
        "headline_en": "Mindful Skincare & Natural Aesthetics in {district}",
        "subheadline_cz": "Klidný estetický prostor zaměřený na zdraví pleti, precizní manikúru a přirozený vzhled. Rezervujte si svůj čas pro sebe.",
        "subheadline_en": "A serene studio dedicated to skin health, precision nail care, and understated beauty.",
        "cta_primary_cz": "Rezervovat ošetření",
        "cta_primary_en": "Book Treatment",
        "cta_secondary_cz": "Přehled péče",
        "cta_secondary_en": "Treatment Menu",
        "features": [
            {"icon": "heart", "title_cz": "Holistický přístup", "title_en": "Skin-First Philosophy", "desc_cz": "Každé ošetření sestavujeme individuálně podle aktuální kondice pleti.", "desc_en": "Treatments tailored to restore your skin's natural barrier and glow."},
            {"icon": "shield-check", "title_cz": "Čistá dermokosmetika", "title_en": "Medical-Grade & Clean", "desc_cz": "Sterilní nástroje a klinicky ověřené netoxické produkty.", "desc_en": "Hospital-grade sterilization and non-toxic botanical formulas."},
            {"icon": "clock", "title_cz": "Soukromí a klid", "title_en": "Private & Unhurried", "desc_cz": "Individuální péče v tichém prostředí bez čekání.", "desc_en": "One-on-one appointments in a calm, sun-lit studio."},
        ],
        "services": [
            {"name_cz": "Hloubkové hydratační ošetření pleti (75 min)", "name_en": "Bespoke Facial & Lymphatic Massage (75 min)", "desc_cz": "Jemné čištění, enzymatický peeling, masáž obličeje a aktivní sérum", "desc_en": "Gentle cleansing, enzymatic peel, sculptural massage & serum mask", "price": "1 290 Kč"},
            {"name_cz": "Přirozená manikúra & BIAB / Gel lak", "name_en": "Minimalist Manicure & BIAB Gel", "desc_cz": "Precizní úprava kůžičky, zpevnění přírodních nehtů a jemný odstín", "desc_en": "Cuticle care, natural nail strengthening & sheer or classic tones", "price": "690 Kč"},
            {"name_cz": "Spa Pedikúra & Relaxační péče", "name_en": "Botanical Spa Pedicure", "desc_cz": "Bylinná lázeň, ošetření chodidel, peeling a lakování", "desc_en": "Warm herbal soak, smoothing care, organic scrub & polish", "price": "850 Kč"},
            {"name_cz": "Lash Lifting & Laminace obočí", "name_en": "Keratin Lash Lift & Brow Sculpt", "desc_cz": "Přirozené zvýraznění a výživa řas i obočí bez zatížení", "desc_en": "Natural curl, tint, and keratin nourishment", "price": "1 190 Kč"},
        ],
        "reviews": [
            {"author": "Tereza Králová", "text_cz": "Nádherný minimalistický salon, kde si člověk skutečně odpočine.", "text_en": "A gorgeous minimalist studio where you genuinely unwind."},
            {"author": "Sophie Laurent", "text_cz": "Nejjemnější kosmetika a manikúra v Praze. Velmi vkusné prostředí.", "text_en": "The most refined facial and manicure in Prague. Truly tasteful aesthetic."},
        ],
    },
    "massage_spa": {
        "theme": "sage",
        "hero_img": "https://images.unsplash.com/photo-1544161515-4ab6ce6db874?auto=format&fit=crop&w=1400&q=85",
        "gallery": [
            "https://images.unsplash.com/photo-1600334089648-b0d9d3028eb2?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1519823551278-64ac92734fb1?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1540555700478-4be289fbecef?auto=format&fit=crop&w=800&q=80",
        ],
        "badge_cz": "Terapeutické Masáže & Relaxace",
        "badge_en": "Therapeutic Massage & Mindful Spa",
        "headline_cz": "Ticho, dotek a hluboké uvolnění v lokalitě {district}",
        "headline_en": "Stillness, Touch & Deep Restoration in {district}",
        "subheadline_cz": "Ulevte unaveným zádům a zklidněte mysl. Certifikovaní terapeuti, teplé bio oleje a soukromé relaxační místnosti.",
        "subheadline_en": "Release physical tension and quiet your mind. Certified bodyworkers, warm organic oils, and tranquil private suites.",
        "cta_primary_cz": "Rezervovat masáž",
        "cta_primary_en": "Book Session",
        "cta_secondary_cz": "Přehled rituálů",
        "cta_secondary_en": "View Rituals",
        "features": [
            {"icon": "feather", "title_cz": "Terapeutická odbornost", "title_en": "Clinical & Holistic Touch", "desc_cz": "Cílené uvolnění hlubokých svalových vrstev, šíje a beder.", "desc_en": "Targeted myofascial release for neck, shoulders, and lower back."},
            {"icon": "droplet", "title_cz": "Teplé organické oleje", "title_en": "Warm Botanical Oils", "desc_cz": "Za studena lisované mandlové a jojobové oleje s esencí eukalyptu.", "desc_en": "Cold-pressed almond and jojoba oils infused with calming botanicals."},
            {"icon": "coffee", "title_cz": "Bylinný čaj po masáži", "title_en": "Post-Session Tea Ritual", "desc_cz": "Každá návštěva končí šálkem sypaného bylinného čaje v klidové zóně.", "desc_en": "Unwind after your session with freshly brewed organic herbal tea."},
        ],
        "services": [
            {"name_cz": "Hloubková terapeutická masáž celého těla (60 min)", "name_en": "Deep Tissue & Full Body Restoration (60 min)", "desc_cz": "Komplexní uvolnění ztuhlých svalů a podpora regenerace", "desc_en": "Comprehensive muscle tension release and posture relief", "price": "990 Kč"},
            {"name_cz": "Aroma rituál s teplým bio olejem (60 / 90 min)", "name_en": "Warm Botanical Oil Ritual (60 / 90 min)", "desc_cz": "Plynulá relaxační masáž pro odbourání stresu a únavy", "desc_en": "Flowing, deeply calming massage with warm aromatic oils", "price": "1 050 / 1 490 Kč"},
            {"name_cz": "Cílená terapie zad, šíje a hlavy (45 min)", "name_en": "Back, Neck & Cranial Relief (45 min)", "desc_cz": "Okamžitá úleva při sedavém zaměstnání a migrénách", "desc_en": "Focused relief for desk tension and headaches", "price": "790 Kč"},
            {"name_cz": "Masáž lávovými kameny & Bylinné měšce (90 min)", "name_en": "Hot Volcanic Stone & Herbal Compress (90 min)", "desc_cz": "Hloubkové prohřátí svalů a kloubů přírodními kameny", "desc_en": "Soothing thermal stone therapy for deep relaxation", "price": "1 590 Kč"},
        ],
        "reviews": [
            {"author": "Petra Němcová", "text_cz": "Oáza klidu uprostřed Prahy. Po hodině masáže jsem se cítila jako znovuzrozená.", "text_en": "An oasis of calm in the middle of Prague. Left feeling completely renewed."},
            {"author": "James Thornton", "text_cz": "Vynikající terapeutická masáž a nádherný čistý interiér.", "text_en": "Exceptional therapeutic massage and a serene, spotless interior."},
        ],
    },
    "auto_service": {
        "theme": "ocean",
        "hero_img": "https://images.unsplash.com/photo-1619642751034-765dfdf7c58e?auto=format&fit=crop&w=1400&q=85",
        "gallery": [
            "https://images.unsplash.com/photo-1487754180451-c456f719a1fc?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1530046339160-ce3e530c7d2f?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1625047509168-a7026f36de04?auto=format&fit=crop&w=800&q=80",
        ],
        "badge_cz": "Moderní Autoservis & Diagnostika",
        "badge_en": "Modern Auto Care & Diagnostics",
        "headline_cz": "Transparentní péče o váš vůz v lokalitě {district}",
        "headline_en": "Transparent, Modern Auto Service in {district}",
        "subheadline_cz": "Pravidelný servis, pneuservis a přesná diagnostika všech značek. Jasná kalkulace předem, fotodokumentace opravy a záruka.",
        "subheadline_en": "Scheduled maintenance, tire care, and computer diagnostics for all makes. Upfront digital quotes and photo reports.",
        "cta_primary_cz": "Rezervovat termín servisu",
        "cta_primary_en": "Schedule Service",
        "cta_secondary_cz": "Ceník úkonů",
        "cta_secondary_en": "Transparent Pricing",
        "features": [
            {"icon": "file-check", "title_cz": "Kalkulace vždy předem", "title_en": "Upfront Digital Approval", "desc_cz": "Žádné překvapení na faktuře. Každou položku schvalujete předem.", "desc_en": "We send a clear quote for your approval before touching a bolt."},
            {"icon": "cpu", "title_cz": "Přesná diagnostika", "title_en": "OEM-Level Diagnostics", "desc_cz": "Moderní vybavení pro evropské i asijské vozy bez ztráty záruky.", "desc_en": "Advanced diagnostic systems for Škoda, VW, BMW, Audi & Toyota."},
            {"icon": "clock", "title_cz": "Servis v ten samý den", "title_en": "Same-Day Turnaround", "desc_cz": "Běžný servis, brzdy a přezutí vyřešíme během jediného dne.", "desc_en": "Most maintenance, brakes, and tire services completed same day."},
        ],
        "services": [
            {"name_cz": "Kompletní přezutí a vyvážení kol (4 ks)", "name_en": "Complete Tire Swap & Digital Balancing", "desc_cz": "Demontáž, montáž, vyvážení a kontrola brzdového obložení", "desc_en": "Mount, precision balance, pressure check & visual brake inspection", "price": "od 890 Kč"},
            {"name_cz": "Roční servis: Výměna oleje, filtrů & prohlídka", "name_en": "Annual Oil Service & 25-Point Inspection", "desc_cz": "Výměna oleje a filtrů + kontrola podvozku, baterie a kapalin", "desc_en": "Oil & filter change plus suspension, battery, and fluid check", "price": "od 1 490 Kč"},
            {"name_cz": "Počítačová diagnostika řídících jednotek", "name_en": "Full Computer OBD-II System Scan", "desc_cz": "Výpis chybových kódů, živá data a návrh efektivního řešení", "desc_en": "Complete fault report and honest repair recommendation", "price": "590 Kč"},
            {"name_cz": "Čištění a plnění klimatizace + Ozón", "name_en": "A/C Recharge & Ozone Cabin Sanitization", "desc_cz": "Test těsnosti, doplnění chladiva a dezinfekce interiéru", "desc_en": "Vacuum test, refrigerant refill, and antibacterial ozone treatment", "price": "od 990 Kč"},
            {"name_cz": "Příprava a vyřízení STK + Emise", "name_en": "Complete STK / MOT Inspection Handling", "desc_cz": "Kontrola vozu na dílně a absolvování oficiální STK za vás", "desc_en": "Pre-check and full handling of official Czech technical inspection", "price": "od 2 400 Kč"},
        ],
        "reviews": [
            {"author": "Martin Procházka", "text_cz": "Čistá dílna, profesionální jednání a férové ceny. Vše poslali předem ke schválení.", "text_en": "Clean workshop, honest communication, and zero surprise charges."},
            {"author": "Chris Evans", "text_cz": "Skvělá komunikace anglicky, rychlá výměna brzd a férový přístup.", "text_en": "Fluent English communication and fast, transparent brake service."},
        ],
    },
    "craft_trades": {
        "theme": "ocean",
        "hero_img": "https://images.unsplash.com/photo-1581578731548-c64695cc6952?auto=format&fit=crop&w=1400&q=85",
        "gallery": [
            "https://images.unsplash.com/photo-1621905251189-08b45d6a269e?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80",
        ],
        "badge_cz": "Technický Servis & Řemeslné Práce",
        "badge_en": "Trusted Home & Technical Services",
        "headline_cz": "Spolehlivé opravy a instalace v lokalitě {district}",
        "headline_en": "Dependable Repairs & Installations in {district}",
        "subheadline_cz": "Dochvilnost, čistá práce a pevná cena před zahájením opravy. Pomáháme domácnostem i firmám po celé Praze.",
        "subheadline_en": "Punctual arrival, spotless workmanship, and fixed quotes before we start. Serving homes and offices across Prague.",
        "cta_primary_cz": "Objednat technika",
        "cta_primary_en": "Request Technician",
        "cta_secondary_cz": "Ceník prací",
        "cta_secondary_en": "Service Rates",
        "features": [
            {"icon": "clock", "title_cz": "Přesný čas příjezdu", "title_en": "Punctual Arrival", "desc_cz": "Vážíme si vašeho času. Vždy dorazíme v dohodnutou hodinu.", "desc_en": "We respect your schedule and arrive within the confirmed window."},
            {"icon": "shield-check", "title_cz": "Záruka & Čistota", "title_en": "Clean & Guaranteed", "desc_cz": "Používáme návleky, pracujeme čistě a poskytujeme plnou záruku.", "desc_en": "Shoe covers worn indoors, tidy workspace, and full warranty."},
            {"icon": "check-circle", "title_cz": "Jasná cena předem", "title_en": "Fixed Upfront Quote", "desc_cz": "Cenu znáte hned po posouzení na místě ještě před zahájením práce.", "desc_en": "Clear pricing confirmed on-site before any work begins."},
        ],
        "services": [
            {"name_cz": "Výjezd technika po Praze & Diagnostika", "name_en": "Technician Visit & On-Site Quote", "desc_cz": "Příjezd, odborné posouzení stavu a pevná cenová kalkulace", "desc_en": "Arrival in Prague, inspection, and fixed-price quotation", "price": "490 Kč"},
            {"name_cz": "Odborná oprava / Montáž (1 hodina práce)", "name_en": "Certified Repair & Installation (Hourly)", "desc_cz": "Práce zkušeného technika s profesionálním vybavením", "desc_en": "Professional labor with certified tools and warranty", "price": "790 Kč / hod"},
            {"name_cz": "Prioritní / Havarijní výjezd ještě dnes", "name_en": "Same-Day Priority Call-Out", "desc_cz": "Rychlé vyřešení akutní poruchy v ten samý den", "desc_en": "Urgent same-day troubleshooting and repair", "price": "od 1 290 Kč"},
            {"name_cz": "Kompletní instalace vybavení / spotřebičů", "name_en": "Complete Fixture & Appliance Setup", "desc_cz": "Zapojení, zkouška těsnosti/funkčnosti a odvoz obalů", "desc_en": "Full hookup, safety testing, and clean finish", "price": "od 990 Kč"},
        ],
        "reviews": [
            {"author": "Lukáš Marek", "text_cz": "Přijeli přesně na čas, vše vyřešili čistě a za předem domluvenou cenu.", "text_en": "Arrived right on time, left the apartment spotless, and charged the exact quoted price."},
            {"author": "Hannah Weiss", "text_cz": "Perfektní domluva v angličtině a velmi slušné vystupování.", "text_en": "Polite, punctual, and fluent in English. Highly recommended in Prague!"},
        ],
    },
    "clinic": {
        "theme": "sage",
        "hero_img": "https://images.unsplash.com/photo-1629909613654-28e377c37b09?auto=format&fit=crop&w=1400&q=85",
        "gallery": [
            "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1579684385127-1ef15d508118?auto=format&fit=crop&w=800&q=80",
        ],
        "badge_cz": "Soukromá Ordinace & Moderní Péče",
        "badge_en": "Private Clinic & Specialist Care",
        "headline_cz": "Citlivá a moderní zdravotní péče v lokalitě {district}",
        "headline_en": "Gentle, Modern Healthcare in {district}",
        "subheadline_cz": "Přijímáme nové pacienty. Klidné prostředí bez stresu, špičková diagnostika a dostatek času na každého pacienta.",
        "subheadline_en": "Welcoming new patients. Calm environment, modern digital diagnostics, and unhurried consultations in Czech & English.",
        "cta_primary_cz": "Objednat se online",
        "cta_primary_en": "Book Appointment",
        "cta_secondary_cz": "Přehled péče",
        "cta_secondary_en": "Services & Fees",
        "features": [
            {"icon": "heart", "title_cz": "Empatický přístup bez bolesti", "title_en": "Calm, Pain-Free Care", "desc_cz": "Vše srozumitelně vysvětlíme a dbáme na váš maximální komfort.", "desc_en": "Clear explanations and gentle techniques for complete peace of mind."},
            {"icon": "calendar", "title_cz": "Termíny bez dlouhého čekání", "title_en": "Short Wait Times", "desc_cz": "Objednáváme na přesný čas, abyste v čekárně netrávili zbytečné minuty.", "desc_en": "Punctual appointments with same-week availability."},
            {"icon": "globe", "title_cz": "Česky & English Speaking", "title_en": "International & Expat Friendly", "desc_cz": "Kompletní lékařská péče a potvrzení v češtině i angličtině.", "desc_en": "Full medical documentation for local and international insurance."},
        ],
        "services": [
            {"name_cz": "Vstupní komplexní vyšetření & Plán péče", "name_en": "Comprehensive Initial Consultation", "desc_cz": "Podrobná diagnostika, konzultace s lékařem a návrh postupu", "desc_en": "Thorough examination, digital imaging & tailored care plan", "price": "1 200 Kč"},
            {"name_cz": "Preventivní péče / Dentální hygiena (60 min)", "name_en": "Preventive Care & Hygiene Session (60 min)", "desc_cz": "Šetrné ultrazvukové ošetření, AirFlow a individuální instruktáž", "desc_en": "Gentle ultrasonic care, AirFlow polish & preventive guidance", "price": "1 690 Kč"},
            {"name_cz": "Specializované terapeutické ošetření", "name_en": "Specialist Therapeutic Procedure", "desc_cz": "Bezbolestné ošetření za použití moderních biokompatibilních materiálů", "desc_en": "Precision care using premium biocompatible materials", "price": "od 1 950 Kč"},
            {"name_cz": "Akutní vyšetření v den zavolání", "name_en": "Same-Day Urgent Consultation", "desc_cz": "Rychlá pomoc při akutních obtížích bez čekání", "desc_en": "Priority same-day slot for urgent discomfort", "price": "1 450 Kč"},
        ],
        "reviews": [
            {"author": "Eva Černá", "text_cz": "Krásná moderní ordinace a neuvěřitelně lidský přístup paní doktorky.", "text_en": "Beautiful modern clinic and an incredibly kind, reassuring medical team."},
            {"author": "Alexander Wright", "text_cz": "Nejlepší soukromá klinika v Praze. Plynulá angličtina a nulové čekání.", "text_en": "Best private clinic experience in Prague. Fluent English and zero wait time."},
        ],
    },
    "boutique": {
        "theme": "pearl",
        "hero_img": "https://images.unsplash.com/photo-1526047932273-341f2a7631f9?auto=format&fit=crop&w=1400&q=85",
        "gallery": [
            "https://images.unsplash.com/photo-1487530811176-3780de880c2d?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1563241527-3004b7be0ffd?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1513519245088-0e12902e5a38?auto=format&fit=crop&w=800&q=80",
        ],
        "badge_cz": "Autorský Ateliér & Květinový Butik",
        "badge_en": "Artisan Studio & Local Boutique",
        "headline_cz": "Autorská tvorba a vkusné dárky v lokalitě {district}",
        "headline_en": "Botanical Artistry & Thoughtful Gifts in {district}",
        "subheadline_cz": "Každý kousek vážeme a vybíráme s citem pro přirozenou estetiku. Vyzvednutí v ateliéru nebo doručení kurýrem po Praze.",
        "subheadline_en": "Curated with an eye for natural beauty. Available for studio pickup or same-day courier delivery across Prague.",
        "cta_primary_cz": "Objednat / Rezervovat",
        "cta_primary_en": "Order / Reserve",
        "cta_secondary_cz": "Prohlédnout kolekci",
        "cta_secondary_en": "View Collection",
        "features": [
            {"icon": "sparkles", "title_cz": "Autorský rukopis", "title_en": "Bespoke Aesthetic", "desc_cz": "Přirozené sezónní kompozice v minimalistickém dárkovém balení.", "desc_en": "Seasonal arrangements wrapped in minimalist linen and paper."},
            {"icon": "truck", "title_cz": "Rozvoz po Praze do 2 hodin", "title_en": "2-Hour Prague Delivery", "desc_cz": "Spolehlivé doručení přímo do rukou s ručně psaným věnováním.", "desc_en": "Hand-delivered across Prague with a custom calligraphy note."},
            {"icon": "heart", "title_cz": "Vždy čerstvý výběr", "title_en": "Sourced Fresh Daily", "desc_cz": "Spolupracujeme s lokálními pěstiteli a malými evropskými ateliéry.", "desc_en": "Direct from local Czech growers and independent makers."},
        ],
        "services": [
            {"name_cz": "Sezónní autorská kytice / Dárkový set", "name_en": "Seasonal Signature Bouquet / Gift Box", "desc_cz": "Vzdušná vazba z čerstvých sezónních květin s kartičkou", "desc_en": "Organic seasonal arrangement with a handwritten note", "price": "od 690 Kč"},
            {"name_cz": "Velká ateliérová vazba Deluxe", "name_en": "Grand Studio Arrangement", "desc_cz": "Bohatá kompozice pro slavnostní příležitosti a výročí", "desc_en": "Generous statement piece for milestones and celebrations", "price": "1 490 Kč"},
            {"name_cz": "Květinové předplatné / Styling interiérů", "name_en": "Floral Subscription & Interior Styling", "desc_cz": "Pravidelné čerstvé květiny pro váš domov, kancelář či recepci", "desc_en": "Weekly or bi-weekly botanical styling for homes and studios", "price": "od 890 Kč"},
            {"name_cz": "Kurýrní doručení po Praze", "name_en": "Same-Day Prague Courier", "desc_cz": "Šetrný převoz v dárkovém balení na přesný čas", "desc_en": "Careful hand-delivery anywhere in Prague 1–10", "price": "190 Kč"},
        ],
        "reviews": [
            {"author": "Klára Veselá", "text_cz": "Nejvkusnější ateliér v Praze. Každá kytice vypadá jako umělecké dílo.", "text_en": "The most tasteful studio in Prague. Every bouquet feels like a work of art."},
            {"author": "Oliver Grant", "text_cz": "Objednáno online a za 90 minut doručeno v perfektním stavu. Děkuji!", "text_en": "Ordered online and delivered across Prague in 90 minutes. Flawless experience!"},
        ],
    },
    "general": {
        "theme": "nordic",
        "hero_img": "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=1400&q=85",
        "gallery": [
            "https://images.unsplash.com/photo-1497366811353-6870744d04b2?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1556761175-5973dc0f32e7?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1521791136064-7986c2920216?auto=format&fit=crop&w=800&q=80",
        ],
        "badge_cz": "Lokální Studio & Služby Praha",
        "badge_en": "Trusted Local Studio in Prague",
        "headline_cz": "Kvalitní služby a osobní přístup v lokalitě {district}",
        "headline_en": "Refined Local Service & Expertise in {district}",
        "subheadline_cz": "Zakládáme si na precizní práci, klidné komunikaci a férových podmínkách. Rezervujte si svůj termín online.",
        "subheadline_en": "Built on craftsmanship, transparent pricing, and personal attention. Book your visit online in Czech or English.",
        "cta_primary_cz": "Rezervovat termín",
        "cta_primary_en": "Book Appointment",
        "cta_secondary_cz": "Přehled služeb",
        "cta_secondary_en": "Our Services",
        "features": [
            {"icon": "award", "title_cz": "Ověřená lokální kvalita", "title_en": "Trusted by Locals", "desc_cz": "Vysoké hodnocení a desítky stálých klientů přímo z naší čtvrti.", "desc_en": "Highly rated by Prague residents and international clients alike."},
            {"icon": "message-square", "title_cz": "Rychlá a jasná domluva", "title_en": "Effortless Communication", "desc_cz": "Okamžité potvrzení termínu přes web nebo WhatsApp.", "desc_en": "Direct online booking and fast responses via WhatsApp."},
            {"icon": "globe", "title_cz": "Česky & English Friendly", "title_en": "Bilingual CZ / EN Care", "desc_cz": "Plný servis v češtině i angličtině bez jazykové bariéry.", "desc_en": "Seamless service in both Czech and English."},
        ],
        "services": [
            {"name_cz": "Úvodní konzultace & Základní služba", "name_en": "Initial Consultation & Core Service", "desc_cz": "Individuální posouzení vašich požadavků a precizní provedení", "desc_en": "Personal assessment and tailored execution", "price": "od 590 Kč"},
            {"name_cz": "Kompletní balíček péče Standard", "name_en": "Complete Signature Service", "desc_cz": "Nejčastěji volená kompletní služba se zárukou kvality", "desc_en": "Our most popular all-inclusive service option", "price": "1 190 Kč"},
            {"name_cz": "Prioritní / Expresní termín", "name_en": "Priority Express Appointment", "desc_cz": "Přednostní odbavení v nejbližším volném okně", "desc_en": "Fast-track scheduling for urgent needs", "price": "890 Kč"},
            {"name_cz": "Individuální řešení na míru", "name_en": "Bespoke Custom Package", "desc_cz": "Nezávazná kalkulace podle vašeho zadání", "desc_en": "Tailored quote prepared specifically for your project", "price": "Kalkulace zdarma"},
        ],
        "reviews": [
            {"author": "Jan Kučera", "text_cz": "Skvělá zkušenost, velmi příjemné prostředí a profesionální výsledek.", "text_en": "Wonderful experience, calm atmosphere, and impeccable results."},
            {"author": "Michael Brown", "text_cz": "Jednoduchá rezervace a perfektní komunikace. Doporučuji!", "text_en": "Easy booking and top-notch quality. Highly recommended!"},
        ],
    },
}


def enrich_with_gemini_if_available(lead: Dict[str, Any], preset: Dict[str, Any], gemini_api_key: str) -> Dict[str, Any]:
    if not gemini_api_key or not gemini_api_key.strip():
        return preset

    try:
        from google import genai
        client = genai.Client(api_key=gemini_api_key.strip())
        prompt = f"""
You are an award-winning 2026 editorial web copywriter in Prague.
Create calm, refined bilingual (Czech and English) website copy for this real Prague local business:
- Business Name: {lead.get('name')}
- Category: {lead.get('category_label_en')} ({lead.get('category_label_cz')})
- District/Address: {lead.get('address')} ({lead.get('district')})

Return ONLY valid JSON with these exact keys:
{{
  "badge_cz": "short 3-4 word category tagline in Czech",
  "badge_en": "short 3-4 word category tagline in English",
  "headline_cz": "calm, refined editorial hero headline in Czech mentioning the neighborhood/Prague",
  "headline_en": "calm, refined editorial hero headline in English mentioning the neighborhood/Prague",
  "subheadline_cz": "2 sentence persuasive subheadline in Czech",
  "subheadline_en": "2 sentence persuasive subheadline in English",
  "services": [
    {{
      "name_cz": "Service/item name in Czech",
      "name_en": "Service/item name in English",
      "desc_cz": "Short description in Czech",
      "desc_en": "Short description in English",
      "price": "Realistic Prague price in Kč (e.g. 590 Kč)"
    }}
  ]
}}
Provide 6 realistic services/menu items in the "services" array.
"""
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        raw_text = response.text or ""
        match = re.search(r"\{[\s\S]*\}", raw_text)
        if match:
            ai_data = json.loads(match.group(0))
            merged = dict(preset)
            for k in ["badge_cz", "badge_en", "headline_cz", "headline_en", "subheadline_cz", "subheadline_en"]:
                if ai_data.get(k):
                    merged[k] = ai_data[k]
            if isinstance(ai_data.get("services"), list) and len(ai_data["services"]) >= 3:
                merged["services"] = ai_data["services"][:6]
            return merged
    except Exception:
        pass

    return preset


def generate_business_website_html(
    lead: Dict[str, Any],
    theme_override: Optional[str] = None,
    gemini_api_key: str = "",
) -> str:
    """
    Generates an ultra-clean, 2026/2027 Awwwards-style editorial minimalist website
    (Light, breathable, soft alabaster/sage/sand/ocean tones, generous whitespace, zero clutter).
    """
    sub_type = lead.get("sub_type", "general")
    preset_base = INDUSTRY_PRESETS.get(sub_type, INDUSTRY_PRESETS["general"])
    preset = enrich_with_gemini_if_available(lead, preset_base, gemini_api_key)

    theme_key = theme_override if (theme_override and theme_override in COLOR_THEMES) else preset["theme"]
    theme = COLOR_THEMES.get(theme_key, COLOR_THEMES["nordic"])

    name = lead.get("name", "Prague Studio")
    district = lead.get("district", "Praha")
    short_district = district.split(",")[-1].strip() if "," in district else district
    address = lead.get("address", district)
    phone = lead.get("phone") or "+420 777 123 456"
    clean_phone = re.sub(r"[^\d+]", "", phone)
    whatsapp_num = clean_phone.lstrip("+") if clean_phone.startswith("+") else f"420{clean_phone}"
    opening_hours = lead.get("opening_hours") or "Po–Pá 09:00–19:00, So 10:00–17:00"
    rating = lead.get("rating", 4.8)
    reviews_count = lead.get("reviews_count", 84)
    lat = float(lead.get("lat") or 50.0755)
    lon = float(lead.get("lon") or 14.4378)
    gmaps_url = lead.get("google_maps_url") or f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"

    headline_cz = preset["headline_cz"].replace("{district}", short_district)
    headline_en = preset["headline_en"].replace("{district}", short_district)
    subheadline_cz = preset["subheadline_cz"]
    subheadline_en = preset["subheadline_en"]

    # Features Bento Grid
    features_html = ""
    for feat in preset["features"]:
        features_html += f"""
        <div class="p-8 rounded-3xl border {theme['card_bg']} transition-all duration-300 hover:shadow-[0_12px_40px_-12px_rgba(0,0,0,0.06)]">
            <div class="w-11 h-11 rounded-2xl {theme['pill_bg']} flex items-center justify-center mb-6">
                <i data-lucide="{feat['icon']}" class="w-5 h-5"></i>
            </div>
            <h3 class="text-lg font-semibold tracking-tight mb-2.5" data-cz="{feat['title_cz']}" data-en="{feat['title_en']}">{feat['title_cz']}</h3>
            <p class="{theme['muted_text']} text-sm leading-relaxed" data-cz="{feat['desc_cz']}" data-en="{feat['desc_en']}">{feat['desc_cz']}</p>
        </div>
        """

    # Clean Editorial Price List
    services_html = ""
    service_options_html = ""
    for srv in preset["services"]:
        n_cz = srv.get("name_cz", "")
        n_en = srv.get("name_en", n_cz)
        d_cz = srv.get("desc_cz", "")
        d_en = srv.get("desc_en", d_cz)
        price = srv.get("price", "")
        services_html += f"""
        <div class="py-6 px-7 rounded-2xl border {theme['card_bg']} flex flex-col sm:flex-row sm:items-center justify-between gap-4 transition hover:shadow-sm">
            <div class="space-y-1">
                <h4 class="font-semibold text-base tracking-tight" data-cz="{n_cz}" data-en="{n_en}">{n_cz}</h4>
                <p class="text-sm {theme['muted_text']}" data-cz="{d_cz}" data-en="{d_en}">{d_cz}</p>
            </div>
            <div class="flex items-center gap-5 shrink-0">
                <span class="text-base font-semibold {theme['accent_text']} whitespace-nowrap">{price}</span>
                <button onclick="openBookingModal('{n_cz.replace("'", "")}')" class="px-4 py-2 rounded-full text-xs font-medium border {theme['secondary_btn']} transition cursor-pointer" data-cz="Rezervovat" data-en="Select">Rezervovat</button>
            </div>
        </div>
        """
        service_options_html += f'<option value="{n_cz} ({price})">{n_cz} — {price}</option>'

    # Minimalist Gallery
    gallery_html = ""
    for img_url in preset["gallery"]:
        gallery_html += f"""
        <div class="overflow-hidden rounded-3xl aspect-[4/3] bg-stone-100">
            <img src="{img_url}" alt="{name}" class="w-full h-full object-cover hover:scale-[1.03] transition duration-700 ease-out" loading="lazy" />
        </div>
        """

    # Calm Editorial Reviews
    reviews_html = ""
    for rev in preset["reviews"]:
        reviews_html += f"""
        <div class="p-8 rounded-3xl border {theme['card_bg']} flex flex-col justify-between">
            <div>
                <div class="flex items-center gap-1 text-sm mb-4 {theme['accent_text']}">
                    <span>★ ★ ★ ★ ★</span>
                    <span class="text-xs {theme['muted_text']} ml-2 font-normal">Google Review</span>
                </div>
                <p class="text-base leading-relaxed mb-6" data-cz="&ldquo;{rev['text_cz']}&rdquo;" data-en="&ldquo;{rev['text_en']}&rdquo;">&ldquo;{rev['text_cz']}&rdquo;</p>
            </div>
            <div class="text-xs font-semibold uppercase tracking-wider {theme['muted_text']}">— {rev['author']}</div>
        </div>
        """

    bbox = f"{lon - 0.005}%2C{lat - 0.003}%2C{lon + 0.005}%2C{lat + 0.003}"
    osm_embed_url = f"https://www.openstreetmap.org/export/embed.html?bbox={bbox}&layer=mapnik&marker={lat}%2C{lon}"

    html = f"""<!DOCTYPE html>
<html lang="cs" class="scroll-smooth">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{name} — {short_district}, Praha</title>
    <meta name="description" content="{subheadline_cz}" />
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Instrument+Serif:ital@0;1&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; letter-spacing: -0.011em; }}
        .font-editorial {{ font-family: 'Instrument Serif', Georgia, serif; letter-spacing: -0.02em; }}
    </style>
</head>
<body class="{theme['page_bg']} antialiased">

    <!-- Floating Minimalist Navigation -->
    <header class="sticky top-0 z-40 backdrop-blur-xl {theme['nav_bg']} border-b">
        <div class="max-w-6xl mx-auto px-6 h-20 flex items-center justify-between gap-4">
            <a href="#" class="text-lg font-semibold tracking-tight flex items-center gap-2.5">
                <span>{name}</span>
            </a>

            <nav class="hidden md:flex items-center gap-8 text-sm {theme['muted_text']}">
                <a href="#about" class="hover:opacity-100 transition" data-cz="O nás" data-en="Philosophy">O nás</a>
                <a href="#services" class="hover:opacity-100 transition" data-cz="Ceník & Služby" data-en="Services & Menu">Ceník & Služby</a>
                <a href="#reviews" class="hover:opacity-100 transition" data-cz="Recenze" data-en="Reviews">Recenze</a>
                <a href="#contact" class="hover:opacity-100 transition" data-cz="Kontakt" data-en="Visit Us">Kontakt</a>
            </nav>

            <div class="flex items-center gap-3">
                <!-- Clean Pill Language Switcher -->
                <div class="inline-flex items-center rounded-full p-1 border {theme['card_bg']} text-xs">
                    <button id="btn-lang-cz" onclick="setLanguage('cz')" class="px-2.5 py-1 rounded-full font-medium {theme['primary_btn']} transition cursor-pointer">CZ</button>
                    <button id="btn-lang-en" onclick="setLanguage('en')" class="px-2.5 py-1 rounded-full font-medium {theme['muted_text']} transition cursor-pointer">EN</button>
                </div>

                <button onclick="openBookingModal('')" class="px-5 py-2.5 rounded-full text-xs font-medium {theme['primary_btn']} transition cursor-pointer" data-cz="{preset['cta_primary_cz']}" data-en="{preset['cta_primary_en']}">
                    {preset['cta_primary_cz']}
                </button>
            </div>
        </div>
    </header>

    <!-- Spacious Split Editorial Hero Section -->
    <section class="max-w-6xl mx-auto px-6 pt-14 pb-24 lg:py-24">
        <div class="grid lg:grid-cols-12 gap-12 lg:gap-16 items-center">
            <div class="lg:col-span-6 space-y-8">
                <div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-medium border {theme['hero_badge']}">
                    <span data-cz="{preset['badge_cz']} • {short_district}" data-en="{preset['badge_en']} • {short_district}">{preset['badge_cz']} • {short_district}</span>
                </div>

                <h1 class="font-editorial text-5xl sm:text-6xl leading-[1.06] font-normal tracking-tight" data-cz="{headline_cz}" data-en="{headline_en}">
                    {headline_cz}
                </h1>

                <p class="text-base sm:text-lg {theme['muted_text']} leading-relaxed max-w-xl" data-cz="{subheadline_cz}" data-en="{subheadline_en}">
                    {subheadline_cz}
                </p>

                <div class="flex flex-wrap items-center gap-3.5 pt-2">
                    <button onclick="openBookingModal('')" class="px-7 py-4 rounded-full text-sm font-medium {theme['primary_btn']} transition cursor-pointer flex items-center gap-2">
                        <span data-cz="{preset['cta_primary_cz']}" data-en="{preset['cta_primary_en']}">{preset['cta_primary_cz']}</span>
                        <i data-lucide="arrow-up-right" class="w-4 h-4"></i>
                    </button>
                    <a href="#services" class="px-7 py-4 rounded-full text-sm font-medium border {theme['secondary_btn']} transition">
                        <span data-cz="{preset['cta_secondary_cz']}" data-en="{preset['cta_secondary_en']}">{preset['cta_secondary_cz']}</span>
                    </a>
                </div>

                <div class="pt-6 border-t border-black/5 flex items-center gap-8 text-xs {theme['muted_text']}">
                    <div>
                        <span class="font-semibold text-sm text-current">{rating} ★</span>
                        <span class="ml-1">({reviews_count}+ Google)</span>
                    </div>
                    <div>📍 {address}</div>
                </div>
            </div>

            <div class="lg:col-span-6">
                <div class="rounded-[32px] overflow-hidden aspect-[4/3] shadow-[0_24px_60px_-15px_rgba(0,0,0,0.08)] bg-stone-200">
                    <img src="{preset['hero_img']}" alt="{name}" class="w-full h-full object-cover" />
                </div>
            </div>
        </div>
    </section>

    <!-- Bento Value Propositions -->
    <section id="about" class="py-20 {theme['section_alt']}">
        <div class="max-w-6xl mx-auto px-6">
            <div class="max-w-xl mb-14">
                <p class="text-xs font-medium uppercase tracking-widest {theme['muted_text']} mb-3" data-cz="NÁŠ PŘÍSTUP" data-en="OUR PHILOSOPHY">NÁŠ PŘÍSTUP</p>
                <h2 class="font-editorial text-4xl sm:text-5xl font-normal" data-cz="Důraz na detail, klid a poctivou kvalitu" data-en="Thoughtful craft, calm atmosphere & honest quality">Důraz na detail, klid a poctivou kvalitu</h2>
            </div>
            <div class="grid md:grid-cols-3 gap-6">
                {features_html}
            </div>
        </div>
    </section>

    <!-- Clean Editorial Services & Pricing -->
    <section id="services" class="py-24 max-w-4xl mx-auto px-6">
        <div class="flex flex-col sm:flex-row sm:items-end justify-between mb-14 gap-4">
            <div>
                <p class="text-xs font-medium uppercase tracking-widest {theme['muted_text']} mb-3" data-cz="CENÍK & NABÍDKA" data-en="TRANSPARENT PRICING">CENÍK & NABÍDKA</p>
                <h2 class="font-editorial text-4xl sm:text-5xl font-normal" data-cz="Vybrané služby a ceník" data-en="Curated Services & Menu">Vybrané služby a ceník</h2>
            </div>
            <button onclick="openBookingModal('')" class="px-5 py-2.5 rounded-full text-xs font-medium {theme['primary_btn']} self-start sm:self-auto cursor-pointer" data-cz="Online rezervace" data-en="Book Online">
                Online rezervace
            </button>
        </div>
        <div class="space-y-3.5">
            {services_html}
        </div>
    </section>

    <!-- Minimalist Visual Gallery -->
    <section class="py-12 max-w-6xl mx-auto px-6">
        <div class="grid md:grid-cols-3 gap-6">
            {gallery_html}
        </div>
    </section>

    <!-- Testimonials -->
    <section id="reviews" class="py-24 max-w-6xl mx-auto px-6">
        <div class="max-w-xl mb-12">
            <p class="text-xs font-medium uppercase tracking-widest {theme['muted_text']} mb-3" data-cz="HODNOCENÍ KLIENTŮ" data-en="CLIENT STORIES">HODNOCENÍ KLIENTŮ</p>
            <h2 class="font-editorial text-4xl font-normal" data-cz="Zkušenosti našich návštěvníků" data-en="Words from Our Community">Zkušenosti našich návštěvníků</h2>
        </div>
        <div class="grid md:grid-cols-2 gap-6">
            {reviews_html}
        </div>
    </section>

    <!-- Location & Contact -->
    <section id="contact" class="py-24 {theme['section_alt']}">
        <div class="max-w-6xl mx-auto px-6 grid lg:grid-cols-12 gap-12 items-center">
            <div class="lg:col-span-5 space-y-8">
                <div>
                    <p class="text-xs font-medium uppercase tracking-widest {theme['muted_text']} mb-3" data-cz="KONTAKT & ADRESA" data-en="VISIT US">KONTAKT & ADRESA</p>
                    <h2 class="font-editorial text-4xl sm:text-5xl font-normal mb-4">{name}</h2>
                    <p class="text-sm {theme['muted_text']} leading-relaxed" data-cz="Zastavte se u nás osobně nebo si rezervujte termín online." data-en="Visit us in person or reserve your preferred time slot online.">
                        Zastavte se u nás osobně nebo si rezervujte termín online.
                    </p>
                </div>

                <div class="space-y-5 text-sm">
                    <div class="p-5 rounded-2xl border {theme['card_bg']}">
                        <div class="text-xs {theme['muted_text']} mb-1" data-cz="Adresa" data-en="Address">Adresa</div>
                        <div class="font-medium">{address}</div>
                        <a href="{gmaps_url}" target="_blank" class="text-xs underline mt-2 inline-block {theme['accent_text']}" data-cz="Otevřít v Google Maps →" data-en="Open in Google Maps →">Otevřít v Google Maps →</a>
                    </div>

                    <div class="p-5 rounded-2xl border {theme['card_bg']}">
                        <div class="text-xs {theme['muted_text']} mb-1" data-cz="Otevírací doba" data-en="Opening Hours">Otevírací doba</div>
                        <div class="font-medium">{opening_hours}</div>
                    </div>

                    <div class="p-5 rounded-2xl border {theme['card_bg']} flex items-center justify-between">
                        <div>
                            <div class="text-xs {theme['muted_text']} mb-1" data-cz="Telefon & WhatsApp" data-en="Direct Contact">Telefon & WhatsApp</div>
                            <a href="tel:{clean_phone}" class="font-medium hover:underline">{phone}</a>
                        </div>
                        <a href="https://wa.me/{whatsapp_num}" target="_blank" class="px-4 py-2 rounded-full text-xs font-medium {theme['primary_btn']}">
                            WhatsApp
                        </a>
                    </div>
                </div>
            </div>

            <div class="lg:col-span-7">
                <div class="rounded-3xl overflow-hidden border {theme['card_bg']} h-[420px] shadow-sm bg-stone-100">
                    <iframe width="100%" height="100%" frameborder="0" scrolling="no" src="{osm_embed_url}" title="{name} Map"></iframe>
                </div>
            </div>
        </div>
    </section>

    <footer class="py-12 px-6 border-t border-black/5 text-xs {theme['muted_text']}">
        <div class="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
            <div class="font-medium text-current">{name} — {short_district}, Praha</div>
            <div data-cz="© 2026 Všechna práva vyhrazena." data-en="© 2026 All rights reserved.">© 2026 Všechna práva vyhrazena.</div>
        </div>
    </footer>

    <!-- Minimalist Booking Modal -->
    <div id="booking-modal" class="fixed inset-0 z-50 hidden bg-black/30 backdrop-blur-sm flex items-center justify-center p-4">
        <div class="bg-white text-[#141413] rounded-3xl max-w-md w-full p-8 shadow-2xl border border-stone-200 relative">
            <button onclick="closeBookingModal()" class="absolute top-5 right-5 w-8 h-8 rounded-full bg-stone-100 hover:bg-stone-200 flex items-center justify-center text-xs cursor-pointer">✕</button>
            <h3 class="font-editorial text-3xl font-normal mb-1" data-cz="Online rezervace" data-en="Reserve Your Visit">Online rezervace</h3>
            <p class="text-xs text-stone-500 mb-6">{name} • {address}</p>

            <form onsubmit="submitBooking(event)" class="space-y-4">
                <div>
                    <label class="block text-xs font-medium text-stone-600 mb-1.5" data-cz="Vybraná služba" data-en="Selected Service">Vybraná služba</label>
                    <select id="modal-service" class="w-full rounded-xl border border-stone-200 bg-stone-50 px-3.5 py-2.5 text-sm">
                        {service_options_html}
                    </select>
                </div>
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs font-medium text-stone-600 mb-1.5" data-cz="Datum" data-en="Date">Datum</label>
                        <input type="date" id="modal-date" required class="w-full rounded-xl border border-stone-200 bg-stone-50 px-3 py-2.5 text-sm" />
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-stone-600 mb-1.5" data-cz="Čas" data-en="Time">Čas</label>
                        <input type="time" id="modal-time" value="14:00" required class="w-full rounded-xl border border-stone-200 bg-stone-50 px-3 py-2.5 text-sm" />
                    </div>
                </div>
                <div>
                    <label class="block text-xs font-medium text-stone-600 mb-1.5" data-cz="Jméno a telefon" data-en="Your Name & Phone">Jméno a telefon</label>
                    <input type="text" id="modal-name" placeholder="Jan Novák, +420..." required class="w-full rounded-xl border border-stone-200 bg-stone-50 px-3.5 py-2.5 text-sm" />
                </div>
                <button type="submit" class="w-full py-3.5 rounded-full font-medium text-sm {theme['primary_btn']} transition cursor-pointer mt-2" data-cz="Potvrdit rezervaci" data-en="Confirm Request">
                    Potvrdit rezervaci
                </button>
            </form>
            <div id="booking-success" class="hidden mt-4 p-4 rounded-2xl bg-stone-100 text-stone-800 text-xs font-medium text-center">
                ✓ <span data-cz="Děkujeme! Vaše rezervace byla přijata." data-en="Thank you! Your request has been received.">Děkujeme! Vaše rezervace byla přijata.</span>
            </div>
        </div>
    </div>

    <script>
        lucide.createIcons();
        function setLanguage(lang) {{
            document.querySelectorAll('[data-' + lang + ']').forEach(el => {{
                el.innerHTML = el.getAttribute('data-' + lang);
            }});
            const btnCz = document.getElementById('btn-lang-cz');
            const btnEn = document.getElementById('btn-lang-en');
            if (lang === 'cz') {{
                btnCz.className = 'px-2.5 py-1 rounded-full font-medium {theme['primary_btn']} transition cursor-pointer';
                btnEn.className = 'px-2.5 py-1 rounded-full font-medium {theme['muted_text']} transition cursor-pointer';
            }} else {{
                btnEn.className = 'px-2.5 py-1 rounded-full font-medium {theme['primary_btn']} transition cursor-pointer';
                btnCz.className = 'px-2.5 py-1 rounded-full font-medium {theme['muted_text']} transition cursor-pointer';
            }}
        }}
        function openBookingModal() {{
            document.getElementById('booking-modal').classList.remove('hidden');
            document.getElementById('booking-success').classList.add('hidden');
            document.getElementById('modal-date').value = new Date().toISOString().split('T')[0];
        }}
        function closeBookingModal() {{
            document.getElementById('booking-modal').classList.add('hidden');
        }}
        function submitBooking(e) {{
            e.preventDefault();
            document.getElementById('booking-success').classList.remove('hidden');
        }}
    </script>
</body>
</html>"""
    return html


def generate_prague_outreach_pitches(lead: Dict[str, Any], preview_url: str, price_czk: int = 8900) -> Dict[str, Any]:
    name = lead.get("name", "Vaše provozovna")
    district = lead.get("district", "Praha")
    short_district = district.split(",")[-1].strip() if "," in district else district
    rating = lead.get("rating", 4.8)
    price_eur = round(price_czk / 25)

    whatsapp_cz = (
        f"Dobrý den do {name},\n\n"
        f"všiml jsem si na Google Maps, že máte v lokalitě {short_district} skvělé hodnocení ({rating} ★), "
        f"ale chybí vám tam moderní webová stránka v češtině a angličtině pro místní i cizince v Praze.\n\n"
        f"Připravil jsem pro {name} čistý, minimalistický návrh webu (s ceníkem, mapou a online rezervací):\n"
        f"{preview_url}\n\n"
        f"Pokud se vám návrh líbí, můžeme ho spustit na vaší doméně během 24 hodin. Přeji hezký den!"
    )

    whatsapp_en = (
        f"Hello {name} team,\n\n"
        f"I noticed on Google Maps that you have wonderful reviews ({rating} ★) in {short_district}, "
        f"but you don't have a bilingual (Czech/English) website linked for locals and expats in Prague.\n\n"
        f"I designed a clean, minimalist live demo website specifically for {name}:\n"
        f"{preview_url}\n\n"
        f"If you like the design, I can connect it to your domain and Google Maps profile within 24 hours."
    )

    walkin_script_tr = (
        f"Yüz Yüze (Walk-In) Satış Notu:\n"
        f"1. Telefonunuzdan {name} için üretilen yalın tasarımı açın ve sağ üstteki CZ / EN dil geçişini gösterin.\n"
        f"2. Kurulum için {price_czk:,} Kč (~{price_eur} €) + aylık 790 Kč bakım teklif edin."
    )

    return {
        "whatsapp_cz": whatsapp_cz,
        "whatsapp_en": whatsapp_en,
        "walkin_tips_tr": walkin_script_tr,
        "recommended_price_czk": f"{price_czk:,} Kč".replace(",", " "),
        "recommended_price_eur": f"~{price_eur} €",
        "monthly_retainer_czk": "790 Kč / měsíc (~32 €)",
    }
