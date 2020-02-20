import discord

from typing import Dict

from core.bot import Bot
from core.command_result import CommandResult


class Command:
    name: str
    description: str = ""
    arguments: str = ""  # Для пользователя. Эта переменная совершенно не влияет на вашу команду.
    permissions: set = set()  # Не переделывайте в списки - множества быстрее.
    future_permissions: set = set()  # Self-provided
    guild_lock: set = set()  # Айди серверов, для которых доступна данная команда. Всегда наследует модуль. Если пусто, открывается для всех
    module = None

    def __init__(self, bot: Bot):
        self.bot = bot

    async def execute(self, message: discord.Message, args: list, keys: Dict[str, bool]) -> CommandResult:
        return CommandResult.success
