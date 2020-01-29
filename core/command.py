import discord

from typing import Dict
from core.command_result import CommandResult


# ЭТО СУКА НАСЛЕДОВАТЬ НАДО
# noinspection PyMethodMayBeStatic,PyUnusedLocal
class Command:
    name: str = "sadkjfaskjfsajkf"
    description: str = ""
    arguments: str = ""  # Для пользователя. Эта переменная совершенно не влияет на вашу команду.
    permissions = {}  # Не переделывайте в списки - множества быстрее.
    sp_permissions = {}  # Self-provided

    def __init__(self):
        if self.name == "sadkjfaskjfsajkf":
            # Что бы юзвери не пытались перехватывать с помощью try-except
            raise BaseException("Warning: change command name.")

    async def execute(self, message: discord.Message, args: str, keys: Dict[str, bool]) -> CommandResult:
        return CommandResult.success
