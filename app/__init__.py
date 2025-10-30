import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login.init_app(app)
    login.login_view = "auth_login"  # назначаем страницу логина

    # создаём папку uploads, если её нет
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    from .views import bp as main_bp
    app.register_blueprint(main_bp)

    return app
