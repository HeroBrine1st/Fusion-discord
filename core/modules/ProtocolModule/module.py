import discord

from core import ModuleBase, CommandResult, Command, Bot, ProtocolService, services, CommandException, FuturePermission, \
    DotDict, \
    Logger, EventListener, Priority
from bot import settings


class ClientMethodCommand(Command):
    name = "clexecute"
    description = "Выполнить Lua код на клиенте протокола."
    arguments = "<method...> --service=default"
    future_permissions = {FuturePermission.GROUP}

    async def execute(self, message: discord.Message, args: list, keys: DotDict) -> CommandResult:
        if len(args) < 2:
            return CommandResult.arguments_insufficient
        client_name = keys.service or "default"
        code = message.content.split("```")
        if len(code) < 3:
            code = " ".join(args)
        else:
            code = code[1].strip().rstrip()
        try:
            client = services[client_name]
        except KeyError:
            raise CommandException("Такого сервиса не существует.")
        result = await client.execute(code)
        embed = self.bot.get_ok_embed(title="Результаты выполнения кода", description="%s значений получено" %
                                                                                      len(result))
        for i, value in enumerate(result):
            embed.add_field(name="Значение %s" % i, value=str(value))
        await message.channel.send(embed=embed)
        return CommandResult.success


class ClientsCommand(Command):
    name = "clients"
    description = "Список клиентов"


class Module(ModuleBase):
    name = "ProtocolModule"
    description = "Взаимодействие с клиентами протокола."
    logger = Logger(app="ProtocolModule")

    @EventListener
    def on_load(self, bot: Bot):
        self.register(ClientMethodCommand(bot))

    @EventListener(priority=Priority.HIGH)
    async def run(self, bot: Bot):
        for service_name in settings.protocol_services:
            self.logger.info("Creating service %s." % service_name)
            client_config = settings.protocol_services[service_name]
            guild = bot.get_guild(client_config["GUILD_ID"])
            client = ProtocolService(auth_token=client_config["AUTH_TOKEN"],
                                     channel=guild.get_channel(client_config["CHANNEL_ID"]),
                                     bot_client=bot, name=service_name)
            client.add()
