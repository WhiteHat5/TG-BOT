import os
import telebot
from telebot import types
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import gspread

# Configuration and global variables
bot_token = '6127346910:AAEavBl4k8mylFzHyoR2JxF7lk1H7NRVlM8'
spreadsheet_id = '13Vp_FUcSIwrWYanqTTvxX8EhAGHInniL6Lv7T_nXUBY'
sheet_range = 'Лист1!A:E'

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
questions = [
    "1) Марка автомобиля:",
    "2) Вес автомобиля:",
    "3) Сколько колес крутится:",
    "4) Адрес откуда забрать:",
    "5) Адрес куда отвезти:",
    "6) ФИО заказчика:",
    "7) Номер телефона:"
]
user_data = {}
current_question = 0

bot = telebot.TeleBot(bot_token)


# Google Sheets authentication
def authenticate_google_sheets():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


# Write data to Google Sheets
def write_to_google_sheets(data):
    try:
        creds = authenticate_google_sheets()
        gc = gspread.authorize(creds)
        worksheet = gc.open_by_key(spreadsheet_id).sheet1
        worksheet.append_row(list(data.values()))
    except Exception as e:
        print(e)


# Bot message handlers
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Вызвать эвакуатор!")
    markup.add(btn1)
    bot.send_message(message.chat.id, "👋 Привет! Я твой бот-помощник!", reply_markup=markup)


def ask_next_question(chat_id):
    global current_question
    if current_question < len(questions):
        bot.send_message(chat_id, questions[current_question])
        current_question += 1
    else:
        write_to_google_sheets(user_data)
        bot.send_message(chat_id, "Данные успешно записаны и были переданы в службу помощи!👍👍👍 В течение нескольких минут с вами свяжется техническая поддержка!🤝😉")
        current_question = 0
        user_data.clear()


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    global current_question
    if message.text == "Вызвать эвакуатор!":
        ask_next_question(message.chat.id)
    elif 0 < current_question <= len(questions):
        user_data[questions[current_question - 1]] = message.text
        ask_next_question(message.chat.id)


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0, timeout=10)
