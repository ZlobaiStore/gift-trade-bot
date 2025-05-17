import logging
import os
from aiogram import Bot, Dispatcher, types, Router
from aiogram.enums import ParseMode
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from bs4 import BeautifulSoup
import aiohttp
import asyncio

TOKEN = os.getenv('TELEGRAM_TOKEN')
if not TOKEN:
    raise RuntimeError('TELEGRAM_TOKEN is not set')

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
router = Router()
dp.include_router(router)

@router.message(Command("start"))
async def start(message: Message):
    await message.answer(
        """Привет! Я GiftTreadeBot — аналитика Telegram Gifts и криптовалют.
Доступные команды:
/help — список команд
/course — курс TON, BTC, ETH
/price <название> — цена подарка с фото
/gift_top — топ подарков
""")

@router.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(
        """📌 Команды:
/start — запуск
/course — курс TON, BTC, ETH
/price <название> — узнать цену подарка
/gift_top — топ подарков
""")

@router.message(Command("course"))
async def course_cmd(message: Message):
    url = "https://api.coingecko.com/api/v3/simple/price?ids=toncoin,bitcoin,ethereum&vs_currencies=usd,rub"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
    msg = "📊 Актуальные курсы:\n"
    for coin, values in data.items():
        name = coin.upper()
        usd = values['usd']
        rub = values['rub']
        msg += f"{name}: {rub:.0f}₽ / ${usd:.2f}\n"
    await message.answer(msg)

@router.message(Command("gift_top"))
async def gift_top(message: Message):
    await message.answer("ТОП подарков:\n1. Cyber Rabbit\n2. Golden Rocket\n3. Pixel Smile")

@router.message(Command("price"))
async def gift_price(message: Message):
    name = message.text.replace("/price", "").strip().lower()
    if not name:
        await message.answer("Напиши название подарка: /price Cyber Rabbit")
        return

    async with aiohttp.ClientSession() as session:
        async with session.get("https://fragment.com/gifts") as resp:
            html = await resp.text()

    soup = BeautifulSoup(html, "html.parser")
    gifts = soup.select("a[href^='/gift/']")

    for gift in gifts:
        title_el = gift.select_one(".text-xl")
        if not title_el:
            continue
        title = title_el.text.strip()
        if name in title.lower():
            price_el = gift.select_one(".text-green, .text-yellow")
            price = price_el.text.strip() if price_el else "Цена не найдена"
            img_el = gift.select_one("img")
            img_url = "https://fragment.com" + img_el["src"] if img_el else None

            text = f"🎁 <b>{title}</b>\nЦена: {price}"
            if img_url:
                async with aiohttp.ClientSession() as session:
                    async with session.get(img_url) as img_resp:
                        if img_resp.status == 200:
                            with open("gift.jpg", "wb") as f:
                                f.write(await img_resp.read())
                            photo = FSInputFile("gift.jpg")
                            await message.answer_photo(photo, caption=text, parse_mode="HTML")
                            os.remove("gift.jpg")
                            return
            await message.answer(text, parse_mode="HTML")
            return

    await message.answer("Подарок не найден.")

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
