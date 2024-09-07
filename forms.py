from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class AnimeForm(FlaskForm):
    name = StringField('Anime Name', validators=[DataRequired(), Length(min=1, max=150)])
    description = TextAreaField('Description', validators=[DataRequired()])
    cover_image = StringField('Cover Image URL', validators=[DataRequired()])
    submit = SubmitField('Add/Update Anime')

class EpisodeForm(FlaskForm):
    number = StringField('Episode Number', validators=[DataRequired()])
    sources = TextAreaField('Sources (comma separated URLs)', validators=[DataRequired()])
    submit = SubmitField('Add Episode')


class AnimeForm(FlaskForm):
    name = StringField('Anime Name', validators=[DataRequired(), Length(min=1, max=150)])
    description = TextAreaField('Description', validators=[DataRequired()])
    cover_image = StringField('Cover Image URL', validators=[DataRequired()])
    genres = StringField('Genres (comma separated)', validators=[DataRequired()])  # Yeni alan
    submit = SubmitField('Add/Update Anime')
