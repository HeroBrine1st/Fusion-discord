import os

from typing import Dict
from core.command import Command
from core.module import Module


class ModuleManager:
    modules: Dict[str, Module] = {}
    commands: Dict[str, Command] = {}

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ModuleManager, cls).__new__(cls)
        return cls.instance

    def __init__(self, modules_path="Modules/"):
        self.modules_path = modules_path

    def force_reload(self):
        for module in self.modules.values():
            module.on_emergency_unload()
        self.modules.clear()
        self.commands.clear()
        for file in os.listdir(self.modules_path):
            if file.endswith(".py"):
                pass
