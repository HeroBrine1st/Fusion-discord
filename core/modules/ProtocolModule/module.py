import discord

from core import ModuleBase, CommandResult, Command, Bot, Client, clients, CommandException, FuturePermission, DotDict
from bot import settings


class ClientMethodCommand(Command):
    name = "clraw"
    description = "Послать запрос клиенту протокола. This is debug feature."
    arguments = "<method...> --client=default"
    future_permissions = {FuturePermission.OWNER}

    async def execute(self, message: discord.Message, args: list, keys: DotDict) -> CommandResult:
        if len(args) < 2:
            return CommandResult.arguments_insufficient
        client_name = keys.client or "default"
        try:
            client = clients[client_name]
        except KeyError:
            raise CommandException("Такого клиента не существует.")
        result = await client.method(*args)
        embed = self.bot.get_ok_embed(title="Результаты выполнения метода", description="%s значений получено" %
                                                                                        len(result))
        for i, value in enumerate(result):
            embed.add_field(name="Значение %s" % i, value=str(value))
        await message.channel.send(embed=embed)
        return CommandResult.success


class Module(ModuleBase):
    name = "ProtocolModule"
    description = "Взаимодействие с клиентами протокола."

    def on_load(self, bot: Bot):
        self.register(ClientMethodCommand(bot))

    async def run(self, bot: Bot):
        for client_name in settings.protocol_clients:
            client_config = settings.protocol_clients[client_name]
            chnl = bot.get_guild(client_config["GUILD_ID"])
            client = Client(auth_token=client_config["AUTH_TOKEN"],
                            channel=chnl.get_channel(client_config["CHANNEL_ID"]),
                            bot_client=bot, name=client_name)
            client.add()
