"""URLs configuration of the 'api' application v1."""

from django.urls import include, path

from api.routers import CustomDefaultRouter
from api.v1.views import CustomUserViewSet

router_v1 = CustomDefaultRouter()

router_v1.register("users", CustomUserViewSet)

urlpatterns = [
    path("auth/", include("djoser.urls.authtoken")),
    path("", include(router_v1.urls)),
]
