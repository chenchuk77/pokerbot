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

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# States
CLUB, ACTION, BALANCE, END = range(4)

clubs1 = ['ultimate', 'poker247', 'lionking']
clubs2 = ['monkeys', 'dragonball', 'rounders']
clubs3 = ['poxi', '7xl', 'pokernuts']
clubs = clubs1 + clubs2 + clubs3

action_buttons = ['summary', 'reports']


def start(update, context):
    reply_keyboard = [clubs1, clubs2, clubs3, action_buttons]
    update.message.reply_text(
        'Choose a club to update balance:\n\n',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return CLUB


def generate_graph(club_name):
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


def generate_graph3(club_name, until, days_count):
    since = until - timedelta(days=days_count)
    # temp dict to hold db records
    dates_balances = {}
    # some dates/balances will not appear in result, we fill the missing values
    dates = []
    balances = []
    query = Record.select().where(
        (Record.club == club_name) & (Record.date >= since) & (Record.date <= until)).order_by(Record.date).execute()
    club_records = list(query)
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


def generate_graph2(club_name, since, until):
    dates = []
    balances = []
    query = Record.select().where(
        (Record.club == club_name) & (Record.date >= since) & (Record.date <= until)).order_by(Record.date).execute()
    club_records = list(query)
    for record in club_records:
        dates.append(record.date)
        balances.append(record.balance)
    x = np.array(dates)
    y = np.array(balances)
    plt.plot(x, y)
    # plt.show()
    plt.savefig('graph-{}.png'.format(club_name))


def generate_graph4(club_name, until, days_count):
    since = until - timedelta(days=days_count)

    # this is the newest club balance until a given date.
    # def get_last_balance(club, until):
    def get_last_balance():
        return Record.select(Record.balance).where((Record.club == club_name) & (Record.date <= until) & (Record.date >= since-timedelta(days=1))).order_by(Record.date).execute()[0].balance

    # generates all dates in a range
    def daterange(start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

    # create an empty list of strings for all dates in range
    all_dates = []
    for single_date in daterange(since.date(), until.date()+timedelta(days=1)):
        print(single_date.strftime("%Y-%m-%d"))
        all_dates.append(single_date.strftime("%Y-%m-%d"))

    # create dict with balances from existing records only
    balances_partial = {}
    last = get_last_balance()
    query = Record.select().where(
        (Record.club == club_name) & (Record.date >= since-timedelta(days=1)) & (Record.date <= until)).order_by(Record.date).execute()
    club_records = list(query)
    for record in club_records:
        date_string = record.date.date().strftime("%Y-%m-%d")
        balances_partial[date_string] = record.balance

    # create final dict, filling the missing gaps with last values
    all_balances = {}
    for date_string in all_dates:
        if date_string in balances_partial.keys():
            last = balances_partial[date_string]
            all_balances[date_string] = balances_partial[date_string]
        else:
            all_balances[date_string] = last

    # summary_balances = [a + b for a, b in zip(list1, list2)]

    # x = np.array(all_dates)
    # y = np.array(all_balances)
    plt.plot(*zip(*all_balances.items()))
    # plt.show()
    plt.savefig('graph-new-{}.png'.format(club_name))





    # return all_balances
    return 0


def club(update, context):
    reply_keyboard = [
        ['update', 'cancel']
    ]
    msg = ""

    if update.message.text == 'summary':
        table = PrettyTable()
        table.field_names = ["Club", "Balance", "Updated"]
        for club in clubs:
            last_record = Record.select().where(Record.club == club).order_by(Record.date.desc())[0]
            table.add_row([club, last_record.balance, str(last_record.date)[:-7]])
            # generate_graph2(club, datetime.now() - timedelta(days=3),datetime.now())
            #generate_graph3(club, datetime.now(), 2)
            generate_graph4(club, datetime.now(), 2)
        message = "```" + str(table) + "```"
        message += '\npress /start to start over.'
        update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        return ConversationHandler.END

    else:

        user = update.message.from_user
        logger.info("%s choose club: %s", user.first_name, update.message.text)

        last_club_record = Record.select().where(Record.club == update.message.text).order_by(Record.date.desc()).get()
        context.user_data['last_club_record'] = last_club_record
        logger.info("%s balance: %s. [%s]", update.message.text, last_club_record.balance, last_club_record.date)

        message = "Club: {} \nDate: {}\nBalance: {}\n\n".format(update.message.text, str(last_club_record.date),
                                                                str(last_club_record.balance))
        update.message.reply_text(message,
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return ACTION


def action(update, context):
    user = update.message.from_user

    if update.message.text == 'update':
        logger.info("update chosen. requesting user amount.")
        update.message.reply_text(
            'Type the current balance for {}: \n'.format(context.user_data['last_club_record'].club))
        return BALANCE
    else:
        logger.info("cancel chosen. exiting to BIO.")
        update.message.reply_text('canceled. press /start to start again\n')
        # return BIO
        return ConversationHandler.END


def skip_action(update, context):
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    update.message.reply_text('I bet you look great! Now, send me your location please, '
                              'or send /skip.')

    return CLUB


def balance(update, context):
    user = update.message.from_user
    new_balance = update.message.text

    # get the record from the context
    old_record = context.user_data['last_club_record']

    logger.info("adding record. [club: {}, balance: {}] (old-balance: {})".format(old_record.club, new_balance,
                                                                                  old_record.balance))
    new_record = Record.create(club=old_record.club, type='update', date=datetime.datetime.now(), balance=new_balance)
    new_record.save()

    message = "Club: {} \nDate: {}\nBalance: {}\n\npress /start to start again\n".format(new_record.club,
                                                                                         str(new_record.date),
                                                                                         str(new_record.balance))

    update.message.reply_text(message)

    # return END
    return ConversationHandler.END


def skip_balance(update, context):
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    update.message.reply_text('You seem a bit paranoid! '
                              'At last, tell me something about yourself.')

    return END


def end(update, context):
    user = update.message.from_user
    logger.info("User %s reach the END state.", user.first_name)
    update.message.reply_text('Done\n. press /start to start again\n')
    return ConversationHandler.END

    logger.info("Bio of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('Thank you! I hope we can talk again some day.')

    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def add_daily_record():
    print('TODO::add daily record at 23:59')


def main():
    db.init()
    logger.info("db initialized. ")

    token = credentials.token
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            # CLUB: [MessageHandler(Filters.all, club)],
            CLUB: [MessageHandler(Filters.text(clubs + action_buttons), club)],

            # ACTION: [MessageHandler(Filters.all, action),
            #          CommandHandler('skip', skip_action)],
            ACTION: [MessageHandler(Filters.text(['update', 'cancel']), action),
                     CommandHandler('skip', skip_action)],

            BALANCE: [MessageHandler(Filters.all, balance),
                      CommandHandler('skip', skip_balance)],

            END: [MessageHandler(Filters.all, end)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # q = updater.job_queue
    # q.run_daily(add_daily_record(), time(hour=10, minute=10, second=10), context=None, name=None)
    # q.run_daily(add_daily_record(), time(hour = 10, minute = 10, second = 10), context=None, name=None)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
