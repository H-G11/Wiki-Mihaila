import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from . import db
from .models import User, Page, PageRevision
from .forms import LoginForm, RegisterForm, PageForm, UploadForm, SearchForm
from .utils import slugify
from sqlalchemy import or_, func

bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    pages = Page.query.order_by(Page.created_at.desc()).limit(20).all()
    return render_template("index.html", pages=pages)

# Auth
@bp.route("/login", methods=["GET", "POST"])
def auth_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Вход выполнен", "success")
            return redirect(url_for("main.index"))
        flash("Неверные данные", "danger")
    return render_template("login.html", form=form)

@bp.route("/logout")
def auth_logout():
    logout_user()
    flash("Вы вышли", "info")
    return redirect(url_for("main.index"))

@bp.route("/register", methods=["GET", "POST"])
def auth_register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Пользователь создан", "success")
        return redirect(url_for("main.auth_login"))
    return render_template("register.html", form=form)

# View page
@bp.route("/page/<slug>")
def view_page(slug):
    page = Page.query.filter_by(slug=slug).first()
    if not page:
        # redirect to edit to create new
        flash("Страница не найдена — можно создать новую.", "info")
        return redirect(url_for("main.edit_page", slug=slug))
    revision = page.current_revision
    html = revision.to_html() if revision else ""
    return render_template("view_page.html", page=page, html=html, revision=revision)

# Edit page
@bp.route("/page/<slug>/edit", methods=["GET", "POST"])
@login_required
def edit_page(slug):
    page = Page.query.filter_by(slug=slug).first()
    if page and page.current_revision:
        initial_content = page.current_revision.content
        title = page.title
    else:
        initial_content = ""
        title = slug.replace("-", " ").title()

    form = PageForm(title=title, content=initial_content)
    if form.validate_on_submit():
        # create revision
        if not page:
            page = Page(title=form.title.data, slug=slugify(form.title.data))
            db.session.add(page)
            db.session.flush()
        # create revision
        rev = PageRevision(page_id=page.id, title=form.title.data, content=form.content.data,
                           author_id=current_user.id, comment=form.comment.data)
        db.session.add(rev)
        db.session.flush()
        # set current revision
        page.current_revision_id = rev.id
        page.title = form.title.data
        page.slug = slugify(form.title.data)
        db.session.commit()
        flash("Страница сохранена", "success")
        return redirect(url_for("main.view_page", slug=page.slug))
    return render_template("edit_page.html", form=form, slug=slug, page=page)

# History
@bp.route("/page/<slug>/history")
def page_history(slug):
    page = Page.query.filter_by(slug=slug).first_or_404()
    revisions = PageRevision.query.filter_by(page_id=page.id).order_by(PageRevision.created_at.desc()).all()
    return render_template("history.html", page=page, revisions=revisions)

# Diff (simple show two versions)
@bp.route("/page/<slug>/revision/<int:rev_id>")
def view_revision(slug, rev_id):
    page = Page.query.filter_by(slug=slug).first_or_404()
    rev = PageRevision.query.get_or_404(rev_id)
    html = rev.to_html()
    return render_template("view_page.html", page=page, html=html, revision=rev)

# Uploads
@bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        f = form.file.data
        filename = f.filename
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        f.save(save_path)
        flash("Файл загружен", "success")
        return redirect(url_for("main.upload"))
    return render_template("upload.html", form=form)

@bp.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

# Search
@bp.route("/search", methods=["GET", "POST"])
def search():
    form = SearchForm()
    results = []
    q = ""
    if form.validate_on_submit():
        q = form.q.data
        # simple search: title or content LIKE
        results = Page.query.join(PageRevision, Page.current_revision_id == PageRevision.id)\
            .filter(or_(Page.title.ilike(f"%{q}%"), PageRevision.content.ilike(f"%{q}%"))).all()
    return render_template("search.html", form=form, results=results, q=q)

# API
@bp.route("/api/page/<slug>")
def api_get_page(slug):
    page = Page.query.filter_by(slug=slug).first_or_404()
    rev = page.current_revision
    return jsonify({
        "id": page.id,
        "title": page.title,
        "slug": page.slug,
        "content": rev.content if rev else "",
        "html": rev.to_html() if rev else "",
        "updated_at": rev.created_at.isoformat() if rev else None
    })