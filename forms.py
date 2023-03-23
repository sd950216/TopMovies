from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FloatField
from wtforms.csrf.core import CSRFTokenField
from wtforms.validators import DataRequired, URL, InputRequired, NumberRange, Length, Email


##WTForm
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(),Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    # csrf_token = CSRFTokenField()

    submit = SubmitField("Log In")


class Movieform(FlaskForm):
    # new_rating = StringField("Your New Rating Out Of 10 :", validators=[DataRequired()])
    new_rating = FloatField('Your New Rating Out Of 10 :', validators=[InputRequired(), NumberRange(min=0, max=10)])
    new_review = StringField("Your Review : ", validators=[DataRequired(), Length(min=6)],
                             render_kw={"placeholder": "Enter your review"})
    submit = SubmitField("Submit")


class Addform(FlaskForm):
    movie_title = StringField("Enter movie title : ", validators=[DataRequired()])
    submit = SubmitField("search")
