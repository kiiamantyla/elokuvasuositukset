import db

def add_item(title, year, recommendation, user_id):
    sql = """INSERT INTO movies (title, year, recommendation, user_id)
             VALUES (?, ?, ?, ?)"""

    db.execute(sql, [title, year, recommendation, user_id])
