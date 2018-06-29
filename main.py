import logging
import os

from discord.ext import commands

import settings
from events import BotEvents
from helpers import descriptions

bot = commands.Bot(
    command_prefix=os.getenv('NOG_CMD_PREFIX', '!'),
    description=descriptions.main,
    pm_help=True
)

BotEvents(bot)

if __name__ == '__main__':
    log = logging.getLogger()
    log.setLevel(logging.INFO)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    log.addHandler(console)
    for extension in settings.extensions:
        bot.load_extension(extension)
    bot.run(os.environ.get('NOG_BOT_TOKEN'))
