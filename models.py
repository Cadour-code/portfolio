from datetime import datetime, date
from flask_login import UserMixin
from extensions import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    school_class = db.Column(db.String(20))
    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    skills = db.relationship('UserSkill', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    goals = db.relationship('Goal', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    achievements = db.relationship('Achievement', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'


class SkillCategory(db.Model):
    __tablename__ = 'skill_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    color_hex = db.Column(db.String(7), nullable=False, default='#3b82f6')

    catalog_skills = db.relationship('SkillCatalog', backref='category', lazy='dynamic')


class SkillCatalog(db.Model):
    __tablename__ = 'skill_catalog'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('skill_categories.id'), nullable=False)
    description = db.Column(db.Text)


class UserSkill(db.Model):
    __tablename__ = 'user_skills'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    catalog_id = db.Column(db.Integer, db.ForeignKey('skill_catalog.id'), nullable=True)
    custom_name = db.Column(db.String(100), nullable=True)
    custom_category_id = db.Column(db.Integer, db.ForeignKey('skill_categories.id'), nullable=True)
    current_level = db.Column(db.Integer, default=0)
    target_level = db.Column(db.Integer, default=100)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    catalog = db.relationship('SkillCatalog', backref='user_skills')
    custom_category = db.relationship('SkillCategory', foreign_keys=[custom_category_id])
    progress_records = db.relationship('SkillProgress', backref='user_skill', lazy='dynamic', cascade='all, delete-orphan')

    linked_goals = db.relationship('Goal', foreign_keys='Goal.linked_skill_id', backref='linked_skill', lazy='dynamic')
    linked_achievements = db.relationship('Achievement', foreign_keys='Achievement.linked_skill_id', backref='linked_skill', lazy='dynamic')

    @property
    def name(self):
        if self.catalog:
            return self.catalog.name
        return self.custom_name or 'Bez názvu'

    @property
    def category(self):
        if self.catalog:
            return self.catalog.category
        return self.custom_category

    def record_progress(self):
        record = SkillProgress(user_skill_id=self.id, level=self.current_level)
        db.session.add(record)


class SkillProgress(db.Model):
    __tablename__ = 'skill_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_skill_id = db.Column(db.Integer, db.ForeignKey('user_skills.id'), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)


class Goal(db.Model):
    __tablename__ = 'goals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    deadline = db.Column(db.Date)
    status = db.Column(db.String(20), default='planned')  # planned, in_progress, completed, cancelled
    progress_percent = db.Column(db.Integer, default=0)
    linked_skill_id = db.Column(db.Integer, db.ForeignKey('user_skills.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    STATUS_LABELS = {
        'planned': 'Plánováno',
        'in_progress': 'Probíhá',
        'completed': 'Dokončeno',
        'cancelled': 'Zrušeno',
    }

    @property
    def status_label(self):
        return self.STATUS_LABELS.get(self.status, self.status)

    @property
    def days_remaining(self):
        if self.deadline:
            delta = self.deadline - date.today()
            return delta.days
        return None


class Achievement(db.Model):
    __tablename__ = 'achievements'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    date_achieved = db.Column(db.Date, nullable=False)
    type = db.Column(db.String(50), default='other')  # certificate, competition, project, publication, internship, volunteering, other
    issuer = db.Column(db.String(200))
    link = db.Column(db.String(500))
    file_path = db.Column(db.String(255))
    file_original_name = db.Column(db.String(500))
    linked_skill_id = db.Column(db.Integer, db.ForeignKey('user_skills.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    TYPE_LABELS = {
        'certificate': 'Certifikát',
        'competition': 'Soutěž',
        'project': 'Projekt',
        'publication': 'Publikace',
        'internship': 'Stáž',
        'volunteering': 'Dobrovolnictví',
        'other': 'Jiné',
    }

    TYPE_ICONS = {
        'certificate': 'fa-certificate',
        'competition': 'fa-trophy',
        'project': 'fa-code',
        'publication': 'fa-book',
        'internship': 'fa-briefcase',
        'volunteering': 'fa-heart',
        'other': 'fa-star',
    }

    @property
    def type_label(self):
        return self.TYPE_LABELS.get(self.type, self.type)

    @property
    def type_icon(self):
        return self.TYPE_ICONS.get(self.type, 'fa-star')
