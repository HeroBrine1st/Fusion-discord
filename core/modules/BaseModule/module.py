import threading
import discord

from bot.settings import cmd_prefix
from core import CommandException, CommandResult, Bot, Command, ModuleBase, FuturePermission, ModuleManager, DotDict, \
    EventListener
from django.db import connection
from beautifultable import BeautifulTable
from .execute import CommandExecute
from .models import SPPermissions


class RestartCommand(Command):
    name = "restart"
    description = "Stops bot and allows bash script start again"
    future_permissions = {FuturePermission.OWNER}

    async def execute(self, message: discord.Message, args: list, keys: DotDict) -> CommandResult:
        await ModuleManager().unload()
        try:
            self.bot.loop.run_until_complete(self.bot.logout())
        except Exception:
            pass
        return CommandResult.success


class HelpCommand(Command):
    name = "help"
    description = "Command list"
    arguments = "--all"

    async def execute(self, message: discord.Message, args: list, keys: DotDict) -> CommandResult:
        module_manager = ModuleManager()
        embed = self.bot.get_special_embed(title="Список%s команд" % (" доступных" if "all" not in keys else ""),
                                           description="Ваши права discord: %s\nВаши права future: %s" %
                                                       (hex(message.author.guild_permissions.value),
                                                        bin(module_manager.get_sp_permissions(message.author.id))),
                                           color=0xb63a6b)
        for command in module_manager.commands.values():
            if "all" in keys or module_manager.check_permissions(message.author.guild_permissions, command.permissions) \
                    and module_manager.check_sp_permissions(message.author.id, command.future_permissions):
                embed.add_field(name="%s%s %s" % (cmd_prefix, command.name, command.arguments),
                                value=command.description, inline=False)
        await message.channel.send(embed=embed)
        return CommandResult.success


class SQLCommand(Command):
    name = "sql"
    description = "Perform a raw SQL query"
    arguments = "[query]"
    future_permissions = {FuturePermission.OWNER}

    async def execute(self, message: discord.Message, args: list, keys: DotDict) -> CommandResult:
        sql_query = message.content[len(cmd_prefix + self.name) + 1:]
        with connection.cursor() as c:
            try:
                c.execute(sql_query)
            except Exception as e:
                raise CommandException(error=type(e).__name__ + ": " + str(e),
                                       title="Произошла ошибка при выполнении SQL")
            if "commit" in keys:
                connection.commit()
            desc = c.description
            if desc is None:
                return CommandResult.success
            fields = [field[0] for field in desc]
            results = c.fetchall()
        tbl = BeautifulTable()
        tbl.column_headers = fields
        for result in results:
            tbl.append_row(result)
        embed = self.bot.get_special_embed(title="Результат выполнения SQL запроса", description="```%s```" % tbl,
                                           color=0xb63a6b)
        if not results:
            embed.description = "Нет результатов."
            embed.color = 0xFF4C4C
        await message.channel.send(embed=embed)
        return CommandResult.success


class ActiveThreadsCommand(Command):
    name = "threads"
    description = "Show active threads"

    async def execute(self, message: discord.Message, args: list, keys: DotDict) -> CommandResult:
        embed = self.bot.get_info_embed(title="Активные потоки")
        for thread in threading.enumerate():
            data = ["TID %s" % thread.ident]
            if thread.isDaemon():
                data.append("Daemon")
            if thread.isAlive():
                data.append("Alive")
            embed.add_field(name=thread.name, value=", ".join(data))
        await message.channel.send(embed=embed)
        return CommandResult.success


class DebugArgsCommand(Command):
    name = "argsdbg"
    description = "Debug arguments parsing"

    async def execute(self, message: discord.Message, args: list, keys: DotDict) -> CommandResult:
        embed = self.bot.get_info_embed(title="Результаты разбора аргументов")
        embed.add_field(name="Args", value=args)
        embed.add_field(name="Kwargs", value=keys)
        await message.channel.send(embed=embed)
        return CommandResult.success


class PermissionsCommand(Command):
    name = "permissions"
    description = "Permission managing"
    arguments = "[add/remove] <permission> <mentions...>"
    future_permissions = {FuturePermission.OWNER}

    async def execute(self, message: discord.Message, args: list, keys: DotDict) -> CommandResult:
        if len(args) < 2:
            return CommandResult.arguments_insufficient
        if args[0] == "add":
            perm = args[1]
            try:
                perm = FuturePermission[perm.upper()]
            except KeyError:
                raise CommandException("Permission \"%s\" don't exists." % perm.upper())
            embed = self.bot.get_ok_embed(title="Установка прав")
            success = 0
            failure = 0
            for mention in message.mentions:
                perms = ModuleManager().get_sp_permissions(mention.id)
                if perms & perm.value == perm.value:
                    embed.add_field(name="Установка разрешения %s пользователю %s не удалась." % (perm, str(mention)),
                                    value="Он уже имеет такое разрешение")
                    failure += 1
                else:
                    try:
                        db_perms: SPPermissions = SPPermissions.objects.get(user_id=mention.id)
                    except SPPermissions.DoesNotExist:
                        db_perms: SPPermissions = SPPermissions()
                        db_perms.user_id = mention.id
                    db_perms.permissions |= perm.value
                    db_perms.save()
                    embed.add_field(name="%s - успешно" % str(mention),
                                    value="Текущие права: %s" % bin(db_perms.permissions))
                    success += 1
            embed.description = "%s успешно\n%s с ошибками" % (success, failure)
            await message.channel.send(embed=embed)
        elif args[0] == "remove":
            perm = args[1]
            try:
                perm = FuturePermission[perm.upper()]
            except KeyError:
                raise CommandException("Permission \"%s\" don't exists." % perm.upper())
            embed = self.bot.get_ok_embed(title="Удаление прав")
            success = 0
            failure = 0
            for mention in message.mentions:
                perms = ModuleManager().get_sp_permissions(mention.id)
                if perms & perm.value != perm.value:
                    embed.add_field(name="Удаление разрешения %s у пользователя %s невозможно." % (perm, str(mention)),
                                    value="Он не имеет такого разрешения.")
                    failure += 1
                else:
                    try:
                        db_perms: SPPermissions = SPPermissions.objects.get(user_id=mention.id)
                    except SPPermissions.DoesNotExist:
                        db_perms: SPPermissions = SPPermissions()
                        db_perms.user_id = mention.id
                    db_perms.permissions ^= perm.value
                    db_perms.save()
                    embed.add_field(name="%s - успешно" % str(mention),
                                    value="Текущие права: %s" % bin(db_perms.permissions))
                    success += 1
            embed.description = "%s успешно\n%s с ошибками" % (success, failure)
            await message.channel.send(embed=embed)
        else:
            return CommandResult.arguments_insufficient
        return CommandResult.success


class Module(ModuleBase):
    name = "BaseModule"
    description = "Basic module for minimal functionality"

    @EventListener
    def on_load(self, bot: Bot):
        self.register(RestartCommand(bot))
        self.register(HelpCommand(bot))
        self.register(SQLCommand(bot))
        self.register(CommandExecute(bot))
        self.register(ActiveThreadsCommand(bot))
        self.register(DebugArgsCommand(bot))
        self.register(PermissionsCommand(bot))
