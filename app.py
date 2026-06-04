from flask import Flask, request, render_template_string
import sqlite3
import re

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('diary.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, 
                  username TEXT UNIQUE, 
                  password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS notes
                 (id INTEGER PRIMARY KEY, 
                  username TEXT, 
                  note TEXT)''')
    c.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'SuperSecretP@ss_2026')")
    c.execute("INSERT OR IGNORE INTO users VALUES (2, 'student', 'qwerty123')")
    c.execute("INSERT OR IGNORE INTO notes VALUES (1, 'admin', 'КТО ПРОЧИТАЛ ТОТ ЛОХ')")
    c.execute("INSERT OR IGNORE INTO notes VALUES (2, 'student', 'Купить молоко')")
    conn.commit()
    conn.close()

def safe_filter(s):
    if re.search(r'\s', s):
        return False
    return True

@app.route('/')
def index():
    return render_template_string('''
        <h2>Вход в дневник</h2>
        <form action="/login" method="post">
            Логин: <input name="username"><br>
            <input type="submit" value="Войти">
        </form>
    ''')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '')

    if not safe_filter(username):
        return "Ха-ха, я запретил пробелы! Инъекцию не сделать!", 403

    conn = sqlite3.connect('diary.db')
    c = conn.cursor()

    query = f"SELECT * FROM users WHERE username='{username}'"

    try:
        c.execute(query)
        user = c.fetchone()
        conn.close()

        if user:
            real_username = user[1]
            conn2 = sqlite3.connect('diary.db')
            notes_cur = conn2.cursor()
            notes_cur.execute(f"SELECT note FROM notes WHERE username='{real_username}'")
            user_notes = notes_cur.fetchall()
            conn2.close()
            return f"Привет, {real_username}!<br>Твои заметки: {user_notes}"
        else:
            return "Пользователь не найден", 404
    except Exception as e:
        conn.close()
        return f"Ошибка SQL: {e}", 500

if __name__ == '__main__':
    init_db()
    app.run(debug=False, host='0.0.0.0', port=5000)