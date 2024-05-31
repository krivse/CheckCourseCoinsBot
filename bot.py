import os

import coinmarketcapapi
import asyncio
import logging
from os import getenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from tg_bot.handlers import register_handlers

load_dotenv()
logger = logging.getLogger(__name__)


async def main():
    """Starting the bot and configuring the logger, coinmarketcap api."""
    # Configure logger for aiogram events
    dispatcher_logger = logging.getLogger('aiogram.event')
    dispatcher_logger.setLevel(logging.ERROR)
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s'
    )
    logger.info('Bot started!')
    bot = Bot(
        token=getenv('BOT_TOKEN'),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())
    register_handlers(dp)

    try:
        await dp.start_polling(bot)
    finally:
        await dp.storage.close()
        logger.error('Bot stopped!')


if __name__ == '__main__':
    asyncio.run(main())
