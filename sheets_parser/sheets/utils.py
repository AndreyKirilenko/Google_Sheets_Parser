import os
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.request import urlopen

from dotenv import load_dotenv
from telegram import Bot

load_dotenv()


LAST_UPDATE_USD_RATE = ['', 0]
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


def get_usd():
    """"Получаем курс доллара на текущее число"""
    # Если обновлялись сегодня возвращаем сохраненный курс
    if LAST_UPDATE_USD_RATE[0] == datetime.now().date():
        return LAST_UPDATE_USD_RATE[1]
    with urlopen('https://www.cbr.ru/scripts/XML_daily.asp') as file:  # Открываем файл
        dollar_rate = ET.parse(file).findtext('.//Valute[@ID="R01235"]/Value')  # Вытаскиваем нужное значение
        rate_usd = float(dollar_rate.replace(',', '.'))  # Меняем запятую на точку
        LAST_UPDATE_USD_RATE[0] = datetime.now().date()  # Запиcываем дату последнего обновления
        LAST_UPDATE_USD_RATE[1] = rate_usd  # Записываем последний курс доллара
        return rate_usd


def check_date(check_date):
    """Проверка даты доставки заказа"""
    if datetime.now().date() > check_date:
        return True
    return False


def send_telegram_message(reservation, delivery_date):
    """Отправляет сообщение в телеграм"""
    message = f'У заявки с № {reservation} закончился \
        срок доставки, назначенный на {delivery_date}'
    print(
        f'У заявки с № {reservation} закончился \
        срок доставки, назначенный на {delivery_date}'
    )
    bot_client = Bot(TELEGRAM_TOKEN)
    return bot_client.send_message(CHAT_ID, message)
