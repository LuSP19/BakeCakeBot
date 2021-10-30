import logging

from environs import Env
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    Filters,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
)


from bot_helpers import get_user, add_user, add_order, count_cost, get_orders

logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
logger = logging.getLogger(__name__)


REGISTER, CONTACT_CONFIRM, PHONE, ADDRESS = range(4)

SET_CAKE_CONFIRM, LEVELS, FORM, TOPPING, BERRIES, DECOR, TEXT, INPUT_TEXT = range(4, 12)

COMMENTS, DELIVERY_DATE, DELIVERY_TIME, PROMOCODE, CONFIRM, COMPLETE = range(12, 18)


def start(update, context):
    user = get_user(str(update.message.from_user.id))
    context.user_data['user_id'] = update.message.from_user.id
    if user:
        reply_text = 'Приветствую! Вы в главном меню.'
        main_menu(update, context, reply_text)
    else:
        update.message.reply_text(
            'Подтвердите согласие на обработку персональных данных.\n'
            'Ознакомьтесь с условиями по ссылке -тут будет ссылка на PDF-',
            reply_markup=ReplyKeyboardMarkup(
                [['Принять', 'Отклонить']],
                resize_keyboard=True,
            ),
        )
    return REGISTER


def main_menu(update, context, reply_text='Вы в главном меню'):
    update.message.reply_text(
        reply_text,
        reply_markup=ReplyKeyboardMarkup(
            [['Собрать торт', 'Мои заказы']],
            resize_keyboard=True,
        ),
    )
    return REGISTER


def phone(update, context):
    # Начало ветки "Контактные данные"
    if context.user_data.get('user_address'):
        del context.user_data['user_address']
    elif context.user_data.get('phone_number'):
        del context.user_data['phone_number']

    phone_request_button = KeyboardButton('Передать контакт', request_contact=True)
    update.message.reply_text(
        'Введите контактный номер телефона',
        reply_markup=ReplyKeyboardMarkup(
            [[phone_request_button, 'Назад']],
            resize_keyboard=True,
            input_field_placeholder='8-999-999-9999',
        ),
    )
    return PHONE


def correct_phone(update, context):
    if update.message.text != 'Назад':
        if update.message.contact:
            phone_number = update.message.contact.phone_number
        else:
            phone_number = update.message.text
        context.user_data['phone_number'] = phone_number
        logger.info('User %s points phone_number %s', update.message.from_user.id, phone_number)
    update.message.reply_text(
        'Введите адрес доставки',
        reply_markup=ReplyKeyboardMarkup(
            [['Назад']],
            resize_keyboard=True,
            input_field_placeholder='ул. Пушкина, д. Колотушкина',
        ),
    )
    return ADDRESS


def incorrect_phone(update, context):
    update.message.reply_text(
        'Пожалуйста, введите номер в формате: "8" и 10 цифр'
    )
    return PHONE


def success_address(update, context):
    user_address = update.message.text
    context.user_data['user_address'] = user_address
    phone_number = context.user_data['phone_number']
    logger.info('User %s points address %s', update.message.from_user.id, user_address)

    update.message.reply_text(
        'Проверьте введенные данные.\n'
        f'Номер телефона: {phone_number}\n'
        f'Адрес: {user_address}',
        reply_markup=ReplyKeyboardMarkup(
            [['Все верно', 'Назад']],
            resize_keyboard=True,
        )
    )
    return CONTACT_CONFIRM


def reg_confirm(update, context):
    user = update.message.from_user
    context.user_data['user_id'] = user.id
    context.user_data['first_name'] = user.first_name
    context.user_data['last_name'] = user.last_name
    phone_number = context.user_data['phone_number']
    user_address = context.user_data['user_address']

    add_user(context.user_data)

    logger.info('Added %s with address %s and phone number %s', user, user_address, phone_number)

    reply_text = 'Поздравляем! Теперь вы можете выбрать компоненты торта.'
    main_menu(update, context, reply_text)
    return REGISTER


def levels(update, context):
    # Начало ветки "Собрать торт"
    if context.user_data.get('levels'):
        del context.user_data['levels']
    elif context.user_data.get('form'):
        del context.user_data['form']
    elif context.user_data.get('topping'):
        del context.user_data['topping']
    elif context.user_data.get('berries'):
        del context.user_data['berries']
    elif context.user_data.get('decor'):
        del context.user_data['decor']
    elif context.user_data.get('text'):
        del context.user_data['text']

    reply_keyboard = [
        ['1 уровень', '2 уровня', '3 уровня'],
        ['Назад', 'Главное меню'],
    ]
    update.message.reply_text(
        'Количество уровней',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            resize_keyboard=True,
        ),
    )
    return LEVELS


def form(update, context):
    if update.message.text != 'Назад':
        context.user_data['levels'] = update.message.text
    reply_keyboard = [
        ['Квадрат', 'Круг', 'Прямоугольник'],
        ['Назад', 'Главное меню'],
    ]
    update.message.reply_text(
        'Форма',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            resize_keyboard=True,
        ),
    )
    return FORM
    

def topping(update, context):
    if update.message.text != 'Назад':
        context.user_data['form'] = update.message.text
    reply_keyboard = [
        ['Без топпинга', 'Белый соус', 'Карамельный сироп'],
        ['Кленовый сироп', 'Клубничный сироп'], 
        ['Черничный сироп', 'Молочный шоколад'],
        ['Назад', 'Главное меню'],
    ]
    update.message.reply_text(
        'Топпинг',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            resize_keyboard=True,
        ),
    )
    return TOPPING


def berries(update, context):
    if update.message.text != 'Назад':
        context.user_data['topping'] = update.message.text
    reply_keyboard = [
        ['Ежевика', 'Малина'],
        ['Голубика', 'Клубника'],
        ['Пропустить'],
        ['Назад', 'Главное меню'],
    ]
    update.message.reply_text(
        'Ягоды',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            resize_keyboard=True,
        ),
    )
    return BERRIES


def decor(update, context):
    if update.message.text != 'Назад':
        context.user_data['berries'] = update.message.text
    reply_keyboard = [
        ['Фисташки', 'Безе', 'Фундук'],
        ['Пекан', 'Маршмеллоу', 'Марципан'],
        ['Пропустить'],
        ['Назад', 'Главное меню'],
    ]
    update.message.reply_text(
        'Декор',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            resize_keyboard=True,
        ),
    )
    return DECOR


def text(update, context):
    if update.message.text != 'Назад':
        context.user_data['decor'] = update.message.text
    reply_keyboard = [
        ['Добавить надпись', 'Пропустить'],
        ['Назад', 'Главное меню'],
    ]
    update.message.reply_text(
        'Мы можем разместить на торте любую надпись, например: «С днем рождения!»',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            resize_keyboard=True,
        ),
    )
    return TEXT


def input_text(update, context):
    reply_keyboard = [
        ['Пропустить'],
        ['Назад', 'Главное меню'],
    ]
    update.message.reply_text(
        'Введите надпись',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            resize_keyboard=True,
            input_field_placeholder='С Днем рождения!',
        ),
    )
    return INPUT_TEXT


def cake_confirm(update, context):
    context.user_data['text'] = update.message.text
    levels = context.user_data['levels']
    form = context.user_data['form']
    topping = context.user_data['topping']
    berries = context.user_data['berries']
    decor = context.user_data['decor']
    text = context.user_data['text']

    reply_keyboard = [
        ['Все верно', 'Изменить'],
        ['Назад', 'Главное меню'],
    ]
    update.message.reply_text(
        f'Проверьте введенные данные.\n'
        f'Количество уровней: {levels}\n'
        f'Форма: {form}\n'
        f'Топпинг: {topping}\n'
        f'Ягоды: {berries}\n'
        f'Декор: {decor}\n'
        f'Текст: {text}\n',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            resize_keyboard=True,
        ),
    )
    return SET_CAKE_CONFIRM


def comments(update, context):
    # Начало ветки "Дополнительные условия заказа"
    if context.user_data.get('comments'):
        del context.user_data['comments']
    if context.user_data.get('delivery_date'):
        del context.user_data['delivery_date']
    if context.user_data.get('delivery_time'):
        del context.user_data['delivery_time']

    reply_keyboard = [['Пропустить','Начать собирать заново']]
    update.message.reply_text(
        'Можете оставить комментарий к заказу',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            resize_keyboard=True,
        ),
    )
    return COMMENTS


def delivery_date(update, context):
    context.user_data['comments'] = update.message.text
    reply_keyboard = [['Начать собирать заново']]
    update.message.reply_text(
        'Укажите дату доставки',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            resize_keyboard=True,
        ),
    )
    return DELIVERY_DATE


def delivery_time(update, context):
    context.user_data['delivery_date'] = update.message.text
    reply_keyboard = [['Начать собирать заново']]
    update.message.reply_text(
        'Укажите время доставки',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            resize_keyboard=True,
        ),
    )
    return DELIVERY_TIME


def promocode(update, context):
    context.user_data['delivery_time'] = update.message.text
    reply_keyboard = [['Пропустить', 'Начать собирать заново']]
    update.message.reply_text(
        'Введите промокод',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            resize_keyboard=True,
        ),
    )
    return PROMOCODE


def order_details(update, context):
    # Начало ветки "Проверка и отправка заказа"
    context.user_data['promocode'] = update.message.text
    reply_keyboard = [['Заказать торт', 'Начать собирать заново', 'Изменить условия']]
    update.message.reply_text(
        'Все готово! Нажмите "Заказать торт", чтобы увидеть стоимость.',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            resize_keyboard=True,
        ),
    )
    return CONFIRM


def order_confirm(update, context):
    for key, value in context.user_data.items():
        logger.info('%s - %s', key, value)
    cost = count_cost(context.user_data['levels'], context.user_data['form'],
                      context.user_data['topping'], context.user_data['berries'],
                      context.user_data['decor'], context.user_data['text'])
    context.user_data['cost'] = cost
    add_order(context.user_data)
    reply_keyboard = [['Отправить заказ', 'Начать собирать заново', 'Изменить условия']]
    update.message.reply_text(
        f'Стоимость торта {cost}',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            resize_keyboard=True,
        ),
    )
    return COMPLETE


def complete_order(update, context):
    user = update.message.from_user
    logger.info("User %s completed order.", user.first_name)
    update.message.reply_text(
        'Заказ отправлен! Ожидайте звонка оператора!',
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


def decline(update, _):
    logger.info("Trying to decline.")
    reply_keyboard = [['Принять', 'Отклонить']]
    update.message.reply_text(
            'К сожалению, без согласия на обработку ПД вы не сможете сделать заказ\n\n'
            'Подтвердите солгасие на обработку персональных данных.\n'
            'Ознакомьтесь с условиями по ссылке -тут будет ссылка на PDF-',
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard,
                resize_keyboard=True,
            )
        )
    return REGISTER


def show_orders(update, context):
    reply_markup=ReplyKeyboardMarkup(
        [['Собрать торт', 'Мои заказы']],
        resize_keyboard=True,
    )
    user = get_user(str(context.user_data['user_id']))
    if user.get('orders'):
        update.message.reply_text('На данный момент у вас такие заказы:')
        for order in get_orders(context.user_data['user_id']):
            update.message.reply_text(
                '\n'.join(order),
                reply_markup=reply_markup,
            )
    else:
        update.message.reply_text(
            'У вас еще не было заказов.',
            reply_markup=reply_markup,
        )
    return REGISTER


def cancel(update, _):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Всего доброго!',
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


def main():
    env = Env()
    env.read_env()

    DEBUG = env.bool('DEBUG', False)

    TG_BOT_TOKEN = env('TG_BOT_TOKEN_WORK') if DEBUG else env('TG_BOT_TOKEN')

    updater = Updater(token=TG_BOT_TOKEN)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            REGISTER: [
                MessageHandler(Filters.regex('^Принять$'), phone),
                MessageHandler(Filters.regex('^Отклонить$'), decline),
                MessageHandler(Filters.regex('^Собрать торт$'), levels),
                MessageHandler(Filters.regex('^Мои заказы$'), show_orders),
            ],
            CONTACT_CONFIRM: [
                MessageHandler(Filters.regex('^Изменить$'), phone),
                MessageHandler(Filters.regex('^Все верно$'), reg_confirm),
                MessageHandler(Filters.regex('^Назад$'), correct_phone),
            ],
            PHONE: [
                MessageHandler(Filters.contact, correct_phone),
                MessageHandler(
                    Filters.regex('^\+?\d{1,3}?( |-)?\d{3}( |-)?\d{3}( |-)?\d{2}( |-)?\d{2}$'),
                    correct_phone,
                ),
                MessageHandler(Filters.regex('^Назад$'), start),
                MessageHandler(Filters.text, incorrect_phone),
            ],
            ADDRESS: [
                MessageHandler(Filters.regex('^Назад$'), phone),
                MessageHandler(Filters.text, success_address),
            ],
            SET_CAKE_CONFIRM: [
                MessageHandler(Filters.regex('^Назад$'), text),
                MessageHandler(Filters.regex('^Главное меню$'), main_menu),
                MessageHandler(Filters.regex('^Собрать торт$|^Изменить$'), levels),
                MessageHandler(Filters.regex('^Все верно$'), comments),
            ],
            LEVELS: [
                MessageHandler(Filters.regex('^Назад$|^Главное меню$'), main_menu),
                MessageHandler(Filters.regex('^1 уровень$|^2 уровня$|^3 уровня$'), form),
            ],
            FORM: [
                MessageHandler(Filters.regex('^Назад$'), levels),
                MessageHandler(Filters.regex('^Главное меню$'), main_menu),
                MessageHandler(Filters.regex('^Квадрат$|^Круг$|^Прямоугольник$'), topping),
                MessageHandler(Filters.regex('^Начать собирать заново$'), levels),
            ],
            TOPPING: [
                MessageHandler(Filters.regex('^Назад$'), form),
                MessageHandler(Filters.regex('^Главное меню$'), main_menu),
                MessageHandler(Filters.regex('^Без топпинга$|^Белый соус$|^Карамельный сироп$'), berries),
                MessageHandler(Filters.regex('^Кленовый сироп$|^Клубничный сироп$'), berries),
                MessageHandler(Filters.regex('^Черничный сироп$|^Молочный шоколад$'), berries),
                MessageHandler(Filters.regex('^Начать собирать заново$'), levels),
            ],
            BERRIES: [
                MessageHandler(Filters.regex('^Назад$'), topping),
                MessageHandler(Filters.regex('^Главное меню$'), main_menu),
                MessageHandler(Filters.regex('^Ежевика$|^Малина$|^Голубика$'), decor),
                MessageHandler(Filters.regex('^Клубника$|^Пропустить$'), decor),
                MessageHandler(Filters.regex('^Начать собирать заново$'), levels),
            ],
            DECOR: [
                MessageHandler(Filters.regex('^Назад$'), berries),
                MessageHandler(Filters.regex('^Главное меню$'), main_menu),
                MessageHandler(Filters.regex('^Фисташки$|^Безе$|^Фундук$'), text),
                MessageHandler(Filters.regex('^Пекан$|^Маршмеллоу$|^Марципан$|^Пропустить$'), text),
                MessageHandler(Filters.regex('^Начать собирать заново$'), levels),
            ],
            TEXT: [
                MessageHandler(Filters.regex('^Назад$'), decor),
                MessageHandler(Filters.regex('^Главное меню$'), main_menu),
                MessageHandler(Filters.regex('^Добавить надпись$'), input_text),
                MessageHandler(Filters.regex('^Пропустить$'), cake_confirm),
                MessageHandler(Filters.regex('^Начать собирать заново$'), levels),
            ],
            INPUT_TEXT: [
                MessageHandler(Filters.regex('^Назад$'), decor),
                MessageHandler(Filters.regex('^Главное меню$'), main_menu),
                MessageHandler(Filters.text, cake_confirm),
            ],
            COMMENTS: [
                MessageHandler(Filters.regex('^Начать собирать заново$'), levels),
                MessageHandler(Filters.text, delivery_date),
            ],
            DELIVERY_DATE: [
                MessageHandler(Filters.regex('^Начать собирать заново$'), levels),
                MessageHandler(Filters.text, delivery_time),
            ],
            DELIVERY_TIME: [
                MessageHandler(Filters.regex('^Начать собирать заново$'), levels),
                MessageHandler(Filters.text, promocode),
            ],
            PROMOCODE: [
                MessageHandler(Filters.regex('^Начать собирать заново$'), levels),
                MessageHandler(Filters.text | Filters.regex('^Пропустить$'), order_details),
            ],
            CONFIRM: [
                MessageHandler(Filters.regex('^Заказать торт$'), order_confirm),
                MessageHandler(Filters.regex('^Изменить условия$'), comments),
                MessageHandler(Filters.regex('^Начать собирать заново$'), levels),
            ],
            COMPLETE: [
                MessageHandler(Filters.regex('^Отправить заказ$'), complete_order),
                MessageHandler(Filters.regex('^Изменить условия$'), comments),
                MessageHandler(Filters.regex('^Начать собирать заново$'), levels),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        name="my_conversation",
        allow_reentry=True
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
