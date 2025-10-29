from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired, Length, EqualTo, Optional

class LoginForm(FlaskForm):
    username = StringField("Имя", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    submit = SubmitField("Войти")

class RegisterForm(FlaskForm):
    username = StringField("Имя", validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField("Email", validators=[Optional()])
    password = PasswordField("Пароль", validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField("Повторите пароль", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Зарегистрироваться")

class PageForm(FlaskForm):
    title = StringField("Заголовок", validators=[DataRequired(), Length(max=255)])
    content = TextAreaField("Содержимое (Markdown)", validators=[DataRequired()])
    comment = StringField("Комментарий к правке", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Сохранить")

class UploadForm(FlaskForm):
    file = FileField("Файл", validators=[DataRequired()])
    submit = SubmitField("Загрузить")

class SearchForm(FlaskForm):
    q = StringField("Поиск", validators=[DataRequired()])
    submit = SubmitField("Найти")