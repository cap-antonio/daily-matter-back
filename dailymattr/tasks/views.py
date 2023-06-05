from rest_framework import generics

from django.forms import model_to_dict
from datetime import date, timedelta
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Tasks, Cards

from .serializers import *

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
            return Response({'error': 'Method PATCH not allowed'})
        try:
            instance = Tasks.objects.get(pk=pk)
        except:
            return Response({'error': 'Object does not exists'})

        serializer = TasksSerializer(data=request.data, instance=instance, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        if not pk:
            return Response({'error': 'Method PUT not allowed'})
        try:
            instance = Tasks.objects.get(pk=pk)
            instance.delete()
        except:
            return Response({'error': 'Object does not exists'})

        return Response(f'delete post {str(pk)}')


class CardsAPIView(APIView):
    def get(self, request):
        cards = Cards.objects.all()
        inst = CardsSerializer(cards, many=True).instance
        ordered = self.order_tasks_by_cards(inst)
        return Response(ordered)

    def post(self, request):
        serializer = CardsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        if not pk:
            return Response({'error': 'Method PATCH not allowed'})
        try:
            instance = Cards.objects.get(pk=pk)
        except:
            return Response({'error': 'Object does not exists'})

        serializer = CardsSerializer(data=request.data, instance=instance, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        if not pk:
            return Response({'error': 'Method DELETE not allowed'})
        try:
            instance = Cards.objects.get(pk=pk)
            instance.delete()
        except:
            return Response({'error': 'Object does not exists'})

        return Response(f'delete post {str(pk)}')

    @staticmethod
    def order_tasks_by_cards(cards):
        card_lst = []
        for card in cards:
            card_dict = model_to_dict(card)
            task_lst = []
            for task in card.tasks_set.all():
                task_lst.append(model_to_dict(task))

            card_dict['tasks'] = task_lst
            card_lst.append(card_dict)
        return card_lst

# ---------------------------------------------------------------------------------------------
# Получение задач до конца рабочей недели
# Пагинация для оставшихся карточек
# Вернуть все записи в том числе текущей рабочей недели, если помещаются в 1 карточку

class CardsAPIListPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 100


class CardsAPIList(generics.ListCreateAPIView):

    queryset = Cards.objects.all()
    serializer_class = CardsSerial
    pagination_class = CardsAPIListPagination

    def get_queryset(self):
        current = self.get_workweek()
        return Cards.objects.filter(dueDate__range=current)

    # def get(self, request):
        # CardsAPIListPagination.page_size = self.count_workdays(2)
        # page = self.paginate_queryset(self.get_queryset())

        # if page is not None:
            # serializer = self.get_serializer(page, many=True)
            # instance = self.order_tasks_by_cards(serializer.instance)
            # return self.get_paginated_response(instance)

    @staticmethod
    def order_tasks_by_cards(cards):
        card_lst = []
        for card in cards:
            card_dict = model_to_dict(card)
            task_lst = []
            for task in card.tasks_set.all():
                task_lst.append(model_to_dict(task))

            card_dict['tasks'] = task_lst
            card_lst.append(card_dict)
        return card_lst

    @staticmethod
    def get_workweek():
        today = date.today()
        week = today.weekday() + 1
        workweek_st = 3

        diff = week - workweek_st if week > workweek_st else 7 - workweek_st + week

        start = today - timedelta(diff)
        end = start + timedelta(5)
        return [today, end]
