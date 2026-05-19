# Studentské portfolio – Gymnázium Šlapanice

Webová aplikace pro sledování dovedností, cílů a úspěchů studentů gymnázia.
Vizualizace pokroku pomocí interaktivních grafů (Chart.js), petrolejová paleta inspirovaná webem školy.

## Požadavky

- Python 3.10+
- pip

## Instalace a spuštění

```bash
# 1. Klonování / rozbalení projektu
git clone <url-repozitare>
cd portfolio

# 2. Virtuální prostředí
python -m venv venv

# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# 3. Závislosti
pip install -r requirements.txt

# 4. Konfigurace prostředí
cp .env.example .env
# Otevřete .env a nastavte SECRET_KEY (libovolný dlouhý náhodný řetězec)

# 5. Naplnění databáze demo daty
python seed.py

# 6. Spuštění
flask run
```

Aplikace bude dostupná na: **http://127.0.0.1:5000**

## Demo přihlašovací údaje

| Pole    | Hodnota                   |
|---------|---------------------------|
| E-mail  | `student@gslapanice.cz`   |
| Heslo   | `Student123!`             |

## Struktura projektu

```
portfolio/
├── app.py              # aplikační továrna + vstupní bod
├── config.py           # konfigurace (SECRET_KEY, DB URI)
├── extensions.py       # SQLAlchemy, LoginManager, Bcrypt, CSRF
├── models.py           # datové modely (User, Skill, Goal, Achievement…)
├── forms.py            # WTForms formuláře s validací
├── seed.py             # naplnění DB kategoriemi, katalogem a demo daty
├── routes/
│   ├── auth.py         # /register, /login, /logout
│   ├── dashboard.py    # /dashboard – přehled
│   ├── skills.py       # /skills – CRUD dovedností + grafy
│   ├── goals.py        # /goals – CRUD cílů (kanban)
│   ├── achievements.py # /achievements – CRUD úspěchů (timeline)
│   └── profile.py      # /profile – údaje, změna hesla, smazání účtu
├── templates/          # Jinja2 šablony
├── static/
│   ├── css/style.css   # celý design (petrolejová paleta)
│   ├── js/charts.js    # Chart.js helpery (radar, line)
│   └── js/main.js      # hamburger menu, confirm dialogy, slidery
├── instance/
│   └── portfolio.db    # SQLite databáze (vytvoří se automaticky)
├── .env.example
├── .gitignore
└── requirements.txt
```

## Funkce

- **Autentizace** – registrace, přihlášení (bcrypt + CSRF), zapamatování
- **Dashboard** – statistické karty, radarový graf TOP dovedností, kanban cílů, aktivitní feed
- **Dovednosti** – CRUD, záložky podle kategorií, okamžitá aktualizace úrovně, liniový graf vývoje, globální radarový přehled
- **Cíle** – kanban board (plánováno / probíhá / dokončeno), progress bary, odpočet dní
- **Úspěchy** – chronologická timeline, typy (certifikát, soutěž, projekt…)
- **Profil** – editace údajů, změna hesla, smazání účtu

## Produkční nasazení

Pro produkci doporučujeme:
- Přejít na **PostgreSQL** (`DATABASE_URL=postgresql://...`)
- Spustit za **gunicorn**: `gunicorn -w 4 "app:create_app()"`
- Přidat reverzní proxy **nginx**
- Nastavit silný `SECRET_KEY` (min. 32 náhodných znaků)
