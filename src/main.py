import logging
import os

from discord.ext import commands

from src import settings
from src.events import BotEvents
from src.helpers import descriptions

bot = commands.Bot(
    command_prefix=os.getenv('NOG_CMD_PREFIX', '!'),
    description=descriptions.main,
    pm_help=True
)

BotEvents(bot)


def setup_logging():
    """Me being playful with logging"""
    log = logging.getLogger()
    log.setLevel(logging.INFO)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter_console = logging.Formatter(
        '\033[92m{asctime} \033[0m| '
        '\033[94m{name:>18}.py \033[0m-> '
        '\033[95m{funcName:>15}() \033[0m-> '
        '\033[96m{lineno:4} \033[0m| '
        '\033[93m{levelname:>8}: \033[0m'
        '{message}',
        "%d.%m.%Y %H:%M:%S",
        style='{'
    )
    console.setFormatter(formatter_console)
    log.addHandler(console)


if __name__ == '__main__':
    setup_logging()
    for extension in settings.extensions:
        bot.load_extension(extension)
    bot.run(os.environ.get('NOG_BOT_TOKEN'))
