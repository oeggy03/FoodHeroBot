from ast import parse
from telegram import *
from telegram.ext import *
import requests
import os
from dotenv import load_dotenv
import logging
import json
import sqlite3
import googlemaps

conn = sqlite3.connect('FoodList.sqlite')
cur = conn.cursor()
#BOT_TOKEN = "5494197007:AAHd9ZEPe1BqdhlGJdf0LzJRoVP-S9XJSw4" #HATHU BOT
BOT_TOKEN = '5498786983:AAHT5oyOBK5AMXb3JfY8KwyXxVjVL1Ec34I'  # LEXUAN BOT
app = ApplicationBuilder().token(BOT_TOKEN).build()
bot = Bot(token=BOT_TOKEN)
gmaps = googlemaps.Client(key='AIzaSyDtO2n3z4jQJMIpZFTFCnKjeiXRjt2bJEk')


# Make Database/ignore if present just incase
# cur.executescript('''
# DROP TABLE IF EXISTS Foodlist;

# CREATE TABLE Foodlist (
#     id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
#     username    TEXT,
#     FoodType    TEXT,
#     FoodName    TEXT,
#     FoodPhoto   BLOB,
#     Halal       TEXT,
#     Kosher      TEXT,
#     Vegetarian  TEXT,
#     Allergens   TEXT,
#     Location    TEXT
# ); ''')

start_str = '''
Food wastage has been an increasing worrying issue over the years, and this bot aims to reduce it through encouraging users to share their spare or leftover food.
If you would like to share your spare/leftover food, please use the command /postfood
If you would like to help us reduce food wastage by taking food from posters, please use the command /getfood.
Type /help for more information on what this bot can do!
'''
allergen_str = '''
Please list any potential allergens that your food product may contain.
Common allergens include shellfish, nut, egg, wheat, oat, grain, soy, milk and fish.
Allergens may be found listed on the back of food packaging. If there are no allergens present, please type "None".
'''
location_str = '''
Thank you!
Please enter a pickup location for the food.'''


##For /start function, stores user information
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_text(f"Welcome to testbot, {update.effective_user.first_name}!"+start_str)

    #Save user information if user is new
    with open('users.json', 'r') as user_db:
        users = json.load(user_db)

    if str(user.id) not in users:
        logger.info("User %s saved.", user.first_name)
        user_info = {
            'username': user.username,
            'name': user.first_name,
            'chat_id': update.effective_chat.id,
            'rating': '5',
            'times_rated': '0',
            'dietary_restrictions': [],
            'preferences': []
            }
        users[user.id] = user_info

        with open('users.json', 'w') as user_db:
            json.dump(users, user_db)


##For /postfood function
#/cancel function
async def cancelpost(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Alright! You may always start again by typing /start."
        "See you next time!", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


# Asks for type of food donated
async def postfood0(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Asks for food type."""
    user = update.effective_user
    cur.execute("INSERT INTO Foodlist ('username') VALUES (?)",
                (user.username,))
    conn.commit()
    reply_keyboard = [["Leftovers"],
                      ["Spare Food"]]

    await update.message.reply_text(
        "Hey there! Thank you for choosing to share your food, and bringing us closer to our goal of 0 food wastage! "
        "You may type /cancel to exit this conversation at any time.\n\n\n"
        "What kind of food will you be donating?\n\n"
        "Leftovers consist of food products which have been partially consumed.\n"
        "Spare food consists of food products/ingredients which you do not intend to use, and have not crossed the expiry date.",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Please select the type of food!"
        ),
    )

    return FOODTYPE


#Asks for dish name
async def postfood1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    user = update.message.from_user
    Typefood = update.message.text
    logger.info("%s will be contributing %s", user.first_name, Typefood)
    cur.execute("SELECT id FROM Foodlist WHERE username = ?",
                (user.username, ))
    user_id = cur.fetchall()[-1][0]
    cur.execute("UPDATE Foodlist SET 'FoodType'= ? WHERE id = ?",
                (Typefood, user_id))
    await update.message.reply_text("Wow, that is great! Thank you for sharing! "
                                    "What is the name of this dish/product/ingredient?")
    return FOODNAME


#Ask for image of food
async def postfood2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    Namefood = update.message.text
    logger.info("%s will be contributing %s", user.first_name, Namefood)
    cur.execute("SELECT id FROM Foodlist WHERE username = ?",
                (user.username, ))
    user_id = cur.fetchall()[-1][0]
    cur.execute("UPDATE Foodlist SET 'FoodName'= ? WHERE id = ?",
                (Namefood, user_id))
    await update.message.reply_text(
        "Wow, that is great! Thank you for sharing! "
        "Please kindly upload a photo of the food product.",
        reply_markup=ReplyKeyboardRemove(),
    )

    return FOODPHOTO


#Asks if food is halal
async def postfood3(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download("foodphoto.jpg")
    with open("foodphoto.jpg", "rb") as p:
        data = p.read()
    user = update.message.from_user
    cur.execute("SELECT id FROM Foodlist WHERE username = ?",
                (user.username, ))
    user_id = cur.fetchall()[-1][0]
    cur.execute("UPDATE Foodlist SET 'FoodPhoto'= ? WHERE id = ?",
                (data, user_id))
    reply_keyboard = [["Yes"],
                      ["No"], ["Not Sure"]]

    await update.message.reply_text(
        "Wow, that looks great!\n"
        "Please kindly answer the following questions. \n\n"
        "Is the food product certified Halal?\n\n"
        "Halal products refer to foods that adhere to islamic dietary laws."
        "To find out more, you may visit <a href=\"https://en.wikipedia.org/wiki/Islamic_dietary_laws\">this page</a>!",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Please select the appropriate option."
        ),
    )

    return HALAL


#Asks if food is kosher
async def postfood4(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    answer = update.message.text
    user = update.message.from_user
    cur.execute("SELECT id FROM Foodlist WHERE username = ?",
                (user.username, ))
    user_id = cur.fetchall()[-1][0]
    cur.execute("UPDATE Foodlist SET 'Halal'= ? WHERE id = ?",
                (answer, user_id))
    reply_keyboard = [["Yes"],
                      ["No"], ["Not Sure"]]

    await update.message.reply_text(
        "Is the food product Kosher?\n\n"
        "Kosher products refer to foods that conform to the Jewish dietary regulations of kashrut."
        "To find out more, you may visit <a href=\"https://en.wikipedia.org/wiki/Kosher_foods\"> this page</a>!",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Please select the appropriate option."
        ),
    )

    return KOSHER


#Asks whether food is vegetarian
async def postfood5(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    answer = update.message.text
    user = update.message.from_user
    cur.execute("SELECT id FROM Foodlist WHERE username = ?",
                (user.username, ))
    user_id = cur.fetchall()[-1][0]
    cur.execute("UPDATE Foodlist SET 'Kosher'= ? WHERE id = ?",
                (answer, user_id))
    reply_keyboard = [["Yes"],
                      ["No"], ["Not Sure"]]

    await update.message.reply_text(
        "Is the food product vegetarian?\n"
        "Vegetarian products refer to food which do not include meat, animal tissue products or byproducts of animal slaughter.",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Please select the appropriate option."
        ),
    )

    return VEGETARIAN


#Ask for allergens in food
async def postfood6(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    answer = update.message.text
    user = update.message.from_user
    cur.execute("SELECT id FROM Foodlist WHERE username = ?",
                (user.username, ))
    user_id = cur.fetchall()[-1][0]
    cur.execute("UPDATE Foodlist SET 'Vegetarian'= ? WHERE id = ?",
                (answer, user_id))

    await update.message.reply_text(allergen_str)

    return ALLERGENS


async def postfood7(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    answer = update.message.text
    user = update.message.from_user
    cur.execute("SELECT id FROM Foodlist WHERE username = ?",
                (user.username, ))
    user_id = cur.fetchall()[-1][0]
    cur.execute("UPDATE Foodlist SET 'Allergens'= ? WHERE id = ?",
                (answer, user_id))
    await update.message.reply_text(location_str)

    return LOCATION


async def review(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ends the conversation."""
    answer = update.message.text
    user = update.message.from_user
    cur.execute("SELECT id FROM Foodlist WHERE username = ?",
                (user.username, ))
    user_id = cur.fetchall()[-1][0]
    cur.execute("UPDATE Foodlist SET 'Location'= ? WHERE id = ?",
                (answer, user_id))
    conn.commit()

    # with open('users.json', 'r') as user_db:
    #     users = json.load(user_db)
    #
    # location = update.message.text
    # logger.info("Food location: %s", str(location))
    # geocode_result = gmaps.geocode(location)
    # lat = geocode_result[0]['geometry']['location']['lat']
    # lng = geocode_result[0]['geometry']['location']['lng']
    #
    # if str(user.id) in users:
    #     user_info = users[str(user.id)]
    #     chat_id = user_info["chat_id"]
    # await bot.send_location(chat_id=chat_id, latitude=lat, longitude=lng)

    logger.info("Bio of %s: %s", user.first_name, update.message.text)

    await update.message.reply_text("Thank you!")

    return ConversationHandler.END


# async def rate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     user=update.effective_user


FOODTYPE, FOODNAME, FOODPHOTO, HALAL, KOSHER, ALLERGENS, VEGETARIAN, LOCATION = range(
    8)
postfood_handler = ConversationHandler(
        entry_points=[CommandHandler("postfood", postfood0)],
        states={
                FOODTYPE: [MessageHandler(filters.Regex("^(Leftovers|Spare Food)$"), postfood1)],
                FOODNAME: [MessageHandler(filters.TEXT, postfood2)],
                FOODPHOTO: [
                    MessageHandler(filters.PHOTO, postfood3),
                    # CommandHandler("skip", skip_photo)
                ],
                HALAL: [
                    MessageHandler(filters.Regex(
                        "^(Yes|No|Not Sure)$"), postfood4),
                    # CommandHandler("skip", skip_location),
                ],
                KOSHER: [
                    MessageHandler(filters.Regex(
                        "^(Yes|No|Not Sure)$"), postfood5),
                    # CommandHandler("skip", skip_location),
                ],
                VEGETARIAN: [
                    MessageHandler(filters.Regex(
                        "^(Yes|No|Not Sure)$"), postfood6),
                    # CommandHandler("skip", skip_location),
                ],
                ALLERGENS: [
                    MessageHandler(filters.TEXT, postfood7),
                    # CommandHandler("skip", skip_location),
                ],
                LOCATION: [
                    MessageHandler(filters.TEXT, review),
                    # CommandHandler("skip", skip_location),
                ]
        },
    fallbacks=[CommandHandler("cancel", cancelpost)],
    )

# SELECT_USER, RATING, REVIEW = range(3)
# ratings_handler = ConversationHandler(
#         entry_points=[CommandHandler("rate", rate)],
#         states={
#             SELECT_USER: [
#                 MessageHandler(filters.TEXT, callback)
#             ],
#             RATING: [
#                 MessageHandler(filters.Regex("^[1-5]$"), rating),
#             ],
#             REVIEW: [
#                 MessageHandler(filters.TEXT, review),
#             ]
#         },
#         fallbacks=[CommandHandler("cancel", cancelpost)],
#     )

##logging function in console
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

app.add_handler(CommandHandler("start", start))
app.add_handler(postfood_handler)
#app.add_handler(ratings_handler)
app.run_polling()
