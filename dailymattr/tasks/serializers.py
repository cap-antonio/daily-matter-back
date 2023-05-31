from rest_framework import serializers
from datetime import date
from .models import Tasks


class TasksSerializer(serializers.Serializer):
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    due_date = serializers.DateField(default=date.today)
    description = serializers.CharField(max_length=140)
    task_comment = serializers.CharField(max_length=140)

    task_numb = serializers.CharField(max_length=32)
    priority = serializers.CharField(max_length=12)
    link = serializers.URLField()
    card_id = serializers.IntegerField(read_only=True)
    status_id = serializers.IntegerField(default=1)
