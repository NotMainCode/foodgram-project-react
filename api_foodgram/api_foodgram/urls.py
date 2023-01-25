"""URL configuration of the 'api_foodgram' application."""

from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from api_foodgram import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "redoc/",
        TemplateView.as_view(template_name="redoc.html"),
        name="redoc",
    ),
]
if settings.DEBUG:
    urlpatterns += (
        path("__debug__/", include("debug_toolbar.urls")),
    )
