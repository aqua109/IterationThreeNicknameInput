from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class NicknameForm(FlaskForm):
    nickname = StringField('Nickname', validators=[DataRequired()])
    colour = SelectField('Colour', choices=[("aqua", "aqua"), ("black", "black"), ("blue", "blue"), ("brown", "brown"), ("cyan", "cyan"), ("darkblue", "darkblue"), ("fuchsia", "fuchsia"), ("green", "green"), ("grey", "grey"), ("lightblue", "lightblue"), ("lime", "lime"), ("magenta", "magenta"), ("maroon", "maroon"), ("navy", "navy"), ("olive", "olive"), ("orange", "orange"), ("purple", "purple"), ("red", "red"), ("silver", "silver"), ("teal", "teal"), ("white", "white"), ("yellow", "yellow")])
    submit = SubmitField('Submit')
