from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

db = SQLAlchemy()


def create_app(config=None):
    app = Flask(__name__, static_folder="../frontend", static_url_path="")
    CORS(app)

    env = os.getenv("FLASK_ENV", "development")

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

    if env == "testing":
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["TESTING"] = True
    elif env == "production":
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
            "DATABASE_URL", "sqlite:///prod_tasks.db"
        )
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
            "DATABASE_URL", "sqlite:///dev_tasks.db"
        )

    if config:
        app.config.update(config)

    db.init_app(app)

    from app.routes import tasks_bp
    app.register_blueprint(tasks_bp)

    @app.route("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    with app.app_context():
        db.create_all()

    return app
