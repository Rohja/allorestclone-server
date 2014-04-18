from django.contrib.auth.models import User
from rest_framework import serializers

from models import *

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'url', 'username',
                  'email', 'groups')


class RestoUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestoUser
        fields = ('id', 'phone', 'user', 'friends')


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ('id', 'user', 'name', 'description')


class RestaurantTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantTable
        fields = ('id', 'restaurant', 'count', 'note')


class DisheSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dishe
        fields = ('id', 'restaurant', 'name',
                  'description', 'price', 'is_speciality')


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ('id', 'user', 'restaurant', 'created_on',
                  'time_start', 'people_count')


class ReservationInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservationInvitation
        fields = ('id', 'host', 'guest', 'reservation')


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'dishe', 'status')


