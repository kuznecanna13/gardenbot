import sqlite3
from config import DATABASE

flowers = [ (_,) for _ in (['Роза', 'Тюльпан', 'Мак', 'Подсолнух', 'Кактус'])]
status = [ (_,) for _ in (['Семечко', 'Росток', 'Цветение'])]

class DB_Manager:
    def __init__(self, database):
        self.database = database
    
    def create_tables(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS flowers (
                            flower_id INTEGER PRIMARY KEY,
                            name TEXT,
                            description TEXT
                        )''')
            conn.execute('''CREATE TABLE IF NOT EXISTS users (
                            user_id INTEGER PRIMARY KEY,
                            user_name TEXT
                        )''')
            conn.execute('''CREATE TABLE IF NOT EXISTS flowers_images (
                            flower_img TEXT,
                            flower_id INTEGER,
                            FOREIGN KEY(flower_id) REFERENCES flowers(flower_id)
                        )''')
            conn.execute('''CREATE TABLE IF NOT EXISTS flowers_users (
                            user_id INTEGER,
                            flower_id INTEGER,
                            status_id INTEGER,
                            water INTEGER DEFAULT 0,
                            FOREIGN KEY(flower_id) REFERENCES flowers(flower_id)
                            FOREIGN KEY(user_id) REFERENCES users(user_id),
                            FOREIGN KEY(status_id) REFERENCES flowers_status(status_id)
                        )''')
            conn.execute('''CREATE TABLE IF NOT EXISTS flowers_status(
                            status_id INTEGER PRIMARY KEY,
                            status_name TEXT
                        )''')


    def __executemany(self, sql, data):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.executemany(sql, data)
            conn.commit()

    def default_insert(self):
        sql = 'INSERT OR IGNORE INTO flowers (name) values(?)'
        data = flowers
        self.__executemany(sql, data)
        sql = 'INSERT OR IGNORE INTO flowers_status (status_name) values(?)'
        data = status
        self.__executemany(sql, data)

    def get_flowers(self):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute('SELECT name FROM flowers')
            return [x[0] for x in cur.fetchall()] 

    def add_user(self, user_id, user_name):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('INSERT INTO users VALUES (?, ?)', (user_id, user_name))
            conn.commit()

    def add_flower(self, user_id, flower_id, status_id):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('INSERT INTO flowers_users(user_id, flower_id, status_id) VALUES (?, ?, ?)', (user_id, flower_id, status_id))
            conn.commit()
    
    def get_users(self):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM users')
            return [x[0] for x in cur.fetchall()] 
    
    def select_flower(self, name):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute('SELECT flower_id, name FROM flowers WHERE name = ?', (name,))
            return [x[0] for x in cur.fetchall()]
        
    def get_flower_img(self, name):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute('''SELECT flower_img FROM flowers_images
                        INNER JOIN flowers ON flowers_images.flower_id = flowers.flower_id
                        WHERE name = ?
                        ORDER BY RANDOM() LIMIT 1 ''', (name,))
            return [x[0] for x in cur.fetchall()]
    
    def get_users_flowers(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute('''SELECT name
                        FROM flowers_users
                        INNER JOIN flowers
                        ON flowers.flower_id = flowers_users.flower_id
                        WHERE user_id = ?''', (user_id,))
            return [x[0] for x in cur.fetchall()]
        
    def get_info_flower(self, user_id, name):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute('''SELECT name, description, water, status_name
                        FROM flowers
                        INNER JOIN flowers_users
                        ON flowers.flower_id = flowers_users.flower_id
                        INNER JOIN flowers_status
                        ON flowers_users.status_id = flowers_status.status_id
                        WHERE user_id = ? AND name = ?
                        ''', (user_id, name))
            return cur.fetchall()
    
    def water(self, water, user_id, flower_id):
        self.__executemany("UPDATE flowers_users SET water = ? WHERE user_id = ? AND flower_id = ?", [(water, user_id, flower_id)])

    def get_water(self, user_id, name):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute('''SELECT water
                        FROM flowers_users
                        INNER JOIN flowers
                        ON flowers.flower_id = flowers_users.flower_id
                        WHERE user_id = ?
                        AND name = ?
                        ''', (user_id, name))
        return [x[0] for x in cur.fetchall()]

    def get_status(self, user_id, flower_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute('''SELECT status_id
                        FROM flowers_users
                        WHERE user_id = ?
                        AND flower_id = ?
                        ''', (user_id, flower_id))
        return [x[0] for x in cur.fetchall()]

    def up_status(self, status, user_id, flower_id):
        self.__executemany("UPDATE flowers_users SET status_id = ? WHERE user_id = ? AND flower_id = ?", [(status, user_id, flower_id)])

    def get_img(self, flower_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute('''SELECT flower_img 
                    FROM flowers_images
                    WHERE flower_id = ?
                    ''', (flower_id,))
        return [x[0] for x in cur.fetchall()]

    def delete_flower(self, user_id, flower_id):
        self.__executemany("DELETE FROM flowers_users WHERE user_id = ? AND flower_id = ?", [(user_id, flower_id)])

if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    manager.create_tables()
    manager.get_users_flowers(1088080528)