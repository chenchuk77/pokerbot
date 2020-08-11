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
from datetime import date

import credentials
import db
from db import Record

import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# states
CLUB, ACTION, AMOUNT, BIO = range(4)


def start(update, context):
    reply_keyboard = [
        ['ultimate', 'poker247', 'lionking'],
        [ 'monkeys', 'dragonball', 'rounders'],
        ['poxi', '7xl', 'pokernuts']
    ]

    update.message.reply_text(
        'Choose a club to update balance:\n\n',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

#    record = Record.get(Record.club == update.message.reply_text)
    for record in Record.select():
        print(record.club)

    return CLUB


def club(update, context):
    reply_keyboard = [
        ['update', 'done']
    ]

    user = update.message.from_user
    logger.info("%s choose club: %s", user.first_name, update.message.text)

    last_club_record = Record.select().where(Record.club == update.message.text).order_by(Record.date.desc()).get()
    context.user_data['last_club_record'] = last_club_record
    logger.info("%s balance: %s. [%s]", update.message.text, last_club_record.balance,last_club_record.date)

    message = "Club: {} \nDate: {}\nBalance: {}\n\n".format(update.message.text, str(last_club_record.date), str(last_club_record.balance))
    update.message.reply_text(message,
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return ACTION

def update_balance(update, context):
    user = update.message.from_user
    logger.info("requesting user amount.")
    update.message.reply_text('Type the current balance: \n')
    return AMOUNT


# def photo(update, context):
#     user = update.message.from_user
#     photo_file = update.message.photo[-1].get_file()
#     photo_file.download('user_photo.jpg')
#     logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
#     update.message.reply_text('Gorgeous! Now, send me your location please, '
#                               'or send /skip if you don\'t want to.')
#
#     return LOCATION

def skip_update_balance(update, context):
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    update.message.reply_text('I bet you look great! Now, send me your location please, '
                              'or send /skip.')

    return CLUB
#
# def skip_photo(update, context):
#     user = update.message.from_user
#     logger.info("User %s did not send a photo.", user.first_name)
#     update.message.reply_text('I bet you look great! Now, send me your location please, '
#                               'or send /skip.')
#
#     return LOCATION


def balance(update, context):
    user = update.message.from_user
    new_balance = update.message.text

    # get the record from the context
    old_record = context.user_data['last_club_record']

    logger.info("adding record. [club: {}, balance {}] (old-balance: {})".format(old_record.club, new_balance, old_record.balance))
    new_record = Record.create(club=old_record.club, date=date.today(), balance=new_balance)
    new_record.save()

    update.message.reply_text('record added... '
                              'At last, tell me something about yourself.')

    return BIO
# def location(update, context):
#     user = update.message.from_user
#     user_location = update.message.location
#     logger.info("Location of %s: %f / %f", user.first_name, user_location.latitude,
#                 user_location.longitude)
#     update.message.reply_text('Maybe I can visit you sometime! '
#                               'At last, tell me something about yourself.')
#
#     return BIO


def skip_balance(update, context):
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    update.message.reply_text('You seem a bit paranoid! '
                              'At last, tell me something about yourself.')

    return BIO
# def skip_location(update, context):
#     user = update.message.from_user
#     logger.info("User %s did not send a location.", user.first_name)
#     update.message.reply_text('You seem a bit paranoid! '
#                               'At last, tell me something about yourself.')
#
#     return BIO


def bio(update, context):
    user = update.message.from_user
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
            #GENDER: [MessageHandler(Filters.regex('^(Boy|Girl|Other)$'), gender)],
            CLUB: [MessageHandler(Filters.all, club)],

            # PHOTO: [MessageHandler(Filters.photo, photo),
            #         CommandHandler('skip', skip_photo)],
            ACTION: [MessageHandler(Filters.all, update_balance),
                    CommandHandler('skip', skip_update_balance)],

            # LOCATION: [MessageHandler(Filters.location, location),
            #            CommandHandler('skip', skip_location)],
            AMOUNT: [MessageHandler(Filters.all, balance),
                       CommandHandler('skip', skip_balance)],

            # BIO: [MessageHandler(Filters.text & ~Filters.command, bio)]
            BIO: [MessageHandler(Filters.all, bio)]
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