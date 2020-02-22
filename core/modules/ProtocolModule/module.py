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


class ClientDisconnectCommand(Command):
    name = "clexit"
    description = "Отключить удаленный клиент"
    arguments = "--service=default"
    future_permissions = {FuturePermission.GROUP}

    async def execute(self, message: discord.Message, args: list, keys: DotDict) -> CommandResult:
        client_name = keys.service or "default"
        try:
            client = services[client_name]
        except KeyError:
            raise CommandException("Такого сервиса не существует.")
        client.disconnect()
        return CommandResult.success


class ClientsCommand(Command):
    name = "clients"
    description = "Список клиентов"

    async def execute(self, message: discord.Message, args: list, keys: DotDict) -> CommandResult:
        embed = self.bot.get_info_embed(title="Список клиентов")
        connected = 0

        for name in services:
            service = services[name]
            if service.connected:
                connected += 1
            embed.add_field(name=name, value="Подключен" if service.connected else "Отключен")
        embed.description = "Всего %s, "
        message.channel.send(embed=embed)
        return CommandResult.success


class Module(ModuleBase):
    name = "ProtocolModule"
    description = "Взаимодействие с клиентами протокола."
    logger = Logger(app="ProtocolModule")

    @EventListener
    def on_load(self, bot: Bot):
        self.register(ClientMethodCommand(bot))
        self.register(ClientDisconnectCommand(bot))
        self.register(ClientsCommand(bot))

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

    @EventListener
    async def on_unload(self):
        self.logger.info("Soft-closing connections for all clients.")
        for service_name in services:
            service = services[service_name]
            service.disconnect()
        self.logger.info("Waiting for threads become dead.")

    @EventListener
    def on_emergency_unload(self):
        self.logger.info("Closing connections for all clients.")
        for service_name in services:
            service = services[service_name]
            if service.connected:
                service.remote_socket.close()
        self.logger.info("Waiting for threads become dead.")
