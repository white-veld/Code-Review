import requests
import re
import telebot
from telebot import types
from bs4 import BeautifulSoup as BS
from database import DataAccessObject
from collections import OrderedDict


class Parser:
    def __init__(self):
        self.list_lessons = OrderedDict()
        self.bot = telebot.TeleBot('Token')
        self.group = None
        self.groups = []

        @self.bot.message_handler(commands=['start'])
        def start(message):
            self.bot.send_message(message.chat.id, 'Здесь ты можешь посмотреть своё расписание')
            get_group(message)

        def get_group(message):
            self.bot.send_message(message.chat.id, 'Напиши свою группу')
            self.bot.register_next_step_handler(message, schedule)
            self.bot.register_next_step_handler(message, parser)

        def schedule(message):
            group = message.text
            self.group = group

        def parser(message):
            self.list_lessons = OrderedDict()
            headers = {
                "Accept": "*/*",
                "User-Agent":
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            }
            url = "https://bgu.ru/student/timetable.aspx"
            req = requests.get(url, headers=headers)
            soup = BS(req.content, 'lxml')
            groups_data = soup.find(class_="groups list-group shadow w-100")
            dictionary = {}
            for i in groups_data:
                i_text = i.text
                i_href = i.get("href")
                dictionary[i_text] = i_href
            new_url = url
            for i in dictionary.keys():
                if self.group == i:
                    new_url += dictionary[i]
            new_req = requests.get(new_url, headers=headers)
            new_soup = BS(new_req.content, 'lxml')
            lessons_data = new_soup.find(id="nav-rasp-1").find_all("tr")
            check = True
            for group in self.groups:
                if group == self.group:
                    check = False
                    break
            if check:
                for item in lessons_data:
                    lessons_tds = item.find_all("td")
                    if len(lessons_tds) == 1:
                        start = lessons_tds[0].text
                        self.list_lessons[start] = None
                    else:
                        start = lessons_tds[0].text
                        discipline = lessons_tds[1].text
                        discipline = re.sub('([А-Я])', r' \1', discipline)
                        # discipline = re.findall('[А-Я][^А-Я]*', discipline)
                        auditorium = lessons_tds[2].text
                        teacher = lessons_tds[3].text
                        if (len(self.list_lessons.keys()) != 0 and self.list_lessons[list(self.list_lessons.keys())[-1]] is
                                None):
                            self.list_lessons[list(self.list_lessons.keys())[-1]] = [
                                [start, discipline, auditorium, teacher]]
                        elif len(self.list_lessons.keys()) != 0:
                            self.list_lessons[list(self.list_lessons.keys())[-1]].append(
                                [start, discipline, auditorium, teacher])
                        else:
                            self.list_lessons['headers'] = [start, discipline, auditorium, teacher]
            self.groups.append(self.group)
            print(self.list_lessons)
            dao = DataAccessObject()
            for i in self.list_lessons.keys():
                if i == 'headers':
                    print(self.list_lessons[i][0])
                    dao.create(None,
                               None,
                               self.list_lessons[i][0],
                               self.list_lessons[i][1],
                               self.list_lessons[i][2],
                               self.list_lessons[i][3])
                    continue
                for j in range(len(self.list_lessons[i])):
                    print(self.list_lessons[i][j][0])
                    dao.create(self.group,
                               i,
                               self.list_lessons[i][j][0],
                               self.list_lessons[i][j][1],
                               self.list_lessons[i][j][2],
                               self.list_lessons[i][j][3])
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            witch_schedule = types.KeyboardButton('Посмотреть расписание другой группы')
            markup.add(witch_schedule)
            self.bot.send_message(message.chat.id, dao.show_base(self.group), parse_mode='Markdown', reply_markup=markup)

            @self.bot.message_handler(func=lambda m: m.text == 'Посмотреть расписание другой группы')
            def other_schedule(message):
                get_group(message)

    def run(self):
        self.bot.polling(none_stop=True, interval=0)


telegram = Parser()
telegram.run()
