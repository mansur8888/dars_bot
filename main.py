import asyncio
import os
from aiogram import Bot, Dispatcher
from aiohttp import web

TOKEN = "BOT_TOKENINGIZNI_SHUYERGA_YOZING"

bot = Bot(token=TOKEN)
dp = Dispatcher()

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
