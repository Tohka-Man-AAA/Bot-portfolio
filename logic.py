import sqlite3
from config import DATABASE

skills = [ (_,) for _ in (['Python', 'SQL', 'API', 'Telegram'])]
statuses = [ (_,) for _ in (['На этапе проектирования', 'В процессе разработки', 'Разработан. Готов к использованию.', 'Обновлен', 'Завершен. Не поддерживается'])]

class DB_Manager:
    def __init__(self, database):
        self.database = database # имя базы данных
        
    def create_tables(self):
        con = sqlite3.connect(self.database)
        with con:
            con.execute('CREATE TABLE projects(project_id INTEGER PRIMARY KEY, user_id INTEGER, project_name TEXT NOT NULL, description TEXT, url TEXT, status_id INTEGER, FOREIGN KEY(status_id) REFERENCES statuses(status_id))')
            con.execute('CREATE TABLE statuses(status_id INTEGER PRIMARY KEY, status_name TEXT)')
            con.execute('CREATE TABLE project_skills(project_id INTEGER, skill_id INTEGER, FOREIGN KEY(project_id) REFERENCES projects(project_id), FOREIGN KEY(skill_id) REFERENCES skills(skill_id))')
            con.execute('CREATE TABLE skills(skills_id INTEGER PRIMARY KEY, skill_name TEXT)')
            con.commit()


    def __executemany(self, sql, data):
        con = sqlite3.connect(self.database)
        with con:
            con.executemany(sql,data)
            con.commit()

    def __select_data(self, sql, data=tuple()):
        con = sqlite3.connect(self.database)
        with con:
            cur = con.cursor()
            cur.execute(sql, data)
            return cur.fetchall()

    def default_insert(self):
        sql = 'INSERT OR IGNORE INTO skills (skill_name) values(?)'
        data = skills
        self.__executemany(sql, data)
        sql = 'INSERT OR IGNORE INTO statuses (status_name) values(?)'
        data = statuses
        self.__executemany(sql, data)

    def insert_project(self, data):
        sql = """INSERT INTO projects 
            (user_id, project_name, url, status_id) 
            values(?, ?, ?, ?)"""
        self.__executemany(sql, data)

    def insert_skill(self, user_id, project_name, skill):
            sql = 'SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?'
            project_id = self.__select_data(sql, (project_name, user_id))[0][0]
            skill_id = self.__select_data('SELECT skill_id FROM skills WHERE skill_name = ?', (skill,))[0][0]
            data = [(project_id, skill_id)]
            sql = 'INSERT OR IGNORE INTO project_skills VALUES(?, ?)'
            self.__executemany(sql, data)


    def get_statuses(self):
            sql = "SELECT status_name from statuses"
            return self.__select_data(sql)
    def get_status_id(self, status_name):
            sql = 'SELECT status_id FROM statuses WHERE status_name = ?'
            res = self.__select_data(sql, (status_name,))
            if res:
                return res[0][0]
            else:
                return None

    def get_projects(self, user_id):
            sql = """SELECT * FROM projects 
WHERE user_id = ?"""  # Запиши сюда правильный SQL запрос
            return self.__select_data(sql, data=(user_id,))

    def get_project_id(self, project_name, user_id):
            return self.__select_data(sql='SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?  ',
                                      data=(project_name, user_id,))[0][0]

    def get_skills(self):
            return self.__select_data(sql='SELECT * FROM skills')

    def get_project_skills(self, project_name):
            res = self.__select_data(sql='''SELECT skill_name FROM projects 
    JOIN project_skills ON projects.project_id = project_skills.project_id 
    JOIN skills ON skills.skill_id = project_skills.skill_id 
    WHERE project_name = ?''', data=(project_name,))
            return ', '.join([x[0] for x in res])

    def get_project_info(self, user_id, project_name):
            sql = """
    SELECT project_name, description, url, status_name FROM projects 
    JOIN status ON
    status.status_id = projects.status_id
    WHERE project_name=? AND user_id=?
    """
            return self.__select_data(sql=sql, data=(project_name, user_id))

    def update_projects(self, param, data):
            sql = f"""UPDATE projects SET {param} = ? 
WHERE project_name = ? AND user_id = ?"""
            self.__executemany(sql, [data])

    def delete_project(self, user_id, project_id):
            sql = """DELETE FROM projects 
WHERE user_id = ? AND project_id = ? """
            self.__executemany(sql, [(user_id, project_id)])

    def delete_skill(self, project_id, skill_id):
            sql = """DELETE FROM skills 
WHERE skill_id = ? AND project_id = ? """
            self.__executemany(sql, [(skill_id, project_id)])


    def create_newtable(self):
        # Подключение к базе данных
        conn = sqlite3.connect('portfolio.db')
        cursor = conn.cursor()

        # Название таблицы
        table_name = 'portfolio'

        # Название нового столбца и его тип данных
        new_column_name = 'foto'
        new_column_type = 'PILLOW'

        # Выполнение запроса на добавление столбца
        alter_query = f"ALTER TABLE {table_name} ADD COLUMN {new_column_name} {new_column_type}"
        cursor.execute(alter_query)

        # Сохранение изменений и закрытие соединения
        conn.commit()
        conn.close()






if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    manager.create_tables()
    manager.default_insert()
