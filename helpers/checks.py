from discord.ext import commands

import settings


def is_dev():
    def predicate(ctx):
        return ctx.message.author.id in settings.devs
    return commands.check(predicate)
