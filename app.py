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
    c.execute(
        "INSERT OR IGNORE INTO notes VALUES (1, 'admin', 'СЕКРЕТНЫЙ ФЛАГ ДЛЯ IDOR: flag{broken_access_control_2024}')")
    c.execute("INSERT OR IGNORE INTO notes VALUES (2, 'student', 'Купить молоко')")
    conn.commit()
    conn.close()

def safe_filter(s):
    if re.search(r'\s', s):
        return False, "Ха-ха, я запретил пробелы! Инъекцию не сделать!"
    blacklist = ['union', 'select', 'or', 'from', 'where']
    for word in blacklist:
        if word in s:
            return False, f"Обнаружена попытка взлома! Слово '{word}' запрещено."
    return True, ""


@app.route('/')
def index():
    return render_template_string('''
        <h2>Вход в дневник</h2>
        <form action="/login" method="post">
            Логин: <input type="text" name="username"><br>
            <input type="submit" value="Войти">
        </form>
        <p><i>Подсказка: админ добавил фильтрацию ключевых слов, теперь всё безопасно!</i></p>
    ''')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '')
    is_safe, error_msg = safe_filter(username)
    if not is_safe:
        return error_msg, 403

    conn = sqlite3.connect('diary.db')
    c = conn.cursor()
    query = f"SELECT * FROM users WHERE username='{username}'"

    try:
        c.execute(query)
        user = c.fetchone()
        if user:
            real_username = user[1]
            c.execute(f"SELECT id FROM notes WHERE username='{real_username}'")
            note_ids = [row[0] for row in c.fetchall()]
            conn.close()
            return render_template_string(f'''
                <h1>Привет, {real_username}!</h1>
                <p>Ваши ID заметок: {note_ids}</p>
                <p>Для просмотра заметки перейдите по ссылке: <code>/view_note?id=ID</code></p>
                <hr>
                <a href="/">Выход</a>
            ''')
        else:
            conn.close()
            return "Пользователь не найден", 404
    except Exception as e:
        conn.close()
        return f"Ошибка SQL: {e}", 500


@app.route('/view_note')
def view_note():
    note_id = request.args.get('id', '')
    conn = sqlite3.connect('diary.db')
    c = conn.cursor()
    query = f"SELECT username, note FROM notes WHERE id = {note_id}"
    c.execute(query)
    result = c.fetchone()
    conn.close()
    if result:
        return f"<h3>Автор: {result[0]}</h3><p>Заметка: {result[1]}</p><a href='javascript:history.back()'>Назад</a>"
    return "Заметка не найдена", 404


if __name__ == '__main__':
    init_db()
    app.run(debug=False, port=5000)