from django.contrib import admin
from models import *

class RestoUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone']

admin.site.register(RestoUser, RestoUserAdmin)

class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'address', 'phone']

admin.site.register(Restaurant, RestaurantAdmin)

class RestaurantTableAdmin(admin.ModelAdmin):
    list_display = ['restaurant', 'count']

admin.site.register(RestaurantTable, RestaurantTableAdmin)

class DisheAdmin(admin.ModelAdmin):
    list_display = ['restaurant', 'name', 'price', 'is_speciality']

admin.site.register(Dishe, DisheAdmin)

class ReservationAdmin(admin.ModelAdmin):
    list_display = ['user', 'restaurant', 'created_on', 'time_start', 'people_count']

admin.site.register(Reservation, ReservationAdmin)

class ReservationInvitationAdmin(admin.ModelAdmin):
    list_display = ['host', 'guest', 'reservation']

admin.site.register(ReservationInvitation, ReservationInvitationAdmin)

class OrderAdmin(admin.ModelAdmin):
    list_display = ['dishe', 'status']

admin.site.register(Order, OrderAdmin)
