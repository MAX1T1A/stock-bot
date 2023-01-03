import sqlite3

connect = sqlite3.connect('data_base.db', check_same_thread=False)


def users_table_create():
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id TEXT,
        first_name TEXT,
        role TEXT
    )""")
    connect.commit()
    cursor.close()


def user_check_in_db(user_id):
    cursor = connect.cursor()
    cursor.execute(f"SELECT users.user_id FROM users WHERE users.user_id = '{user_id}'")
    if cursor.fetchone() is None:
        cursor.close()
        return False
    else:
        cursor.close()
        return True


def user_add_in_db(user):
    cursor = connect.cursor()
    cursor.execute("INSERT INTO users VALUES (?, ?, ?);", user)
    connect.commit()
    cursor.close()

