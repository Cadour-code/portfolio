"""Seed script – fills DB with categories, skill catalog, and a demo user."""
import os
import sys
import io
from datetime import datetime

# Ensure UTF-8 output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Allow running directly: python seed.py
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from extensions import db, bcrypt
from models import SkillCategory, SkillCatalog, User


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        # ── Categories ──────────────────────────────────────────────────────
        categories_data = [
            ('Technické',       '#3b82f6'),
            ('Jazykové',        '#10b981'),
            ('Měkké dovednosti','#f0b800'),
            ('Akademické',      '#8b5cf6'),
            ('Kreativní',       '#ec4899'),
        ]
        cats = {}
        for name, color in categories_data:
            existing = SkillCategory.query.filter_by(name=name).first()
            if not existing:
                cat = SkillCategory(name=name, color_hex=color)
                db.session.add(cat)
                db.session.flush()
                cats[name] = cat
            else:
                cats[name] = existing
        db.session.commit()
        print('✓ Kategorie vytvořeny')

        # ── Skill Catalog ────────────────────────────────────────────────────
        catalog_data = [
            ('Python',                    'Technické',        'Programování v jazyce Python'),
            ('HTML/CSS',                  'Technické',        'Tvorba webových stránek'),
            ('JavaScript',                'Technické',        'Interaktivní skripty pro web'),
            ('Excel / Tabulkový procesor','Technické',        'Práce s tabulkami a daty'),
            ('Git a verzování',           'Technické',        'Správa verzí zdrojového kódu'),
            ('SQL a databáze',            'Technické',        'Dotazování a správa databází'),
            ('Anglický jazyk',            'Jazykové',         'Anglický jazyk – komunikace i odborný text'),
            ('Německý jazyk',             'Jazykové',         'Německý jazyk'),
            ('Španělský jazyk',           'Jazykové',         'Španělský jazyk'),
            ('Francouzský jazyk',         'Jazykové',         'Francouzský jazyk'),
            ('Komunikace',                'Měkké dovednosti', 'Efektivní ústní i písemná komunikace'),
            ('Týmová práce',              'Měkké dovednosti', 'Spolupráce v týmu a skupinové projekty'),
            ('Prezentační dovednosti',    'Měkké dovednosti', 'Příprava a přednes prezentací'),
            ('Kritické myšlení',          'Měkké dovednosti', 'Analytický přístup a hodnocení informací'),
            ('Time management',           'Měkké dovednosti', 'Plánování a efektivní využití času'),
            ('Psaní esejí',               'Akademické',       'Akademické a strukturované psaní'),
            ('Matematika',                'Akademické',       'Matematická analýza, algebra, statistika'),
            ('Výzkumné dovednosti',       'Akademické',       'Rešerše, citace, vědecká práce'),
            ('Grafický design',           'Kreativní',        'Tvorba vizuálních materiálů (Canva, Figma, GIMP)'),
            ('Fotografie',                'Kreativní',        'Fotografování a úprava fotek'),
            ('Video editace',             'Kreativní',        'Střih a produkce videa'),
            ('Hudební produkce',          'Kreativní',        'Tvorba hudby a zvukový design'),
            ('Kreslení',                  'Kreativní',        'Ruční kresba a digitální ilustrace'),
        ]
        for skill_name, cat_name, desc in catalog_data:
            existing = SkillCatalog.query.filter_by(name=skill_name).first()
            if not existing:
                entry = SkillCatalog(name=skill_name, category_id=cats[cat_name].id, description=desc)
                db.session.add(entry)
        db.session.commit()
        print('✓ Katalog dovedností naplněn')

        # ── Admin user ───────────────────────────────────────────────────────
        # Smazat všechny stávající uživatele (cascade odstraní jejich data)
        User.query.delete()
        db.session.commit()
        print('✓ Stávající uživatelé smazáni')

        demo = User(
            email='admin@gslap.cz',
            password_hash=bcrypt.generate_password_hash('Riegrova17-').decode('utf-8'),
            first_name='Admin',
            last_name='',
        )
        db.session.add(demo)
        db.session.commit()
        print('✓ Admin účet vytvořen')

        print('\n══════════════════════════════════')
        print('  Seed dokončen!')
        print('  Admin přihlašovací údaje:')
        print('  E-mail:  admin@gslap.cz')
        print('  Heslo:   Riegrova17-')
        print('══════════════════════════════════\n')


if __name__ == '__main__':
    seed()
