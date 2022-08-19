# Food Hero

_A Telegram bot for users to share their leftover food._

Food wastage has been an increasing worrying issue over the years, and this bot aims to reduce it by creating a platform for sharing spare or leftover food.
This bot was created within 24 hours for the Lifehack 2022 hackathon. You may find out more about our submission here: https://devpost.com/software/kalilinux

## Dependencies
1. python-telegram-bot
2. googlemaps
3. requests


## How to Deploy
1. Install all dependencies using `pip install [packagename]` 
2. Install Python 3
3. Clone this repository to by running `git clone https://github.com/oeggy/TelegramBot`
4. Get inside the repository folder by running `cd TelegramBot`
5. Using Telegram, create your own bot with Botfather and obtain an API key.
6. Edit Lifehack.py with your editor and replace the API key with your own.
7. Finally, run the program using `python3 Lifehack.py`


## How to Use
1. Run `/start`
2. To share your leftover food, run `/postfood`
3. To retrieve food someone else has posted, run `/getfood`
4. To see what food you have posted and to remove expired listings, run `/myposts`
5. Once a transaction has been completed, run `/completeseller` if your food been given out or `/completebuyer` if you have recieved your food.
