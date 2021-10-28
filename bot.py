import logging

from environs import Env
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    Filters,
    CommandHandler,
    MessageHandler,
)

from bot_helpers import get_user, add_user, add_address


logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
logger = logging.getLogger(__name__)


def start(update, _):
    user = get_user(str(update.message.from_user.id))
    if user:
        if user.get('orders'):
            reply_keyboard = [['Собрать торт', 'Заказы']]
            reply_text = 'Соберите торт или посмотрите свои заказы'
        else:
            reply_keyboard = [['Собрать торт']]
            reply_text = 'Соберите торт'
    else:
        reply_keyboard = [['Принять', 'Отклонить']]
        reply_text = (
            'Подтвердите солгасие на обработку персональных данных.\n'
            'Ознакомьтесь с условиями по ссылке -тут будет ссылка на PDF-'
        )
        
    update.message.reply_text(
        reply_text,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard),
    )


def accept(update, _):
    phone_request_button = KeyboardButton('Передать контакт', request_contact=True)
    reply_keyboard = [['Введите контактный номер телефона']]

    update.message.reply_text(
        'Изготовление тортов на заказ.',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            input_field_placeholder='+7-999-999-99-99',
        )
    )


def phone(update, _):
    user_id = str(update.message.from_user.id)
    name = update.message.from_user.first_name
    surname = update.message.from_user.last_name
    phone_number = update.message.text
    add_user(user_id, name, surname, phone_number)
    reply_keyboard = [['Введите адрес доставки']]
    user = update.message.from_user
    logger.info('Match %s with %s', user, phone_number)
    update.message.reply_text(
        'Изготовление тортов на заказ.',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard),
    )


def contact(update, _):
    user_id = str(update.message.from_user.id)
    name = update.message.from_user.first_name
    surname = update.message.from_user.last_name
    phone_number = update.message.contact.phone_number
    add_user(user_id, name, surname, phone_number)
    reply_keyboard = [['Введите адрес доставки']]
    user = update.message.from_user
    logger.info('Match %s with %s', user, phone_number)
    update.message.reply_text(
        'Изготовление тортов на заказ.',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard),
    )


def address(update, _):
    print('In address')
    user_id = str(update.message.from_user.id)
    address = update.message.text
    print('address', address)
    add_address(user_id, address)
    reply_keyboard = [['Собрать торт']]
    user = update.message.from_user
    logger.info('Match %s with %s', user, address)
    update.message.reply_text('Вы успешно зарегистрированы!')
    update.message.reply_text(
        'Выберите ингредиенты, форму, основу, надпись, '
        'а мы привезем готовый торт к вашему празднику.',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard),
    )


def cancel(update, _):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    reply_keyboard = [['Принять', 'Отклонить']]
    update.message.reply_text(
            'К сожалению, без согласия на обработку ПД вы не сможете сделать заказ\n\n'
            'Подтвердите солгасие на обработку персональных данных.\n'
            'Ознакомьтесь с условиями по ссылке -тут будет ссылка на PDF-',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard)
        )


def main():
    env = Env()
    env.read_env()

    updater = Updater(token=env('TG_BOT_TOKEN'))
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    accept_handler = MessageHandler(Filters.regex('Принять'), accept)
    phone_handler = MessageHandler(
        Filters.regex('^\+?\d{1,3}?( |-)?\d{3}( |-)?\d{3}( |-)?\d{2}( |-)?\d{2}$'),
        phone,
    )
#    contact_handler = MessageHandler(Filters.contact, accept)
    address_handler = MessageHandler(Filters.regex('^.{8,}$'), address)
    cancel_handler = MessageHandler(Filters.text('Отклонить'), cancel)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(accept_handler)
    dispatcher.add_handler(phone_handler)
#    dispatcher.add_handler(contact_handler)
    dispatcher.add_handler(address_handler)
    dispatcher.add_handler(cancel_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
