import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiohttp import web

TOKEN = "8685388983:AAFwjfV-RvOrq4vT1hI_SxIqIPd0-lZ6cZg"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# /start buyrug'iga javob qaytarish
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Salom! Bot muvaffaqiyatli ishga tushdi va Render'da 24/7 ishlayapti!")

# Har qanday yozilgan xabarni qaytarish (echo)
@dp.message()
async def echo_handler(message: types.Message):
    await message.answer(f"Siz yozdingiz: {message.text}")

async def handle(request):
    return web.Response(text="Bot ishlayapti!")

async def main():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
