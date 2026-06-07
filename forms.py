from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, PasswordField, BooleanField, TextAreaField,
                     SelectField, IntegerField, DateField, URLField, SubmitField)
from wtforms.validators import (DataRequired, Email, Length, EqualTo,
                                NumberRange, Optional, URL, ValidationError)
from models import User


class RegistrationForm(FlaskForm):
    first_name = StringField('Jméno', validators=[DataRequired(), Length(max=100)])
    last_name = StringField('Příjmení', validators=[DataRequired(), Length(max=100)])
    email = StringField('E-mail', validators=[DataRequired(), Email(), Length(max=255)])
    school_class = StringField('Třída', validators=[Optional(), Length(max=20)])
    password = PasswordField('Heslo', validators=[DataRequired(), Length(min=8, message='Heslo musí mít alespoň 8 znaků.')])
    confirm_password = PasswordField('Potvrdit heslo', validators=[DataRequired(), EqualTo('password', message='Hesla se neshodují.')])
    submit = SubmitField('Registrovat se')

    def validate_email(self, field):
        if not field.data.lower().endswith('@gslap.cz'):
            raise ValidationError('Registrace je povolena pouze pro e-maily s doménou @gslap.cz.')
        user = User.query.filter_by(email=field.data.lower()).first()
        if user:
            raise ValidationError('Tento e-mail je již registrován.')


class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Heslo', validators=[DataRequired()])
    remember = BooleanField('Zapamatovat si mě')
    submit = SubmitField('Přihlásit se')


class ProfileForm(FlaskForm):
    first_name = StringField('Jméno', validators=[DataRequired(), Length(max=100)])
    last_name = StringField('Příjmení', validators=[DataRequired(), Length(max=100)])
    school_class = StringField('Třída', validators=[Optional(), Length(max=20)])
    bio = TextAreaField('O mně', validators=[Optional(), Length(max=1000)])
    submit = SubmitField('Uložit změny')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Stávající heslo', validators=[DataRequired()])
    new_password = PasswordField('Nové heslo', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Potvrdit nové heslo', validators=[DataRequired(), EqualTo('new_password', message='Hesla se neshodují.')])
    submit = SubmitField('Změnit heslo')


class SkillForm(FlaskForm):
    catalog_id = SelectField('Dovednost z katalogu', coerce=int, validators=[Optional()])
    custom_name = StringField('Vlastní název dovednosti', validators=[Optional(), Length(max=100)])
    custom_category_id = SelectField('Kategorie vlastní dovednosti', coerce=int, validators=[Optional()])
    current_level = IntegerField('Aktuální úroveň (0–100)', validators=[DataRequired(), NumberRange(min=0, max=100)])
    target_level = IntegerField('Cílová úroveň (0–100)', validators=[DataRequired(), NumberRange(min=0, max=100)])
    notes = TextAreaField('Poznámky', validators=[Optional(), Length(max=2000)])
    submit = SubmitField('Uložit')

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False
        if not self.catalog_id.data and not self.custom_name.data:
            self.custom_name.errors.append('Vyberte dovednost z katalogu nebo zadejte vlastní název.')
            return False
        if self.custom_name.data and not self.custom_category_id.data:
            self.custom_category_id.errors.append('Pro vlastní dovednost vyberte kategorii.')
            return False
        return True


class UpdateSkillLevelForm(FlaskForm):
    current_level = IntegerField('Úroveň', validators=[DataRequired(), NumberRange(min=0, max=100)])
    submit = SubmitField('Aktualizovat')


class GoalForm(FlaskForm):
    title = StringField('Název cíle', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Popis', validators=[Optional(), Length(max=2000)])
    deadline = DateField('Termín', validators=[Optional()])
    status = SelectField('Stav', choices=[
        ('planned', 'Plánováno'),
        ('in_progress', 'Probíhá'),
        ('completed', 'Dokončeno'),
        ('cancelled', 'Zrušeno'),
    ])
    progress_percent = IntegerField('Pokrok (%)', validators=[DataRequired(), NumberRange(min=0, max=100)], default=0)
    linked_skill_id = SelectField('Propojená dovednost', coerce=int, validators=[Optional()])
    submit = SubmitField('Uložit')


class AchievementForm(FlaskForm):
    title = StringField('Název', validators=[DataRequired(), Length(max=200)])
    type = SelectField('Typ', choices=[
        ('certificate', 'Certifikát'),
        ('competition', 'Soutěž'),
        ('project', 'Projekt'),
        ('publication', 'Publikace'),
        ('internship', 'Stáž'),
        ('volunteering', 'Dobrovolnictví'),
        ('other', 'Jiné'),
    ])
    date_achieved = DateField('Datum dosažení', validators=[DataRequired()])
    description = TextAreaField('Popis', validators=[Optional(), Length(max=2000)])
    issuer = StringField('Vydavatel / Organizátor', validators=[Optional(), Length(max=200)])
    link = URLField('Odkaz', validators=[Optional(), URL(message='Zadejte platnou URL adresu.')])
    file = FileField('Příloha', validators=[
        FileAllowed(['pdf', 'png', 'jpg', 'jpeg'], 'Povolené formáty: PDF, PNG, JPG.')
    ])
    linked_skill_id = SelectField('Propojená dovednost', coerce=int, validators=[Optional()])
    submit = SubmitField('Uložit')


class ForgotPasswordForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    submit = SubmitField('Odeslat odkaz pro obnovu hesla')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nové heslo', validators=[DataRequired(), Length(min=8, message='Heslo musí mít alespoň 8 znaků.')])
    confirm_password = PasswordField('Potvrdit nové heslo', validators=[DataRequired(), EqualTo('password', message='Hesla se neshodují.')])
    submit = SubmitField('Nastavit nové heslo')
