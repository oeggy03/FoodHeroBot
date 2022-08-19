from ast import parse
from math import sqrt
from tkinter import END
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
BOT_TOKEN = "Your own telegram bot token here"
# BOT_TOKEN = "5445899302:AAFXbwblV5JqenYg3yInJUN_t6HwZhb8DPg"  # HATHU BOT
# BOT_TOKEN = '5498786983:AAHT5oyOBK5AMXb3JfY8KwyXxVjVL1Ec34I'  # LEXUAN BOT
app = ApplicationBuilder().token(BOT_TOKEN).build()
bot = Bot(token=BOT_TOKEN)
gmaps = googlemaps.Client(key='AIzaSyDtO2n3z4jQJMIpZFTFCnKjeiXRjt2bJEk')

##logging function in console
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

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
help_str = '''This bot helps you save your leftover food and groceries by giving them to other users.

Here are some helpful commands:
/start - registers your account
/help - lists operable commands
/postfood - post your leftover food
/getfood - show and collect someone else's leftover food
/myposts - shows food you've posted, and allows you to remove your posts
/completebuyer - complete the transaction (for buyers)'''


##For /start function, stores user information
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_text(f"Welcome to testbot, {update.effective_user.first_name}!"+start_str)

    #Save user information if user is new
    # with open('users.json', 'r') as user_db:
    #     users = json.load(user_db)
    cur.execute("SELECT chat_id FROM Users WHERE username =?",(user.username,))
    if cur.fetchone() == None:
        logger.info("User %s saved.", user.first_name)
        cur.execute("INSERT INTO Users(username,name,chat_id,rating,times_rated,active_buy) VALUES(?,?,?,?,?,?)",(user.username,user.first_name,update.effective_chat.id,5,0,0))
        conn.commit()
        # user_info = {
        #     'username': user.username,
        #     'name': user.first_name,
        #     'chat_id': update.effective_chat.id,
        #     'rating': '5',
        #     'times_rated': '0',
        #     'dietary_restrictions': [],
        #     'preferences': []
        #     }
        # users[user.id] = user_info

        # with open('users.json', 'w') as user_db:
        #     json.dump(users, user_db)
        
   
#For the /help function
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_text(help_str)
    cur.execute("SELECT chat_id FROM Users WHERE username =?",
                (user.username,))
    if cur.fetchone() == None:
        logger.info("User %s saved.", user.first_name)
        cur.execute("INSERT INTO Users(username,name,chat_id,rating,times_rated,active_buy) VALUES(?,?,?,?,?,?)",
                    (user.username, user.first_name, update.effective_chat.id, 5, 0, 0))
        conn.commit()


##For /postfood function
#/cancel function
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    conn.rollback()
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Alright! You may always start again by typing /start."
        , reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


# Asks for type of food donated
async def postfood0(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Asks for food type."""
    user = update.effective_user
    conn.rollback()
    cur.execute("INSERT INTO Foodlist ('username', 'Hide') VALUES (?,?)",(user.username,0,))

    reply_keyboard = [["Leftovers"],
                      ["Spare Food"]]

    await update.message.reply_text(
        "Hey there! Thank you for choosing to share your food, and bringing us closer to our goal of 0 food wastage! "
        "You may type /cancel to exit this conversation at any time.\n\n\n"
        "What kind of food will you be donating?\n\n"
        "Leftovers consist of food products which have been partially consumed. Please ensure that they are still safe to eat!\n"
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
    await update.message.reply_text("Wow, that is great! Thank you for sharing!\n"
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
    await photo_file.download("foodphoto.png")
    with open("foodphoto.png", "rb") as p:
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
        "Is the food product Halal?\n\n"
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


#Ask for pickup location
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


#Review post
async def review(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    answer = update.message.text
    user = update.message.from_user
    cur.execute("SELECT id FROM Foodlist WHERE username = ?",
                (user.username, ))
    user_id = cur.fetchall()[-1][0]
    cur.execute("UPDATE Foodlist SET 'Location'= ? WHERE id = ?",
                (answer, user_id))
    geocode_result = gmaps.geocode(answer)
    lat = geocode_result[0]['geometry']['location']['lat']
    long = geocode_result[0]['geometry']['location']['lng']
    cur.execute("UPDATE Foodlist SET 'Location'= ? WHERE id = ?",
                (answer, user_id))
    cur.execute("UPDATE Foodlist SET 'Lat'= ? WHERE id = ?",
                (lat, user_id))
    cur.execute("UPDATE Foodlist SET 'Long'= ? WHERE id = ?",
                (long, user_id))

    #SaveMe-Reviewfetch from SQL
    cur.execute("SELECT FoodName FROM Foodlist WHERE id = ?", (user_id,))
    Foodname = cur.fetchone()[0]

    a = cur.execute("SELECT FoodPhoto FROM Foodlist WHERE id = ?", (user_id,))
    for i in a:
        rec_data = i[0]
        print(type(rec_data))
    with open("foodphoto.png", "wb") as f:
        f.write(rec_data)

    cur.execute("SELECT FoodType FROM Foodlist WHERE id = ?", (user_id,))
    Foodtype = cur.fetchone()[0]

    cur.execute("SELECT Halal FROM Foodlist WHERE id = ?", (user_id,))
    Foodhalal = cur.fetchone()[0]

    cur.execute("SELECT Kosher FROM Foodlist WHERE id = ?", (user_id,))
    Foodkosher = cur.fetchone()[0]

    cur.execute("SELECT Vegetarian FROM Foodlist WHERE id = ?", (user_id,))
    Foodvege = cur.fetchone()[0]

    cur.execute("SELECT Allergens FROM Foodlist WHERE id = ?", (user_id,))
    Foodaller = cur.fetchone()[0]

    cur.execute("SELECT Location FROM Foodlist WHERE id = ?", (user_id,))
    Foodloca = cur.fetchone()[0]

    logger.info("Bio of %s: %s", user.first_name, update.message.text)
    await update.message.reply_photo(photo=open("foodphoto.png", 'rb'), caption="Thank you! Here is a preview of your post:\n\n" +
                                     "Food Name: " + Foodname + "\n"
                                     "Food Type: " + Foodtype + "\n"
                                     "Is it Halal?: " + Foodhalal + "\n"
                                     "Is it Kosher?: " + Foodkosher + "\n"
                                     "Is it vegetarian?: " + Foodvege + "\n"
                                     "Potential Allergens: " + Foodaller + "\n"
                                     "Pickup Location: " + Foodloca
                                     )

    reply_keyboard = [["Yes, post it!"],
                      ["No, let's start over."]]

    await update.message.reply_text(
        "Would you like to post this?\n",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Please select the appropriate option."
        ),
    )

    return ENDING

#Agree to post
async def wantpost(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Option: Post it."""
    conn.commit()
    await update.message.reply_text(
        "Thank you for sharing!\n"
        "You may view all of your food posts by typing /myposts !",
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END

#Start over
async def startover(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Option: Start over."""
    conn.rollback()
    await update.message.reply_text(
        "No problem, we will not post this.\n"
        "You may start a new food post by typing /postfood !",
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END

FOODTYPE, FOODNAME, FOODPHOTO, HALAL, KOSHER, ALLERGENS, VEGETARIAN, LOCATION, ENDING = range(
    9)
#convo handler for /postfood
postfood_handler = ConversationHandler(
        entry_points=[CommandHandler("postfood", postfood0)],
        states={
            FOODTYPE: [MessageHandler(filters.Regex("^(Leftovers|Spare Food)$") & (~filters.COMMAND), postfood1)],
            FOODNAME: [MessageHandler(filters.TEXT & (~filters.COMMAND), postfood2)],
            FOODPHOTO: [
                MessageHandler(filters.PHOTO & ~filters.COMMAND, postfood3),
                # CommandHandler("skip", skip_photo)
            ],
            HALAL: [
                MessageHandler(filters.Regex(
                    "^(Yes|No|Not Sure)$" ) & (~filters.COMMAND), postfood4),
                # CommandHandler("skip", skip_location),
            ],
            KOSHER: [
                MessageHandler(filters.Regex(
                    "^(Yes|No|Not Sure)$" )& (~filters.COMMAND), postfood5),
                # CommandHandler("skip", skip_location),
            ],
            VEGETARIAN: [
                MessageHandler(filters.Regex(
                    "^(Yes|No|Not Sure)$") & (~filters.COMMAND), postfood6),
                # CommandHandler("skip", skip_location),
            ],
            ALLERGENS: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), postfood7),
                # CommandHandler("skip", skip_location),
            ],
            LOCATION: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), review),
                # CommandHandler("skip", skip_location),
            ],
            ENDING: [
                MessageHandler(filters.Regex("^(Yes, post it!)$") & (~filters.COMMAND), wantpost),
                MessageHandler(filters.Regex(
                    "^(No, let's start over.)$") & (~filters.COMMAND), startover),
                # CommandHandler("skip", skip_location),
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

async def myposts0(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Shows you a list of your posts"""
    user = update.effective_user
    SQL_user=user.username
    cur.execute("SELECT * FROM Foodlist WHERE username = ?",(SQL_user,))
    
    SQL_temp=cur.fetchall()
    
    if len(SQL_temp)==0:
        await update.message.reply_text(
            "You have no active posts. Type /postfood to create one!"
        )

        return ConversationHandler.END

    str_temp=''''''
    x=1
    for i in range(len(SQL_temp)):

        Foodid= SQL_temp[i][0]
        Foodname= SQL_temp[i][3]
        # Foodtype= SQL_temp[i][2]
        # Foodhalal= SQL_temp[i][5]
        # Foodkosher= SQL_temp[i][6]
        # Foodvege= SQL_temp[i][7]
        # Foodaller= SQL_temp[i][8]
        # Foodloca= SQL_temp[i][9]
        # with open("foodphoto.png","wb") as f:
        #     f.write(SQL_temp[i][4])
        str_temp= str_temp + "Post No. " + str(x)+": "+ Foodname +"\n"
        x+=1


    await update.message.reply_photo(photo= open("ActuallyGoodFood.jpg",'rb'), caption= 
    "Welcome, "+user.first_name+"! These are your active posts. \n"
    "Please type the Food_id of the post you would like to view!\n"+
    "Type /cancel to exit out of this page!\n\n"
        +str_temp
        )
    
    return POSTNO

#User selects item x
async def awaitpostno(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """When you get post number"""
    try:
        i= (int(update.message.text)-1)
        aadad= sqrt(i)
        user = update.effective_user
        SQL_user=user.username
        cur.execute("SELECT * FROM Foodlist WHERE username = ?",(SQL_user,))
        SQL_temp=cur.fetchall()
        Foodid= SQL_temp[i][0]
    except:
        await update.message.reply_text(
            "That was an invalid input.\n"
            "Please type the post number and try again!"
        )

        return RETURNMENU
    # i= (int(update.message.text)-1)
    # aadad= sqrt(i)
    # user = update.effective_user
    # SQL_user=user.username
    # cur.execute("SELECT * FROM Foodlist WHERE username = ?",(SQL_user,))
    # tempid=
    cur.execute("SELECT * FROM Transactions WHERE item_id = ?",(Foodid,))
    x=cur.fetchone()
    if  x is None:
        Reservedby = "No"
        buyer="\n"
    else:
        Reservedby = "Yes"
        cur.execute("SELECT buyer_user FROM Transactions WHERE item_id=?",(Foodid,))
        buyer=", by " + str(cur.fetchone()[0]) +" .\n"
    

    Foodname= SQL_temp[i][3]
    Foodtype= SQL_temp[i][2]
    Foodhalal= SQL_temp[i][5]
    Foodkosher= SQL_temp[i][6]
    Foodvege= SQL_temp[i][7]
    Foodaller= SQL_temp[i][8]
    Foodloca= SQL_temp[i][9]
    with open("foodphoto.png","wb") as f:
        f.write(SQL_temp[i][4])

    reply_keyboard = [["Remove post"],
                      ["Return to post menu"]]

    remid = Foodid
    context.user_data["remid"] = remid

    await update.message.reply_photo(photo= open("foodphoto.png",'rb'), caption=
        "Food Name: "+ Foodname +"\n"
        "Food Type: "+ Foodtype +"\n"
        "Is it Halal?: "+ Foodhalal +"\n"
        "Is it Kosher?: "+ Foodkosher +"\n"
        "Is it vegetarian?: "+ Foodvege +"\n"
        "Potential Allergens: "+ Foodaller +"\n"
        "Is it reserved? "+ Reservedby + buyer +
        "Pickup Location: "+ Foodloca + "\n\n"+
        "If the item has been reserved, it means that someone is coming to pick it up.",reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Please select the appropriate option." 
        ),
    )
    return POSTRESULT

#User chooses remove
async def removal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """User chooses to remove"""
    choice= update.message.text
    remid = context.user_data["remid"]
    reply_keyboard = [["Yes"],
                      ["No"]]
    await update.message.reply_text(
            "Are you sure you want to remove this post? It cannot be recovered!",
            reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Please select the appropriate option."
            )
    )
    return CONFIRM

#User confirms deleted
async def cancelpost(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    remid = context.user_data["remid"]
    cur.execute("DELETE FROM Foodlist WHERE id=?", (remid,))
    conn.commit()
    await update.message.reply_text(
        "Alright! Post has been deleted. Run /myposts again to view your posts! "
    )
    return ConversationHandler.END

POSTNO, POSTRESULT, RETURNMENU, CONFIRM = range(4)
#ConvoHandlerforMyPosts
myposts_handler = ConversationHandler(
        entry_points=[CommandHandler("myposts", myposts0)],
        states={
            POSTNO: [MessageHandler(filters.TEXT & (~filters.COMMAND), awaitpostno)],
            RETURNMENU: [MessageHandler(filters.TEXT & (~filters.COMMAND), myposts0)],
            POSTRESULT: [MessageHandler(filters.Regex("^(Remove post)$"), removal),
                         MessageHandler(filters.Regex("^(Return to post menu)$"), myposts0)],
            CONFIRM: [MessageHandler(filters.Regex("^(Yes)$") & (~filters.COMMAND), cancelpost),
                      MessageHandler(filters.Regex("^(No)$") & (~filters.COMMAND), myposts0)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )


##getfood
async def getfood0(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows food items available"""

    user = update.effective_user
    cur.execute("INSERT OR IGNORE INTO ScrollTrack(scrollcount,username) VALUES (?,?)", (0,user.username,))
    cur.execute("SELECT scrollcount FROM ScrollTrack WHERE username = ?",(user.username,))
    x=cur.fetchone()[0]
    id_count = cur.execute("SELECT COUNT (id) FROM FoodList WHERE Hide=?",(0,) ).fetchall()[0][0]

    if x>=id_count:
        cur.execute("UPDATE ScrollTrack SET scrollcount =? WHERE username= ?", (0,user.username,))
        cur.execute("SELECT scrollcount FROM ScrollTrack WHERE username = ?",(user.username,))
        x=cur.fetchone()[0]

    cur.execute("SELECT id FROM Foodlist WHERE Hide = ?",(0,))
    temp_id=cur.fetchall()[x][0]
    pic=cur.execute("SELECT FoodPhoto from Foodlist WHERE id = ?", (temp_id,))
    with open("foodphoto.png", "wb") as f:
        f.write(cur.fetchone()[0])
    cur.execute("SELECT FoodName from Foodlist WHERE id = ?", (temp_id,))
    Foodname = cur.fetchone()[0]
    cur.execute("SELECT FoodType from Foodlist WHERE id = ?", (temp_id,))
    Foodtype = cur.fetchone()[0]
    cur.execute("SELECT Halal from Foodlist WHERE id = ?", (temp_id,))
    Foodhalal = cur.fetchone()[0] 
    cur.execute("SELECT Kosher from Foodlist WHERE id = ?", (temp_id,))
    Foodkosher = cur.fetchone()[0] 
    cur.execute("SELECT Vegetarian from Foodlist WHERE id = ?", (temp_id,))
    Foodvege = cur.fetchone()[0] 
    cur.execute("SELECT Allergens from Foodlist WHERE id = ?", (temp_id,))
    Foodaller = cur.fetchone()[0] 
    cur.execute("SELECT Location from Foodlist WHERE id = ?", (temp_id,))
    Foodloca = cur.fetchone()[0] 
    cur.execute("SELECT username from Foodlist WHERE id = ?", (temp_id,))
    Fooduser = cur.fetchone()[0] 

    foodie = Fooduser
    context.user_data["foodie"] = foodie
    x+=1
    cur.execute("UPDATE ScrollTrack set scrollcount=? WHERE username=?",(x,user.username, ))


    select_id=temp_id
    seller_id= Fooduser
    context.user_data["select_id"] = select_id
    context.user_data["seller_id"] = seller_id
    reply_keyboard = [["I would like this!"],
                      ["Please show me another post."],]

    await update.message.reply_photo(photo=open("foodphoto.png", 'rb'), caption=
                                        "Get it if it is to your liking! If not, try looking at another post or view a list of all the posts we have!\n\n\n"
                                         "Food Name: " + Foodname + "\n"
                                         "Food Type: " + Foodtype + "\n"
                                         "Is it Halal?: " + Foodhalal + "\n"
                                         "Is it Kosher?: " + Foodkosher + "\n"
                                         "Is it vegetarian?: " + Foodvege + "\n"
                                         "Potential Allergens: " + Foodaller + "\n"
                                         "Pickup Location: " + Foodloca +"\n\n\n"
                                         "Posted by: " + Fooduser,
                                    reply_markup=ReplyKeyboardMarkup(
                                        reply_keyboard, one_time_keyboard=True, input_field_placeholder="Please select the appropriate option."     
                                    )
    )
    
    return FOODCATA

async def rate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    await update.message.reply_text(
        "Who would you like to rate? Please enter their Telegram handle.", reply_markup=ReplyKeyboardRemove()
         )
    return SELECT_USER


async def userSelect(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    temp_user_to_rate = update.message.text
    await update.message.reply_text(
        "What would you rate them as? (1 to 5, only whole numbers)", reply_markup=ReplyKeyboardRemove()
         )
    return RATING


async def userScore(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    score_rated = update.message.text
    user_id = cur.execute("SELECT username FROM Users WHERE username = ?",
                          (temp_user_to_rate, )).fetchall()[-1][0]
    cur.execute("SELECT rating FROM Users WHERE username = ?",
                (temp_user_to_rate, ))
    average_rating = float(cur.fetchall()[-1][0])
    cur.execute("SELECT times_rated FROM Users WHERE username = ?",
                (temp_user_to_rate, ))
    times_rated = int(cur.fetchall()[-1][0])
    cur.execute("UPDATE Users SET 'rating'= ? WHERE id = ?",
                (str((average_rating*times_rated + score_rated)/times_rated + 1), user_id))
    cur.execute("UPDATE Users SET 'times_rated'= ? WHERE id = ?",
                (str(times_rated + 1), user_id))
    return

SELECT_USER, RATING = range(2)
temp_user_to_rate = ""
ratings_handler = ConversationHandler(
         entry_points=[CommandHandler("rate", rate)],
         states={
             SELECT_USER: [
                 MessageHandler(filters.TEXT, userSelect)
             ],
             RATING: [
                 MessageHandler(filters.Regex("^[1-5]$"), userScore),
             ]
         },
         fallbacks=[CommandHandler("cancel", cancel)],
     )


app.add_handler(ratings_handler)

async def getfood1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start Transaction"""
    conn.rollback()
    user = update.effective_user
    foodie=context.user_data["foodie"] 
    if user.username == foodie:
        await update.message.reply_text("You cannot reserve your own item!\n"
        "Type /getfood to restart.")

        return ConversationHandler.END
            
    
    select_id = int(context.user_data["select_id"])
    seller_id = context.user_data["seller_id"]
    cur.execute("SELECT username FROM Foodlist WHERE id = ?",(select_id,))
    seller=cur.fetchone()[0]
    cur.execute("SELECT chat_id FROM Users WHERE username =?",(seller_id,))
    chatseller=cur.fetchone()[0]
    cur.execute("SELECT rating FROM Users WHERE username = ?",(seller_id,))
    sellerrate=cur.fetchone()[0]
    cur.execute("SELECT times_rated FROM Users WHERE username = ?",(seller_id,))
    sellertimesrate=cur.fetchone()[0]
    cur.execute('''INSERT INTO Transactions
    (seller_user,buyer_user,item_id,seller_complete,buyer_complete,transaction_complete,buyer_chat,seller_chat) VALUES (?, ? ,?, ?,?,?,?,?)''',
    (seller,user.username,select_id,0,0,0,update.effective_chat.id,chatseller)) #NEEDS SELLER'S CHAT_ID

    chat_id= update.effective_chat.id
    cur.execute("SELECT lat FROM Foodlist WHERE ID=?",(select_id,))
    lat=cur.fetchone()[0]
    cur.execute("SELECT Long FROM Foodlist WHERE ID=?",(select_id,))
    lng=cur.fetchone()[0]

    cur.execute("SELECT active_buy FROM Users WHERE username=?",(user.username,))
    eligible=int(cur.fetchone()[0])
    if eligible == 1:
        await update.message.reply_text("You already have a transaction ongoing. Please collect any food items that you have previously confirmed before selecting a new one!"
            )

        return ConversationHandler.END

    else:  
        reply_keyboard = [["Yes, I am sure!"],
                        ["No, let me pick again."]]

        await update.message.reply_text("This food listing was posted by @"+ seller_id +", who has a rating of " + str(sellerrate) +" out of " + str(sellertimesrate) + " reviews.\n\n"
                                        + "Would you like to confirm this selection?",
                                        reply_markup=ReplyKeyboardMarkup(
                                            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Please select the appropriate option."     
                                        )
        )
        await bot.send_location(chat_id=chat_id, latitude=lat, longitude=lng)
        

        return CONFIRMPUR

async def getfood2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Transaction confirmed"""
    user = update.effective_user
    select_id = int(context.user_data["select_id"])
    cur.execute("UPDATE Users SET active_buy=1 WHERE username = ?",(user.username,))
    cur.execute("UPDATE Foodlist SET hide=1 WHERE id = ?",(select_id,))
    cur.execute("SELECT username FROM Foodlist WHERE id=?",(select_id,))
    seller=cur.fetchone()[0]
    conn.commit()
    await update.message.reply_text("You have successfully reserved the food item!\n"+
        "You may also contact the poster directly at @" + seller +" .\n\n\n"
        +"When you have received the food and completed the transaction, please type /completeget to confirm its completion.")

    cur.execute("SELECT Foodname FROM Foodlist WHERE id =?",(select_id,))
    foodname=cur.fetchone()[0]
    cur.execute("SELECT seller_chat FROM Transactions WHERE item_id =?",(select_id,))
    sellerid=cur.fetchone()[0]
    return ConversationHandler.END
    
FOODCATA, CONFIRMPUR = range(2)
getfood_handler = ConversationHandler(
        entry_points=[CommandHandler("getfood", getfood0)],
        states={
            FOODCATA: [MessageHandler(filters.Regex("^(I would like this!)$"), getfood1),
                       MessageHandler(filters.Regex("^(Please show me another post.)$"), getfood0)],
            CONFIRMPUR: [MessageHandler(filters.Regex("^(Yes, I am sure!)$"), getfood2),
                         MessageHandler(filters.Regex("^(No, let me pick again.)$"), getfood0)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

##complete
async def completeget(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """For Buyer to confirm any listing."""
    user=update.effective_user
    cur.execute("SELECT active_buy FROM Users WHERE username = ?",(user.username,))
    usercat=cur.fetchone()[0]
    if usercat == 0:
        await update.message.reply_text("You do not have an active order!")
    else:
        cur.execute("UPDATE Transactions SET 'buyer_complete' = 1 WHERE 'buyer_user' = ?",(user.username,))
        cur.execute("UPDATE Users SET active_buy=0 WHERE username=?",(user.username,))
        cur.execute("DELETE FROM Foodlist WHERE id=?",(itemid,))
        cur.execute("DELETE FROM Transactions WHERE id=?",(itemid,))
        cur.execute("SELECT item_id FROM Transactions WHERE buyer_user = ?",(user.username,))
        itemid=cur.fetchone()[0]
        cur.execute("SELECT Foodname FROM Foodlist WHERE id =?",(itemid,))
        foodname=cur.fetchone()[0]
        conn.commit()
        conn.commit()
        await update.message.reply_text("Order \""+ foodname +"\" has been completed! Type /rating to leave the poster a rating.")
            





app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help))
app.add_handler(CommandHandler("completeget", completeget))
app.add_handler(postfood_handler)
app.add_handler(myposts_handler)
app.add_handler(getfood_handler)
app.add_handler(myposts_handler)
app.add_handler(completepost_handler)
app.run_polling()

# async def getfood(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Shows food items available"""
#     user = update.message.from_user
#     id_count = cur.execute("SELECT COUNT (id) FROM FoodList").fetchall()[0][0]
#     display_times = 3 if id_count > 3 else id_count
#     for i in range(display_times):
#         cur.execute("SELECT FoodName FROM Foodlist")
#         Foodname=cur.fetchall()[i][0]

#         a = cur.execute("SELECT FoodPhoto FROM Foodlist")
#         with open("foodphoto.png", "wb") as f:
#             f.write(cur.fetchall()[i][0])

#         cur.execute("SELECT FoodType FROM Foodlist")
#         Foodtype = cur.fetchall()[i][0]

#         cur.execute("SELECT Halal FROM Foodlist")
#         Foodhalal = cur.fetchall()[i][0]

#         cur.execute("SELECT Kosher FROM Foodlist")
#         Foodkosher = cur.fetchall()[i][0]

#         cur.execute("SELECT Vegetarian FROM Foodlist")
#         Foodvege = cur.fetchall()[i][0]

#         cur.execute("SELECT Allergens FROM Foodlist")
#         Foodaller = cur.fetchall()[i][0]

#         cur.execute("SELECT Location FROM Foodlist")
#         Foodloca = cur.fetchall()[i][0]

#         cur.execute("SELECT username FROM Foodlist")
#         Foodseller = cur.fetchall()[i][0]

#         logger.info("Bio of %s: %s", user.first_name, update.message.text)
#         await update.message.reply_photo(photo=open("foodphoto.png", 'rb'), caption="Thank you! Here is a preview of your post:\n\n" +
#                                          "Food Name: " + Foodname + "\n"
#                                          "Food Type: " + Foodtype + "\n"
#                                          "Is it Halal?: " + Foodhalal + "\n"
#                                          "Is it Kosher?: " + Foodkosher + "\n"
#                                          "Is it vegetarian?: " + Foodvege + "\n"
#                                          "Potential Allergens: " + Foodaller + "\n"
#                                          "Pickup Location: " + Foodloca +"\n\n\n"
#                                          "This food posting was made by @"+ Foodseller
                                    
#                                          )
#     await update.message.reply_text(
#         "Alright! Now display the first 3 posts. "
#         )


# async def rate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     user=update.effective_user

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


