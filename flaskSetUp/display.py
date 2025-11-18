from flask import Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
from werkzeug.exceptions import abort
from flaskSetUp.auth import login_required
from flaskSetUp.db import get_db

bp = Blueprint('display', __name__)

@bp.route('/displayhomes', methods=('GET', 'POST'))
def displayHomes():
    db = get_db()
    items = db.execute('SELECT id, wood_required, brick_required, nails_required, pipe_required created FROM homes ORDER BY created DESC').fetchall()
    prices = db.execute('SELECT wood_price, brick_price, nails_price, pipe_price FROM prices WHERE id = 1').fetchone()

    homeSelected = None
    if request.method == 'POST':
        choice = request.form.get('homes')
        # map form values to row ids (adjust as appropriate)
        mapping = {}
        for item in items:
            mapping[str(item['id'])] = item['id']
        home_id = mapping.get(choice)

        if home_id:
            homeSelected = db.execute(
                'SELECT id, wood_required, brick_required, nails_required, pipe_required, created FROM homes WHERE id = ?',
                (home_id,)
            ).fetchone()


        else:
            flash('Invalid home selection.')
            homeSelected = None


    return render_template('display/homeDisplay.html', items=items, homeSelected=homeSelected, prices=prices)

@bp.route('/manageHomes', methods=('GET', 'POST'))
def manageHomes():

    db = get_db()
    items = db.execute('SELECT id, wood_required, brick_required, nails_required, pipe_required created FROM homes ORDER BY created DESC').fetchall()
    prices = db.execute('SELECT wood_price, brick_price, nails_price, pipe_price FROM prices WHERE id = 1').fetchone()
    choice = None
    homeSelected = None
    if request.method == 'POST':
        action = request.form.get('display')

        if action == "select":
            choice = request.form.get('options')
            print("choice value:", choice)

            if choice != "NewHome" and choice != "changePrices":
                homeSelected = db.execute(
                    'SELECT id, wood_required, brick_required, nails_required, pipe_required, created FROM homes WHERE id = ?',
                    (choice,)
                ).fetchone()

            elif choice == "NewHome":
                flash('new home creation selected.')
                choice = None
            elif choice == "changePrices":
                flash('price change selected.')
                
                prices = db.execute('SELECT wood_price, brick_price, nails_price, pipe_price FROM prices WHERE id = 1').fetchone()
        elif action == "submit":    
            wood_price = request.form.get('wood_price')
            brick_price = request.form.get('brick_price')
            nails_price = request.form.get('nails_price')
            pipe_price = request.form.get('pipe_price')
            if not wood_price or not brick_price or not nails_price or not pipe_price:
                flash('All price fields are required.')
            else:
                db.execute(
                    'UPDATE prices SET wood_price = ?, brick_price = ?, nails_price = ?, pipe_price = ? WHERE id = 1',
                    (wood_price, brick_price, nails_price, pipe_price)
                )
                db.commit()
                flash('Prices updated successfully.')

        else:
            flash('Invalid selection.')
            choice = None

    return render_template('display/manageHomes.html', items=items, prices=prices, choice=choice)

