from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FloatField, EmailField, validators
from wtforms.validators import DataRequired, InputRequired, NumberRange, Length


# WTForm

class LoginForm(FlaskForm):
    email = EmailField('Email', [validators.DataRequired(), validators.Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    # csrf_token = CSRFTokenField()
    submit = SubmitField("Log In")


class RegisterForm(FlaskForm):
    email = EmailField('Email', [validators.DataRequired(), validators.Email()])
    username = StringField("Username", validators=[InputRequired(), Length(min=4, max=32)])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8, max=64)])
    submit = SubmitField("Register")


class MovieRatingForm(FlaskForm):
    # new_rating = StringField("Your New Rating Out Of 10 :", validators=[DataRequired()])
    new_rating = FloatField(label='Your New Rating Out Of 10 :',
                            validators=[InputRequired(), NumberRange(min=0, max=10)])
    submit = SubmitField("Submit")


class SearchForm(FlaskForm):
    movie_title = StringField("Enter movie title : ", validators=[DataRequired()])
    submit = SubmitField("search")
