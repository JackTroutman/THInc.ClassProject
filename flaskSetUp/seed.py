from flaskSetUp import create_app
from flaskSetUp.db import get_db

def seed():
    db = get_db()
    # don't insert if already has rows
    if db.execute('SELECT 1 FROM homes LIMIT 1').fetchone():
        print('homes table not empty; skipping seed')
        return


    db.executemany(
        'INSERT INTO homes (wood_required, brick_required, nails_required, pipe_required) VALUES (?, ?, ?, ?)',
        [
            (100, 50, 200, 30),
            (80, 120, 150, 20),
            (120, 40, 250, 50),
            (90, 60, 180, 25),
            (110, 70, 220, 40)
        ]
    )

    db.execute(
        'Insert INTO prices (wood_price, brick_price, nails_price, pipe_price) VALUES (?, ?, ?, ?)',
        (10, 20, 1, 5)
        )

    db.commit()
    print('seed complete')

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        seed()