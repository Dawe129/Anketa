# 🗳️ Webová Anketa v2 – README

## Struktura projektu
```
anketa/
├── app.py              ← Flask server (hlavní logika + IP ochrana)
├── votes.json          ← Počty hlasů per možnost
├── users.json          ← Záznamy: IP hash → {username, choice}
├── static/
│   └── style.css       ← Styling
└── templates/
    ├── login.html      ← Přihlášení jménem
    ├── index.html      ← Hlasovací stránka
    └── results.html    ← Výsledky + seznam hlasujících
```

## Instalace a spuštění

```bash
pip install flask
python app.py
# → http://localhost:5000
```

## Tok aplikace
```
Uživatel → login.html → POST /login → kontrola IP
                                        ├── IP existuje → chyba
                                        └── IP nová → session → /vote-form
                                                          ↓
                                                    POST /vote
                                                          ↓
                                                    votes.json + users.json
                                                          ↓
                                                    results.html
```

## Bezpečnost
- IP adresa uživatele se **hashuje** (SHA-256) – nikde se neukládá v čitelné podobě
- Každá IP může hlasovat jen **jednou**
- Dvojitá kontrola: při přihlášení i při odeslání hlasu
- Session se vymaže po hlasování

## Konfigurace (app.py)
| Proměnná | Popis |
|----------|-------|
| `RESET_TOKEN` | Token pro reset hlasování (výchozí: `tajny123`) |
| `QUESTION` | Text otázky |
| `OPTIONS` | Seznam odpovědí |
| `app.secret_key` | Tajný klíč pro session – **změň před nasazením!** |