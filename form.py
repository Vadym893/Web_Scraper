from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired,Length
class Id_Form(FlaskForm):
    id =StringField("Id Search",validators=[DataRequired(),Length(min=7,max=10)])
    submit=SubmitField("Search")
class Chart_check(FlaskForm):
    chart_check=SubmitField('Display Chart')
class Graph_exit(FlaskForm):
    exit=SubmitField('Back')