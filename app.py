from flask import Flask,render_template, request, url_for, redirect, session
import sqlite3 # подключаем Sqlite в наш проект 
import hashlib # библиотека для хеширования 

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # подствавьте свой секретный ключ
# секретный ключ для хеширования данных сессии при авторизации

# Устанавливаем соединение с Базой Данных
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/bootstrap")
def bootstrap():
    return render_template('bootstrap.html')

@app.route('/login', methods = ['GET','POST'])
def login():
    error = None # обнуляем переменную ошибок 
    if request.method == 'POST':
        username = request.form['username'] # обрабатываем запрос с нашей формы который имеет атрибут name="username"
        password = request.form['password'] # обрабатываем запрос с нашей формы который имеет атрибут name="password"
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest() # шифруем пароль в sha-256

        # устанавливаем соединение с БД
        conn = get_db_connection() 
        # создаем запрос для поиска пользователя по username,
        # если такой пользователь существует, то получаем все данные id, password
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        # закрываем подключение БД
        conn.close() 
        
        # теперь проверяем если данные сходятся формы с данными БД
        if user and user['password'] == hashed_password:
            # в случае успеха создаем сессию в которую записываем id пользователя
            session['user_id'] = user['id']
            # и делаем переадресацию пользователя на новую страницу -> в нашу адимнку
            return redirect(url_for('admin'))

        else:
            error = 'Неправильное имя пользователя или пароль'

    return render_template('login.html', error=error)

@app.route("/admin")
def admin():
    # делаем доп проверку если сессия авторизации была создана
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    blocks = conn.execute('SELECT * FROM content').fetchall()  # Получаем все записи из таблицы content
    conn.close()

    # Преобразование данных из БД в список словарей
    blocks_list = [dict(ix) for ix in blocks]
    # print(blocks_list) [{строка 1 из бд},{строка 2 из бд},{строка 3 из бд}, строка 4 из бд]

     # Теперь нужно сделать группировку списка в один словарь json
    # Группировка данных в словарь JSON
    json_data = {}
    for raw in blocks_list:
        # Создание новой записи, если ключ еще не существует
        if raw['idblock'] not in json_data:
            json_data[raw['idblock']] = []

        # Добавление данных в существующий ключ
        json_data[raw['idblock']].append({
            'id': raw['id'],
            'short_title': raw['short_title'],
            'img': raw['img'],
            'altimg': raw['altimg'],
            'title': raw['title'],
            'contenttext': raw['contenttext'],
            'author': raw['author'],
            'timestampdata': raw['timestampdata']
        })

    # print(json_data)
    # передаем на json на фронт - далее нужно смотреть admin_panel.html и обрабатывать там
    return render_template('admin.html', json_data=json_data)

@app.route('/logout')
def logout():
    # Удаление данных пользователя из сессии
    session.clear()
    
    # Перенаправление на главную страницу или страницу входа
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)