from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
import hashlib
import logging

app = Flask(__name__)
app.secret_key = "super_tajny_klic_2024"  # Nutné pro session

# Nastavení logování
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='a'  # Přidávat do souboru
)

# --- Konfigurace ---
VOTES_FILE = "votes.json"
USERS_FILE = "users.json"
RESET_TOKEN = "tajny123"  # Token pro reset hlasování

ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

QUESTION = "Jaký je tvůj oblíbený programovací jazyk?"
OPTIONS = ["a) Python", "b) JavaScript", "c) Java", "d) C++"]


# ── Pomocné funkce ──────────────────────────────────────────────

def load_json(filepath: str, default: dict) -> dict:
    """Načte JSON soubor, nebo vrátí výchozí hodnotu."""
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return default


def save_json(filepath: str, data: dict) -> None:
    """Uloží data do JSON souboru."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_client_ip_hash() -> str:
    """
    Získá hash IP klienta pro identifikaci.
    """
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        ip = forwarded_for.split(",")[0].strip()
    else:
        ip = request.remote_addr or "unknown"

    # Hash IP adresy – nepotřebujeme znát přesnou IP, jen ji identifikovat
    return hashlib.sha256(ip.encode()).hexdigest()[:16]


def get_client_ip_real() -> str:
    """
    Získá skutečnou IP klienta.
    """
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        ip = forwarded_for.split(",")[0].strip()
    else:
        ip = request.remote_addr or "unknown"
    return ip


def init_files() -> None:
    """Inicializuje datové soubory, pokud neexistují."""
    if not os.path.exists(VOTES_FILE):
        save_json(VOTES_FILE, {option: 0 for option in OPTIONS})
    if not os.path.exists(USERS_FILE):
        save_json(USERS_FILE, {})


# ── Routes ──────────────────────────────────────────────────────

@app.route("/")
def home():
    """Přesměrování na přihlášení."""
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    GET  → zobrazí login formulář
    POST → zkontroluje IP, uloží jméno do session, přesměruje na hlasování
    """
    if request.method == "POST":
        username = request.form.get("username", "").strip()

        if not username:
            return render_template("login.html", error="Zadej prosím své jméno.")

        ip_hash = get_client_ip_hash()
        users = load_json(USERS_FILE, {})

        # Kontrola: existuje tato IP v users.json?
        if ip_hash in users:
            existing_user = users[ip_hash]["username"]
            logging.warning(f"Pokus o opakované hlasování z IP {ip_hash} (uživatel: {existing_user})")
            return render_template(
                "login.html",
                error=f"Z tohoto počítače už hlasoval/a '{existing_user}'. Každý může hlasovat jen jednou."
            )

        # IP není v databázi → uložíme jméno do session a pustíme dál
        session["username"] = username
        session["ip_hash"] = ip_hash
        logging.info(f"Uživatel {username} (IP: {ip_hash}) se přihlásil k hlasování")
        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/vote-form")
def index():
    """Hlasovací stránka – vyžaduje přihlášení."""
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    return render_template("index.html", question=QUESTION, options=OPTIONS, username=username)


@app.route("/vote", methods=["POST"])
def vote():
    """
    Zpracování hlasu:
    1. Ověří session
    2. Zkontroluje IP znovu (ochrana proti manipulaci)
    3. Uloží hlas do votes.json a users.json
    4. Přesměruje na výsledky
    """
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    ip_hash = get_client_ip_hash()
    ip_real = get_client_ip_real()

    # Dvojitá kontrola IP (ochrana proti obejití session)
    users = load_json(USERS_FILE, {})
    if ip_hash in users:
        return redirect(url_for("results"))

    chosen = request.form.get("choice")
    if not chosen or chosen not in OPTIONS:
        return redirect(url_for("index"))

    # Uložit hlas do votes.json
    votes = load_json(VOTES_FILE, {option: 0 for option in OPTIONS})
    votes[chosen] = votes.get(chosen, 0) + 1
    save_json(VOTES_FILE, votes)

    # Uložit uživatele do users.json  →  IP hash: {username, choice, ip}
    users[ip_hash] = {"username": username, "choice": chosen, "ip": ip_real}
    save_json(USERS_FILE, users)

    logging.info(f"Uživatel {username} (IP: {ip_real}) hlasoval pro: {chosen}")

    # Vymazat session po hlasování
    session.clear()

    return redirect(url_for("results"))


@app.route("/results")
def results():
    """Stránka s výsledky – přístupná bez přihlášení."""
    votes = load_json(VOTES_FILE, {option: 0 for option in OPTIONS})
    users = load_json(USERS_FILE, {})
    total = sum(votes.values())
    # Pro běžné uživatele skrýt IP adresy
    users_list = [{"username": info["username"], "choice": info["choice"]} for info in users.values()]
    return render_template(
        "results.html",
        question=QUESTION,
        votes=votes,
        total=total,
        users=users_list
    )


@app.route("/reset", methods=["POST"])
def reset():
    """
    Reset hlasování:
    Správný token → vynuluje votes.json i users.json
    Špatný token  → nic se nestane
    """
    token = request.form.get("token", "")
    votes = load_json(VOTES_FILE, {option: 0 for option in OPTIONS})
    users = load_json(USERS_FILE, {})
    total = sum(votes.values())

    if token == RESET_TOKEN:
        empty_votes = {option: 0 for option in OPTIONS}
        save_json(VOTES_FILE, empty_votes)
        save_json(USERS_FILE, {})
        message = "✅ Hlasování bylo úspěšně resetováno."
        votes = empty_votes
        users = {}
        total = 0
        logging.info("Hlasování bylo resetováno správným tokenem")
    else:
        message = "❌ Špatný token. Reset neproveden."
        logging.warning(f"Pokus o reset se špatným tokenem: {token}")

    # Pro běžné uživatele skrýt IP adresy
    users_list = [{"username": info["username"], "choice": info["choice"]} for info in users.values()]
    return render_template(
        "results.html",
        question=QUESTION,
        votes=votes,
        total=total,
        users=users_list,
        message=message
    )


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """
    Přihlášení pro admina.
    """
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username == ADMIN_USER and password == ADMIN_PASS:
            session["admin"] = True
            logging.info(f"Admin {username} se přihlásil")
            return redirect(url_for("admin_results"))
        else:
            return render_template("admin_login.html", error="Špatné přihlašovací údaje.")

    return render_template("admin_login.html")


@app.route("/admin/results")
def admin_results():
    """
    Admin stránka s výsledky – zobrazuje IP adresy.
    """
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    votes = load_json(VOTES_FILE, {option: 0 for option in OPTIONS})
    users = load_json(USERS_FILE, {})
    total = sum(votes.values())
    return render_template(
        "admin_results.html",
        question=QUESTION,
        votes=votes,
        total=total,
        users=users
    )


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("results"))


# ── Error handling ───────────────────────────────────────────────

@app.errorhandler(404)
def not_found(error):
    logging.error(f"404 Error: {request.url}")
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_error(error):
    logging.error(f"500 Error: {error}")
    return render_template("500.html"), 500


# ── Start ────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_files()
    app.run(debug=True)