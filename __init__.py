from flask import ( 
    Flask, redirect, url_for, render_template, request, flash)

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from datetime import timedelta

import os

db = SQLAlchemy()
DB_NAME = 'poe3.db'

def create_app():
    # App
    app = Flask(__name__)
    app.secret_key = 'dev'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///db/{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    # Cookies
    app.permanent_session_lifetime = timedelta(minutes=20)

    from . import auth
    app.register_blueprint(auth.auth)
    
    from . import post
    app.register_blueprint(post.post)

    from .model import User, Post

    create_database(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

def create_database(app):
    if not os.path.exists('poe3/db/' + DB_NAME):
        os.mkdir('poe3/db')
        db.create_all(app=app)
        print(' * Database created!')