from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


##WTForm
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")


class Movieform(FlaskForm):
    new_rating = StringField("Your New Rating Out Of 10 :", validators=[DataRequired()])
    new_review = StringField("Your Review : ", validators=[DataRequired()])
    submit = SubmitField("Submit")


class Addform(FlaskForm):
    movie_title = StringField("Enter movie title : ", validators=[DataRequired()])
    submit = SubmitField("search")
