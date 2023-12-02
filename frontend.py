import telebot
from telebot import types
from backend import Parser


class TelegramBot:
    def __init__(self):
        self.bot = telebot.TeleBot('6980241396:AAEorBOe_DnoX6XiMt3AasWQwgpXhcittA8')
        self.group = None
        self.pars = Parser()
        Parser.get_groups(self.pars)

        @self.bot.message_handler(commands=['start'])
        def start(message):
            self.bot.send_message(message.chat.id, 'Здесь ты можешь посмотреть своё расписание')
            ask_group(message)

        def ask_group(message):
            self.bot.send_message(message.chat.id, 'Напиши свою группу', reply_markup=types.ReplyKeyboardRemove())
            self.bot.register_next_step_handler(message, get_group)

        def get_group(message):
            group = message.text
            self.group = group
            schedule(message)

        def schedule(message):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            witch_schedule = types.KeyboardButton('Посмотреть расписание другой группы')
            markup.add(witch_schedule)
            answer = self.pars.parser(self.group)
            if answer == 'Введи корректно название группы':
                self.bot.send_message(message.chat.id, answer)
                self.bot.register_next_step_handler(message, get_group)
            else:
                self.bot.send_message(message.chat.id,   answer, parse_mode='Markdown',
                                      reply_markup=markup)

        @self.bot.message_handler(func=lambda m: m.text == 'Посмотреть расписание другой группы')
        def other_schedule(message):
            ask_group(message)

    def run(self):
        self.bot.polling(none_stop=True, interval=0)


telegram = TelegramBot()
telegram.run()
