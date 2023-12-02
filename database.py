import sqlite3
from prettytable import PrettyTable


class DataAccessObject:
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        self.connect = sqlite3.connect('mydata.db')
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
        self.tab.execute(
            'INSERT INTO schedule (name_group, day, time, discipline, auditorium, teacher) VALUES(?, ?, ?, ?, ?, ?)',
            (name_group, day, time, discipline, auditorium, teacher))
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
