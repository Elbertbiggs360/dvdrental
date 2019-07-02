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
    lang_id = add_language('English')
    movies = [
        {
            'title': 'Dark Knight',
            'description': 'Lorem ipsum',
            'release_year': 2012,
            'language_id': lang_id,
            'rental_duration': 12,
            'rental_rate': 2.99,
            'length': 86,
            'replacement_cost': 12.99
        },
                {
            'title': 'Dark Knight 2',
            'description': 'Lorem ipsum',
            'release_year': 2012,
            'language_id': lang_id,
            'rental_duration': 12,
            'rental_rate': 2.99,
            'length': 86,
            'replacement_cost': 12.99
        },
        {
            'title': 'Dark Knight 3',
            'description': 'Lorem ipsum',
            'release_year': 2012,
            'language_id': lang_id,
            'rental_duration': 12,
            'rental_rate': 2.99,
            'length': 86,
            'replacement_cost': 12.99
        },
    ]
    for movie in movies:
        cur.execute(
            """
            INSERT INTO film (title, description, release_year, language_id, rental_duration, rental_rate, length, replacement_cost)
            VALUES ('{}', '{}', {}, {}, {}, {}, {}, {})
            """.format(*[v for k, v in movie.items()])
        )
    try:
        conn.commit()
        return json.dumps(movies)
    except Exception as e:
        return 'Error: {}.'.format(e)

def create_ratings(list):
    cur.execute(f"CREATE TYPE mpaa_ratings as ENUM ('PG', 'G', 'NC-17', 'PG-13')")
    if conn.commit():
        return True
    return False

def add_language(lang):
    cur.execute(f"INSERT INTO language (name) VALUES ('{lang}')") # add ON CONFLICT (name) DO NOTHING for unique columns
    cur.execute(f"SELECT language_id FROM language where name='{lang}'")
    lang_id = cur.fetchone()[0]
    if conn.commit():
        return lang_id
    return lang_id
