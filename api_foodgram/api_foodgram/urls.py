"""URL configuration of the 'api_foodgram' application."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path("api/", include("api.urls")),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += (
        path("__debug__/", include("debug_toolbar.urls")),
        path("api-auth/", include("rest_framework.urls")),
        path(
            "redoc/",
            TemplateView.as_view(template_name="redoc.html"),
            name="redoc",
        ),
    )
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
