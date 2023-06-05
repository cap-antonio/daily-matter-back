from rest_framework import serializers
from datetime import date
from .models import Tasks, Cards


class TasksSerializer(serializers.Serializer):
    createdAt = serializers.DateTimeField(read_only=True)
    updatedAt = serializers.DateTimeField(read_only=True)
    dueDate = serializers.DateField(default=date.today)
    description = serializers.CharField(max_length=140)
    taskComment = serializers.CharField(max_length=140)

    taskNumb = serializers.CharField(max_length=32)
    priority = serializers.CharField(max_length=12)
    link = serializers.URLField()
    card_id = serializers.IntegerField(read_only=True)
    status_id = serializers.IntegerField(default=1)

    def create(self, validated_data):
        card_id = self.get_card_id(validated_data)
        return Tasks.objects.create(**validated_data, card_id=card_id)

    def update(self, instance, validated_data):
        if validated_data.get('dueDate'):
            instance.dueDate = validated_data['dueDate']
            instance.card_id = self.get_card_id(validated_data)

        instance.updatedAt = validated_data.get('updatedAt', instance.updatedAt)
        instance.description = validated_data.get('description', instance.description)
        instance.taskComment = validated_data.get('taskComment', instance.taskComment)
        instance.taskNumb = validated_data.get('taskNumb', instance.taskNumb)
        instance.priority = validated_data.get('priority', instance.priority)
        instance.link = validated_data.get('link', instance.link)
        instance.save()
        return instance

    @staticmethod
    def get_card_id(validated_data):
        try:
            post_date = validated_data['dueDate']
        except KeyError:
            post_date = date.today()

        card = Cards.objects.filter(dueDate=post_date).values()
        return card[0]['id'] if card else Cards.objects.create(dueDate=post_date).id


class CardsSerial(serializers.ModelSerializer):
    class Meta:
        model = Cards
        fields = '__all__'

class CardsSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=64)
    dueDate = serializers.DateField()

    def create(self, validated_data):
        dueDate = validated_data['dueDate']
        card = Cards.objects.filter(dueDate=dueDate)
        return card[0] if card else Cards.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.save()
        return instance
