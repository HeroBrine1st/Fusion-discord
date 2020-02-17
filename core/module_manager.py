from typing import Dict
from core.bot import Bot
from core.command import Command
from core.modulebase import ModuleBase


class ModuleManager:
    _modules: Dict[str, ModuleBase] = {}
    _commands: Dict[str, Command] = {}

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ModuleManager, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        pass

    def force_unload(self):
        for module in self._modules.values():
            module.on_emergency_unload()
        self._modules.clear()
        self._commands.clear()

    def add_module(self, m: ModuleBase):
        self._modules[m.name] = m

    def add_command(self, c: Command):
        self._commands[c.name] = c

    def initialize(self, bot: Bot):
        for module in self._modules.values():
            module.on_load(bot)

    def run_modules(self, bot: Bot):
        for module in self._modules.values():
            module.run(bot)
