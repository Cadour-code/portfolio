from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import Goal, UserSkill
from forms import GoalForm
from datetime import datetime

goals_bp = Blueprint('goals', __name__, url_prefix='/goals')


def _populate_goal_form(form, user_id):
    skill_choices = [(0, '— Žádná —')]
    for s in UserSkill.query.filter_by(user_id=user_id).all():
        skill_choices.append((s.id, s.name))
    form.linked_skill_id.choices = skill_choices


@goals_bp.route('/')
@login_required
def list():
    status_filter = request.args.get('status', 'all')
    sort = request.args.get('sort', 'deadline')

    query = Goal.query.filter_by(user_id=current_user.id)
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    if sort == 'deadline':
        query = query.order_by(Goal.deadline.asc().nullslast())
    else:
        query = query.order_by(Goal.created_at.desc())

    goals = query.all()

    planned = [g for g in Goal.query.filter_by(user_id=current_user.id, status='planned').order_by(Goal.deadline.asc().nullslast()).all()]
    in_progress = [g for g in Goal.query.filter_by(user_id=current_user.id, status='in_progress').order_by(Goal.deadline.asc().nullslast()).all()]
    completed = [g for g in Goal.query.filter_by(user_id=current_user.id, status='completed').order_by(Goal.deadline.desc()).all()]

    return render_template('goals/list.html',
        goals=goals,
        planned=planned,
        in_progress=in_progress,
        completed=completed,
        status_filter=status_filter,
        sort=sort,
    )


@goals_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = GoalForm()
    _populate_goal_form(form, current_user.id)
    if form.validate_on_submit():
        goal = Goal(
            user_id=current_user.id,
            title=form.title.data,
            description=form.description.data,
            deadline=form.deadline.data,
            status=form.status.data,
            progress_percent=form.progress_percent.data,
            linked_skill_id=form.linked_skill_id.data if form.linked_skill_id.data else None,
        )
        db.session.add(goal)
        db.session.commit()
        flash('Cíl byl přidán.', 'success')
        return redirect(url_for('goals.list'))
    form.progress_percent.data = form.progress_percent.data or 0
    return render_template('goals/form.html', form=form, title='Přidat cíl')


@goals_bp.route('/<int:goal_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(goal_id):
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    form = GoalForm(obj=goal)
    _populate_goal_form(form, current_user.id)
    if form.validate_on_submit():
        goal.title = form.title.data
        goal.description = form.description.data
        goal.deadline = form.deadline.data
        goal.status = form.status.data
        goal.progress_percent = form.progress_percent.data
        goal.linked_skill_id = form.linked_skill_id.data if form.linked_skill_id.data else None
        db.session.commit()
        flash('Cíl byl aktualizován.', 'success')
        return redirect(url_for('goals.list'))
    if request.method == 'GET':
        form.linked_skill_id.data = goal.linked_skill_id or 0
    return render_template('goals/form.html', form=form, title='Upravit cíl', goal=goal)


@goals_bp.route('/<int:goal_id>/complete', methods=['POST'])
@login_required
def complete(goal_id):
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    goal.status = 'completed'
    goal.progress_percent = 100
    db.session.commit()
    flash(f'Cíl „{goal.title}" byl označen jako dokončený!', 'success')
    return redirect(url_for('goals.list'))


@goals_bp.route('/<int:goal_id>/delete', methods=['POST'])
@login_required
def delete(goal_id):
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    db.session.delete(goal)
    db.session.commit()
    flash('Cíl byl smazán.', 'success')
    return redirect(url_for('goals.list'))
