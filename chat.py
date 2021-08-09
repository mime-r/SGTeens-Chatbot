from telegram.ext import *
import requests
import urllib
from datetime import datetime
from tinydb import TinyDB, Query
import logging
import os

import fuckit


token_ = os.environ['token']


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Live variables
db = TinyDB('users.json')
s = Query()

queue = TinyDB('queue.json')

# ties two users together

chat = []

helpstring = """How to use:
/connect to find a random stranger.
/disconnect to stop talking to the stranger.
/leavequeue to leave the queue.
/info for info about this project.
"""

welcome = f""" Welcome to SGTeens Chatbot :) Where you can talk to random people and make new friends!
{helpstring}
"""


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    update.message.reply_text(welcome)


def connect(update, context):
    """Send a message when the command /start is issued."""
    message = update.message.from_user

    id, username = int(message["id"]), message["username"]
    if len(db.search(s.userid == id)) == 0:
        update.message.reply_text(welcome)
        db.insert({'userid': id, 'joined': str(datetime.now())})
    else:
        if len(queue.search(s.userid == id)) == 0:
            update.message.reply_text(f'Adding you into the queue...')
            queue.insert(
                {"userid": id, 'username': username, "talkingto": None})
            update.message.reply_text(f'You have been added into the queue!')

            # Check the queue
            not_matched = queue.search(s.talkingto == None)
            # update.message.reply_text(not_matched)

        else:
            update.message.reply_text(f"You're already in the queue.")

            not_matched = queue.search(s.talkingto == None)
            filtered_result = [d for d in not_matched if d['userid'] != id]

            if len(filtered_result) > 0:

                connected_host = urllib.parse.quote_plus("You are connected with a stranger! (host)")

                queue.update(
                    {"talkingto": filtered_result[0]["userid"]}, s.userid == id)
                update.message.reply_text(connected_host)

                # inform the other user
                talkingto_ = filtered_result[0]["userid"]

                queue.update({"talkingto": id}, s.userid ==
                             filtered_result[0]["userid"])
                connected_receive = urllib.parse.quote_plus("You are connected with a stranger! (recipient)")

                requests.get(
                    f"https://api.telegram.org/bot{token_}/sendMessage?chat_id={talkingto_}&text={connected_receive}")


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text(helpstring)


def echo(update, context):
    """Echo the user message."""
    _message = update.message.from_user
    id_, username = int(_message["id"]), _message["username"]
    echo_search = queue.search(s.userid == id_)
    #update.message.reply_text(queue.all(), id_)
    if len(echo_search) == 0:
        update.message.reply_text(helpstring)
    elif echo_search[0]["talkingto"] == None:
        update.message.reply_text('You are not connected to a stranger yet!')

    else:
        other_id = echo_search[0]["talkingto"]

        message_ = update.message.text
        text = urllib.parse.quote_plus(f"Stranger: {message_}")

        website = f'https://api.telegram.org/bot{token_}/sendMessage?chat_id={other_id}&text={text}'
        requests.get(website)


def error(update, context):
    """Log Errors caused by Updates."""
    global error_
    error_ = f"Update {update}, caused error {context.error}"
    logger.warning(error_)


@fuckit
def disconnect(update, context):
    message = update.message.from_user

    id, username = int(message["id"]), message["username"]
    if queue.search(s.userid == update.message.from_user["id"])[0]["talkingto"] != None:
        update.message.reply_text("Disconnecting...")

        queue.remove(s.userid == queue.search(s.userid == id)[0]["talkingto"])
        queue.remove(s.userid == id)
        

        text = urllib.parse.quote_plus("Stranger has disonnected! Oof.") 
        website = f'https://api.telegram.org/bot{token_}/sendMessage?chat_id={recipient_id}&text={text}'
        requests.get(website)
        update.message.reply_text("You have disconnected ...")
    else:
        update.message.reply_text(
            "You can't disconnect when you aren't even connected.")


def leavequeue(update, context):
    message = update.message.from_user
    id, username = int(message["id"]), message["username"]
    if len(queue.search(s.userid == id)) > 0:
        queue.remove(s.userid == id)
        update.message.reply_text("Successfuly left the queue.")


__version__ = "1.1"


def info(update, context):
    info = f"""SGTeens Chatbot (Omegle service) v{__version__}:
Creator: Samuel Cheng
Server: repl.it
Location: Singapore
How to reach me: t.me/fez_tival
/changelog for more info."""
    update.message.reply_text(info)


def changelog(update, context):
    changelog = f"""Changelog:
v1.1 (5/8/2021)
- Bot is now hosted 24/7 on repl.it thanks to uptimerobot.com
v1.0 (4/8/2021)
- Change command names, added /info and /changelog, added more code bits
v0.5 (4/8/2021)
- Made working commands
"""
    update.message.reply_text(changelog)

def reportbug(update, context):
    pass

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(token_, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("changelog", changelog))
    dp.add_handler(CommandHandler("info", info))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("connect", connect))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("disconnect", disconnect))
    dp.add_handler(CommandHandler("leavequeue", leavequeue))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    with fuckit:
        main()
