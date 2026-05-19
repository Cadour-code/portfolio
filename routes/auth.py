from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from extensions import db, bcrypt, mail
from models import User
from forms import RegistrationForm, LoginForm, ForgotPasswordForm, ResetPasswordForm

auth_bp = Blueprint('auth', __name__)


def _serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])


def _generate_reset_token(email):
    return _serializer().dumps(email, salt='pw-reset-salt')


def _verify_reset_token(token, max_age=3600):
    try:
        return _serializer().loads(token, salt='pw-reset-salt', max_age=max_age)
    except Exception:
        return None


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            email=form.email.data.lower(),
            password_hash=hashed,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            school_class=form.school_class.data,
        )
        db.session.add(user)
        db.session.commit()
        flash('Registrace proběhla úspěšně. Nyní se přihlaste.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'Vítej zpět, {user.first_name}!', 'success')
            return redirect(next_page or url_for('dashboard.index'))
        flash('Nesprávný e-mail nebo heslo.', 'danger')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Byl jsi úspěšně odhlášen.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = _generate_reset_token(user.email)
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            msg = Message(
                subject='Obnova hesla – Studentské portfolio',
                recipients=[user.email],
                body=(
                    f'Dobrý den, {user.first_name},\n\n'
                    f'Obdrželi jsme žádost o obnovu hesla k vašemu účtu.\n\n'
                    f'Pro nastavení nového hesla klikněte na odkaz níže (platný 1 hodinu):\n'
                    f'{reset_url}\n\n'
                    f'Pokud jste o obnovu hesla nežádali, tento e-mail ignorujte.\n\n'
                    f'Gymnázium Šlapanice – Studentské portfolio'
                )
            )
            try:
                mail.send(msg)
            except Exception:
                flash('Nepodařilo se odeslat e-mail. Zkontrolujte nastavení SMTP v souboru .env.', 'danger')
                return render_template('auth/forgot_password.html', form=form)
        # Vždy zobrazit stejnou zprávu – ochrana proti zjišťování registrovaných e-mailů
        flash('Pokud je e-mail registrován, odeslali jsme odkaz pro obnovu hesla.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot_password.html', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    email = _verify_reset_token(token)
    if not email:
        flash('Odkaz pro obnovu hesla je neplatný nebo vypršel.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('Účet nenalezen.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        db.session.commit()
        flash('Heslo bylo úspěšně změněno. Nyní se přihlaste.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form, token=token)
