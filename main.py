from functools import wraps
import requests
from flask import Flask, render_template, redirect, url_for, request, flash,session
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import false
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import check_password_hash

from forms import LoginForm, Addform, Movieform

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


class Recommendation(db.Model, Base):
    __tablename__ = "my_recommendations"
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


class Requests(db.Model, Base):
    __tablename__ = "Requests"
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


def addminonly(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            is_admin = current_user.id == 1
            if not is_admin:
                flash("You are not authorized to access this page")
                return redirect(url_for('login'))
            return func(*args, **kwargs)
        flash("You are not authorized to access this page")
        return redirect(url_for('login'))

    return decorated_function


def logged_in(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        return func(*args, **kwargs)

    return decorated_function


def execute(media_id, media_type, search_type, title, year, description, rating, ranking, review, img_url, site_url):
    movie_classes = {'trending': Trending, 'discover': Discover, 'movie': Recommendation}
    rounded_rating = round(float(rating), 1)
    MovieClass = movie_classes[search_type]
    new_media = MovieClass(media_id=media_id, media_type=media_type, title=title, year=year, description=description,
                           rating=rounded_rating, ranking=ranking,
                           review=review, img_url=img_url, site_url=site_url)
    try:
        db.session.add(new_media)
        db.session.commit()
    except:
        print("failed creating record")


# execute("drive", 2011, "A mysterious Hollywood stuntman and mechanic moonlights as a getaway driver and finds"
#                        "himself in trouble when he helps out his neighbor in this action drama.", 7, 8, "insane",
#         "https://www.shortlist.com/media/images/2019/05/the-30-coolest-alternative-movie-posters-ever-2"
#         "-1556670563-K61a-column-width-inline.jpg")
#


def sort_movies(Class):
    movie_classes = {'trending': Trending, 'discover': Discover, 'movie': Recommendation}

    all_movies = movie_classes[Class].query.order_by(movie_classes[Class].rating.desc()).all()

    # This line loops through all the movies
    for i in range(len(all_movies)):
        # This line gives each movie a new ranking reversed from their order in all_movies
        all_movies[i].ranking = i + 1
    db.session.commit()
    return all_movies


def filter_data(json_list, **kwargs):
    filtered_list = []
    for json_input in json_list:
        filtered_dict = {
            'name': json_input.get('name', json_input.get('title', None)),
            'year': json_input.get('first_air_date', json_input.get('release_date', None)),
            'overview': json_input.get('overview', None),
            'poster_path': json_input.get('poster_path', None),
            'vote_average': json_input.get('vote_average', None),
            'media_type': json_input.get('media_type', kwargs['to_discover']),
            'media_id': json_input.get('id', None),

        }
        filtered_list.append(filtered_dict)

    return filtered_list


def search(query, query_type, page, **kwargs):
    lang = session.get('lang', 'not_set')
    api_key = '99944e74de511cfa307148e77ddb77d4'
    base_urls = {
        'discover': f'https://api.themoviedb.org/3/discover/{kwargs["to_discover"]}?api_key={api_key}&language={lang}&sort_by=popularity'
                    f'.desc&include_adult=false&include_video=false&page={page}',
        'trending': f'https://api.themoviedb.org/3/trending/all/day?api_key={api_key}&page={page}&language={lang}',
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
    return filter_data(data, to_discover=kwargs['to_discover'])


def update_database(database_name, page, **kwargs):
    database = {'movie': Recommendation, 'discover': Discover, 'trending': Trending, }
    db.session.query(database[database_name]).delete()
    db.session.commit()
    discover_data = search('database_name', database_name, page, to_discover=kwargs['to_discover'])
    for item in discover_data:
        media_id = item['media_id']
        movie_title = item['name']
        movie_year = item['year']
        movie_rating = round(item['vote_average'], 1)
        movie_description = item['overview']
        media_type = item['media_type']
        try:
            movie_img_url = "".join(["https://www.themoviedb.org/t/p/w220_and_h330_face/", item['poster_path']])
        except:
            movie_img_url = 'https://telegra.ph/file/ef7a1fe2c26acfdfc8832.jpg'
        site_url = f'https://www.themoviedb.org/{media_type}/{media_id}-{movie_title}'
        execute(media_id, media_type, database_name, movie_title,
                movie_year.split('-')[0],
                movie_description,
                movie_rating, 10, 'topp',
                movie_img_url, site_url)


discover_global_var = 1
trending_global_var = 1


@app.route("/")
def home():
    admin = False
    if current_user.is_authenticated:
        admin = True
    movies = sort_movies('movie')
    return render_template("index.html", movies=movies, admin=admin)


@app.route('/<language>')
def change_language(language):
    previous_url = request.referrer
    if language == 'en':
        session['lang'] = 'en'

    elif language == 'ar':
        session['lang'] = 'ar'
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
        # user = User()
        # user.username = "trap"
        # user.email = form.email.data.replace(" ", "")
        # user.password = generate_password_hash(form.password.data)
        # db.session.add(user)
        # db.session.commit()
    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
        return redirect(url_for('home'))
    return redirect(url_for('login'))


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
@addminonly
def edit():
    form = Movieform()
    if request.method == 'POST' and form.validate():
        # UPDATE RECORD
        movie_id = request.args.get('id')
        movie_to_update = Recommendation.query.get(movie_id)
        # movie_to_update.rating = form.new_rating.data
        movie_to_update.review = form.new_review.data
        movie_to_update.rating = form.new_rating.data
        db.session.commit()
        return redirect(url_for('home'))
    movie_id = request.args.get('id')
    movie_selected = Recommendation.query.get(movie_id)
    return render_template("edit.html", movie=movie_selected, form=form)


@app.route('/delete', methods=['GET', 'POST'])
@addminonly
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
@addminonly
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
@addminonly
def select():
    movie_title = request.args.get('title')
    movie_year = request.args.get('year')
    movie_rating = request.args.get('rating')
    movie_description = request.args.get('description')
    movie_img_url = "".join(["https://www.themoviedb.org/t/p/w220_and_h330_face/", request.args.get('img_url')])
    media_type = request.args.get("media_type")
    media_id = request.args.get("movie_id")
    execute(media_id, media_type, 'movie', movie_title, movie_year.split('-')[0],
            movie_description, movie_rating, 10,
            'topp', movie_img_url
            ,
            site_url=f'https://www.themoviedb.org/{media_type}/{media_id}-{movie_title}')

    movie_selected = Recommendation.query.filter_by(title=movie_title).first()
    movie_id = movie_selected.id
    return redirect(url_for('edit', id=movie_id))


#
# @app.route("/request/<site>", methods=['GET', 'POST'])
# def request(site):
#     database_alias = {'discover': Discover, 'trending': Trending, }
#     database = database_alias[site]
#     form = Movieform()
#     if request.method == "POST":
#         # UPDATE RECORD
#         media_id = request.args.get('media_id')
#         movie_to_update = database.query.get(media_id)
#         # movie_to_update.rating = form.new_rating.data
#         execute()
#         movie_to_update.review = form.new_review.data
#         movie_to_update.rating = form.new_rating.data
#         db.session.commit()
#         return redirect(url_for('home'))
#     movie_id = request.args.get('id')
#     movie_selected = Recommendation.query.get(movie_id)
#     return render_template("edit.html", movie=movie_selected, form=form)

@app.route('/cancel')
@addminonly
def cancel():
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
