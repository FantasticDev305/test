from io import StringIO
import logging
from pickle import FALSE, TRUE
from typing import Tuple
from xmlrpc.client import boolean
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters
from flask import Flask
from flask import request
from flask import Response
from pyngrok import ngrok
import requests
import telebot
import pymongo
import telegram
import json
import imp
import webbrowser
# Opening JSON file
with open('data.json',encoding='utf-8') as json_file:
    lang_data = json.load(json_file)

TOKEN = "5367007480:AAFt41LL0KPgdFtQeO_9YgepRtQv6ohcZQo"
ONE , TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE= range(9)

bot = telegram.Bot(token=TOKEN)
application = Application.builder().token("5571203589:AAHJbqya4r15y8AEzXuVKfp7ZDyADCCVMcU").build()
is_registered = False
lang = ''

#DB settings

connection_url="mongodb://localhost:27017/"
client=pymongo.MongoClient(connection_url)
database_name = "PTB_info"
PTB_db=client["PTB_info"]
user_collection=PTB_db["user_info"]

#user information definition.

user_info_list = {
    "chat_id":"",
    "Full name":"", 
    "Date of Birth":"", 
    "Email":"", 
    "Phone Number":"", 
    "Nickname":"", 
    "Bank Cart":"",
    "ID Verification/Selfie":""
}


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context) -> None:
    """Sends a message with inline buttons attached."""
    duplicated = is_duplicated(update, context)
    context.user_data['duplicated'] = duplicated
    if duplicated == False:
        registerhandler()
        await update.message.reply_text("Please register. /register")
    else:
        mainhandler()
        await update.message.reply_text("To mainboard /main")
       
async def button(update: Update, context):
    query = update.callback_query
    lang = query.data
    string = 'Enter your full name'
    if lang != 'English':
        string = lang_data[string]
    await query.answer()
    context.user_data['language'] = lang
    await query.edit_message_text(string)
    if context.user_data['duplicated']  == False:
        return TWO
    else:
        return EXCHANGE

async def help_command(update: Update, context) -> None:
    await update.message.reply_text(str(1))


def is_duplicated(update: Update, context):
    query={"userid": update.message.from_user.id}
    if len(list(user_collection.find(query))) > 0:
        return True
    return False

#----------language handler definition------------

async def lang_handler(update: Update, context):
    button = [
                [
                    InlineKeyboardButton("EGLISH", callback_data = "English"), 
                    InlineKeyboardButton("FARSI", callback_data= "Farsi")
                ]
    ]
    reply_markup =InlineKeyboardMarkup(button)
    await update.message.reply_text("Pick the language.", reply_markup=reply_markup)
    if context.user_data['duplicated'] == False:
        return ONE
    else:
        return EXCHANGE

# ---------- functions for register full name---------
async def register_fname(update: Update, context):
    string = 'Date of birth'
    lang = context.user_data['language']
    if lang != 'English':
        string = lang_data[string]
    name = update.message.text
    context.user_data["name"] = name
    await update.message.reply_text(string)
    print("your name is -->", context.user_data['name'])
    return THREE

# ---------- functions for register birthday---------
async def register_birth(update: Update, context):
    string = 'Email'
    lang = context.user_data['language']
    if lang != 'English':
        string = lang_data[string]
    birth = update.message.text # now we got the name
    context.user_data["birth"] = birth
    await update.message.reply_text(string)
    return FOUR

async def register_email(update: Update, context):
    string = 'phone number'
    lang = context.user_data['language']
    if lang != 'English':
        string = lang_data[string]
    email = update.message.text
    context.user_data["email"] = email
    await update.message.reply_text(string)
    return FIVE

async def register_phone(update: Update, context):
    string = 'Nickname'
    lang = context.user_data['language']
    if lang != 'English':
        string = lang_data[string]
    phone = update.message.text
    context.user_data["phone"] = phone
    await update.message.reply_text(string)
    return SIX

async def register_nick(update: Update, context):
    string = 'Bank Card Number'
    lang = context.user_data['language']
    if lang != 'English':
        string = lang_data[string]
    nick = update.message.text
    context.user_data["nick"] = nick
    await update.message.reply_text(string)
    return SEVEN

async def register_bcart(update: Update, context):
    string = 'ID Verification/Selfie'
    lang = context.user_data['language']
    if lang != 'English':
        string = lang_data[string]
    bcart = update.message.text
    context.user_data["bcart"] = bcart
    await update.message.reply_text(string)
    return EIGHT

async def register_verify(update: Update, context):
    string = 'Date of birth'
    lang = context.user_data['language']
    if lang != 'English':
        string = "Can you save your input?y/n"
    else:
        string = "An féidir leat do shonraí a shábháil?y/n"
    id_verify = update.message.text
    context.user_data["id_verify"] = id_verify
    await update.message.reply_text(string)
    return NINE
    

#----------ending register-------------------------

#-----------save the input for register-----------------------
async def save(update: Update, context):
    user_data = {
        "user_id":update.message.from_user.id,
        "fname": context.user_data["name"],
        "birth": context.user_data["birth"],
        "email": context.user_data["email"],
        "phone": context.user_data["phone"],
        "nick": context.user_data["nick"],
        "bcart": context.user_data["bcart"],
        "id_verify": context.user_data["id_verify"],
        "language": context.user_data['language'],
    }
    print("your user_data is---->>>", user_data)
    if update.message.text == "y":
        user_collection.insert_one(user_data)
        await update.message.reply_text("Register completed!")
        is_registered = True
        cancel(update, context)
    if update.message.text == "n":
        return ONE
#------------cancel all precess---------------
async def cancel(update: Update, context):
    # chat_id = update.message.chat_id
    # await bot.send_message(chat_id , text = "process done !")
    await update.message.reply_text("to enter main  input /main")
    mainhandler()
    
    return ConversationHandler.END

async def poll(update: Update, context) -> None:
    """Sends a predefined poll"""
    questions = ["BTC", "Gold"]
    message = await context.bot.send_poll(
        update.effective_chat.id,
        "Please pick your favourite",
        questions,
        is_anonymous=False,
        allows_multiple_answers=True,
    )
    # Save some info about the poll the bot_data for later use in receive_poll_answer
    payload = {
        message.poll.id: {
            "questions": questions,
            "message_id": message.message_id,
            "chat_id": update.effective_chat.id,
            "answers": 0,
        }
    }
    context.bot_data.update(payload)


async def receive_poll_answer(update: Update, context) -> None:
    """Summarize a users poll vote"""
    answer = update.poll_answer
    answered_poll = context.bot_data[answer.poll_id]
    try:
        questions = answered_poll["questions"]
    # this means this poll answer update is from an old poll, we can't do our answering then
    except KeyError:
        return
    selected_options = answer.option_ids
    answer_string = ""
    for question_id in selected_options:
        if question_id != selected_options[-1]:
            answer_string += questions[question_id] + " and "
        else:
            answer_string += questions[question_id]
    await context.bot.send_message(
        answered_poll["chat_id"],
        f"{update.effective_user.mention_html()} picks {answer_string}!",
        parse_mode=ParseMode.HTML,
    )
    
#-------------------------client mainboard part-------------------------------
#contant definition
EXCHANGE, UPDATE = range(2)
def mainhandler():
    handler = ConversationHandler(entry_points=[CommandHandler("main", lang_handler)],
     states={
        EXCHANGE:[
              CallbackQueryHandler(button)
        ],
        
        UPDATE:[
              MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), register_fname
                )
        ],

        THREE:[
            MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), register_birth
            )
        ],

        FOUR:[
            MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), register_email
            )
        ],

        FIVE:[
            MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), register_phone
            )
        ],

        SIX:[
            MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), register_nick
            )
        ],
        
        SEVEN:[
            MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), register_bcart
            )
        ],

        EIGHT:[
            MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), register_verify
            )
        ],
        
        NINE:[
            MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), save
            )
        ],
    }, fallbacks = [CommandHandler('Done', cancel)])
    application.add_handler(handler)

def registerhandler():
    handler = ConversationHandler(entry_points=[CommandHandler("register", lang_handler)],
     states={
        ONE:[
              CallbackQueryHandler(button)
        ],
        
        TWO:[
              MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), register_fname
                )
        ],

        THREE:[
            MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), register_birth
            )
        ],

        FOUR:[
            MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), register_email
            )
        ],

        FIVE:[
            MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), register_phone
            )
        ],

        SIX:[
            MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), register_nick
            )
        ],
        
        SEVEN:[
            MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), register_bcart
            )
        ],

        EIGHT:[
            MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), register_verify
            )
        ],
        
        NINE:[
            MessageHandler(
                    (filters.Regex("^y$") | filters.Regex("^n$")), save
            )
        ],
    }, fallbacks = [CommandHandler('Done', cancel)])
    application.add_handler(handler)

async def update_handler(update: Update, context):
    button1 = [
                [
                    InlineKeyboardButton("ENGLISH", callback_data = "English"), 
                    InlineKeyboardButton("FARSI", callback_data= "Farsi")
                ]
    ]

    reply_markup =InlineKeyboardMarkup(button1)
    await update.message.reply_text("Pick the language.", reply_markup=reply_markup)
    if context.user_data['duplicated'] == False:
        return ONE
    else:
        return EXCHANGE


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    
    application.add_handler(CommandHandler("start", start))
    # application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("help", help_command))



    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()