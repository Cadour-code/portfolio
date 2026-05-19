from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import desc
from models import UserSkill, Goal, Achievement, SkillProgress
from extensions import db
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    skills = current_user.skills.all()
    goals = current_user.goals.all()
    achievements = current_user.achievements.all()

    skill_count = len(skills)
    avg_level = round(sum(s.current_level for s in skills) / len(skills), 1) if skills else 0
    active_goals = sum(1 for g in goals if g.status in ('planned', 'in_progress'))
    achievement_count = len(achievements)

    # Top 6 skills for radar chart
    top_skills = sorted(skills, key=lambda s: s.current_level, reverse=True)[:6]
    radar_labels = [s.name for s in top_skills]
    radar_data = [s.current_level for s in top_skills]

    # 3 upcoming goals (closest deadline, not completed/cancelled)
    upcoming_goals = [g for g in goals if g.status in ('planned', 'in_progress') and g.deadline]
    upcoming_goals.sort(key=lambda g: g.deadline)
    upcoming_goals = upcoming_goals[:3]

    # Activity timeline (last 5 combined)
    activities = []
    for s in skills:
        activities.append({'type': 'skill', 'title': f'Přidána dovednost: {s.name}', 'date': s.created_at, 'icon': 'fa-bolt'})
    for g in goals:
        activities.append({'type': 'goal', 'title': f'Cíl: {g.title}', 'date': g.created_at, 'icon': 'fa-bullseye'})
    for a in achievements:
        activities.append({'type': 'achievement', 'title': f'Úspěch: {a.title}', 'date': a.created_at, 'icon': 'fa-trophy'})
    activities.sort(key=lambda x: x['date'], reverse=True)
    activities = activities[:5]

    return render_template('dashboard.html',
        skill_count=skill_count,
        avg_level=avg_level,
        active_goals=active_goals,
        achievement_count=achievement_count,
        radar_labels=radar_labels,
        radar_data=radar_data,
        upcoming_goals=upcoming_goals,
        activities=activities,
    )
