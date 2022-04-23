from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from users import users_blueprint
from models import connect_db
from flask_jwt_extended import JWTManager, create_access_token
import os
from datetime import timedelta

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://@localhost:5433/cocktails_two')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'shh')
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
jwt = JWTManager(app)
debug = DebugToolbarExtension(app)

connect_db(app)

app.register_blueprint(users_blueprint, url_prefix="/users")

@app.route('/')
def index():
    return "in app.py"
