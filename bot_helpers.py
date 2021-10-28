import json


def get_user(user_id):
    return None

def add_user(name, surname, phone, user_id):
    user = { 'name': name,
             'surname': surname,
             'phone': phone,
             'orders': []}
    with open('bakes.json', 'r') as bakes_file:
        users = json.load(bakes_file)
        if str(user_id) not in users.keys():
            users.update({ str(user_id): user })
    with open('bakes.json', 'w') as bakes_file:
        json.dump(users, bakes_file, ensure_ascii=False)


