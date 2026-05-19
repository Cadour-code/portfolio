# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Flask MVP studentského portfolia pro Gymnázium Šlapanice. České UI, petrolejová barevná paleta (`--color-primary: #1d504c`). Demo přihlášení: `student@gslapanice.cz` / `Student123!`.

## Spuštění a vývoj

```powershell
# Aktivace virtualenv (Windows)
.\venv\Scripts\activate

# Spuštění dev serveru
flask run

# Naplnění DB demo daty (nutné při prázdné DB)
python seed.py

# Migrace nových sloupců (SQLite nepodporuje automatické ALTER TABLE)
# Po přidání sloupce do modelu spustit ručně:
python -c "
from app import create_app
from extensions import db
from sqlalchemy import text
app = create_app()
with app.app_context():
    with db.engine.connect() as conn:
        conn.execute(text('ALTER TABLE tabulka ADD COLUMN sloupec TYP'))
        conn.commit()
"
```

Aplikace běží na `http://127.0.0.1:5000`. Není CI/CD ani testy – ověřování probíhá ručním testováním v prohlížeči.

## Architektura

### App factory (`app.py`)

`create_app()` inicializuje všechny Flask extensions, registruje blueprinty a nastavuje upload složku (`instance/uploads/achievements/`). Limit uploadu: 8 MB. `db.create_all()` se volá při každém startu – nové tabulky se vytvoří, ale nové sloupce do existujících tabulek se **nepřidají** (viz výše).

### Extensions (`extensions.py`)

Centrální místo pro sdílené objekty: `db` (SQLAlchemy), `bcrypt`, `login_manager`, `csrf` (Flask-WTF), `mail` (Flask-Mail). Importovat odtud, ne vytvářet nové instance.

### Modely (`models.py`)

Všechny modely jsou v jednom souboru. Klíčové vztahy:

- `User` → `UserSkill`, `Goal`, `Achievement` (one-to-many, cascade delete)
- `UserSkill` → `SkillProgress` (historické záznamy úrovně)
- `UserSkill.name` a `UserSkill.category` jsou properties – vracejí hodnoty z katalogu nebo vlastní
- `Goal.status` má 4 hodnoty: `'planned'`, `'in_progress'`, `'completed'`, `'cancelled'` – kanban zobrazuje jen první tři sloupce
- `Achievement` má `file_path` (UUID název na disku) a `file_original_name` (zobrazovaný název)
- `SkillCatalog` je sdílená knihovna dovedností; uživatel si vybírá z ní nebo zadá vlastní

### Blueprinty (`routes/`)

| Blueprint | Prefix | Funkce |
|-----------|--------|--------|
| `auth` | – | `/login`, `/logout`, `/register`, `/forgot-password`, `/reset-password/<token>` |
| `dashboard` | – | `/` přehled se stat kartami a grafy |
| `skills` | `/skills` | CRUD + `/update-level` (POST), `/files/<id>` detail s grafem |
| `goals` | `/goals` | CRUD, kanban board + `/<id>/complete` (POST) |
| `achievements` | `/achievements` | CRUD + `/files/<filename>` (chráněné stahování) + `/delete-file` |
| `profile` | `/profile` | `/update`, `/change-password`, `/delete` |

Každá route chráněna `@login_required`. Všechny dotazy filtrují `user_id=current_user.id` – nikdy nepracovat s cizími záznamy.

### Formuláře (`forms.py`)

WTForms s CSRF ochranou (automaticky přes Flask-WTF). `AchievementForm` obsahuje `FileField` s `FileAllowed` – validuje formát pouze pokud je soubor přiložen.

`linked_skill_id.choices` je dynamický SelectField – musí se naplnit před každým renderem i re-renderem po chybě. Funkce `_populate_achievement_form()` (achievements) a `_populate_goal_form()` (goals) to zajišťují v příslušných routách.

`SkillForm` má vlastní `validate()` – buď musí být vyplněno `catalog_id`, nebo `custom_name` + `custom_category_id`; jinak validace selže.

### Šablony

`base.html` poskytuje `{% block content %}`, `{% block head %}` a `{% block scripts %}`. Auth stránky (`login.html`, `register.html`, `forgot_password.html`, `reset_password.html`) jsou standalone – **nedědí** z `base.html`.

Responzivní breakpointy: 1024px (tablet landscape), 768px (tablet portrait), 640px (mobil), 480px (malý mobil), 400px (velmi malý). Dvousloupcové formulářové gridy: třída `.form-grid-2` (ne inline style).

### Soubory k úspěchům

Uploady ukládány do `instance/uploads/achievements/` jako `{uuid}.{ext}`. Přístup přes `/achievements/files/<filename>` – ověřuje vlastnictví přes DB dotaz. Při smazání záznamu se soubor maže z disku v `_remove_upload()`.

### E-mail (obnova hesla)

Flask-Mail + `itsdangerous.URLSafeTimedSerializer` (salt `'pw-reset-salt'`, platnost 1 hodina). SMTP konfigurace přes proměnné prostředí `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`. Tokeny generuje `_generate_reset_token(email)` v `routes/auth.py`.

### Grafy

Chart.js 4.4.0 přes CDN. Helpery v `static/js/charts.js` – radar chart pro dovednosti, line chart pro historii pokroku. Data předávána z routy jako JSON do Jinja2 šablony, pak do JS.

### CSS

Jeden soubor `static/css/style.css`. Barvy definovány jako CSS custom properties v `:root`. Třída `.no-print` skrývá prvky při tisku. Třída `.print-exclude` na `.timeline-item` skryje nevybrané úspěchy při tisku.

## Konfigurace prostředí (`.env`)

```
SECRET_KEY=...              # povinné
DATABASE_URL=...            # volitelné, výchozí SQLite
MAIL_SERVER=smtp.gmail.com  # pro obnovu hesla
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=...
MAIL_PASSWORD=...
MAIL_DEFAULT_SENDER=...
```

`instance/` je v `.gitignore` – obsahuje `portfolio.db` a `uploads/`.
