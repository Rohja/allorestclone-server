#!/usr/bin/env python

from WebSocketCommand import WebSocketCmd

from arestoclsrv.server.models import *
from arestoclsrv.server.serializers import *


def get_restouser(django_userid):
    try:
        user = RestoUser.objects.get(user__id=django_userid)
    except RestoUser.DoesNotExist:
        return None
    return user


# SPECIAL: AUTH
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

class AuthUsersCmd(WebSocketCmd):
    """
    Authentification cmd
    require username and password (both strings)
    """
    cmd_name = "user_auth"

    delayed_process = False

    raw_user = None

    def filter_data(self):
        # FIXME: Add colander filtering.
        pass

    def pre_process(self):
        # self.answer = {"echo": str(time.time())}
        if not self.data.get('username') or not self.data.get('password'):
            self.error = "Missing username or password."
        else:
            user = authenticate(username=self.data['username'], password=self.data['password'])
            if user:
                self.raw_user = user
                user = UserSerializer(user)
                user = user.data
            self.answer = {"user": user}

    def process(self):
        self.pre_process()


class CreateUserCmd(WebSocketCmd):
    cmd_name = "user_create"

    delayed_process = False

    raw_user = None

    def filter_data(self):
        # FIXME: Add colander filtering.
        pass

    def pre_process(self):
        # self.answer = {"echo": str(time.time())}
        if not self.data.get('username'):
            self.error = "Missing username."
        elif not self.data.get('password'):
            self.error = "Missing password."
        elif not self.data.get('email'):
            self.error = "Missing email."
        elif not self.data.get('phone'):
            self.error = "Missing phone number."    
        else:
            try:
                user = User.objects.get(username=self.data['username'])
            except User.DoesNotExist:
                # GOOD
                user = User(username=self.data['username'],
                            email=self.data['email'])
                user.set_password(self.data['password'])
                user.is_active = True
                user.save()
                user_ser = UserSerializer(user)
                restouser = RestoUser(user=user, phone=self.data['phone'])
                restouser.save()
                self.answer = {"user": user_ser.data}
            else:
                self.error = "Username already in use."

    def process(self):
        self.pre_process()


## RestoUser
# GET
class GetRestoUsersCmd(WebSocketCmd):
    """
    Echo command. Give timestamp.
    """
    cmd_name = "restouser_get"

    delayed_process = False

    def filter_data(self):
        # FIXME: Add colander filtering.
        pass

    def pre_process(self):
        # self.answer = {"echo": str(time.time())}
        if not self.data.get('id'):
            self.error = "Missing user id."
        else:
            try:
                user = RestoUser.objects.get(id=self.data['id'])
            except RestoUser.DoesNotExist:
                user = None
            else:
                user = RestoUserSerializer(user)
            if user:
                user = user.data
            self.answer = {"user": user}

    def process(self):
        self.pre_process()

# UPDATE
class UpdateUserPasswordCmd(WebSocketCmd):
    cmd_name = "password_update"

    delayed_process = False

    django_user = None

    def filter_data(self):
        # FIXME: Add colander filtering.
        pass

    def pre_process(self):
        # self.answer = {"echo": str(time.time())}
        if not self.django_user:
            self.error = "Not loged in."
            return
        if not self.data.get('password'):
            self.error = "No password to set."
            return
        id = self.django_user

        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            self.error = "User not found."
            return
        else:
            user.set_password(self.data['password'])
            user.save()
            user_ser = UserSerializer(user)
            self.answer = {'user': user_ser.data}

    def process(self):
        self.pre_process()

class UpdateRestoUserCmd(WebSocketCmd):
    cmd_name = "restouser_update"

    delayed_process = False

    django_user = None

    def filter_data(self):
        # FIXME: Add colander filtering.
        pass

    def pre_process(self):
        # self.answer = {"echo": str(time.time())}
        if not self.django_user:
            self.error = "Not loged in."
            return

        user = get_restouser(self.django_user)
        if not user:
            self.error = "RestoUser not found."
            return

        if not self.data.get("phone"):
            self.error = "Nothing to update."
            return

        user.phone = self.data['phone']
        user.save()
        user_ser = RestoUserSerializer(user)
        self.answer = {'user': user_ser.data}

    def process(self):
        self.pre_process()

# Add friend
class AddFriendUserCmd(WebSocketCmd):
    cmd_name = "friend_add"

    delayed_process = False

    django_user = None

    def filter_data(self):
        # FIXME: Add colander filtering.
        pass

    def pre_process(self):
        # self.answer = {"echo": str(time.time())}
        if not self.django_user:
            self.error = "Not loged in."
            return

        if not self.data.get('friend_username'):
            self.error = "You need to supply friend username."
            return
        else:
            try:
                friend = RestoUser.objects.get(user__username=self.data['friend_username'])
            except RestoUser.DoesNotExist:
                self.error = "Friend with providen username not found."
                return

        user = get_restouser(self.django_user)
        if not user:
            self.error = "RestoUser not found."
            return

        user.friends.add(friend)
        user.save()
        user_ser = RestoUserSerializer(user)
        self.answer = {'user': user_ser.data}

    def process(self):
        self.pre_process()

## Restaurant
# CREATE

class AddRestaurantCmd(WebSocketCmd):
    cmd_name = "restaurant_create"

    delayed_process = False

    django_user = None

    def filter_data(self):
        # FIXME: Add colander filtering.
        pass

    def pre_process(self):
        if not self.data.get('name'):
            self.error = "Missing name."
            return
        if not self.data.get('desc'):
            self.error = "Missing description."
            return
        if not self.data.get('addr'):
            self.error = "Missing address."
            return
        if not self.data.get('phone'):
            self.error = "Missing phone number."
            return

        owner = get_restouser(self.django_user)
        restaurant = Restaurant(owner=owner,
                               name=self.data['name'],
                               description=self.data['desc'],
                               address=self.data['address'],
                               phone=self.data['phone'])
        restaurant.save()
        restaurant_ser = RestaurantSerializer(restaurant)
        self.answer = {'restaurant': restaurant_ser.data}

    def process(self):
        self.pre_process()

# GET

class GetRestaurantCmd(WebSocketCmd):
    cmd_name = "restaurant_get"

    delayed_process = False

    django_user = None

    def filter_data(self):
        # FIXME: Add colander filtering.
        pass

    def pre_process(self):
        if self.data.get('id'):
            try:
                restaurants = Restaurant.objects.get(id=self.data['id'])
                restaurant_ser = RestaurantSerializer(restaurants)
            except Restaurant.DoesNotExist:
                self.error = "Restaurant not found."
                return
        elif self.data.owner('owner'):
            owner = get_restouser(self.django_user)
            restaurants = Restaurant.objects.filter(owner=owner)
            restaurant_ser = RestaurantSerializer(restaurants, many=True)                
        else:
            restaurants = Restaurant.objects.all()
            restaurant_ser = RestaurantSerializer(restaurants, many=True)
        self.answer = {'restaurant': restaurant_ser.data}

    def process(self):
        self.pre_process()

# UPDATE

class UpdateRestaurantCmd(WebSocketCmd):
    cmd_name = "restaurant_update"

    delayed_process = False

    django_user = None

    def filter_data(self):
        # FIXME: Add colander filtering.
        pass

    def pre_process(self):
        if not self.data.get('id'):
            self.error = "Missing restaurant id."
            return

        owner = get_restouser(self.data['id'])
        try:
            restaurant = Restaurant.objects.get(id=self.data['id'], owner=owner)
        except Restaurant.DoesNotExist:
            self.error = "Restaurant does not exist."
            return
        if self.data.get('name'):
            restaurant.name = self.data['name']
        if self.data.get('desc'):
            restaurant.description = self.data['desc']
        if self.data.get('addr'):
            restaurant.address = self.data['addr']
        if self.data.get('phone'):
            restaurant.phone = self.data['phone']

        restaurant.save()
        restaurant_ser = RestaurantSerializer(restaurant)
        self.answer = {'restaurant': restaurant_ser.data}

    def process(self):
        self.pre_process()


## Dishe
# GET

class GetDisheCmd(WebSocketCmd):
    cmd_name = "dishe_get"

    delayed_process = False

    django_user = None

    def filter_data(self):
        # FIXME: Add colander filtering.
        pass

    def pre_process(self):
        if not self.data.get('restaurant_id') and not self.data.get('dishe_id'):
            self.error = "Missing restaurant id/dishe id."
            return
        
        if self.data.get('restaurant_id'):
            try:
                restaurant = Restaurant.objects.get(id=self.data['restaurant_id'])
                dishes = DisheSerializer(restaurant.dishe_set.all(), many=True)
            except Restaurant.DoesNotExist:
                self.error = "Restaurant not found."
                return
        elif self.data.get('dishe_id'):
            try:
                dishes = Dishe.objects.get(id=self.data['dishe_id'])
                dishes = DisheSeriliser(dishes)
            except Dishe.DoesNotExist:
                self.error = "Dishe not found."
                return

        self.answer = {"dishes": dishes.data}

    def process(self):
        self.pre_process()

# CREATE
class CreateDisheCmd(WebSocketCmd):
    cmd_name = "dishe_create"

    delayed_process = False

    django_user = None

    def filter_data(self):
        # FIXME: Add colander filtering.
        pass

    def pre_process(self):
        if not self.data.get('restaurant_id'):
            self.error = "Missing restaurant id."
            return
        
        owner = get_restouser(self.django_user)
        try:
            restaurant = Restaurant.objects.get(id=self.data['restaurant_id'], owner=owner)
        except Restaurant.DoesNotExist:
            self.error = "Restaurant not found."
            return

        if not self.data.get('name'):
            self.error = "Missing name."
            return
        if not self.data.get('desc'):
            self.error = "Missing description."
            return
        if not self.data.get('price'):
            self.error = "Missing price."
            return
        
        if self.data.get('speciality'):
            spec = bool(self.data['speciality'])
        else:
            spec = False

        dishe = Dishe(restaurant=restaurant,
                      name=self.data['name'],
                      description=self.data['desc'],
                      price=self.data['price'],
                      speciality=spec)
        restaurant.dishe_set.add(dishe)
        restaurant.save()
        dishe.save()
        dishe_ser = DisheSerializer(dishe)
        self.answer = {"dishe": dishe.data}

    def process(self):
        self.pre_process()

# UPDATE
class UpdateDisheCmd(WebSocketCmd):
    cmd_name = "dishe_update"

    delayed_process = False

    django_user = None

    def filter_data(self):
        # FIXME: Add colander filtering.
        pass

    def pre_process(self):
        if not self.data.get('id'):
            self.error = "Missing dishe id."
            return
        
        owner = get_restouser(self.django_user)
        try:
            dishe = Dishe.objects.get(id=self.data['id'], restaurant__owner=owner)
        except Dishe.DoesNotExist:
            self.error = "Dishe not found."
            return

        if self.data.get('name'):
            dishe.name = self.data['name']
        if self.data.get('desc'):
            dishe.description = self.data['desc']
        if not self.data.get('price'):
            dishe.price = self.data['price']
        
        if self.data.get('speciality'):
            spec = bool(self.data['speciality'])
        else:
            spec = False

        dishe.speciality = spec

        dishe.save()
        dishe_ser = DisheSerializer(dishe)
        self.answer = {"dishe": dishe.data}

    def process(self):
        self.pre_process()

# DELETE
class DeleteDisheCmd(WebSocketCmd):
    cmd_name = "dishe_delete"

    delayed_process = False

    django_user = None

    def filter_data(self):
        # FIXME: Add colander filtering.
        pass

    def pre_process(self):
        if not self.data.get('id'):
            self.error = "Missing dishe id."
            return
        
        owner = get_restouser(self.django_user)
        try:
            dishe = Dishe.objects.get(id=self.data['id'], restaurant__owner=owner)
        except Dishe.DoesNotExist:
            self.error = "Dishe not found."
            return

        dishe.delete()
        self.answer = {"dishe": None}

    def process(self):
        self.pre_process()


## Reservation
# GET
class GetReservationCmd(WebSocketCmd):
    cmd_name = "reservation_get"

    delayed_process = False

    django_user = None

    def filter_data(self):
        # FIXME: Add colander filtering.
        pass

    def pre_process(self):
        client = get_restouser(self.django_user)
        if self.data.get('id'):
            try:
                reservations = client.reservation_set.get(id=self.data['id'])
                reservations_ser = ReservationSerializer(reservations)
            except Reservation.DoesNotExist:
                self.error = "Reservation not found."
                return
        else:
            reservations = client.reservation_set.all()
            reservations_ser = ReservationSerializer(reservations, many=True)
        self.answer = {"reservations": reservations_ser.data}

    def process(self):
        self.pre_process()

# CREATE
class CreateReservationCmd(WebSocketCmd):
    cmd_name = "reservation_create"

    delayed_process = False

    django_user = None

    def filter_data(self):
        # FIXME: Add colander filtering.
        pass

    def pre_process(self):
        client = get_restouser(self.django_user)
        if not self.data.get('restaurant_id'):
            self.error = "Missing restaurant id."
            return
        try:
            restaurant = Restaurant.objects.get(id=self.data['restaurant_id'])
        except Restaurant.DoesNotExist:
            self.error = "Restaurant not found."
            return
        if not self.data.get('time_start'):
            self.error = "Missing reservation date."
            return
        if not self.data.get('people_count'):
            self.error = "Missing people count."
            return

        reservation = Reservation(client=client,
                                  restaurant=restaurant,
                                  time_start=self.data['time_start'],
                                  people_count=self.data['people_count'])
        reservation.save()
        reservation_ser = ReservationSerializer(reservation)
        self.answer = {"reservation": reservation_ser.data}

    def process(self):
        self.pre_process()

# UPDATE
class UpdateReservationCmd(WebSocketCmd):
    cmd_name = "reservation_update"

    delayed_process = False

    django_user = None

    def filter_data(self):
        # FIXME: Add colander filtering.
        pass

    def pre_process(self):
        client = get_restouser(self.django_user)
        if not self.data.get('id'):
            self.error = "Missing reservation id."
            return

        try:
            reservation = Reservation.objects.get(id=self.data['id'],
                                                  client=client)
        except Reservation.DoesNotExist:
            try:
                reservation = Reservation.objects.get(id=self.data['id'], restaurant__owner=client)
            except Reservation.DoesNotExist:
                self.error = "Reservation not found."
                return
        if reservation.status != 0: # 0 = pending
            self.error = "Reservation already validated. Please directly call the restaurant."
            return

        if self.data.get('time_start'):
            reservation.time_start = self.data['time_start']
        if self.data.get('people_count'):
            reservation.people_count = self.data['people_count']

        if reservation.restaurant.owner == client and self.data.get('status'):
            reservation.status = self.data['status']

        reservation.save()

        reservation_ser = ReservationSerializer(reservation)
        self.answer = {"reservation": reservation_ser.data}

    def process(self):
        self.pre_process()


# DELETE
class DeleteReservationCmd(WebSocketCmd):
    cmd_name = "reservation_delete"

    delayed_process = False

    django_user = None

    def filter_data(self):
        # FIXME: Add colander filtering.
        pass

    def pre_process(self):
        client = get_restouser(self.django_user)
        if not self.data.get('id'):
            self.error = "Missing restaurant id."
            return

        try:
            reservation = Reservation.objects.get(id=self.data['id'],
                                                  client=client)
        except Reservation.DoesNotExist:
            try:
                reservation = Reservation.objects.get(id=self.data['id'], restaurant__owner=client)
            except Reservation.DoesNotExist:
                self.error = "Reservation not found."
                return

        reservation.delete()

        self.answer = {"reservation": None}

    def process(self):
        self.pre_process()

