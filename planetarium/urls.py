from django.urls import path, include
from rest_framework import routers

from planetarium.views import AstronomyShowViewSet, ShowThemeViewSet, PlanetariumDomeViewSet, ShowSessionViewSet, \
    ReservationViewSet, TicketViewSet

router = routers.DefaultRouter()
router.register("astronomy-shows", AstronomyShowViewSet),
router.register("show-themes", ShowThemeViewSet),
router.register("planetarium-domes", PlanetariumDomeViewSet),
router.register("show-sessions", ShowSessionViewSet),
router.register("reservations", ReservationViewSet),
router.register("tickets", TicketViewSet),



app_name = "planetarium"

urlpatterns = [
    path("", include(router.urls)),
]
