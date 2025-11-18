import functools
import click
from flask import Blueprint, flash, Flask, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flaskSetUp.db import get_db

# sets all auth pages with the default url
bp = Blueprint('auth', __name__, url_prefix='/auth')

# user registration (only acessable by the admin)
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        # collects data from the html
        username = request.form['username']
        password = request.form['password']
        position = request.form['position']

        #access db and makes sure error is default none
        db = get_db()
        error = None

        # confirms username and password are used (incase html issues are pressent)
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        # manages errors, making sure users dont already exist
        if error is None:
            try:
                # creates user
                db.execute(
                    'INSERT INTO users (username, password, position) VALUES (?, ?, ?)',
                    (username, generate_password_hash(password), position)
                )
                db.commit()
                return redirect(url_for('display.displayHomes'))
            # if user creation fails notify user
            except db.IntegrityError:
                error = f"User {username} is already registered."
            # redirect to home page on success
            else:
                return redirect(url_for('display.displayHomes'))

        # discloses errors
        flash(error)

    # renders the register page
    return render_template('auth/register.html')

# login available fpr all users
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        # collects data from html
        username = request.form['username']
        password = request.form['password']
        # gets database data and sets error to default
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()

        # checks for errors in login making sure user exists and password is correct
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        # if no errors, clear session and log user in
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('display.displayHomes'))

        flash(error)

    return render_template('auth/login.html')

# loads the logged in user for use in other parts of the app
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

# creates an admin user via command line
@click.command('init-admin')
def init_admin_command():
    username = input("Enter admin username: ")
    password = input("Enter admin password: ")
    db = get_db()
    error = None

    if not username:
        error = 'Username is required.'
    elif not password:
        error = 'Password is required.'
    if error is None:
        try:
            db.execute(
                'INSERT INTO users (username, password, position) VALUES (?, ?, ?)',
                (username, generate_password_hash(password), 'admin')
            )
            db.commit()
            print(f'Admin user {username} created successfully.')
        except db.IntegrityError:
            error = f"User {username} is already registered."


# requires login if user is not loged in
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

# sets up the app to use the init admin command
def init_app(app):
    app.cli.add_command(init_admin_command)