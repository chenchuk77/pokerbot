# from datetime import date
# import datetime
from datetime import datetime, timedelta
from peewee import *
import random

# this will create poker.db file in cwd
db = SqliteDatabase('poker.db')


# model is a table
class Record(Model):
    club = CharField()
    type = CharField()
    # date = DateField()
    date = DateTimeField(default=datetime.now)
    balance = IntegerField()

    class Meta:
        database = db  # This model uses the "poker.db" database.


def init():
    db.connect()
    db.create_tables([Record])
    init_balance = {'ultimate':   generate_series(500,  'win'),
                    'poker247':   generate_series(500,  'win'),
                    'lionking':   generate_series(800,  'win'),
                    'monkeys':    generate_series(500,  'lose'),
                    'dragonball': generate_series(500,  'random'),
                    'rounders':   generate_series(000,  'zeros'),
                    'poxi':       generate_series(1000, 'lose'),
                    '7xl':        generate_series(100,  'lose'),
                    'pokernuts':  generate_series(1000, 'random')
                    }
    for i in range(9, -1, -1):
        for club, balances in init_balance.items():
            r = Record.create(club=club, type='init', date=datetime.now() - timedelta(days=i), balance=balances[9 - i])
            r.save()


def generate_series(start_value, type='random'):
    if type not in ['win', 'lose', 'random']:
        return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    factor = 0.5
    if type == 'win': factor = 0.25
    if type == 'lose': factor = 0.75
    rv = []
    last = start_value
    for i in range(10):
        x = random.random()
        if x > factor:
            new_value = last + random.randrange(1, 100)
        elif x <= factor:
            new_value = last - random.randrange(1, 100)
            if new_value < 0:
                new_value = 0
        last = new_value
        rv.append(new_value)
    return rv


# init db if this script invoked manually
if __name__ == '__main__':
    print("initializing dataset")
    init()
