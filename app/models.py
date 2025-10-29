from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db, login

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

class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=True, nullable=False, index=True)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    current_revision_id = db.Column(db.Integer, db.ForeignKey("page_revision.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    current_revision = db.relationship("PageRevision", foreign_keys=[current_revision_id], post_update=True)

    revisions = db.relationship("PageRevision", back_populates="page", order_by="desc(PageRevision.created_at)")

class PageRevision(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.Integer, db.ForeignKey("page.id"))
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    comment = db.Column(db.String(255), nullable=True)

    page = db.relationship("Page", back_populates="revisions")
    author = db.relationship("User")

    def to_html(self):
        import markdown2
        return markdown2.markdown(self.content or "")
    