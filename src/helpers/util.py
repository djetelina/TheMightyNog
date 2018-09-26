# coding=utf-8
from discord.ext import commands


def channel_uid_from_ctx(ctx: commands.Context) -> str:
    guild = getattr(ctx.guild, "name", "None")
    channel = getattr(ctx.channel, "name", "None")
    return f'{guild}-{channel}'
