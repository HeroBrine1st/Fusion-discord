import discord

from typing import Dict
from core import ModuleBase, CommandResult, Command, Bot, Client, clients, CommandException


class ClientMethodCommand(Command):
    name = "clraw"
    description = "Послать запрос клиенту протокола."
    arguments = "<client> <method...>"

    async def execute(self, message: discord.Message, args: list, keys: Dict[str, bool]) -> CommandResult:
        if len(args) < 2:
            return CommandResult.arguments_insufficient
        try:
            client = clients[args[0]]
        except KeyError:
            raise CommandException("Такого клиента не существует.")
        result = await client.method(*args[1:])
        await message.channel.send(str(result))
        return CommandResult.success


class Module(ModuleBase):
    name = "ProtocolModule"
    description = "Взаимодействие с клиентами протокола."

    def on_load(self, bot: Bot):
        self.register(ClientMethodCommand(bot))

    async def run(self, bot: Bot):
        guild: discord.Guild = bot.get_guild(547876610032926757)
        client = Client(auth_token="password", channel=guild.get_channel(668454176631554049), client=bot, name="Test")
        client.add()
