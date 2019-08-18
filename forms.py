from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, FloatField
from wtforms.validators import DataRequired

class MovieForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    description = StringField('description')
    release_year = IntegerField('Release Year')
    language = StringField('Language', validators=[DataRequired()])
    rental_duration = IntegerField('Rental Duration', validators=[DataRequired()])
    rental_rate = FloatField('Rental Rate', validators=[DataRequired()])
    length = IntegerField('Length')
    replacement_cost = FloatField('Replacement Cost')
    submit = SubmitField('Add movie')