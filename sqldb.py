import sqlite3

def ensure_connection(func):
    """ Декоратор для подключения к СУБД: открывает соединение,
        выполняет переданную функцию и закрывает за собой соединение.
        Потокобезопасно!
    """

    def inner(*args, **kwargs):
        with sqlite3.connect('courses.db') as conn:
            kwargs['conn'] = conn
            res = func(*args, **kwargs)
        return res

    return inner


# Ретурн найденного человека в базе
@ensure_connection
def get_have_user_in_a_base(conn, id_telegram: int):
    c = conn.cursor()
    c.execute("SELECT id_telegram FROM user_reg WHERE id_telegram = ?", (id_telegram,))
    user_result_id = c.fetchall()
    if not user_result_id:
        return 0
    else:
        return 1


# Функция, которая регистрирует пользователя в таблице user_reg.
@ensure_connection
def user_info(conn, id_telegram: int, username: str, date_last: str):
    c = conn.cursor()
    c.execute(
        'INSERT INTO user_reg (id_telegram, username, date_last) VALUES (?, ?, ?)',
        (id_telegram, username, date_last))
    conn.commit()
    print('Store have a new user')


# Функция, которая заносит курс.
@ensure_connection
def course(conn,id:int, name_val: str, price: str):
    c = conn.cursor()
    c.execute(
        'INSERT INTO course (id,name_val, price) VALUES (?,?,?)',
        (id,name_val, price))
    conn.commit()