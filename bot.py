import logging

from environs import Env
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    Filters,
    CommandHandler,
    MessageHandler,
)

from bot_helpers import get_user, add_user


logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
logger = logging.getLogger(__name__)


def start(update, _):
    user = get_user(update.message.from_user.id)
    print('User ID:', update.message.from_user.id)
    if get_user(user):
        if user.get('orders'):
            reply_keyboard = [['Собрать торт', 'Заказы', 'Отклонить']]
        else:
            reply_keyboard = [['Собрать торт', 'Отклонить']]
    else:
        reply_keyboard = [['Регистрация', 'Отклонить']]

        update.message.reply_text(
                'Перед использованием бота нужно зарегистрироваться',
                reply_markup=ReplyKeyboardMarkup(reply_keyboard)
            )


def register(update, _):
    reply_keyboard = [['Принять', 'Отклонить']]

    with open('personal_data.pdf', 'rb') as pd_file:
        update.message.reply_document(pd_file)

    update.message.reply_text(
            'Подтвердите солгасие на обработку персональных данных',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard)
        )


def accept(update, _):
    phone_request_button = KeyboardButton('Передать контакт', request_contact=True)
    reply_keyboard = [[phone_request_button, 'Ввести номер', 'Отклонить']]

    update.message.reply_text(
        'Изготовление тортов на заказ.',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            input_field_placeholder='+7-999-9999',
        )
    )


def phone(update, _):
    name = update.message.from_user.first_name
    surname = update.message.from_user.last_name
    if update.message.contact:
        phone_number = update.message.contact.phone_number
    else:
        phone_number = update.message.text
    add_user(name, surname, phone)
    reply_keyboard = [['Собрать торт']]
    user = update.message.from_user
    logger.info('Match %s with %s', user, phone_number)
    update.message.reply_text('Вы успешно зарегистрированы!')
    update.message.reply_text(
        'Выберите ингредиенты, форму, основу, надпись, '
        'а мы привезем готовый торт к вашему празднику.',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard),
    )


def cancel(update, _):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Всего доброго!',
        reply_markup=ReplyKeyboardRemove(),
    )


def main():
    env = Env()
    env.read_env()

    updater = Updater(token=env('TG_BOT_TOKEN'))
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    register_handler = MessageHandler(Filters.regex('Регистрация'), register)
    accept_handler = MessageHandler(Filters.regex('Принять'), accept)
    phone_handler = MessageHandler(
        Filters.regex('^\+?\d{1,3}?( |-)?\d{3}( |-)?\d{3}( |-)?\d{2}( |-)?\d{2}$'),
        phone,
    )
    cancel_handler = MessageHandler(Filters.text('Отклонить'), cancel)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(register_handler)
    dispatcher.add_handler(accept_handler)
    dispatcher.add_handler(phone_handler)
    dispatcher.add_handler(cancel_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
