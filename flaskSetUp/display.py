from flask import Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
from werkzeug.exceptions import abort
from flaskSetUp.auth import login_required
from flaskSetUp.db import get_db
from flask import session
# sets up the display blueprint
bp = Blueprint('display', __name__)

# displays homes to all users
@bp.route('/displayhomes', methods=('GET', 'POST'))
def displayHomes():
    # prepares data for display
    db = get_db()
    items = db.execute('SELECT id, wood_required, brick_required, nails_required, pipe_required created FROM homes ORDER BY created DESC').fetchall()
    prices = db.execute('SELECT wood_price, brick_price, nails_price, pipe_price FROM prices WHERE id = 1').fetchone()

    # handles form submission
    homeSelected = None
    if request.method == 'POST':
        choice = request.form.get('homes')
        # map form values to row ids (adjust as appropriate)
        mapping = {}
        for item in items:
            mapping[str(item['id'])] = item['id']
        home_id = mapping.get(choice)

        # makes sure a valid home was selected
        if home_id:
            homeSelected = db.execute(
                'SELECT id, wood_required, brick_required, nails_required, pipe_required, created FROM homes WHERE id = ?',
                (home_id,)
            ).fetchone()
        else:
            flash('Invalid home selection.')
            homeSelected = None

    # renders the display template with data
    return render_template('display/homeDisplay.html', items=items, homeSelected=homeSelected, prices=prices)

# allows admin to manage homes
@bp.route('/manageHomes', methods=('GET', 'POST'))
def manageHomes():
    # prepares data for display
    db = get_db()
    items = db.execute(
        'SELECT id, wood_required, brick_required, nails_required, pipe_required, created FROM homes ORDER BY created DESC'
    ).fetchall()
    prices = db.execute(
        'SELECT wood_price, brick_price, nails_price, pipe_price FROM prices WHERE id = 1'
    ).fetchone()
    choice = None
    homeSelected = None

    # handles form submission
    if request.method == 'POST':
        # used to determine which form was submitted
        action = request.form.get('display')

        # process based data from the first form
        if action == 'select':
            choice = request.form.get('options')

            # modifying a previous home
            if choice and choice.isdigit():
                session['home_id'] = choice
                homeSelected = db.execute(
                    'SELECT * FROM homes WHERE id = ?', (choice,)
                ).fetchone()
                if not homeSelected:
                    flash('Home not found.')
            else:
                flash('Invalid selection.')

        # process data from the second form (specificly adding a home)
        elif action == 'submit New Home':
            # collects data from the form
            wood = request.form.get('wood_count')
            brick = request.form.get('brick_count')
            nails = request.form.get('nails_count')
            pipe = request.form.get('pipe_count')

            # validates the input
            if not all([wood, brick, nails, pipe]):
                flash('All fields are required to create a new home.')
            else:
                # inserts the new home into the database
                db.execute(
                    'INSERT INTO homes (wood_required, brick_required, nails_required, pipe_required, created) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)',
                    (wood, brick, nails, pipe)
                )
                db.commit()
                flash('New home added successfully.')
                return redirect(url_for('display.manageHomes'))

        # process data from the second form (updating a home)
        elif action == 'submit Home Update':
            # to identify the curent home I did have to use the session
            home_id = session.get('home_id')
            # collects data from the form
            wood = request.form.get('wood_required')
            brick = request.form.get('brick_required')
            nails = request.form.get('nails_required')
            pipe = request.form.get('pipe_required')
            # test data
            print(choice)
            print(home_id, wood, brick, nails, pipe)

            # validates the input
            if not all([home_id, wood, brick, nails, pipe]):
                flash('All fields are required to update the home.')
            else:
                # updates the home in the database
                db.execute(
                    'UPDATE homes SET wood_required = ?, brick_required = ?, nails_required = ?, pipe_required = ? WHERE id = ?',
                    (wood, brick, nails, pipe, home_id)
                )
                db.commit()
                flash(f'Home {home_id} updated successfully.')

    return render_template(
        'display/manageHomes.html',
        items=items,
        prices=prices,
        choice=choice,
        homeSelected=homeSelected)
