import logging
import os

from prometheus_client import start_http_server

import settings
from mighty_nog import MightyNog
from helpers import commands_info


def setup_logging():
    """Me being playful with logging"""
    log = logging.getLogger()
    log.setLevel(logging.INFO)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter_console = logging.Formatter(
        '\033[92m{asctime} \033[0m| '
        '\033[94m{name:>18}.py \033[0m-> '
        '\033[93m{levelname:>8}: \033[0m'
        '{message}',
        "%d.%m.%Y %H:%M:%S",
        style='{'
    )
    console.setFormatter(formatter_console)
    log.addHandler(console)


setup_logging()

bot = MightyNog(
    command_prefix=os.getenv('NOG_CMD_PREFIX', '!'),
    description=commands_info.main,
    pm_help=True,
    db=os.environ['NOG_DB_DSN']
)


if __name__ == '__main__':
    start_http_server(8000)
    for extension in settings.extensions:
        bot.load_extension(extension)
    bot.run(os.environ.get('NOG_BOT_TOKEN'))
