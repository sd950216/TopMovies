from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FloatField
from wtforms.csrf.core import CSRFTokenField
from wtforms.validators import DataRequired, URL, InputRequired, NumberRange, Length, Email


##WTForm
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    # csrf_token = CSRFTokenField()
    submit = SubmitField("Log In")


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(),Email()])
    username = StringField("Username", validators=[InputRequired(), Length(min=4, max=32)])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8, max=64)])
    submit = SubmitField("Register")


class MovieRatingForm(FlaskForm):
    # new_rating = StringField("Your New Rating Out Of 10 :", validators=[DataRequired()])
    new_rating = FloatField(label='Your New Rating Out Of 10 :', validators=[InputRequired(), NumberRange(min=0, max=10)])
    submit = SubmitField("Submit")


class SearchForm(FlaskForm):
    movie_title = StringField("Enter movie title : ", validators=[DataRequired()])
    submit = SubmitField("search")
