import os
import random
import smtplib
from functools import wraps
import requests
from flask import Flask, render_template, redirect, url_for, request, flash, session, current_app
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import false
from sqlalchemy.exc import IntegrityError, DataError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.testing.plugin.plugin_base import logging
from werkzeug.security import check_password_hash, generate_password_hash
from PIL import Image, ImageDraw, ImageFont
import urllib.parse
from forms import LoginForm, Addform, Movieform, RegisterForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = False  # disable CSRF protection

csrf = CSRFProtect(app)
Bootstrap(app)
db = SQLAlchemy(app)
app.app_context().push()
Base = declarative_base()
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin, Base):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), unique=True)
    password = db.Column(db.String(250))
    username = db.Column(db.String(250))
    role = db.Column(db.String(50))
    recommendations = db.relationship('Recommendation', backref='user', lazy=True)

    def __init__(self, email, password, username, role):
        self.email = email
        self.password = password
        self.username = username
        self.role = role

    @staticmethod
    def get(user_id):
        return User.query.filter_by(id=user_id).first()

    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()

    def is_admin(self):
        return self.role == 'admin'


class Recommendation(db.Model, Base):
    __tablename__ = "my_recommendations"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    media_id = db.Column(db.Integer, nullable=False)
    media_type = db.Column(db.String, nullable=False)
    title = db.Column(db.String(250), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String, nullable=False)
    img_url = db.Column(db.String, nullable=False)
    site_url = db.Column(db.String, nullable=False)

    def __init__(self, user_id, media_id, media_type, title, year, description, rating, ranking, img_url, site_url,
                 review):
        self.user_id = user_id
        self.media_id = media_id
        self.media_type = media_type
        self.title = title
        self.year = year
        self.description = description
        self.rating = rating
        self.ranking = ranking
        self.img_url = img_url
        self.site_url = site_url
        self.review = review


#
# rec = Recommendation(user_id=2,media_id=45,media_type='tv',title="title",year=2000,
#                      description="description",rating=10.1,ranking="ranking",img_url="img_url",site_url="site_url",review="review")
# db.session.add(rec)
# db.session.commit()


class Trending(db.Model, Base):
    __tablename__ = "Trending"
    id = db.Column(db.Integer, primary_key=True)
    media_id = db.Column(db.Integer, nullable=False)
    media_type = db.Column(db.String, nullable=False)
    title = db.Column(db.String(250), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String, nullable=False)
    img_url = db.Column(db.String, nullable=False)
    site_url = db.Column(db.String, nullable=False)


class Discover(db.Model, Base):
    __tablename__ = "Discover"
    id = db.Column(db.Integer, primary_key=True)
    media_id = db.Column(db.Integer, nullable=False)
    media_type = db.Column(db.String, nullable=False)
    title = db.Column(db.String(250), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String, nullable=False)
    img_url = db.Column(db.String, nullable=False)
    site_url = db.Column(db.String, nullable=False)


class Searches(db.Model, Base):
    __tablename__ = "Searches"
    id = db.Column(db.Integer, primary_key=True)
    media_id = db.Column(db.Integer, nullable=False)
    media_type = db.Column(db.String, nullable=False)
    title = db.Column(db.String(250), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String, nullable=False)
    img_url = db.Column(db.String, nullable=False)
    site_url = db.Column(db.String, nullable=False)
    requested_by = db.Column(db.String, nullable=false)


# db.drop_all()
# db.create_all()


def admin_only(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return _handle_unauthorized()
        if current_user.id != 1:
            return _handle_unauthorized('You are not authorized to access this page')
        return view_func(*args, **kwargs)

    return wrapper


@login_manager.unauthorized_handler
def _handle_unauthorized(message='You are not authorized to access this page'):
    flash(message)
    return redirect(url_for('login'))


def logged_in(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        return func(*args, **kwargs)

    return decorated_function


def execute(media_id, media_type, search_type, title, year, description, rating, ranking, review, img_url, site_url,
            **kwargs):
    movie_classes = {'trending': Trending, 'discover': Discover, 'movie': Recommendation}
    rounded_rating = round(float(rating), 1)
    movie_class = movie_classes[search_type]
    # new_media = movie_class(user_id=kwargs['user_id'], media_id=media_id, media_type=media_type, title=title,
    #                         year=year, description=description,
    #                         rating=rounded_rating, ranking=ranking,
    #                         review=review, img_url=img_url, site_url=site_url)
    new_media = movie_class(media_id=media_id, media_type=media_type, title=title,
                            year=year, description=description,
                            rating=rounded_rating, ranking=ranking,
                            review=review, img_url=img_url, site_url=site_url)
    try:
        print(new_media)
        db.session.add(new_media)
        db.session.commit()
    except (IntegrityError, DataError) as e:
        logging.exception('Error adding media record: %s', e)
        raise


def generate_code_and_send_email():
    # Generate a 6-digit random code
    code = random.randint(100000, 999999)
    # Print the code to the console
    print("Your verification code is:", code)
    # Create an SMTP object and login to your Gmail account
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("your_email_address@gmail.com", "your_email_password")
    # Compose the email message
    message = "Subject: Verification Code\n\nYour verification code is: " + str(code)
    # Send the email
    server.sendmail("your_email_address@gmail.com", "recipient_email_address@gmail.com", message)
    # Close the SMTP connection
    server.quit()
    return code


def sort_movies(Class):
    movie_classes = {'trending': Trending, 'discover': Discover, 'movie': Recommendation}
    user_id = 1
    if current_user.is_authenticated:
        user_id = current_user.id
    if Class == "movie":
        all_movies = movie_classes[Class].query.filter_by(user_id=user_id).order_by(
            movie_classes[Class].rating.desc()).all()
    else:
        all_movies = movie_classes[Class].query.order_by(movie_classes[Class].rating.desc()).all()

    for i, movie in enumerate(all_movies):
        movie.ranking = i + 1

    db.session.commit()
    return all_movies


def filter_data(json_list, **kwargs):
    return [
        {
            'name': json_input.get('name', json_input.get('title', None)),
            'year': json_input.get('first_air_date', json_input.get('release_date', None)),
            'overview': json_input.get('overview', None),
            'poster_path': json_input.get('poster_path', None),
            'vote_average': json_input.get('vote_average', None),
            'media_type': json_input.get('media_type', kwargs['to_discover']),
            'media_id': json_input.get('id', None),
        }
        for json_input in json_list
    ]


def search(query, query_type, page, **kwargs):
    lang = session.get('lang', 'ar')
    api_key = '99944e74de511cfa307148e77ddb77d4'
    base_urls = {
        'discover': f'https://api.themoviedb.org/3/discover/{kwargs["to_discover"]}?api_key={api_key}&language={lang}&sort_by=popularity'
                    f'.desc&include_adult=false&include_video=false&page={page}',
        'trending': f'https://api.themoviedb.org/3/trending/all/day?api_key={api_key}&page={page}&language={lang}&include_adult=false',
        'search': 'https://api.themoviedb.org/3/search/multi',
    }
    if query_type in ('discover', 'trending'):
        response = requests.get(url=base_urls[query_type])
    else:
        parameters = {
            'api_key': api_key,
            'query': query,
            'page': 1,
            'include_adult': 'false',
            'language': lang
        }
        response = requests.get(url=base_urls['search'], params=parameters)
    data = response.json()['results']
    filtered_data = []
    for json_input in data:
        filtered_dict = {
            'name': json_input.get('name', json_input.get('title', None)),
            'year': json_input.get('first_air_date', json_input.get('release_date', None)),
            'overview': json_input.get('overview', None),
            'poster_path': json_input.get('poster_path', None),
            'vote_average': json_input.get('vote_average', None),
            'media_type': json_input.get('media_type', kwargs['to_discover']),
            'media_id': json_input.get('id', None),
        }
        filtered_data.append(filtered_dict)
    return filtered_data


def update_database(database_name, page, **kwargs):
    database = {'movie': Recommendation, 'discover': Discover, 'trending': Trending, }
    db.session.query(database[database_name]).delete()
    db.session.commit()
    discover_data = search('database_name', database_name, page, to_discover=kwargs['to_discover'])
    for item in discover_data:
        try:
            media_id = item['media_id']
            movie_title = item['name']
            movie_year = item['year']
            movie_rating = round(item['vote_average'], 1)
            movie_description = item['overview']
            media_type = item['media_type']
            movie_img_url = "".join(["https://www.themoviedb.org/t/p/w220_and_h330_face/", item['poster_path']])
            site_url = f'https://www.themoviedb.org/{media_type}/{media_id}-{movie_title}'

            execute(media_id, media_type, database_name, movie_title,
                    movie_year.split('-')[0],
                    movie_description,
                    movie_rating, 10, 'topp',
                    movie_img_url, site_url)
        except:
            pass


discover_global_var = 1
trending_global_var = 1


@app.route("/")
def home():
    movies = sort_movies('movie')
    pfp_update()

    return render_template("index.html", movies=movies)


def generate_avatar(name, size):
    url = "https://ui-avatars.com/api/"
    params = {
        "background": "#{:06x}".format(random.randint(0, 0xFFFFFF)),
        "color": "fff",
        "rounded": True,
        "size": size,
        "name": name
    }
    response = requests.get(url, params=params)

    # Check if the response was successful
    if response.status_code == 200:
        # Save the image to the static folder of the Flask app
        image_file = f"{name}_avatar.png"
        image_path = os.path.join(app.static_folder, 'profile_pics', image_file)
        with open(image_path, "wb") as f:
            f.write(response.content)
        return image_file
    else:
        print("Error getting image.")
        return None


def pfp_update():
    if current_user.is_authenticated:
        session["pic"] = url_for('static', filename=f'/profile_pics/{current_user.username}_avatar.png')
        print(session["pic"])
    else:
        session['pic'] = 'https://telegra.ph/file/5f61b3e51d033ecbbe32a.png'


@app.route('/profile')
@login_required
def view_profile():
    # user = User.get_by_username(current_user.username)
    user = current_user.username

    if not user:
        flash('User not found')
        return redirect(url_for('index'))
    return render_template('profile.html')


@app.route('/<language>')
def change_language(language):
    previous_url = request.referrer
    if language == 'en':
        session['lang'] = 'en'

    elif language == 'ar':
        session['lang'] = 'ar'
    else:
        return redirect(url_for('home'))

    return redirect(previous_url)


@app.route('/login', methods=['GET', 'POST'])
@logged_in
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data.replace(" ", "")).first()
            if user:
                if check_password_hash(user.password, form.password.data):
                    login_user(user)
                    pfp_update()
                    return redirect(url_for('home'))
                else:
                    flash('Error: Invalid username or password.')
                    return render_template('login.html', form=form)
            else:
                flash('Error: Invalid username or password.')
                return render_template('login.html', form=form)
        else:
            flash('Error: All fields are required.')
            return render_template('login.html', form=form)

    return render_template("login.html", form=form)


# user = User(email='user@user.com', password=generate_password_hash('123'), username='user', role='user')
# db.session.add(user)
# db.session.commit()


@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
        return redirect(url_for('home'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
@logged_in
def register():
    if request.method == 'POST':
        form = RegisterForm(request.form)
        if form.validate_on_submit():
            if User.query.filter_by(email=form.email.data).first():
                flash('Email address already registered.')
                return redirect(url_for('register'))
            username = form.username.data.replace(" ", "")
            email = form.email.data.replace(" ", "")
            password = generate_password_hash(form.password.data)
            user = User(username=username, email=email, password=password, role="admin")

            db.session.add(user)
            db.session.commit()
            login_user(user)
            generate_avatar(current_user.username, 200)

            return redirect(url_for('home'))
        else:
            return render_template('register.html', form=form)
    form = RegisterForm()
    return render_template("register.html", form=form)


@app.route("/rest/<site>/<discover_type>")
def rest(site, discover_type):
    global discover_global_var
    global trending_global_var
    if site == 'disc' and discover_type == "movie":
        discover_global_var = 1
        return redirect(url_for('discover', page=1, discover_type=discover_type))
    elif site == 'disc' and discover_type == "tv":
        trending_global_var = 1
        return redirect(url_for('discover', page=1, discover_type=discover_type))
    else:
        trending_global_var = 1
        return redirect(url_for('trending', page=1))


@app.route("/discover/<discover_type>/<int:page>")
def discover(page, discover_type):
    global discover_global_var
    discover_global_var += 1

    # if search_type == "discover":
    update_database('discover', to_discover=discover_type, page=page)
    movies = sort_movies('discover')
    return render_template("discover.html", movies=movies, page_number=discover_global_var, discover_type=discover_type)


@app.route("/trending/<int:page>")
def trending(page):
    global trending_global_var
    trending_global_var += 1
    # if search_type == "discover":
    update_database('trending', page=page, to_discover='none')
    movies = sort_movies('trending')
    return render_template("trending.html", movies=movies, page_number=trending_global_var)


@app.route("/edit", methods=['GET', 'POST'])
@login_required
def edit():
    form = Movieform()
    if request.method == 'POST' and form.validate():
        # UPDATE RECORD
        movie_id = request.args.get('id')
        movie_to_update = Recommendation.query.get(movie_id)
        # movie_to_update.rating = form.new_rating.data
        movie_to_update.rating = form.new_rating.data
        db.session.commit()
        return redirect(url_for('home'))
    movie_id = request.args.get('id')
    movie_selected = Recommendation.query.get(movie_id)
    return render_template("edit.html", movie=movie_selected, form=form)


@app.route('/delete', methods=['GET', 'POST'])
@login_required
def delete():
    if request.method == "POST":
        # UPDATE RECORD
        movie_id = request.args.get('id')
        movie_to_delete = Recommendation.query.get(movie_id)
        db.session.delete(movie_to_delete)
        db.session.commit()
        return redirect(url_for('home'))
    movie_id = request.args.get('id')
    movie_selected = Recommendation.query.get(movie_id)
    return render_template("delete.html", movie=movie_selected)


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = Addform()
    if request.method == 'POST' and form.validate():
        data = search(form.movie_title.data, 'multi', 1, to_discover='none')
        temp_data = []
        # Loop through the list of dictionaries in reverse order
        for movie in data:
            if movie['media_type'] == 'person':
                movie = "person"
            else:
                try:
                    movie['poster_path'] = "".join(
                        ["https://www.themoviedb.org/t/p/w220_and_h330_face", movie['poster_path']])
                    movie.update({'site_url': f"https://www.themoviedb.org/{movie['media_type']}"
                                              f"/{movie['media_id']}-{movie['name']}"})
                    movie['vote_average'] = f"{round(movie['vote_average'], 1)}"
                except:
                    movie = "person"
            if movie != "person":
                temp_data.append(movie)

        return render_template('select.html', data=temp_data)

    return render_template("add.html", form=form)


@app.route('/select', methods=['GET', 'POST'])
@login_required
def select():
    movie_title = request.args.get('title')
    movie_year = request.args.get('year')
    movie_rating = request.args.get('rating')
    movie_description = request.args.get('description')
    movie_img_url = "".join(["https://www.themoviedb.org/t/p/w220_and_h330_face/", request.args.get('img_url')])
    media_type = request.args.get("media_type")
    media_id = request.args.get("movie_id")
    rec = Recommendation(user_id=current_user.id, media_id=media_id, media_type=media_type, title=movie_title,
                         year=movie_year,
                         description=movie_description, rating=movie_rating, ranking=10, img_url=movie_img_url,
                         site_url="site_url", review="review")
    db.session.add(rec)
    db.session.commit()
    movie_selected = Recommendation.query.filter_by(user_id=current_user.id, title=movie_title).first()
    # movie_selected = Recommendation.query.filter_by(title=movie_title).first()
    movie_id = movie_selected.id
    return redirect(url_for('edit', id=movie_id))


@app.route('/cancel')
@login_required
def cancel():
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run()
