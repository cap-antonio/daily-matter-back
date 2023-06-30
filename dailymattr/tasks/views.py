from rest_framework import generics

from django.forms import model_to_dict
from datetime import date, timedelta, datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Abscences, Cards, Tasks

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


class CardsAPIList(generics.ListCreateAPIView):
    queryset = Cards.objects.all()
    serializer_class = CardsSerializer

    def get(self, request):
        week_coeficient = request.data.get('week_coeficient', 1)
        start, end = self.get_workweek()

        cards = self.get_previous_workweek_cards(week_coeficient, start, end)
        serialized_instance = CardsSerializer(cards, many=True).instance
        prepared_cards = self.group_tasks_by_cards(serialized_instance)

        return Response(prepared_cards)

    @staticmethod
    def get_workweek():
        '''
        Getting a range of start and end dates for the workweek.
        '''
        today = date.today()
        iso_day = today.isoweekday()
        start_day = 1
        workweek_length = 5

        # Number of days since the start of the working week
        difference = iso_day - start_day if iso_day > start_day else 7 - start_day + iso_day

        start = today - timedelta(difference)
        end = start + timedelta(workweek_length - 1)
        return [start, end]

    @staticmethod
    def get_previous_workweek_cards(coeficient, start, end):
        '''
        Getting a list of cards for the specified amount of previous workweeks.
        '''
        cards_lst = []

        for i in range(coeficient):
            weekly_cards = Cards.objects.filter(dueDate__range=[start, end]).order_by('dueDate')
            cards_lst.append(weekly_cards)

            # Changing the search time range back
            start = start - timedelta(7)
            end = end - timedelta(7)

        return [card for week in cards_lst for card in week]

    @staticmethod
    def group_tasks_by_cards(cards):
        '''
        Grouping tasks according to the corresponding cards.
        '''
        card_lst = []

        for card in cards:
            card_dict = model_to_dict(card)

            if card.abscence:
                card_dict['abscence'] = {
                        "description": card.abscence.absDescription,
                        "approvement": card.abscence.approvement
                        }

            task_lst = []
            for task in card.tasks_set.all():
                task_lst.append(model_to_dict(task))

            card_dict['tasks'] = task_lst
            card_lst.append(card_dict)

        return card_lst

# --- Active

class AbscencesAPIView(APIView):
    def post(self, request):
        post_new = Abscences.objects.create(
            absDescription = request.data['absDescription'],
            startDate = request.data['startDate'],
            endDate = request.data['endDate']
        )

        dates = self.create_dates_list(post_new.startDate, post_new.endDate)
        self.create_abscards(dates, post_new.pk)

        return Response({model_to_dict(post_new)})

    @staticmethod
    def create_dates_list(start, end):
        '''
        Creation of a list of dates for further creation of absence info cards.
        '''
        # Convert a date string into a date() object
        start_dt = datetime.strptime(start, '%Y-%m-%d').date()
        end_dt = datetime.strptime(end, '%Y-%m-%d').date()

        # Create a list of dates within a range of dates
        delta = timedelta(days=1)
        dates = []
        while start_dt <= end_dt:
            dates.append(start_dt.isoformat())
            start_dt += delta

        return dates

    @staticmethod
    def create_abscards(dates, pk):
        '''
        Creating cards in the absence range or change the foreign key of an existing card.
        '''
        for i in dates:
            if not Cards.objects.filter(dueDate=i):
                Cards.objects.create(
                        dueDate=i,
                        abscence=Abscences.objects.get(pk=pk)
                    )
            else:   # If the card exists change the foreign key
                card = Cards.objects.get(dueDate=i)
                card.abscence = Abscences.objects.get(pk=pk)
                card.save()
