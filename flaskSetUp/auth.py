import functools
import click
from flask import Blueprint, flash, Flask, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flaskSetUp.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        position = request.form['position']
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
                    (username, generate_password_hash(password), position)
                )
                db.commit()
                return redirect(url_for('display.displayHomes'))
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for('display.displayHomes'))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('display.displayHomes'))

        flash(error)

    return render_template('auth/login.html')

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



def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


def init_app(app):
    app.cli.add_command(init_admin_command)