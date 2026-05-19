"""Seed script – fills DB with categories, skill catalog, and a demo user."""
import os
import sys
import io
from datetime import date, datetime, timedelta

# Ensure UTF-8 output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Allow running directly: python seed.py
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from extensions import db, bcrypt
from models import SkillCategory, SkillCatalog, User, UserSkill, SkillProgress, Goal, Achievement


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

        # ── Demo user ────────────────────────────────────────────────────────
        demo_email = 'student@gslapanice.cz'
        demo = User.query.filter_by(email=demo_email).first()
        if not demo:
            demo = User(
                email=demo_email,
                password_hash=bcrypt.generate_password_hash('Student123!').decode('utf-8'),
                first_name='Jan',
                last_name='Novák',
                school_class='3.A',
                bio='Mám rád programování, matematik a fotografii. Chtěl bych se stát softwarovým inženýrem.',
            )
            db.session.add(demo)
            db.session.commit()
            print('✓ Demo uživatel vytvořen')
        else:
            print('  Demo uživatel již existuje, přeskočeno')

        # ── Demo skills ──────────────────────────────────────────────────────
        if not UserSkill.query.filter_by(user_id=demo.id).first():
            cat_lookup = {c.name: c for c in SkillCatalog.query.all()}

            demo_skills = [
                ('Python',                     72, 90),
                ('HTML/CSS',                   60, 80),
                ('JavaScript',                 45, 75),
                ('Anglický jazyk',             80, 95),
                ('Komunikace',                 70, 85),
                ('Prezentační dovednosti',     55, 80),
                ('Matematika',                 85, 90),
                ('Grafický design',            40, 70),
                ('Fotografie',                 65, 80),
            ]
            created_skills = {}
            now = datetime.utcnow()
            for skill_name, current, target in demo_skills:
                cat_entry = cat_lookup.get(skill_name)
                if not cat_entry:
                    continue
                us = UserSkill(
                    user_id=demo.id,
                    catalog_id=cat_entry.id,
                    current_level=current,
                    target_level=target,
                    created_at=now - timedelta(days=60),
                )
                db.session.add(us)
                db.session.flush()
                created_skills[skill_name] = us

                # Progress history
                start_level = max(0, current - 30)
                steps = 5
                for i in range(steps):
                    lvl = start_level + int((current - start_level) * i / (steps - 1))
                    rec = SkillProgress(
                        user_skill_id=us.id,
                        level=lvl,
                        recorded_at=now - timedelta(days=60 - i * 12),
                    )
                    db.session.add(rec)
                # Final current
                db.session.add(SkillProgress(user_skill_id=us.id, level=current, recorded_at=now))

            db.session.commit()
            print('✓ Demo dovednosti vytvořeny')

        # ── Demo goals ───────────────────────────────────────────────────────
        if not Goal.query.filter_by(user_id=demo.id).first():
            python_skill = UserSkill.query.join(SkillCatalog).filter(
                UserSkill.user_id == demo.id, SkillCatalog.name == 'Python'
            ).first()

            goals_data = [
                ('Dokončit kurz Pythonu pro začátečníky', 'Projít celý online kurz na Udemy a vyřešit všechny úkoly.', date.today() + timedelta(days=30), 'in_progress', 60, python_skill.id if python_skill else None),
                ('Vytvořit osobní web portfolio', 'Napsat portfolio web v HTML/CSS/JS a zveřejnit ho na GitHubu.', date.today() + timedelta(days=45), 'planned', 20, None),
                ('Získat certifikát PCEP', 'Složit Python Certified Entry-Level Programmer certifikát.', date.today() + timedelta(days=90), 'planned', 10, python_skill.id if python_skill else None),
                ('Připravit maturitní esej', 'Napsat strukturovanou esej na 5 stránek k maturitnímu tématu.', date.today() - timedelta(days=10), 'completed', 100, None),
            ]
            for title, desc, deadline, status, progress, skill_id in goals_data:
                g = Goal(user_id=demo.id, title=title, description=desc,
                         deadline=deadline, status=status, progress_percent=progress,
                         linked_skill_id=skill_id)
                db.session.add(g)
            db.session.commit()
            print('✓ Demo cíle vytvořeny')

        # ── Demo achievements ────────────────────────────────────────────────
        if not Achievement.query.filter_by(user_id=demo.id).first():
            python_skill = UserSkill.query.join(SkillCatalog).filter(
                UserSkill.user_id == demo.id, SkillCatalog.name == 'Python'
            ).first()
            photo_skill = UserSkill.query.join(SkillCatalog).filter(
                UserSkill.user_id == demo.id, SkillCatalog.name == 'Fotografie'
            ).first()

            ach_data = [
                ('Certifikát CS50x – Introduction to Computer Science', 'certificate', date(2024, 6, 15), 'Absolvoval jsem online kurz Harvard CS50x s výsledkem 95 %.', 'Harvard / edX', 'https://cs50.harvard.edu', python_skill.id if python_skill else None),
                ('3. místo – školní olympiáda z matematiky', 'competition', date(2024, 3, 20), 'Umístil jsem se na 3. místě v krajském kole matematické olympiády kategorie B.', 'Gymnázium Šlapanice', None, None),
                ('Fotografická výstava „Šlapanice v zimě"', 'project', date(2024, 2, 5), 'Připravil jsem výstavu 12 fotografií zachycujících zimní Šlapanice. Vystaveno v aule gymnázia.', None, None, photo_skill.id if photo_skill else None),
                ('Dobrovolnická práce na školním webu', 'volunteering', date(2023, 11, 1), 'Pomáhal jsem s redesignem školního webu – HTML, CSS a základní JS.', 'Gymnázium Šlapanice', None, None),
            ]
            for title, atype, dt, desc, issuer, link, skill_id in ach_data:
                a = Achievement(user_id=demo.id, title=title, type=atype, date_achieved=dt,
                                description=desc, issuer=issuer, link=link,
                                linked_skill_id=skill_id)
                db.session.add(a)
            db.session.commit()
            print('✓ Demo úspěchy vytvořeny')

        print('\n══════════════════════════════════')
        print('  Seed dokončen!')
        print('  Demo přihlašovací údaje:')
        print('  E-mail:  student@gslapanice.cz')
        print('  Heslo:   Student123!')
        print('══════════════════════════════════\n')


if __name__ == '__main__':
    seed()
