from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user, logout_user
from extensions import db, bcrypt
from forms import ProfileForm, ChangePasswordForm

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')


@profile_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    profile_form = ProfileForm(obj=current_user)
    password_form = ChangePasswordForm()

    if profile_form.validate_on_submit() and 'save_profile' in profile_form._fields:
        current_user.first_name = profile_form.first_name.data
        current_user.last_name = profile_form.last_name.data
        current_user.school_class = profile_form.school_class.data
        current_user.bio = profile_form.bio.data
        db.session.commit()
        flash('Profil byl aktualizován.', 'success')
        return redirect(url_for('profile.index'))

    return render_template('profile.html', profile_form=profile_form, password_form=password_form)


@profile_bp.route('/update', methods=['POST'])
@login_required
def update():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.school_class = form.school_class.data
        current_user.bio = form.bio.data
        db.session.commit()
        flash('Profil byl aktualizován.', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{error}', 'danger')
    return redirect(url_for('profile.index'))


@profile_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not bcrypt.check_password_hash(current_user.password_hash, form.old_password.data):
            flash('Stávající heslo je nesprávné.', 'danger')
        else:
            current_user.password_hash = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            db.session.commit()
            flash('Heslo bylo úspěšně změněno.', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{error}', 'danger')
    return redirect(url_for('profile.index'))


@profile_bp.route('/delete', methods=['POST'])
@login_required
def delete():
    user = current_user._get_current_object()
    logout_user()
    db.session.delete(user)
    db.session.commit()
    flash('Váš účet byl smazán.', 'info')
    return redirect(url_for('auth.login'))
