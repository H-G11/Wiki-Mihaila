from app import create_app, db
from flask_migrate import Migrate
from app.models import User, Page, PageRevision

app = create_app()
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return {"db": db, "User": User, "Page": Page, "PageRevision": PageRevision}

if name == "main":
    app.run(debug=True)