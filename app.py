import os
from flask import Flask, render_template, abort
from psycopg2 import connect
from config import app_config
import json
import decimal
import datetime
from utils import Ratings

app = Flask(__name__)
app_config_file = app_config[os.getenv('APP_SETTINGS') or 'development']
app.config.from_object(app_config_file)
app.config.from_pyfile('config.py')

conn = connect(
    database=app_config_file.DB_NAME,
    user=app_config_file.DB_USER,
    password=app_config_file.DB_PASSWORD)
cur = conn.cursor()

@app.route('/')
def healthcheck():
    return 'ok'

@app.route('/movies')
def movies():
    cur.execute('SELECT title FROM film')
    items = cur.fetchall()
    return render_template('movies.html', movies=items, total=len(items))

@app.route('/movies/<movie_name>')
def movie(movie_name):
    return render_template('movie.html', movie_name=movie_name)

@app.route('/categories')
def categories():
    pass

@app.route('/condition3')
def condition3():
    pass

@app.route('/movies/search')
def filterMovies():
    pass

@app.route('/movies/add')
def add_movie():
    movie = {
        'title': 'Dark Knight',
        'description': 'Lorem ipsum',
        'release_year': 2012,
        'language_id': 1,
        'rental_duration': 12,
        'rental_rate': 2.99,
        'length': 86,
        'replacement_cost': 12.99,
        'rating': 'PG',
        'last_update': datetime.datetime.now(),
        'special_features': 'test'
    }
    movie['fulltext'] = ', '.join(movie['title'])
    cur.execute(
        '''
        INSERT INTO film (title, description, release_year, language_id, rental_duration, rental_rate, length, replacement_cost, rating, special_features)
        VALUES ('{}', '{}', {}, {}, {}, {}, {}, {}, {}, '{}')
        '''.format(*['a', 'b', 3, 1, 12, 6.99, 7, 8.99, Ratings.PG, 'test'])
    )
    try:
        conn.commit()
        return json.dumps(movie)
    except Exception as e:
        return 'Error: {}.'.format(e)
