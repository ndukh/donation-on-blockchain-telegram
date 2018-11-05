#  encoding: utf-8
# based on https://habr.com/post/316666/ by @saluev

import configparser

import base58
from static import get, MyLogger
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater

config = configparser.ConfigParser()
config.read('config.ini', 'utf-8')

BOT_TOKEN = config.get('bot', 'BOT_TOKEN')

LOGGING_URL = config.get('logging', 'SERVER')
LOGGING_PORT = int(config.get('logging', 'PORT'))

START_TEXT = config.get('text', 'START_TEXT')
HELP_TEXT = config.get('text', 'HELP_TEXT')
BASE58CHECK_TEXT = config.get('text', 'BASE58CHECK_TEXT')
SMALL_LEN_TEXT = config.get('text', 'SMALL_LEN_TEXT')
ERROR_TEXT = config.get('text', 'ERROR_TEXT')
WRONG_VALUE_TEXT = config.get('text', 'WRONG_VALUE_TEXT')
SUCCESS_TEXT = config.get('text', 'SUCCESS_TEXT')
COMMANDS_TEXT = config.get('text', 'COMMANDS_TEXT')
EXAMPLE_ID = config.get('text', 'EXAMPLE_ID')

ID_LEN = int(config.get('settings', 'ID_LEN'))
SERVER = config.get('settings', 'SERVER')
GET_INFO = config.get('settings', 'GET_INFO')
ADD_DONATION = config.get('settings', 'ADD_DONATION')
ADD_TRANSACTION = config.get('settings', 'ADD_TRANSACTION')

logger = MyLogger(LOGGING_URL, LOGGING_PORT)


def start(bot, update):
    # подробнее об объекте update: https://core.telegram.org/bots/api#update
    bot.sendMessage(chat_id=update.message.chat_id, text=START_TEXT + ' ' + COMMANDS_TEXT)


def help(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text=HELP_TEXT + ' ' + COMMANDS_TEXT)


def success(bot, update, donation_id):
    bot.sendMessage(chat_id=update.message.chat_id, text=SUCCESS_TEXT)
    donation_steps = request_donation_steps(donation_id)
    for step in donation_steps:
        bot.sendMessage(chat_id=update.message.chat_id, text=step)


def wrong_value(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text=WRONG_VALUE_TEXT)


def error(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text=ERROR_TEXT)


def small_len_error(bot, update):
    error(bot, update)
    bot.sendMessage(chat_id=update.message.chat_id, text=SMALL_LEN_TEXT)


def base58check_error(bot, update):
    error(bot, update)
    bot.sendMessage(chat_id=update.message.chat_id, text=BASE58CHECK_TEXT)
    bot.sendMessage(chat_id=update.message.chat_id, text=EXAMPLE_ID)


def handle_message(bot, update):
    message = update.message.text
    if len(message) == ID_LEN:
        try:
            success(bot, update, base58.b58decode_check(bytes(message, encoding='utf-8')).decode('utf-8'))
        except ValueError as ve:
            logger.debug(message, ve)
            base58check_error(bot, update)
            logger.debug(message, ve)
            wrong_value(bot, update)
        except Exception as exc:
            logger.error(message, exc)
            error(bot, update)
    else:
        small_len_error(bot, update)


def request_donation_steps(donation_id):
    url = SERVER + '/' + GET_INFO
    params = {'donateId': donation_id}
    donation_info = get(url, params)
    result = donation_info['result']
    logger.info(f'donation_info[\'result\']={result}, donation_id={donation_id}')
    donation_track = donation_info['output']
    if len(donation_track) == 0:
        messages = ['Пока что информации по этому номеру нет.']
    else:
        donation_message = 'Дата пожертвования: {}\n' \
                           'Назначение пожертвования: {}\n' \
                           'Сумма пожертвования: {}\n' \
                           'Израсходовано: {}\n' \
                           'Остаток: {}'.format(donation_track[0]['timeStamp'],
                                                donation_track[0]['description'],
                                                donation_track[0]['amount'],
                                                donation_track[0]['amount'] - donation_track[-1]['balance'],
                                                donation_track[-1]['balance'])
        messages = [donation_message]

        for i, transaction in enumerate(donation_track):
            message = '{}. Дата перевода: {}\n' \
                      'Сумма: {}\n ' \
                      'Описание платежа: {}\n ' \
                      'Получатель: {}\n' \
                      'ИНН получателя: {}'.format(i + 1,
                                                  transaction['transitionTime'],
                                                  transaction['amount'],
                                                  transaction['purpose'],
                                                  transaction['organizationName'],
                                                  transaction['taxId'])
            messages.append(message)
    return messages


updater = Updater(token=BOT_TOKEN)  # тут токен, который выдал вам Ботский Отец!

start_handler = CommandHandler('start', start)  # этот обработчик реагирует только на команду /start
help_handler = CommandHandler('help', help)

message_handler = MessageHandler(Filters.text, handle_message)

updater.dispatcher.add_handler(start_handler)  # регистрируем в госреестре обработчиков
updater.dispatcher.add_handler(help_handler)
updater.dispatcher.add_handler(message_handler)
updater.start_polling()  # поехали!
