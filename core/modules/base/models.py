from django.db import models


class SPPermissions(models.Model):
    user_id = models.IntegerField()
    permissions = models.IntegerField()
