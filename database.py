import psycopg2
from prettytable import PrettyTable


class DataAccessObject:
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        self.connect = psycopg2.connect(
            host="db",
            user="root",
            password="root",
            port="5432",
            dbname="test_db",
        )
        self.tab = self.connect.cursor()
        self.tab.execute('''CREATE TABLE IF NOT EXISTS schedule (
                          name_group TEXT,
                          day TEXT,
                          time TEXT, 
                          discipline TEXT, 
                          auditorium TEXT, 
                          teacher TEXT)
                        ''')
        self.connect.commit()

    def create(self, name_group, day, time, discipline, auditorium, teacher):
        sql = 'INSERT INTO schedule (name_group, day, time, discipline, auditorium, teacher) VALUES(%s, %s, %s, %s, %s, %s)'
        data = (name_group, day, time, discipline, auditorium, teacher)
        self.tab.execute(sql, data)
        self.connect.commit()

    def show_base(self, group):
        self.tab.execute('SELECT * FROM schedule')
        result = self.tab.fetchall()
        items = []
        for i in range(len(result)):
            if result[i][0] == group:
                items.append(result[i])
        table = PrettyTable()
        table.field_names = result[0][2:]
        for i in range(len(items)):
            if items[i][1] != items[i - 1][1]:
                table.add_row([items[i][1], '', '', ''])
            table.add_row(items[i][2:])
        response = '```\n{}```'.format(table.get_string())
        return response

    def close_database(self):
        self.connect.close()
