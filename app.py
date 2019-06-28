from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def healthcheck():
    return 'ok'

@app.route('/movies')
def movies():
    return 'list of movies'

@app.route('/movies/<movie_name>')
def movie(movie_name):
    return render_template('movie.html', movie_name=movie_name)