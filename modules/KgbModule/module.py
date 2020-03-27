import discord

from core import ModuleBase, CommandResult, Command, Bot, DotDict, EventListener, Priority
from .models import *

module_dir = os.path.dirname(os.path.abspath(__file__))


class TemplateCommand(Command):
    name = "hello"
    description = "Template command"

    async def execute(self, message: discord.Message, args: list, keys: DotDict) -> CommandResult:
        await message.channel.send("Hello!")
        return CommandResult.success


class Module(ModuleBase):
    name = "KGB"
    description = "Module KgbModule"

    @EventListener
    def on_load(self, bot: Bot):
        self.register(TemplateCommand(bot))

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
    async def on_message_edit(self, old_message: discord.Message, new_message: discord.Message, bot: Bot):
        try:
            message_db: Message = Message.objects.get(message_id=old_message.id)
        except Message.DoesNotExist:
            return
        message_db.content = new_message.content
        history_db = History()
        history_db.type = 0
        history_db.time = new_message.edited_at is None and datetime.datetime.now() or new_message.edited_at
        history_db.message = message_db
        history_db.message_id = old_message.id
        history_db.content = old_message.content
        history_db.sent = old_message.created_at
        history_db.guild_id = old_message.guild.id
        try:
            history_db.author = Member.objects.get(id=old_message.author.id)
        except Member.DoesNotExist:
            author_db = Member()
            author_db.id = old_message.author.id
            author_db.nickname = str(old_message.author)
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
        history_db = History()
        history_db.type = 1
        history_db.message_id = message.id
        history_db.content = message.content
        history_db.sent = message.created_at
        history_db.guild_id = message.guild.id
        try:
            history_db.author = Member.objects.get(id=message.author.id)
        except Member.DoesNotExist:
            author_db = Member()
            author_db.id = message.author.id
            author_db.nickname = str(message.author)
            author_db.save()
            history_db.author = author_db
        history_db.save()
        message_db.save()



