import os
import requests
import time
from bs4 import BeautifulSoup
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.executor import start_webhook


logging.basicConfig(level=logging.DEBUG)

loop = asyncio.get_event_loop()
BOT_TOKEN = os.environ['TOKEN']
bot = Bot(BOT_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage, loop=loop)

WEBHOOK_HOST = 'https://btc4me-bot.herokuapp.com'  # name your app
WEBHOOK_PATH = '/webhook/'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = os.environ.get('PORT')


class Currency:
    def __init__(self):
        self.differece = 500.0
        self.BTC_DOLLAR = 'https://www.google.com/search?q=btc+in+dollars&oq=btc+in+dolla&aqs=chrome.1.69i57j0l7.11710j1j4&sourceid=chrome&ie=UTF-8'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}
        self.current_currency = float(self.get_currency().replace('.', '').replace(',', '.'))

    def get_currency(self):
        page = requests.get(self.BTC_DOLLAR, headers=self.headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        convert = soup.findAll("span", {"class": "DFlfde",
                                        "class": "SwHCTb",
                                        "data-precision": 2})
        return convert[0].text

    def check_currency(self):
        currency = self.get_currency()
        currency = currency.replace('.', '')
        return float(currency.replace(',', '.'))


@dp.message_handler(commands='start')
async def send_to_admin(message: types.Message):
    await bot.send_message(message.chat.id, "I'm working")
    currency = Currency()
    while True:
        btc = currency.check_currency()
        current = currency.current_currency
        if abs(current - btc) >= currency.differece:
            await bot.send_message(message.chat.id,
                                   "Now Bitcoin costs {}$".format(str(btc)))
            currency.current_currency = btc
        else:
            pass
        time.sleep(1000)


async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)


if __name__ == '__main__':
    start_webhook(dispatcher=dp, webhook_path=WEBHOOK_PATH,
                  on_startup=on_startup,
                  host=WEBAPP_HOST, port=WEBAPP_PORT)
