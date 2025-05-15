# Dash app initialization
from dash import Dash
import dash_bootstrap_components as dbc
# User management initialization
from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy
import secrets

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server
app.config.suppress_callback_exceptions = True
server.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://boshlike:Telegraph1265!@localhost:5432/pairs_dash'
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

server.config.update(
    SECRET_KEY=secrets.token_hex(),
    SQLALCHEMY_ECHO=True
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