from telegram import *
from telegram.ext import *
import requests
import os
from dotenv import load_dotenv
import logging


BOT_TOKEN = "5494197007:AAHd9ZEPe1BqdhlGJdf0LzJRoVP-S9XJSw4"
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

bot= ApplicationBuilder().token(BOT_TOKEN).build()

bot.run_polling()