from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import os
from dotenv import load_dotenv
load_dotenv()


MOVIE_DB_API_KEY = os.environ.get('MOVIE_DB_API_KEY')
MOVIE_DB_SERACH_URL = os.environ.get('MOVIE_DB_SERACH_URL')
MOVIE_DB_INFO_URL = os.environ.get('MOVIE_DB_INFO_URL')
MOVIE_DB_IMAGE_URL = os.environ.get('MOVIE_DB_IMAGE_URL')

'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)


#Create DB
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///movies.db'
db = SQLAlchemy(app)

#Create Table
class Movie(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(100),nullable=False,unique=True)
    year = db.Column(db.Integer,nullable=False)
    description = db.Column(db.String(500),nullable=False)
    rating = db.Column(db.Float,nullable=True)
    ranking = db.Column(db.Integer,nullable=True)
    review = db.Column(db.String(200),nullable=True)
    img_url = db.Column(db.String(200),nullable=False)

# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )

# second_movie = Movie(
#     title="Avatar The Way of Water",
#     year=2022,
#     description="Set more than a decade after the events of the first film, learn the story of the Sully family (Jake, Neytiri, and their kids), the trouble that follows them, the lengths they go to keep each other safe, the battles they fight to stay alive, and the tragedies they endure.",
#     rating=7.3,
#     ranking=9,
#     review="I liked the water.",
#     img_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg"
# )

# with app.app_context():
#     #Create table if it doesn't exist already
#     db.session.add(new_movie)
#     db.session.add(second_movie)
#     db.session.commit()
    # db.create_all()

class RateMovieForm(FlaskForm):
    rating = StringField('You rating out of 10 e.g. 7.5')
    review = StringField('Your Review')
    submit = SubmitField('Done')


class AddMovieForm(FlaskForm):
    title=StringField("Movie Title",validators=[DataRequired()])
    submit=SubmitField('Add Movie')


@app.route('/add',methods=["GET","POST"])
def add_movie():
    print("Adding new movie")
    form=AddMovieForm()
    if form.validate_on_submit():
        movie_title=form.title.data
        response=requests.get(MOVIE_DB_SERACH_URL,params={"api_key":MOVIE_DB_API_KEY,"query":movie_title})
        data=response.json()['results']
        return render_template('select.html',options=data)
    return render_template('add.html',form=form)

@app.route('/find')
def find_movie():
    movie_id=request.args.get('id')
    if movie_id:
        movie_api_url=f"{MOVIE_DB_INFO_URL}/{movie_id}"
        response=requests.get(movie_api_url,params={'api_key':MOVIE_DB_API_KEY})
        data=response.json()
        new_movie=Movie(
            title=data['title'],
            year=data['release_date'].split('-')[0],
            img_url=f"{MOVIE_DB_IMAGE_URL}{data['poster_path']}",
            description=data['overview']
        )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('rate_movie', id=new_movie.id))



@app.route("/")
def home():
    movies = Movie.query.order_by(Movie.rating.desc()).all()
    for i in range(len(movies)):
        movies[i].ranking = i+1
    db.session.commit()
    return render_template("index.html",movies=movies)

@app.route('/edit',methods=["GET","POST"])
def rate_movie():
    form=RateMovieForm()
    movie_id=request.args.get("id")
    movie=Movie.query.filter_by(id=movie_id).first()
    if form.validate_on_submit():
        movie.rating=float(form.rating.data)
        movie.review=form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html',movie=movie,form=form)

@app.route('/delete')
def delete_movie():
    movie_id=int(request.args.get("id"))
    movie=Movie.query.filter_by(id=movie_id).one()
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
