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
    host=app_config_file.DB_HOST,
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

@app.route('/condition2')
def condition2():
    '''
    Find the names (first and last) of all the actors and customers whose
    first name is the same as the first name of the actor with ID 8.
    Do not return the actor with ID 8 himself.
    Note that you cannot use the name of the actor with ID 8 as a constant
    (only the ID)
    '''
    cur.execute(f"""
                    SELECT
                        a.actor_id,
                        a.first_name a_first_name,
                        a.last_name a_last_name,
                        c.first_name c_first_name,
                        c.last_name c_last_name
                    FROM
                        actor a
                    INNER JOIN
                        customer c ON a.first_name = c.first_name
                    WHERE a.first_name IN (
                        SELECT a.first_name from actor a WHERE actor_id = 8
                    )
                """
    )
    res = cur.fetchall()
    res
    return json.dumps(res)

@app.route('/condition3')
def condition3():
    '''b
    Find all the film categories in which there are between 55 and 65 films.
    Return the names of these categories and the number of films per category, sorted by the number of films.
    '''
    cur.execute(f"""
                    select c.name, COUNT(fc.film_id) as num_film
                    from category c
                    join film_category fc
                    ON c.category_id = fc.category_id
                    GROUP BY c.name
                    HAVING COUNT(fc.film_id) BETWEEN 55 AND 65
                    ORDER BY COUNT(fc.film_id) DESC
                """
    )
    res = cur.fetchall()
    data = json.dumps(res)
    return data

@app.route('/movies/search')
def filterMovies():
    cur.execute(f"SELECT * FROM film where fulltext @@ to_tsquery('Shark & Crocodile')")
    res = cur.fetchall()
    return f'Movies involving shark and croc: {len(res)}'

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

def add_language(lang):
    cur.execute(f"INSERT INTO language (name) VALUES ('{lang}')")
    cur.execute(f"SELECT language_id FROM language where name='{lang}'")
    lang_id = cur.fetchone()[0]
    if conn.commit():
        return lang_id
    return lang_id
