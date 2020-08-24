# from datetime import date
# import datetime
from datetime import datetime, timedelta
from peewee import *
import random

# this will create/refer-to poker.db file in cwd
db = SqliteDatabase('poker.db')


# model is a table
class Record(Model):
    club = CharField()
    type = CharField()
    date = DateField(default=datetime.now().date())
    profit = IntegerField(default=0)
    balance = IntegerField(default=0)

    class Meta:
        database = db  # This model uses the "poker.db" database.


class Deposit(Model):
    club = CharField()
    type = CharField()
    date = DateField(default=datetime.now().date())
    amount = IntegerField()

    class Meta:
        database = db  # This model uses the "poker.db" database.


class Withdraw(Model):
    club = CharField()
    type = CharField()
    date = DateField(default=datetime.now().date())
    amount = IntegerField()

    class Meta:
        database = db  # This model uses the "poker.db" database.


# inject file of real records that created by the show-records.sh script
def inject_records(file):
    records = open(file).readlines()
    for record in records:
        # example: ['9', 'pokernuts', 'update', '2020-08-07 21:54:55.149959', '0','1001']
        r = record.split('|')
        r_club = r[1]
        r_type = r[2]
        r_date = datetime.strptime(r[3], '%Y-%m-%d')
        r_profit = r[4]
        r_balance = r[5]
        r = Record.create(club=r_club, type=r_type, date=r_date, profit=r_profit, balance=r_balance)
        r.save()

# inject deposits file of real records that created by the show-records-deposits.sh script
def inject_deposits(file):
    deposits = open(file).readlines()
    for deposit in deposits:
        # example: ['9', 'pokernuts', 'deposit', '2020-08-07', '2000']
        d = deposit.split('|')
        d_club = d[1]
        d_type = d[2]
        d_date = datetime.strptime(d[3], '%Y-%m-%d')
        d_amount = d[4]
        d = Deposit.create(club=d_club, type=d_type, date=d_date, amount=d_amount)
        d.save()

# inject withdraws file of real records that created by the show-records-withdraws.sh script
def inject_withdraws(file):
    withdraws = open(file).readlines()
    for withdraw in withdraws:
        # example: ['9', 'pokernuts', 'withdraw', '2020-08-07', '2000']
        w = withdraw.split('|')
        w_club = w[1]
        w_type = w[2]
        w_date = datetime.strptime(w[3], '%Y-%m-%d')
        w_amount = w[4]
        w = Withdraw.create(club=w_club, type=w_type, date=w_date, amount=w_amount)
        w.save()



def inject_test_records():
    init_balance = {'ultimate':   generate_series(500,  'win'),
                    'poker247':   generate_series(500,  'win'),
                    'lionking':   generate_series(800,  'win'),
                    'monkeys':    generate_series(500,  'lose'),
                    'dragonball': generate_series(500,  'random'),
                    'academy':    generate_series(500,  'random'),
                    'poxi':       generate_series(1000, 'lose'),
                    '7xl':        generate_series(100,  'lose'),
                    'pokernuts':  generate_series(1000, 'random')
                    }
    for i in range(9, -1, -1):
        for club, balances in init_balance.items():
            r = Record.create(club=club, type='init', date=datetime.now() - timedelta(days=i), balance=balances[9 - i])
            r.save()

def recreate_db():
    """Recreating db from scratch

        use this ONLY for recreate db from scratch.
        it will inject records from OLD__db-init file

        before use this, make sure to execute ./db-backup.sh
        to save the current records and inject them upon start.
       """
    db.create_tables([Record, Deposit, Withdraw])
    inject_records('db-init-records')
    inject_deposits('db-init-deposits')
    inject_withdraws('db-init-withdraws')
    #inject_test_records()


def init(recreate=False):
    db.connect()
    if recreate:
        recreate_db()


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
    """Initializing local Sqlite DB.
        This file SHOULD NOT run directly, only in case DB should be re-init.
       """
    print("initializing dataset")
    init(recreate=False)
