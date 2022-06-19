##################################################
#
#  start_update() - Запускает параллельный поток для получения
#       данных Google sheets
#
#  stop_update() - Останавливает обновление
#
#  update_sheet() - Основная функция обновления таблицы:
#       полуает таблицу c данными,
#       Получает курс доллара
#       отправляет данные на запись в БД в record_data()
#
#  get_sheet()
#       Авторизуется и получает данные из таблицы Google Sheets
#       Возвращает данные ввиде списка списков
#
#  record_data()
#       Проверяет дату последней отправки сообщений в телеграм
#       Записывает в базу данные с таблицы, добавляя колонку цены в рублях
#       Отдает на проверку даты из заявки если прошли, отдает на отправку
#       сообщений в телеграм
#  view_date()
#       Рендерит данные в шаблон Django
#
###########################################
import os
import threading
import time
from datetime import datetime

from dotenv import load_dotenv
import gspread
from django.conf import settings
from django.db import connection
from django.shortcuts import redirect, render

from .models import Sheet
from .utils import check_date, get_usd, send_telegram_message

load_dotenv()

STOP_UPDATE = False  # Флаг остановки демона потока
SENT_MESSAGE_TODAY = True  # Флаг отправки сообщения сегодня

LAST_MESSAGE_DATE = datetime(1900, 1, 1).date()


def start_update(request):
    """Запуск параллельного потока для обновления бд из Google Sheets"""
    global STOP_UPDATE
    if STOP_UPDATE:
        return redirect('view_data',)
    STOP_UPDATE = True
    t = threading.Thread(target=update_sheet, args=(), kwargs={})
    t.start()
    print(t)
    return redirect('view_data',)


def stop_update(request):
    """Остановка параллельного потока обновления бд из Google Sheets"""
    global STOP_UPDATE
    STOP_UPDATE = False
    return redirect('view_data',)


def update_sheet():
    """Обновление таблицы в БД"""
    while STOP_UPDATE:
        list_of_list = get_sheet()  # Получаем таблицу в виде списка списков
        usd_rate = get_usd()  # Получаем курс доллара
        record_data(list_of_list, usd_rate)  # Записываем данные в БД
        print("Обновлено ", datetime.now())  # Сервисное
        time.sleep(30)  # Время до следующего обновления в секундах


def get_sheet():
    """Получение таблицы из Google Sheets"""
    gc = gspread.service_account(filename=settings.KEY_FILE)  # Файл с данными для авторизации
    sh = gc.open_by_key(os.getenv('KEY_TABLE'))  # Открываем таблицу
    worksheet = sh.sheet1  # Выбираем нужный лист
    return worksheet.get_all_values()  # Возвращает ввиде списка списков


def record_data(list_of_list, usd_rate):
    """Модификация и запись данных из листа Google Sheets, в БД"""
    global SENT_MESSAGE_TODAY
    global LAST_MESSAGE_DATE
    if check_date(LAST_MESSAGE_DATE):  # Если текущая дата больше даты последней отправки сообщения
        SENT_MESSAGE_TODAY = True
    sent_message = False
    cursor = connection.cursor()
    cursor.execute("""DELETE FROM sheets_sheet""")  # Очищаем таблицу перед записью
    insert_table_sql = """INSERT INTO sheets_sheet \
        (num, reservation, price_usd, price_rub, delivery_date)
    VALUES (%s, %s, %s, %s, %s);"""  # SQL Запрос к БД
    for row in list_of_list[1:]:  # Перебираем построчно список
        prise_usd = float(row[2])*usd_rate  # Получаем стоимость заказа в рублях
        row.insert(3, prise_usd)  # Вставляем значене стоимости в строку
        cursor.execute(insert_table_sql, tuple(row))  # Вставляем строку в БД
        if SENT_MESSAGE_TODAY:  # Если СЕГОДНЯ не отправляли сообщения в Телеграм
            if check_date(datetime.strptime(row[4], '%d.%m.%Y').date()):  # Если дата в таблице прошла
                send_telegram_message(row[1], row[4])  # Отправляем соообщение в телеграм
                sent_message = True  # Устанавливаем флаг что сообщение отправлено
    connection.close()
    if sent_message:  # Если отправлялось в цикле
        LAST_MESSAGE_DATE = datetime.now().date()
        SENT_MESSAGE_TODAY = False  # Ставим запрет на отправку СЕГОДНЯ


def view_date(request):
    """Рендер таблицы в шаблоне """
    table = Sheet.objects.all()
    update = STOP_UPDATE
    return render(
        request, 'sheets/sheet.html', {'table': table, 'update': update}
    )
