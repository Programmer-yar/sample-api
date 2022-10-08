from django.db import models

class Logger(models.Model):
    title = models.CharField(max_length=255)
    date_format = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tasks'