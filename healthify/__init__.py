from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
# setting up the app variable and assigning a instance of flask class to it
# __name__ is a special instance variable in python that is just the name of the module
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


from healthify import routes

app.config['SECRET_KEY']='cc7c57b2c96ec3ccdb44f54d830a4829'

