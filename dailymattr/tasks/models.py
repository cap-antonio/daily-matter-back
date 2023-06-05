from django.db import models
from datetime import date


class Tasks(models.Model):
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    dueDate = models.DateField(default=date.today)
    description = models.CharField(max_length=140, blank=True)
    taskComment = models.CharField(max_length=140, blank=True)

    taskNumb = models.CharField(max_length=32, blank=True)
    priority = models.CharField(max_length=12, blank=True)
    link = models.URLField(blank=True)
    card = models.ForeignKey('Cards', on_delete=models.CASCADE)
    status = models.ForeignKey('Status', on_delete=models.PROTECT, default=1)


class Cards(models.Model):
    title = models.CharField(max_length=64, blank=True)
    dueDate = models.DateField()
    # userId = models.ForeignKey('Users')


class Status(models.Model):
    statusType = models.CharField(max_length=64, db_index=True)

    def __str__(self):
        return self.status_type
