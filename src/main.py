import logging
import os
import pathlib

from prometheus_client import start_http_server

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
