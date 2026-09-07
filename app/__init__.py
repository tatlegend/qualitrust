"""
QualiTrust - Qualification Verification System
Application factory module.
"""
import os
from flask import Flask
from app.db import init_db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "qualitrust.sqlite"),
    )

    if test_config:
        app.config.update(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    init_db(app)

    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app
