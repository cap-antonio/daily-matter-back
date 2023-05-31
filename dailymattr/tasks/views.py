from django.forms import model_to_dict
from datetime import date
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Tasks, Cards
from .serializers import TasksSerializer


class TasksAPIView(APIView):
    def get(self, request):
        t = Tasks.objects.all()
        return Response(TasksSerializer(t, many=True).data)


    def post(self, request):
        serializer = TasksSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class CardsAPIView(APIView):
    def get(self, request):

        def order_tasks_by_cards():
            card_lst = []
            for card in Cards.objects.all():
                card_d = model_to_dict(card)
                task_lst = []
                for task in card.tasks_set.all():
                    task_lst += [model_to_dict(task)]

                card_d['tasks'] = task_lst
                card_lst.append(card_d)
            return card_lst

        return Response(order_tasks_by_cards())

    def post(self, request):
        post_new = Cards.objects.get_or_create(due_date=request.data['due_date'])[0]
        return Response(model_to_dict(post_new))
