import os
from flask import Flask
from flask import redirect, url_for


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev', # make this random during production
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists (for use in a production enviroment)
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # initializes the database
    from . import db
    db.init_app(app)

    # seeds the database ideally will be removed or simplified before production
    from . import seed
    with app.app_context():
        seed.seed()

    # allows the user to login
    from . import auth
    app.register_blueprint(auth.bp)
    auth.init_app(app)
    # defaults the login page for security
    @app.route('/')
    def default():
        return redirect(url_for('auth.login'))

    # sets up the display pages
    from . import display
    app.register_blueprint(display.bp)

    # returns the flask app when create_app() is called
    return app