import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.utils.markdown import hbold

from aiohttp import ClientSession
from bs4 import BeautifulSoup

TOKEN = os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

async def get_course():
    return {
        "TON": "199.50₽",
        "BTC": "5 843 000₽",
        "ETH": "275 000₽"
    }

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(f"Привет, {hbold(message.from_user.full_name)}!")
Я аналитический бот по Telegram Gifts и криптовалюте. Напиши /help для списка команд.")

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("📌 Команды:
/course — курс TON, BTC, ETH
/price <название> — узнать цену подарка
/gift_top — топ подарков
/help — справка")

@dp.message(Command("course"))
async def cmd_course(message: Message):
    data = await get_course()
    text = "\n".join([f"{coin}: {value}" for coin, value in data.items()])
    await message.answer(f"📊 Актуальные курсы:
{text}")

@dp.message(Command("gift_top"))
async def cmd_gift_top(message: Message):
    await message.answer("🎁 Топ Telegram Gifts:
1. Золотая Ракета
2. Медвежонок
3. Огонь")

@dp.message(Command("price"))
async def cmd_price(message: Message):
    name = message.text.replace("/price", "").strip().lower()
    if not name:
        await message.answer("Введите название подарка: /price Медвежонок")
        return
    await message.answer(f"🔍 Цена на подарок '{name.title()}':
~120 TON (~23 000₽)")

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
