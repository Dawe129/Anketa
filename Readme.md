# 🗳️ Webová Anketa

Jednoduchá webová aplikace pro hlasování v anketě, napsaná v Pythonu s Flask. Každý uživatel může hlasovat pouze jednou z jedné IP adresy. Data se ukládají do JSON souborů a přežijí restart aplikace.

## 🚀 Funkce
- **Přihlášení jménem**: Uživatel zadá jméno a aplikace kontroluje IP adresu.
- **Hlasování**: Výběr z předdefinovaných odpovědí.
- **Výsledky**: Zobrazení počtu hlasů a seznamu hlasujících (s IP hashi).
- **Reset**: Správným tokenem lze vynulovat všechna data. (Formulář již není veřejně dostupný v navigaci; administrátor musí zadat `/reset` ručně.)

- **Hlásit chyby**: Pokud najdete problém, vytvořte prosím issue na
  <https://github.com/Dawe129/Anketa/issues>. Díky za pomoc!
- **Bezpečnost**: IP adresy se hashují pro ochranu soukromí.
- **Favicon**: Stránka nyní používá malou ikonu (vloženou jako SVG) pro lepší rozpoznání v záložkách.
- **Analytics**: Google Analytics snippet byl odstraněn, aby se předešlo stahování nevyužitého JavaScriptu; lze jej snadno znovu přidat, pokud bude potřeba sledovat události.
- **Logování**: Všechny akce se logují do `app.log` pro historii.
- **Error handling**: 404 a 500 chyby s vlastními stránkami.

## 📋 Požadavky
- Python 3.9+
- Flask 2.3+
- (Volitelně) Docker pro kontejnerizaci

## 🛠️ Instalace a spuštění

### Lokálně (bez Docker)
1. Naklonuj nebo stáhni projekt.
2. Nainstaluj závislosti: `pip install -r requirements.txt`
3. Spusť aplikaci: `python app.py`
4. Otevři v prohlížeči: `http://localhost:5000`

### S Docker Compose
1. Ujisti se, že máš Docker nainstalovaný (`docker --version`).
2. Spusť: `docker-compose up --build`
3. Otevři: `http://localhost:5000`
4. Zastav: `docker-compose down`

## 📁 Struktura projektu
```
Anketa/
├── app.py              # Flask server (hlavní logika, IP ochrana, logování)
├── requirements.txt    # Závislosti Python
├── Dockerfile          # Pro Docker build
├── docker-compose.yml  # Pro Docker Compose
├── app.log             # Log soubor (vytvoří se automaticky)
├── votes.json          # Počty hlasů per možnost
├── users.json          # Záznamy: IP hash → {username, choice}
├── static/
│   └── style.css       # CSS styly
└── templates/
    ├── login.html      # Přihlášení jménem
    ├── index.html      # Hlasovací stránka
    ├── results.html    # Výsledky + seznam hlasujících
    ├── 404.html        # Chyba 404
    └── 500.html        # Chyba 500
```

## 🔄 Tok aplikace
1. **Přihlášení**: Uživatel zadá jméno → kontrola IP v `users.json`.
   - IP existuje → chyba "Už jsi hlasoval".
   - IP nová → uložení do session → přesměrování na hlasování.
2. **Hlasování**: Výběr odpovědi → uložení do `votes.json` a `users.json`.
3. **Výsledky**: Zobrazení grafu hlasů a tabulky hlasujících.
4. **Reset**: Pouze se správným tokenem (`tajny123`) vynuluje data. Formulář byl přesunut do zabezpečeného administrátorského panelu (`/admin/dashboard` po přihlášení). Pro veřejné uživatele zůstávají výsledky dostupné na `/results`.

- **Admin panel**: Přihlášení je možné na `/admin/login`. Po přihlášení se dostanete na `/admin/dashboard` kde jsou k dispozici výsledky s IP, reset a odkazy na další nástroje.
- **O anketě**: Nová veřejná stránka `/about` poskytuje základní informace o aktuální otázce a možnostech.

## 🔒 Bezpečnost
- **IP hashování**: IP adresy se hashují (SHA-256) – neukládají se v čitelné podobě.
- **Jedno hlasování per IP**: Dvojitá kontrola při přihlášení i hlasování.
- **Session management**: Session se vymaže po hlasování.
- **Token pro reset**: Chráněno tajným tokenem.
- **CSP**: Server přidává hlavičku `Content-Security-Policy: default-src 'self'` aby zabránil načítání obsahů z jiných domén.
- **HTTPS redirect**: Veškeré HTTP požadavky jsou přesměrovány na HTTPS automaticky díky `@before_request` hooku; zajišťuje, že komunikace probíhá pouze přes šifrovaný kanál.
## ⚙️ Konfigurace
Uprav v `app.py`:
| Proměnná | Popis | Výchozí |
|----------|-------|---------|
| `RESET_TOKEN` | Token pro reset | `tajny123` |
| `QUESTION` | Text otázky | "Jaký je tvůj oblíbený programovací jazyk?" |
| `OPTIONS` | Seznam odpovědí | `["a) Python", "b) JavaScript", ...]` |
| `app.secret_key` | Klíč pro session | Změň před nasazením! |

## 📊 Logování
- Všechny akce (přihlášení, hlasování, reset, chyby) se logují do `app.log`.
- Formát: `čas - úroveň - zpráva` (např. `2026-02-23 10:00:00 - INFO - Uživatel Jan hlasoval`).
- Prohlédni si logy: `cat app.log` nebo otevři v editoru.

## 🐛 Troubleshooting
- **Chyba "Flask not found"**: Nainstaluj `pip install flask`.
- **Port 5000 obsazený**: Změň v `app.run(port=XXXX)`.
- **Docker nefunguje**: Zkontroluj, jestli je Docker spuštěný.
- **Žádné logy**: Zkontroluj `app.log` v adresáři.


