from django.db import models


class SPPermissions(models.Model):
    user_id = models.IntegerField()
    permissions = models.IntegerField(default=0)

    class Meta:
        db_table = 'sp_permissions'
