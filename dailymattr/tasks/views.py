from django.forms import model_to_dict
from datetime import date
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Tasks, Cards
from .serializers import TasksSerializer, CardsSerializer


class TasksAPIView(APIView):
    def get(self, request):
        t = Tasks.objects.all()
        return Response(TasksSerializer(t, many=True).data)

    def post(self, request):
        serializer = TasksSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        if not pk:
            return Response({'error': 'Method PUT not allowed'})
        try:
            instance = Tasks.objects.get(pk=pk)
        except:
            return Response({'error': 'Object does not exists'})

        serializer = TasksSerializer(data=request.data, instance=instance, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CardsAPIView(APIView):

    def get(self, request):
        cards = Cards.objects.all()
        inst = CardsSerializer(cards, many=True).instance
        ordered = self.order_tasks_by_cards(inst)
        return Response(ordered)

    def post(self, request):
        post_new = Cards.objects.get_or_create(due_date=request.data['due_date'])[0]
        return Response(model_to_dict(post_new))

    @staticmethod
    def order_tasks_by_cards(cards):
        card_lst = []
        for card in cards:
            card_d = model_to_dict(card)
            task_lst = []
            for task in card.tasks_set.all():
                task_lst += [model_to_dict(task)]

            card_d['tasks'] = task_lst
            card_lst.append(card_d)
        return card_lst
