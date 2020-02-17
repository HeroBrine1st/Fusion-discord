import discord

from typing import Dict, Set
from core.command_result import CommandResult


class Command:
    name: str
    description: str = ""
    arguments: str = ""  # Для пользователя. Эта переменная совершенно не влияет на вашу команду.
    permissions: set = set()  # Не переделывайте в списки - множества быстрее.
    sp_permissions: set = set()  # Self-provided
    guild_lock: set = set()  # Айди серверов, для которых доступна данная команда. Всегда наследует модуль. Если пусто, открывается для всех
    module = None

    async def execute(self, message: discord.Message, args: list, keys: Dict[str, bool]) -> CommandResult:
        return CommandResult.success
