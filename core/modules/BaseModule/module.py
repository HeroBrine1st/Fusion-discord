import discord

from typing import Dict
from bot.settings import cmd_prefix
from core import CommandException, CommandResult, Bot, Command, ModuleBase, FuturePermission, ModuleManager
from django.db import connection
from beautifultable import BeautifulTable


class RestartCommand(Command):
    name = "restart"
    description = "Stops bot and allow bash script to restart it"
    future_permissions = {FuturePermission.OWNER}

    async def execute(self, message: discord.Message, args: list, keys: Dict[str, bool]) -> CommandResult:
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

    async def execute(self, message: discord.Message, args: list, keys: Dict[str, bool]) -> CommandResult:
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

    async def execute(self, message: discord.Message, args: list, keys: Dict[str, bool]) -> CommandResult:
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


class Module(ModuleBase):
    name = "BaseModule"
    description = "Basic module for minimal functionality"

    def on_load(self, bot: Bot):
        self.register(RestartCommand(bot))
        self.register(HelpCommand(bot))
        self.register(SQLCommand(bot))
