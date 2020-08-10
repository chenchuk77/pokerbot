from datetime import date
from peewee import *

# this will create poker.db file in cwd
db = SqliteDatabase('poker.db')

# model is a table
class Record(Model):
    club = CharField()
    date = DateField()
    balance = IntegerField()

    class Meta:
        database = db # This model uses the "poker.db" database.

def init():
    db.connect()
    db.create_tables([Record])
    records = [
        Record.create(club='ultimate',    date=date(1977, 3, 1), balance=394),
        Record.create(club='poker-24-7',  date=date(1988, 3, 1), balance=1093),
        Record.create(club='lionking',    date=date(1988, 3, 1), balance=1388),
        Record.create(club='monkeys',     date=date(1988, 3, 1), balance=881),
        Record.create(club='dragon-ball', date=date(1988, 3, 1), balance=320),
        Record.create(club='rounders',    date=date(1988, 3, 1), balance=0),
        Record.create(club='poxi',        date=date(1988, 3, 1), balance=228),
        Record.create(club='7xl',         date=date(1988, 3, 1), balance=938),
        Record.create(club='pokernuts',   date=date(1988, 3, 1), balance=100)
    ]
    for record in records:
        record.save()
