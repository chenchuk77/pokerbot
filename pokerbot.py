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
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np

from db import Record
from prettytable import PrettyTable

import logging
from telegram import ParseMode
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

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


#clubs = ['ultimate', 'poker247', 'lionking', 'monkeys', 'dragonball', 'rounders', 'poxi', '7xl', 'pokernuts']


# def start(update, context):
#     # reply_keyboard = [
#     #     ['ultimate', 'poker247', 'lionking'],
#     #     ['monkeys', 'dragonball', 'rounders'],
#     #     ['poxi', '7xl', 'pokernuts']
#     # ]
#     reply_keyboard = [ clubs1, clubs2, clubs3 ]
#     update.message.reply_text(
#         'Choose a club to update balance:\n\n',
#         reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
#     return CLUB
#

def start(update, context):

    reply_keyboard = [ clubs1, clubs2, clubs3, action_buttons ]
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
    plt.plot(x,y)
    # plt.show()
    plt.savefig('graph-{}.png'.format(club_name))


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
            generate_graph(club)
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
    new_record = Record.create(club=old_record.club, date=datetime.datetime.now(), balance=new_balance)
    new_record.save()

    message = "Club: {} \nDate: {}\nBalance: {}\n\npress /start to start again\n".format(new_record.club,
                                                                                         str(new_record.date),
                                                                                         str(new_record.balance))

    update.message.reply_text(message)

    #return END
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
            ACTION: [MessageHandler(Filters.text(['update','cancel']), action),
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

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
