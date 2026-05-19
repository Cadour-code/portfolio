from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import UserSkill, SkillCatalog, SkillCategory, SkillProgress
from forms import SkillForm, UpdateSkillLevelForm
from datetime import datetime

skills_bp = Blueprint('skills', __name__, url_prefix='/skills')


def _populate_skill_form_choices(form):
    catalog_choices = [(0, '— Vyberte z katalogu —')]
    for skill in SkillCatalog.query.join(SkillCategory).order_by(SkillCategory.name, SkillCatalog.name).all():
        catalog_choices.append((skill.id, f'{skill.name} ({skill.category.name})'))
    form.catalog_id.choices = catalog_choices

    cat_choices = [(0, '— Vyberte kategorii —')]
    for cat in SkillCategory.query.order_by(SkillCategory.name).all():
        cat_choices.append((cat.id, cat.name))
    form.custom_category_id.choices = cat_choices


@skills_bp.route('/')
@login_required
def list():
    category_filter = request.args.get('category', 'all')
    skills = current_user.skills.all()
    categories = SkillCategory.query.order_by(SkillCategory.name).all()

    if category_filter != 'all':
        filtered = []
        for s in skills:
            cat = s.category
            if cat and str(cat.id) == category_filter:
                filtered.append(s)
        skills = filtered

    # Radar data per category for global chart
    cat_skills = {}
    for cat in categories:
        cat_skills[cat.id] = {
            'name': cat.name,
            'color': cat.color_hex,
            'labels': [],
            'data': [],
        }
    for s in current_user.skills.all():
        cat = s.category
        if cat and cat.id in cat_skills:
            cat_skills[cat.id]['labels'].append(s.name)
            cat_skills[cat.id]['data'].append(s.current_level)

    return render_template('skills/list.html',
        skills=skills,
        categories=categories,
        category_filter=category_filter,
        cat_skills=cat_skills,
    )


@skills_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = SkillForm()
    _populate_skill_form_choices(form)
    if form.validate_on_submit():
        skill = UserSkill(
            user_id=current_user.id,
            catalog_id=form.catalog_id.data if form.catalog_id.data else None,
            custom_name=form.custom_name.data or None,
            custom_category_id=form.custom_category_id.data if form.custom_category_id.data else None,
            current_level=form.current_level.data,
            target_level=form.target_level.data,
            notes=form.notes.data,
        )
        db.session.add(skill)
        db.session.flush()
        skill.record_progress()
        db.session.commit()
        flash('Dovednost byla přidána.', 'success')
        return redirect(url_for('skills.list'))
    form.current_level.data = form.current_level.data or 0
    form.target_level.data = form.target_level.data or 100
    return render_template('skills/form.html', form=form, title='Přidat dovednost')


@skills_bp.route('/<int:skill_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(skill_id):
    skill = UserSkill.query.filter_by(id=skill_id, user_id=current_user.id).first_or_404()
    form = SkillForm(obj=skill)
    _populate_skill_form_choices(form)
    if form.validate_on_submit():
        old_level = skill.current_level
        skill.catalog_id = form.catalog_id.data if form.catalog_id.data else None
        skill.custom_name = form.custom_name.data or None
        skill.custom_category_id = form.custom_category_id.data if form.custom_category_id.data else None
        skill.current_level = form.current_level.data
        skill.target_level = form.target_level.data
        skill.notes = form.notes.data
        skill.updated_at = datetime.utcnow()
        if skill.current_level != old_level:
            skill.record_progress()
        db.session.commit()
        flash('Dovednost byla aktualizována.', 'success')
        return redirect(url_for('skills.list'))
    if request.method == 'GET':
        form.catalog_id.data = skill.catalog_id or 0
        form.custom_category_id.data = skill.custom_category_id or 0
    return render_template('skills/form.html', form=form, title='Upravit dovednost', skill=skill)


@skills_bp.route('/<int:skill_id>/update-level', methods=['POST'])
@login_required
def update_level(skill_id):
    skill = UserSkill.query.filter_by(id=skill_id, user_id=current_user.id).first_or_404()
    form = UpdateSkillLevelForm()
    if form.validate_on_submit():
        if skill.current_level != form.current_level.data:
            skill.current_level = form.current_level.data
            skill.updated_at = datetime.utcnow()
            skill.record_progress()
            db.session.commit()
            flash('Úroveň dovednosti byla aktualizována.', 'success')
    else:
        flash('Neplatná hodnota.', 'danger')
    return redirect(url_for('skills.list'))


@skills_bp.route('/<int:skill_id>')
@login_required
def detail(skill_id):
    skill = UserSkill.query.filter_by(id=skill_id, user_id=current_user.id).first_or_404()
    progress = skill.progress_records.order_by(SkillProgress.recorded_at).all()
    labels = [p.recorded_at.strftime('%d.%m.%Y %H:%M') for p in progress]
    data = [p.level for p in progress]
    update_form = UpdateSkillLevelForm()
    return render_template('skills/detail.html', skill=skill, labels=labels, data=data, update_form=update_form)


@skills_bp.route('/<int:skill_id>/delete', methods=['POST'])
@login_required
def delete(skill_id):
    skill = UserSkill.query.filter_by(id=skill_id, user_id=current_user.id).first_or_404()
    db.session.delete(skill)
    db.session.commit()
    flash('Dovednost byla smazána.', 'success')
    return redirect(url_for('skills.list'))
