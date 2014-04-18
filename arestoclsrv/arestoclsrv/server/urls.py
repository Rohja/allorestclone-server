from django.conf.urls import patterns, url, include
from rest_framework import routers
from arestoclsrv.server import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'restaurants', views.RestaurantViewSet)
router.register(r'tables', views.RestaurantViewSet)
router.register(r'dishes', views.DisheViewSet)
router.register(r'reservations', views.ReservationViewSet)
router.register(r'invitations', views.ReservationInvitationViewSet)
router.register(r'order', views.OrderEntryViewSet)
router.register(r'orders', views.OrderViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.
urlpatterns = patterns('',
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)
