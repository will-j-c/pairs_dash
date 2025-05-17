# Dash app initialization
from dash import Dash
import dash_bootstrap_components as dbc
# User management initialization
from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy
import secrets
from dotenv import load_dotenv
import os

load_dotenv(override=True)
user = os.getenv('USER')
password = os.getenv('PASSWORD')
host = os.getenv('PG_HOST')
port = os.getenv('PG_PORT')
db = os.getenv('DB')

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server
app.config.suppress_callback_exceptions = True

server.config.update(
    SECRET_KEY = secrets.token_hex(),
    SQLALCHEMY_ECHO = False,
    SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}',
    SQLALCHEMY_TRACK_MODIFICATIONS = False
)

db = SQLAlchemy()
db.init_app(server)

# Setup the LoginManager for the server
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'


# Create User class with UserMixin
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)

with server.app_context():
    db.create_all()

# callback to reload the user object
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))