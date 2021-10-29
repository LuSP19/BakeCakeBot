from pathlib import Path

import json


def read_db():
    if Path('bakecake_db.json').is_file():
        with open('bakes.json', 'r') as db_file:
            try:
                db = json.load(db_file)
            except:
    	        return None
        return db


def get_user(user_id):
    db = read_db()
    if db:
        return db.get(user_id)
    return None


def get_last_order_id(users):
    last_order_id = 0
    for user_data in users.values():
        orders = user_data.get('orders')
        for order in orders:
            order_id = order['order_id']
            if last_order_id < order_id:
                last_order_id = order_id
    return last_order_id


def add_order(context_data):
    with open('bakes.json', 'r') as bakes_file:
        users = json.load(bakes_file)
    order_id = get_last_order_id(users) + 1
    user_id = str(context_data['user_id'])
    cost = count_cost(levels, form, topping, berries, decor,
        text, delivery_date, delivery_time)
    order = {
        'order_id': order_id,
        'levels': context_data['levels'],
        'form': context_data['form'],
        'topping': context_data['topping'],
        'berries': context_data['berries'],
        'decor': context_data['decor'],
        'text': context_data['text'],
        'comment': context_data['comments'],
        'delivery_date': context_data['delivery_date'],
        'delivery_time': context_data['delivery_time'],
        'status': 'заявка обрабатывается',
        'cost' : cost
    }
    users[user_id]['orders'].append(order)
    users[user_id].update({'orders': users[user_id]['orders']})
    with open('bakes.json', 'w') as bakes_file:
        json.dump(users, bakes_file, ensure_ascii=False, indent=2)


def add_user(context_data):
    user_id = str(context_data['user_id'])
    user = {
        'name': context_data['first_name'],
        'surname': context_data['last_name'],
        'phone': context_data['phone_number'],
        'address': context_data['user_address'],
        'orders': [],
    }
    with open('bakes.json', 'r') as bakes_file:
        users = json.load(bakes_file)
        if str(user_id) not in users.keys():
            users.update({ user_id: user })
    with open('bakes.json', 'w') as bakes_file:
        json.dump(users, bakes_file, ensure_ascii=False, indent=2)


def count_cost(levels, form, topping, berries, decor, text):
    cost = 0
    if levels[0] == '1':
        cost += 400
    elif levels[0] == '2':
        cost += 750
    else:
        cost += 1100
    
    if form == 'Круг':
        cost += 400
    elif form == 'Квадрат':
        cost += 600
    else:
        cost += 1000

    if topping == 'Белый соус':
        cost += 200
    elif topping == 'Карамельный сироп':
        cost += 180
    elif topping == 'Кленовый сироп':
        cost += 200
    elif topping == 'Клубничный сироп':
        cost += 300
    elif topping == 'Черничный сироп':
        cost += 350
    else:
        cost += 200

    if berries == 'Ежевика':
        cost += 400
    elif berries == 'Малина':
        cost += 300
    elif berries == 'Голубика':
        cost += 450
    elif berries == 'Клубника':
        cost += 500

    if decor == 'Фисташки':
        cost += 300
    elif decor == 'Безе':
        cost += 400
    elif decor == 'Фундук':
        cost += 350
    elif decor == 'Пекан':
        cost += 300
    elif decor == 'Маршмеллоу':
        cost += 200
    elif decor == 'Марципан':
        cost += 280

    if text != 'Пропустить':
        cost += 500

    return str(cost)