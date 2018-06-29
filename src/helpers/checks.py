"""Home for decorators that limit commands to specific users/groups etc."""
from discord.ext import commands

import settings


def is_dev():
    """For limiting commands to developers (reloads and such)"""
    def predicate(ctx):
        return ctx.message.author.id in settings.devs
    return commands.check(predicate)
