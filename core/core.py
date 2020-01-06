import os

from core.bot import Bot

bot = Bot()

bot.run(os.getenv("fds_token"))