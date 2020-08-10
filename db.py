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
    records = [
      Record.create(club='poxi', date=date(1977, 3, 1), balance=100),
      Record.create(club='7xl',  date=date(1988, 3, 1), balance=200)
    ]
    for record in records:
        record.save()

def main():
    db.connect()
    db.create_tables([Record])
    init()

if __name__ == '__main__':
    main()
