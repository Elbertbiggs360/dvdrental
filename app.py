import os
import hmac
from flask import Flask, render_template, abort, flash, redirect, url_for, session
from flask_session import Session
from psycopg2 import connect
from config import app_config
import json
import decimal
import datetime
from utils import Ratings
from forms import MovieForm, SearchForm
from hashlib import sha256
from datetime import datetime, timedelta

app = Flask(__name__)

TIME_FORMAT = '%Y%m%d%H%M%S'

app_config_file = app_config[os.getenv('APP_SETTINGS') or 'development']
app.config.from_object(app_config_file)
app.config.from_pyfile('config.py')
Session(app)

conn = connect(
    database=app_config_file.DB_NAME,
    host=app_config_file.DB_HOST,
    user=app_config_file.DB_USER,
    password=app_config_file.DB_PASSWORD)
cur = conn.cursor()


def generate_csrf_token():
    session['csrf'] = session.get('csrf', sha256(os.urandom(64)).hexdigest())
    time_limit = timedelta(minutes=app_config_file.TOKEN_TIMEOUT)
    expires = (datetime.now() + time_limit).strftime(TIME_FORMAT)
    
    csrf_build = f'{session["csrf"]}{expires}'
    hmac_csrf = hmac.new(
        app_config_file.SECRET_KEY.encode('utf-8'),
        csrf_build.encode('utf8'),
        digestmod=sha256
    )
    
    return f'{expires}##{hmac_csrf.hexdigest()}'

def verify_csrf_token(csrf_token):
    if not csrf_token or '##' not in csrf_token:
        return False
    expires, hmac_csrf = csrf_token.split('##', 1)
    
    check_val = (session['csrf'] + expires).encode('utf8')
    hmac_compare = hmac.new(app_config_file.SECRET_KEY.encode('utf-8'), check_val, digestmod=sha256)
    if hmac_compare.hexdigest() != hmac_csrf:
        raise ValueError('CSRF failed')
    
    now_formatted = datetime.now().strftime(TIME_FORMAT)
    if now_formatted > expires:
        raise 'Token Expired'
    return True


@app.route('/')
def index():
    return render_template('index.html', title='Home')

@app.route('/ping')
def healthcheck():
    return 'ok'

@app.route('/movies')
def movies():
    try:
        cur.execute('SELECT title FROM film')
    except Exception as e:
        print('Failing: ', e)
    items = cur.fetchall()
    return render_template('movies.html', movies=items, total=len(items))

@app.route('/movies/<movie_name>')
def movie(movie_name):
    return render_template('movie.html', movie_name=movie_name)

@app.route('/actors/condition2')
def actors_filtered():
    '''
    Find the names (first and last) of all the actors and customers whose
    first name is the same as the first name of the actor with ID 8.
    Do not return the actor with ID 8 himself.
    Note that you cannot use the name of the actor with ID 8 as a constant
    (only the ID)
    '''
    cur.execute("""
                    SELECT
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
    result_list = []
    for row in res:
        result_list.append(row[:2])
        result_list.append(row[2:])
    actor_8 = result_list.pop(0) # remove the actor with id 8 who is the first match
    results = list(set(result_list))
    return render_template('actors.html', title='Actors', actors=results)

@app.route('/categories/condition3')
def categories_filtered():
    '''b
    Find all the film categories in which there are between 55 and 65 films.
    Return the names of these categories and the number of films per category, sorted by the number of films.
    '''
    cur.execute("""
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
    return render_template('categories.html', title='Categories', categories=res)

@app.route('/movies/search', methods=['GET', 'POST'])
def search_films():
    form = SearchForm()
    if not verify_csrf_token(form.data['manual_csrf_token']):
        token = generate_csrf_token()
        form.manual_csrf_token.data = token
        return render_template('search.html', title='Search for films', form=form)
    
    search_terms = form.data['term'].split(' ')
    search_string = ' & '.join(search_terms)
    cur.execute("SELECT * FROM film where fulltext @@ to_tsquery(%s)", (search_string, ))
    res = cur.fetchall()
    return render_template('search_results.html', title='Home', res=len(res))

@app.route('/movies/add', methods=['GET', 'POST'])
def add_movie():
    form = MovieForm()
    if not verify_csrf_token(form.data['manual_csrf_token']):
        token = generate_csrf_token()
        form.manual_csrf_token.data = token
        return render_template('new_movie.html', title='Add New Movie', form=form)
    lang_id = add_language(form.data['language'])
    movie = {
            'title': '',
            'description': '',
            'release_year': 0,
            'rental_duration': 0,
            'rental_rate': 0.00,
            'length': 0,
            'replacement_cost': 0.00
        }
    for k, v in movie.items():
        movie[k] = form.data[k]
    movie['language_id'] = movie.get('language_id', lang_id)
    cur.execute(
        """
        INSERT INTO film (title, description, release_year, language_id, rental_duration, rental_rate, length, replacement_cost)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, [(v, ) for k, v in movie.items()]
    )
    try:
        cur.execute("SELECT * FROM film where fulltext @@ to_tsquery(%s)", (movie['title'], ))
        res = cur.fetchall()
        conn.commit()
        return redirect(url_for('movies'))
    except Exception as e:
        return redirect(url_for('index'))

def add_language(lang):
    try:
        cur.execute("INSERT INTO language (name) VALUES (%s)", (lang, ))
    except Exception as e:
        pass
    cur.execute("SELECT language_id FROM language where name=%s", (lang, ))
    lang_id = cur.fetchone()[0]
    if conn.commit():
        return lang_id
    return lang_id
