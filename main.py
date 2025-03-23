import random
import  telebot
import psycopg2
from telebot import types
from dotenv import load_dotenv
import os

# Загружаем переменные окружения из файла .env
load_dotenv()

# Получаем значения из файла .env
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_schema_name = os.getenv("DB_SCHEMA_NAME")

bot = telebot.TeleBot(telegram_bot_token)

# Метод, который получает сообщения и обрабатывает их
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    # Если написали
    if message.text == "/start":

        # Подключение к локальной базе данных PostgreSQL
        try:
            # Создание соединения
            connection = psycopg2.connect(
                host=db_host,  # Хост
                database=db_name,  # Название базы данных
                user=db_user,  # имя пользователя PostgreSQL
                password=db_password  # пароль
            )

            cursor = connection.cursor()

            query = f'''SELECT * FROM {db_schema_name}.user WHERE tg_id = '{message.from_user.id}';'''

            cursor.execute(query)

            # Получение результатов запроса
            user = cursor.fetchone()

            if user is None:
                msg = 'Привет! Я бот, который запоминает твои тренировки 😊'
                # Добавляем пользователя в базу данных
                cursor.execute(f'''INSERT INTO {db_schema_name}.user(tg_id, last_menu) VALUES ({message.from_user.id}, 'new_user');''')
                connection.commit()
            else:
                msg = 'Привет! Удачных тренировок 🐒'

            keyboard = types.InlineKeyboardMarkup()
            key_start = types.InlineKeyboardButton(text='Начать тренировку', callback_data='start')
            # И добавляем кнопку на экран
            keyboard.add(key_start)
            # Показываем все кнопки сразу и пишем сообщение о выборе
            bot.send_message(message.from_user.id, text=msg, reply_markup=keyboard)

        except Exception as error:
            print("Ошибка при работе с PostgreSQL:", error)

        finally:
            # Закрытие курсора и соединения
            if connection:
                cursor.close()
                connection.close()
                print("Соединение с PostgreSQL закрыто")

    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /start.")

# Обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):

    if call.data == "start":
        try:
            msg = 'Для начала выбери тренировочный день'
            connection = psycopg2.connect(
                host=db_host,  # Хост
                database=db_name,  # Название базы данных
                user=db_user,  # имя пользователя PostgreSQL
                password=db_password  # пароль
            )

            cursor = connection.cursor()
            cursor.execute(
                f'''UPDATE {db_schema_name}.user SET last_menu = 'choose_day' WHERE tg_id = {call.from_user.id};''')
            connection.commit()

            keyboard = types.InlineKeyboardMarkup()
            key_new_training = types.InlineKeyboardButton(text='Создать новый тренировочный день', callback_data='new_training_day')
            key_back = types.InlineKeyboardButton(text='Назад', callback_data='back_menu')
            # И добавляем кнопку на экран
            keyboard.add(key_new_training)
            keyboard.add(key_back)
            # Показываем все кнопки сразу и пишем сообщение о выборе
            bot.send_message(call.from_user.id, text=msg, reply_markup=keyboard)
        except Exception as error:
            print("Ошибка при работе с PostgreSQL:", error)

        finally:
            # Закрытие курсора и соединения
            if connection:
                cursor.close()
                connection.close()
                print("Соединение с PostgreSQL закрыто")

    else:
        bot.send_message(call.from_user.id, "Я тебя не понимаю. Напиши /start.")

# Запускаем постоянный опрос бота в Телеграме
bot.polling(none_stop=True, interval=0)