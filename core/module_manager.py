from typing import Dict
from core.command import Command
from core.module import Module


class ModuleManager:
    modules = Dict[str, Module]
    commands = Dict[str, Command]