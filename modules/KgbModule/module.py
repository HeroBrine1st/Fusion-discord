import os

import discord

from core import ModuleBase, Bot, EventListener, Priority
from .models import *

module_dir = os.path.dirname(os.path.abspath(__file__))


class Module(ModuleBase):
    name = "KGB"
    description = "Module KgbModule"

    @EventListener
    async def run(self, bot: Bot):
        try:  # Ебучая винда, ну так блять везде делают, нахуй проверять что-то
            os.mkdir(os.path.join(module_dir, "logger_attachments"))
        except Exception:
            pass

    @EventListener(priority=Priority.LOW)
    async def on_message(self, message: discord.Message, bot: Bot):
        message_db = Message()
        message_db.message_id = message.id
        message_db.content = message.content
        message_db.sent = message.created_at
        message_db.guild_id = message.guild.id
        try:
            message_db.author = Member.objects.get(id=message.author.id)
        except Member.DoesNotExist:
            author_db = Member()
            author_db.id = message.author.id
            author_db.nickname = str(message.author)
            author_db.save()
            message_db.author = author_db
        message_db.save()  # Нужно для связи Many-To-Many
        for attachment in message.attachments:
            attachment_db = Attachment()
            attachment_db.id = attachment.id
            attachment_db.filename = attachment.filename
            attachment_db.size = attachment.size
            with open(os.path.join(module_dir, "logger_attachments", str(attachment.id)), "wb") as f:
                await attachment.save(f)
            attachment_db.save()
            message_db.attachments.add(attachment_db)

    @EventListener(priority=Priority.LOW)
    async def on_message_edit(self, before: discord.Message, after: discord.Message, bot: Bot):
        try:
            message_db: Message = Message.objects.get(message_id=before.id)
        except Message.DoesNotExist:
            return
        message_db.content = after.content
        message_db.save()
        history_db = History(type=0, time=after.edited_at is None and datetime.datetime.now() or after.edited_at,
                             message=message_db, content=before.content)
        try:
            history_db.author = Member.objects.get(id=before.author.id)
        except Member.DoesNotExist:
            author_db = Member(id=before.author.id, nickname=str(before.author))
            author_db.save()
            history_db.author = author_db
        history_db.save()

    @EventListener(priority=Priority.LOW)
    async def on_message_delete(self, message: discord.Message, bot: Bot):
        try:
            message_db: Message = Message.objects.get(message_id=message.id)
        except Message.DoesNotExist:
            return
        message_db.state = False
        history_db = History(type=1, message=message_db, content=message.content, time=datetime.datetime.now())
        try:
            history_db.author = Member.objects.get(id=message.author.id)
        except Member.DoesNotExist:
            author_db = Member(id=message.author.id, nickname=str(message.author))
            author_db.save()
            history_db.author = author_db
        history_db.save()
        message_db.save()
