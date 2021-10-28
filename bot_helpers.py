from pathlib import Path

import json


def read_db():
    if Path('bakecake_db.json').is_file():
        with open('bakecake_db.json', 'r', encoding='utf-8') as db_file:
            try:
                db = json.load(db_file)
            except:
    	        return None
        return db


def write_db(db):
    with open("bakecake_db.json", "w", encoding='utf-8') as db_file:
        json.dump(db, db_file, ensure_ascii=False, indent=2)


def get_user(user_id):
    db = read_db()
    if db:
        return db.get(user_id)
    return None


def add_user(user_id, name, surname, phone):
    db = read_db()
    if not db:
        db = dict()
    db[user_id] = {
        'name': name,
        'surname': surname,
        'phone': phone,
        }
    write_db(db)


def add_address(user_id, address):
    db = read_db()
    db[user_id]['address'] = address
    write_db(db)
