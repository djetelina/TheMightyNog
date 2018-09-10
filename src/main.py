import logging
import os
import pathlib

from prometheus_client import start_http_server
from raven.conf import setup_logging as add_sentry_handler
from raven.handlers.logging import SentryHandler

import settings
from mighty_nog import MightyNog
from helpers import commands_info


def setup_logging():
    """Me being playful with logging"""
    log = logging.getLogger()
    log.setLevel(logging.INFO)
    if os.getenv('NOG_LOG_STDOUT', False):
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
    log_path = pathlib.Path(__file__).resolve().parent.parent / 'log'
    log_path.mkdir(exist_ok=True)
    file_handler = logging.FileHandler(log_path / 'nog_info.log')
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('[{asctime}] {name} | {levelname}: {message}', "%d.%m.%Y %H:%M:%S", style='{')
    file_handler.setFormatter(file_formatter)
    log.addHandler(file_handler)

    sentry_handler = SentryHandler(os.environ['NOG_SENTRY_URL'])
    sentry_handler.setLevel(logging.ERROR)
    add_sentry_handler(sentry_handler)


setup_logging()

bot = MightyNog(
    command_prefix=os.getenv('NOG_CMD_PREFIX', '!'),
    description=commands_info.main,
    pm_help=True,
    db=os.environ['NOG_DB_DSN'],
    sg_password=os.environ['NOG_SG_PASSWORD']
)


if __name__ == '__main__':
    start_http_server(8000)
    for extension in settings.extensions:
        bot.load_extension(extension)
    bot.run(os.environ.get('NOG_BOT_TOKEN'))
