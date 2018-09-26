"""
Trivia game for Artifact game
"""
import asyncio
from pathlib import Path
from typing import Dict

import toml
from discord import TextChannel, Message
from discord.ext import commands

from helpers import commands_info
from helpers.util import channel_uid_from_ctx
from logic.artifact.trivia import TriviaGame


class Trivia:
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        questions_path = (Path(__file__).resolve().parent.parent.parent / 'logic' / 'artifact' / 'trivia_questions.tml')
        with open(questions_path, 'r') as f:
            self.questions = toml.load(f)['questions']
        self.__channel_games: Dict[str, TriviaGame] = {}
        self.bot.add_listener(self.answer_question, 'on_message')

    @commands.group(**commands_info.artifact_trivia)
    async def trivia(self, ctx: commands.Context) -> None:
        async with ctx.typing():
            if ctx.invoked_subcommand is None:
                if channel_uid_from_ctx(ctx) in self.__channel_games:
                    await ctx.send('There is an Artifact trivia game in progress')
                elif not isinstance(ctx.channel, TextChannel):
                    await ctx.send("You can only play Artifact trivia in Server text channels.")
                else:
                    await ctx.send("There's no Artifact trivia game going on, try `!trivia start` to start one!")

    @trivia.command(**commands_info.artifact_trivia_start)
    async def _start(self, ctx: commands.Context) -> None:
        if ctx.channel in self.__channel_games:
            return
        elif not isinstance(ctx.channel, TextChannel):
            await ctx.send("You can only play Artifact trivia in Server text channels.")
        else:
            channel = channel_uid_from_ctx(ctx)
            self.__channel_games[channel] = TriviaGame(self.questions, 20)
            asyncio.ensure_future(self.play(ctx))

    @trivia.command(**commands_info.artifact_trivia_stop)
    async def _stop(self, ctx: commands.Context) -> None:
        if channel_uid_from_ctx(ctx) not in self.__channel_games:
            await ctx.send('There is no game to stop')
        else:
            self.__channel_games[channel_uid_from_ctx(ctx)].stop()
            del self.__channel_games[channel_uid_from_ctx(ctx)]
            await ctx.send('Game stopped')

    async def play(self, ctx: commands.Context) -> None:
        game = self.__channel_games[channel_uid_from_ctx(ctx)]
        async for line in game.play():
            await ctx.send(line)
        if not game.stopped:
            await ctx.send('Those are all my questions, thank you for playing!')
            del self.__channel_games[channel_uid_from_ctx(ctx)]

    async def answer_question(self, message: Message) -> None:
        try:
            channel_uid = f'{message.guild.name}-{message.channel.name}'
        except AttributeError:
            return
        if channel_uid in self.__channel_games:
            if self.__channel_games[channel_uid].answer_question(message.content):
                await message.channel.send(f'Correct answer from {message.author.name}!')


def setup(bot) -> None:
    bot.add_cog(Trivia(bot))
