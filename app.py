import os
from flask import Flask, render_template
from psycopg2 import connect
from config import app_config
import json
import decimal

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
def add_movie(params):
    pass