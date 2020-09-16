#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

# local python resources
import credentials
import db
from datetime import datetime, timedelta, time
import matplotlib.pyplot as plt
import numpy as np

from db import Record
from prettytable import PrettyTable

import logging
from telegram import ParseMode
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, JobQueue)

def tester_generate_graph(club_name):
    dates = []
    balances = []
    query = Record.select().where(Record.club == club_name).order_by(Record.date).execute()
    club_records = list(query)
    for record in club_records:
        dates.append(record.date)
        balances.append(record.balance)
    x = np.array(dates)
    y = np.array(balances)
    plt.plot(x, y)
    # plt.show()
    plt.savefig('graph-{}.png'.format(club_name))


def tester_generate_graph(club_name, until, days_count):
    since = until - timedelta(days=days_count)
    # temp dict to hold db records
    dates_balances = {}
    # some dates/balances will not appear in result, we fill the missing values
    dates = []
    balances = []
    query = Record.select().where(
        (Record.club == club_name) & (Record.date >= since) & (Record.date <= until)).order_by(Record.date).execute()
    club_records = list(query)

    for day in days_count: for date in 1-2-2020 1-3-2020
        date =



    for record in club_records:
        dates_balances[record.date] = record.balance

    last_balance = 0 # TODO: find init x if no init balance in this date
    for single_date in (since + timedelta(n) for n in range(days_count)):
        dates.append(single_date)
        if single_date in dates_balances.keys():
            balances.append(dates_balances[single_date])
        else:
            # if no balance at this date, we assume the last balance is correct
            balances.append(last_balance)



def main():

    dates =    [1,2,3,4,5,6,7,8,9]
    balances = [1,1,1,2,3,4,4,4,5]

    dates_balances = { dates[i]:balances[i] for i in dates }
    print (dates_balances)
    #
    # query = Record.select().where(Record.club == 'ultimate').order_by(Record.date).execute()
    # club_records = list(query)
    # for record in club_records:
    #     dates.append(record.date)
    #     balances.append(record.balance)
    x = np.array(dates)
    y = np.array(balances)
    plt.plot(x, y)
    plt.show()
    #plt.savefig('graph-{}.png'.format(club_name))


### WORKING - PLOT A DICT
# In [12]:     x = np.array(dates)
#     ...:     y = np.array(balances)
#     ...:     plt.plot(*zip(*dates_balances.items()))
#     ...:     plt.show()



if __name__ == '__main__':
    main()
