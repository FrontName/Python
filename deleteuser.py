import sqlite3

    # Подключение к нашей базе данных
conn = sqlite3.connect('database.db')
c = conn.cursor()

    # Удаление нового пользователя
c.execute('DELETE FROM users WHERE id=1')

    # Сохранение изменений и закрытие соединения с базой данных
conn.commit()
conn.close()

# Замените 'admin' и 'your_password' на желаемые имя пользователя и пароль