import discord

from typing import Dict, Set

from fusion.settings import settings
from fusion.bot import Bot
from fusion.command import Command
from fusion.modulebase import ModuleBase
from fusion.permissions import DiscordPermission


class ModuleManager:
    modules: Dict[str, ModuleBase] = {}
    commands: Dict[str, Command] = {}

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ModuleManager, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        pass

    @staticmethod
    def check_permissions(member_perms: discord.Permissions, perms_set: Set[DiscordPermission]) -> bool:
        perms_set = set(map(lambda x: x.value, perms_set))
        if sum(perms_set) == 0:
            return True

        if member_perms.value & sum(perms_set) == sum(perms_set):
            return True
        return False

    @staticmethod
    def check_sp_permissions(member_id, perms_set: set):
        if member_id == settings.owner_id:
            return True
        perms_set = set(map(lambda x: x.value, perms_set))
        if sum(perms_set) == 0:
            return True
        from fusion.modules.BaseModule.models import SPPermissions
        try:
            perms: SPPermissions = SPPermissions.objects.get(user_id=member_id)
        except SPPermissions.DoesNotExist:
            return False
        if perms.permissions & sum(perms_set) == sum(perms_set):
            return True
        return False

    def force_unload(self):
        for module in self.modules.values():
            module.on_emergency_unload()
        self.modules.clear()
        self.commands.clear()

    async def unload(self):
        for module in self.modules.values():
            await module.on_unload()
        self.commands.clear()

    def add_module(self, m: ModuleBase):
        self.modules[m.name] = m

    def add_command(self, c: Command, m: ModuleBase):
        c.module = m
        c.guild_lock.update(m.guild_lock)
        self.commands[c.name] = c

    def initialize(self, bot: Bot):
        for module in self.modules.values():
            module.on_load(bot)

    async def run_modules(self, bot: Bot):
        for module in self.modules.values():
            await module.run(bot)

    @property
    def modules_count(self):
        return len(self.modules)

    @property
    def commands_count(self):
        return len(self.commands)
