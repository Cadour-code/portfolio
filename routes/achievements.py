import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, current_app, send_from_directory
from flask_login import login_required, current_user
from extensions import db
from models import Achievement, UserSkill
from forms import AchievementForm

achievements_bp = Blueprint('achievements', __name__, url_prefix='/achievements')

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}


def _allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _save_upload(file_storage):
    ext = file_storage.filename.rsplit('.', 1)[1].lower()
    stored_name = f"{uuid.uuid4().hex}.{ext}"
    folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(folder, exist_ok=True)
    file_storage.save(os.path.join(folder, stored_name))
    return stored_name


def _remove_upload(stored_name):
    if stored_name:
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], stored_name)
        if os.path.exists(path):
            os.remove(path)


def _populate_achievement_form(form, user_id):
    skill_choices = [(0, '— Žádná —')]
    for s in UserSkill.query.filter_by(user_id=user_id).all():
        skill_choices.append((s.id, s.name))
    form.linked_skill_id.choices = skill_choices


@achievements_bp.route('/')
@login_required
def list():
    achievements = Achievement.query.filter_by(user_id=current_user.id).order_by(Achievement.date_achieved.desc()).all()
    return render_template('achievements/list.html', achievements=achievements)


@achievements_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = AchievementForm()
    _populate_achievement_form(form, current_user.id)
    if form.validate_on_submit():
        ach = Achievement(
            user_id=current_user.id,
            title=form.title.data,
            type=form.type.data,
            date_achieved=form.date_achieved.data,
            description=form.description.data,
            issuer=form.issuer.data or None,
            link=form.link.data or None,
            linked_skill_id=form.linked_skill_id.data if form.linked_skill_id.data else None,
        )
        f = form.file.data
        if f and f.filename and _allowed(f.filename):
            ach.file_path = _save_upload(f)
            ach.file_original_name = f.filename
        db.session.add(ach)
        db.session.commit()
        flash('Úspěch byl přidán.', 'success')
        return redirect(url_for('achievements.list'))
    return render_template('achievements/form.html', form=form, title='Přidat úspěch')


@achievements_bp.route('/<int:ach_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(ach_id):
    ach = Achievement.query.filter_by(id=ach_id, user_id=current_user.id).first_or_404()
    form = AchievementForm(obj=ach)
    _populate_achievement_form(form, current_user.id)
    if form.validate_on_submit():
        ach.title = form.title.data
        ach.type = form.type.data
        ach.date_achieved = form.date_achieved.data
        ach.description = form.description.data
        ach.issuer = form.issuer.data or None
        ach.link = form.link.data or None
        ach.linked_skill_id = form.linked_skill_id.data if form.linked_skill_id.data else None
        f = form.file.data
        if f and f.filename and _allowed(f.filename):
            _remove_upload(ach.file_path)
            ach.file_path = _save_upload(f)
            ach.file_original_name = f.filename
        db.session.commit()
        flash('Úspěch byl aktualizován.', 'success')
        return redirect(url_for('achievements.list'))
    if hasattr(form, 'linked_skill_id'):
        form.linked_skill_id.data = ach.linked_skill_id or 0
    return render_template('achievements/form.html', form=form, title='Upravit úspěch', ach=ach)


@achievements_bp.route('/<int:ach_id>/delete', methods=['POST'])
@login_required
def delete(ach_id):
    ach = Achievement.query.filter_by(id=ach_id, user_id=current_user.id).first_or_404()
    _remove_upload(ach.file_path)
    db.session.delete(ach)
    db.session.commit()
    flash('Úspěch byl smazán.', 'success')
    return redirect(url_for('achievements.list'))


@achievements_bp.route('/<int:ach_id>/delete-file', methods=['POST'])
@login_required
def delete_file(ach_id):
    ach = Achievement.query.filter_by(id=ach_id, user_id=current_user.id).first_or_404()
    _remove_upload(ach.file_path)
    ach.file_path = None
    ach.file_original_name = None
    db.session.commit()
    flash('Soubor byl odstraněn.', 'success')
    return redirect(url_for('achievements.edit', ach_id=ach_id))


@achievements_bp.route('/files/<filename>')
@login_required
def serve_file(filename):
    Achievement.query.filter_by(user_id=current_user.id, file_path=filename).first_or_404()
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
