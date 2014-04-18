from django.db import models

class RestoUser(models.Model):
    '''
    RestoUser: Extend Django user model to add phone
    number and postal address.

    FIXME: Filtrate phone field ?
    FIXME: Replace Phone CharField by a phone field (need extension)
    FIXME: Many address ? (ManyToManyField)
    '''
    phone = models.CharField(verbose_name="Phone number", max_length=12)
    address = models.CharField(verbose_name="Address", max_length=100)
    # Django user
    user = models.ForeignKey('auth.User' ,verbose_name="User")
    friends = models.ManyToManyField("self", verbose_name="Friends")

    def __str__(self):
        return "%s - %s" % (self.user, self.phone)


class Restaurant(models.Model):
    '''
    Restaurant entry.
    TODO: Add address and phone field.
    '''
    user = models.OneToOneField(RestoUser, verbose_name="Owner")
    name = models.CharField(verbose_name="Name", max_length=50)
    description = models.CharField(verbose_name="Description", max_length=200)

    def __str__(self):
        return "%s" % self.name

class RestaurantTable(models.Model):
    '''
    Table in a restaurant
    '''
    restaurant = models.ForeignKey(Restaurant, verbose_name="Restaurant")
    count = models.PositiveIntegerField(verbose_name="Seats count")
    note = models.CharField(max_length=100, verbose_name="Note")

    def __str__(self):
        return "%s - %d seats" % (self.restaurant.name, self.count)


class Dishe(models.Model):
    '''
    Food entry.
    '''
    restaurant = models.ForeignKey(Restaurant, verbose_name="Restaurant")
    name = models.CharField(verbose_name="Name", max_length=50)
    description = models.CharField(verbose_name="Description", max_length=200)
    price = models.PositiveIntegerField(verbose_name="Price")
    is_speciality = models.BooleanField(default=False, verbose_name="Is restaurant's speciality")
    
    def __str__(self):
        return "%s - %s (%sRMB)" % (self.restaurant.name, self.name, self.price)


class Reservation(models.Model):
    '''
    Reservation in a restaurant for X people on a given datetime
    '''
    user = models.ForeignKey(RestoUser, verbose_name="Client")
    restaurant = models.ForeignKey(Restaurant, verbose_name="Restorant")
    created_on = models.DateTimeField(auto_now_add=True, verbose_name="Reservation took on")
    time_start = models.DateTimeField(verbose_name="Reservation for")
    people_count = models.PositiveIntegerField(verbose_name="People count")
    
    def __str__(self):
        return "By %s at %s for %s (%d people(s))" % (self.user, self.restaurant.name, self.time_start, self.people_count)

class ReservationInvitation(models.Model):
    '''
    Invitation for a reservation between two users.
    '''
    host = models.ForeignKey(RestoUser, verbose_name="Host", related_name="host_set")
    guest = models.ForeignKey(RestoUser, verbose_name="Guest", related_name="guest_set")
    reservation = models.ForeignKey(Reservation, verbose_name="Reservation")

    def __str__(self):
        return "by %s to %s at %s" % (self.host, self.guest, self.restaurant.name)


class OrderEntry(models.Model):
    '''
    Order entry = Dishe + count
    '''
    dishe = models.ForeignKey(Dishe, verbose_name="Dishe")
    count = models.PositiveIntegerField(verbose_name="Count")
    status = models.CharField(max_length=20, verbose_name="Status")

    def __str__(self):
        return "%s x%d" % (self.dishe.name, self.count)


class Order(models.Model):
    '''
    Order list for reservation.
    '''
    dishes = models.ManyToManyField(OrderEntry, verbose_name="Orders")
    reservation = models.OneToOneField(Reservation, verbose_name="Client reservation")

    def __str__(self):
        return "Orders for reservation %s" % self.reservation
