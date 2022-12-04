import sqlite3

connect = sqlite3.connect("data_base.db")


def product_table_create():
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS products (
        name TEXT, 
        taste TEXT,
        volume REAL,
        type TEXT,
        country TEXT,
        amount INT,
        price INT
    )""")
    connect.commit()
    cursor.close()

#name is Название
#taste is Вкус
#volume is Объем
#type is Тип
#country is Страна

#amount is Количество
#price is Цена


def products_add_in_db(products):
    cursor = connect.cursor()
    cursor.execute("INSERT INTO products VALUES (?, ?, ?, ?, ?, ?, ?);", products)
    connect.commit()
    cursor.close()


def products_check_in_db(products_list):
    cursor = connect.cursor()
    cursor.execute(f"SELECT rowid FROM products WHERE name=? AND taste=? AND volume=? AND type=? AND country=?", products_list[:5])
    if cursor.fetchone() is None:
        cursor.close()
        return True
    else:
        cursor.close()
        return False


def select_all_in_table():
    tables = []
    cursor = connect.cursor()
    cursor.execute("SELECT rowid, * FROM products")
    for tab in cursor.fetchall():
        tables.append(tab)
    if not tables:
        return True
    return tables


def select_name_in_table(name):
    names = []
    cursor = connect.cursor()
    cursor.execute(f"SELECT rowid, * FROM products WHERE name = '{name.upper()}'")
    for tab in cursor.fetchall():
        names.append(tab)
    if not names:
        return True
    return names


def update_row(row_id, value, number):
    cursor = connect.cursor()
    cursor.execute(f"UPDATE products SET {value} = {number} WHERE rowid = {row_id}")
    connect.commit()


def delete_row(row_id):
    cursor = connect.cursor()
    cursor.execute("DELETE FROM products WHERE rowid = ?", row_id)
    connect.commit()
