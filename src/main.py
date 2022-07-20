import asyncio

import config
from services.logging import setup_logging
from services.database.database import init_database, stop_database
# from services.dispatcher.dispatcher import full_reload_database
#  In case I would like to reload photos

from telegram_bot.bot import PBBot


def main():
    setup_logging()
    try:
        asyncio.run(init_database())
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        bot = PBBot(config.TELEGRAM_API_TOKEN)
        print("Starting the bot")
        bot.start()
    finally:
        asyncio.run(stop_database())


if __name__ == '__main__':
    main()

