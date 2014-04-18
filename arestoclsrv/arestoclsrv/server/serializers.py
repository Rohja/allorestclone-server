from django.contrib.auth.models import User
from rest_framework import serializers

from models import *

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'url', 'username',
                  'email', 'groups')


class RestaurantSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Restaurant
        fields = ('id', 'user', 'name', 'description')


class RestaurantTableSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RestaurantTable
        fields = ('id', 'restaurant', 'count', 'note')


class DisheSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Dishe
        fields = ('id', 'restaurant', 'name',
                  'description', 'price', 'is_speciality')


class ReservationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Reservation
        fields = ('id', 'user', 'restaurant', 'created_on',
                  'time_start', 'people_count')


class ReservationInvitationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ReservationInvitation
        fields = ('id', 'host', 'guest', 'reservation')


class OrderEntrySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OrderEntry
        fields = ('id', 'dishe', 'count', 'status')


class OrderSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'dishes', 'reservation')

