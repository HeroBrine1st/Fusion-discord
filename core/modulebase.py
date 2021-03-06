import discord

from core.bot import Bot
from core.command import Command
from core.event_listener import EventListener


class ModuleBase:
    name: str = "sadkjfaskjfsajkf"
    description: str = ""
    guild_lock: set = set()  # Айди серверов, для которых доступен данный модуль. Наследуется командами.

    def __init__(self):
        if self.name == "sadkjfaskjfsajkf":
            # Что бы юзвери не пытались перехватывать с помощью try-except
            raise BaseException("Warning: change module name.")

    def register(self, obj):
        from core.module_manager import ModuleManager
        if isinstance(obj, Command):
            ModuleManager().add_command(obj, self)
            return True
        return False

    @EventListener
    def on_load(self, bot: Bot):
        pass

    @EventListener
    async def run(self, bot: Bot):
        pass

    @EventListener
    async def on_unload(self):
        pass

    @EventListener
    def on_emergency_unload(self):
        pass

    @EventListener
    async def on_message(self, message: discord.Message, bot: Bot):
        pass

    @EventListener
    async def on_message_delete(self, message: discord.Message, bot: Bot):
        pass

    @EventListener
    async def on_message_edit(self, before: discord.Message, after: discord.Message, bot: Bot):
        pass

    @EventListener
    async def on_member_remove(self, member: discord.Member, bot: Bot):
        pass

    @EventListener
    async def on_disconnect(self, bot: Bot):
        pass

    @EventListener
    async def on_resumed(self, bot: Bot):
        pass

    @EventListener
    async def on_error(self, event, bot: Bot, *args, **kwargs):
        pass

    @EventListener
    async def on_socket_raw_receive(self, msg, bot: Bot):
        pass

    @EventListener
    async def on_socket_raw_send(self, payload, bot: Bot):
        pass

    @EventListener
    async def on_typing(self, channel, user, when, bot: Bot):
        pass

    @EventListener
    async def on_bulk_message_delete(self, messages, bot: Bot):
        pass

    @EventListener
    async def on_raw_message_delete(self, payload, bot: Bot):
        pass

    @EventListener
    async def on_raw_bulk_message_delete(self, payload, bot: Bot):
        pass

    @EventListener
    async def on_raw_message_edit(self, payload, bot: Bot):
        pass

    @EventListener
    async def on_reaction_add(self, reaction, user, bot: Bot):
        pass

    @EventListener
    async def on_raw_reaction_add(self, payload, bot: Bot):
        pass

    @EventListener
    async def on_reaction_remove(self, reaction, user, bot: Bot):
        pass

    @EventListener
    async def on_raw_reaction_remove(self, payload, bot: Bot):
        pass

    @EventListener
    async def on_reaction_clear(self, message, reactions, bot: Bot):
        pass

    @EventListener
    async def on_raw_reaction_clear(self, payload, bot: Bot):
        pass

    @EventListener
    async def on_private_channel_delete(self, channel, bot: Bot):
        pass

    @EventListener
    async def on_private_channel_create(self, channel, bot: Bot):
        pass

    @EventListener
    async def on_private_channel_update(self, before, after, bot: Bot):
        pass

    @EventListener
    async def on_private_channel_pins_update(self, channel, last_pin, bot: Bot):
        pass

    @EventListener
    async def on_guild_channel_delete(self, channel, bot: Bot):
        pass

    @EventListener
    async def on_guild_channel_create(self, channel, bot: Bot):
        pass

    @EventListener
    async def on_guild_channel_update(self, before, after, bot: Bot):
        pass

    @EventListener
    async def on_guild_channel_pins_update(self, channel, last_pin, bot: Bot):
        pass

    @EventListener
    async def on_guild_integrations_update(self, guild, bot: Bot):
        pass

    @EventListener
    async def on_webhooks_update(self, channel, bot: Bot):
        pass

    @EventListener
    async def on_member_join(self, member, bot: Bot):
        pass

    @EventListener
    async def on_member_update(self, before, after, bot: Bot):
        pass

    @EventListener
    async def on_user_update(self, before, after, bot: Bot):
        pass

    @EventListener
    async def on_guild_join(self, guild, bot: Bot):
        pass

    @EventListener
    async def on_guild_remove(self, guild, bot: Bot):
        pass

    @EventListener
    async def on_guild_update(self, before, after, bot: Bot):
        pass

    @EventListener
    async def on_guild_role_create(self, role, bot: Bot):
        pass

    @EventListener
    async def on_guild_role_delete(self, role, bot: Bot):
        pass

    @EventListener
    async def on_guild_role_update(self, before, after, bot: Bot):
        pass

    @EventListener
    async def on_guild_emojis_update(self, guild, before, after, bot: Bot):
        pass

    @EventListener
    async def on_guild_available(self, guild, bot: Bot):
        pass

    @EventListener
    async def on_guild_unavailable(self, guild, bot: Bot):
        pass

    @EventListener
    async def on_voice_state_update(self, member, before, after, bot: Bot):
        pass

    @EventListener
    async def on_member_ban(self, guild, user, bot: Bot):
        pass

    @EventListener
    async def on_member_unban(self, guild, user, bot: Bot):
        pass

    @EventListener
    async def on_group_join(self, channel, user, bot: Bot):
        pass

    @EventListener
    async def on_group_remove(self, channel, user, bot: Bot):
        pass

    @EventListener
    async def on_relationship_add(self, relationship, bot: Bot):
        pass

    @EventListener
    async def on_relationship_remove(self, relationship, bot: Bot):
        pass

    @EventListener
    async def on_relationship_update(self, before, after, bot: Bot):
        pass
