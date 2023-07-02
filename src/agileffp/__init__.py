import os
import tempfile
from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        UPLOAD_FOLDER=tempfile.gettempdir(),
        ALLOWED_EXTENSIONS={"yml", "yaml"},
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from agileffp.blueprints import landing
    from agileffp.blueprints import gantt
    from agileffp.blueprints import estimation

    app.register_blueprint(landing.bp)
    app.register_blueprint(gantt.bp)
    app.register_blueprint(estimation.bp)

    return app
