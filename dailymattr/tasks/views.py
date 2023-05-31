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


        def get_card():
            try:
                post_date = request.data['due_date']
            except KeyError:
                post_date = date.today()

            card = Cards.objects.filter(due_date=post_date).values()
            return card[0]['id'] if card else Cards.objects.create(due_date=post_date).id


        post_new = Tasks.objects.create(
                due_date = request.data['due_date'],
                task_numb = request.data['task_numb'],
                priority = request.data['priority'],
                link = request.data['link'],
                description = request.data['description'],
                task_comment = request.data['task_comment'],
                card_id = get_card()
                )

        return Response(model_to_dict(post_new))


class CardsAPIView(APIView):
    def get(self, request):
        return Response(Cards.objects.all().values())

    def post(self, request):
        post_new = Cards.objects.get_or_create(due_date=request.data['due_date'])[0]
        return Response(model_to_dict(post_new))
