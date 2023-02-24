from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FloatField
from wtforms.validators import DataRequired, URL, InputRequired, NumberRange, Length
from flask_ckeditor import CKEditorField


##WTForm
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")


class Movieform(FlaskForm):
    # new_rating = StringField("Your New Rating Out Of 10 :", validators=[DataRequired()])
    new_rating = FloatField('Your New Rating Out Of 10 :', validators=[NumberRange(min=0, max=10)])
    new_review = StringField("Your Review : ",validators = [Length(min=6)],render_kw={"placeholder": "Enter your review"})
    submit = SubmitField("Submit")



class Addform(FlaskForm):
    movie_title = StringField("Enter movie title : ", validators=[DataRequired()])
    submit = SubmitField("search")
