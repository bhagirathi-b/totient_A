from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Location
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Location
from datetime import datetime
from django.core import serializers

@api_view(['POST'])
def register(request):
    if request.method == 'POST':
        try:
            password = request.data.get('password', '')
            first_name = request.data.get('first_name', '')
            last_name = request.data.get('last_name', '')
            email = request.data.get('username', '')

            if not (email and password and first_name and last_name):
                return Response({'error': 'Please provide these values - username and password and first_name and last_name'},
                                status=status.HTTP_400_BAD_REQUEST)

            ex_user = User.objects.filter(username=email)
            if ex_user.exists():
                return Response({'error': 'User already exists'},
                                status=status.HTTP_400_BAD_REQUEST)

            user = User(username=email, email=email, first_name=first_name, last_name=last_name)
            user.set_password(password)
            user.save()
            return Response({'detail': 'User created'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def set_travel(request):
    if request.method == 'POST':
        try:
            locations = request.data.get('locations', '')
            if not locations:
                return Response({'error': 'Please provide locations'},
                                status=status.HTTP_400_BAD_REQUEST)
            user = request.user
            for _loc in locations:
                _from = _loc.get('from')
                to = _loc.get('to')
                distance = _loc.get('distance')
                Location.objects.create(user=user, from_location=_from, to_location=to, distance=distance)

            return Response({'detail': 'Locations updated'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def distance_covered(locations):
    total = 0
    for loc in locations:
        total += loc.distance
    return total


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def get_travel(request):
    if request.method == 'POST':
        try:
            from_date = request.data.get('from_date', '')
            to_date = request.data.get('to_date', '')
            user_email = request.data.get('email', '')
            user = request.user
            user_instance = None
            if user.is_superuser:
                if not user_email:
                    return Response({'error': 'Please provide user_email'},
                                    status=status.HTTP_400_BAD_REQUEST)
                user_instance = User.objects.get(email=user_email)
            else:
                user_instance = user

            if from_date:
                from_date_instance = None
                to_date_instance = None
                try:
                    from_date_instance = datetime.strptime(from_date, '%Y-%m-%d')
                    to_date_instance = datetime.strptime(to_date, '%Y-%m-%d')
                except:
                    return Response({'error': "Please provide dates with this format '%Y-%m-%d' "},
                                    status=status.HTTP_400_BAD_REQUEST)

                locations = Location.objects.filter(user=user_instance,
                                                    created_at__range=[from_date_instance, to_date_instance])
                location_data = list()
                for loc in locations:
                    location_data.append({'from': loc.from_location, 'to': loc.to_location, 'date': loc.created_at.date()})
                total_covered = distance_covered(locations)

                return Response({'detail': location_data, 'distance_covered' : total_covered}, status=status.HTTP_200_OK)
            else:
                location = Location.objects.filter(user=user_instance).order_by('-created_at').first()
                last_location = location.to_location

                locations = Location.objects.filter(user=user_instance,
                                                    created_at__contains=location.created_at.date()).all()
                location_data = list()
                for loc in locations:
                    location_data.append(
                        {'from': loc.from_location, 'to': loc.to_location, 'date': loc.created_at.date()})
                total_covered = distance_covered(locations)
                return Response({'last_location': last_location,
                                 'distance_covered': total_covered,
                                 'roots': location_data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
