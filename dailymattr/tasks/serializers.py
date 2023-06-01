from rest_framework import serializers
from datetime import date
from .models import Tasks, Cards


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

    def create(self, validated_data):
        card_id = self.get_card_id(validated_data)
        return Tasks.objects.create(**validated_data, card_id=card_id)

    def update(self, instance, validated_data):
        if validated_data.get('due_date'):
            instance.due_date = validated_data['due_date']
            instance.card_id = self.get_card_id(validated_data)

        instance.updated_at = validated_data.get('updated_at', instance.updated_at)
        instance.description = validated_data.get('description', instance.description)
        instance.task_comment = validated_data.get('task_comment', instance.task_comment)
        instance.task_numb = validated_data.get('task_numb', instance.task_numb)
        instance.priority = validated_data.get('priority', instance.priority)
        instance.link = validated_data.get('link', instance.link)
        instance.save()
        return instance

    @staticmethod
    def get_card_id(validated_data):
        try:
            post_date = validated_data['due_date']
        except KeyError:
            post_date = date.today()

        card = Cards.objects.filter(due_date=post_date).values()
        return card[0]['id'] if card else Cards.objects.create(due_date=post_date).id


class CardsSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=64)
    due_date = serializers.DateField()
