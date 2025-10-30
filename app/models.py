from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db, login
from flask_sqlalchemy import SQLAlchemy

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


db = SQLAlchemy()

class Page(db.Model):
    __tablename__ = 'page'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Явно указываем внешний ключ для relationship
    revisions = db.relationship(
        'PageRevision',
        backref='page',
        foreign_keys='PageRevision.page_id',  # <- ключ, который соединяет Page и PageRevision
        lazy='dynamic'
    )

class PageRevision(db.Model):
    __tablename__ = 'page_revision'
    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.Integer, db.ForeignKey('page.id'))
    
    # Если есть другой внешний ключ на Page, например parent_id,
    # его отдельно использовать в другом relationship, если нужно
    parent_id = db.Column(db.Integer, db.ForeignKey('page.id'))