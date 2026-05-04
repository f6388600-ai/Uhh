import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from loader import load_plugins
from utils.logger import logger
from keep_alive import keep_alive

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def main():
    logger.info("🚀 Bot Started")
    load_plugins(dp)
    await dp.start_polling(bot)

if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())
