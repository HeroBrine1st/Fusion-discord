import datetime

from django.db import models


# Create your models here.
class Member(models.Model):
    id = models.IntegerField(primary_key=True)
    nickname = models.TextField()


class Attachment(models.Model):
    id = models.IntegerField(primary_key=True)
    filename = models.CharField(max_length=256)
    size = models.BigIntegerField()


class Message(models.Model):
    message_id = models.IntegerField(primary_key=True)
    guild_id = models.IntegerField(default=0)
    content = models.TextField()
    sent = models.DateTimeField()
    author = models.ForeignKey(Member, on_delete=models.CASCADE)
    attachments = models.ManyToManyField(Attachment)
    state = models.BooleanField(default=True)  # False - deleted


class History(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    time = models.DateTimeField(default=datetime.datetime.min)
    type = models.SmallIntegerField(default=0)  # 0 - edit, 1 - delete
    content = models.TextField()
