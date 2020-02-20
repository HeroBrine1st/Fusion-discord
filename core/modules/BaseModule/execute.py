import discord

from core import Command, CommandResult, FuturePermission
from core.utils import DotDict

premade_code = """
import io
import asyncio
from contextlib import redirect_stdout
async def execute():
    out = io.StringIO()
    is_error = False
    with redirect_stdout(out):
        try:
%s
        except Exception as e:
            is_error = True
            out.write(str(e))
    if is_error:
        await bot.send_error_embed(message.channel, out.getvalue(), "Код выполнен с ошибкой")
    else:
        if len(out.getvalue()) <= 2048:
            await bot.send_ok_embed(message.channel, out.getvalue(), "Код успешно выполнен")
        else:
            await bot.send_ok_embed(message.channel, "Размер вывода превышает 2048 символов", "Код успешно выполнен")
asyncio.ensure_future(execute())
"""


class MyGlobals(dict):
    # noinspection PyMissingConstructor
    def __init__(self, globs, locs):
        self.globals = globs
        self.locals = locs

    def __getitem__(self, name):
        try:
            return self.locals[name]
        except KeyError:
            return self.globals[name]

    def __setitem__(self, name, value):
        self.globals[name] = value

    def __delitem__(self, name):
        del self.globals[name]


def _exec(code: str, g, l):
    d = MyGlobals(g, l)
    code_for_embed = ""
    for line in code.splitlines(keepends=True):
        code_for_embed = code_for_embed + "            " + line
    exec(premade_code % code_for_embed, d)


class CommandExecute(Command):
    name = "execute"
    description = "Execute python code from a message"
    arguments = "```Python Code```"
    future_permissions = {FuturePermission.OWNER}

    async def execute(self, message: discord.Message, args: list, keys: DotDict) -> CommandResult:
        code = message.content.split("```")
        if len(code) < 3:
            return CommandResult.arguments_insufficient
        bot = self.bot
        _exec(code[1].strip().rstrip(), globals(), locals())

        return CommandResult.success
