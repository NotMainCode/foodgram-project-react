"""URLs configuration of the 'api' application v1."""

from django.urls import include, path
from djoser.views import UserViewSet
from rest_framework.routers import DefaultRouter

from api.v1.views import (
    CustomUserViewSet,
    FavoriteViewSet,
    IngredientViewSet,
    RecipeViewSet,
    ShoppingCartViewSet,
    SubscribeViewSet,
    TagViewSet,
)

router_v1 = DefaultRouter()

router_v1.register("users", CustomUserViewSet, basename="users")
router_v1.register("ingredients", IngredientViewSet, basename="ingredients")
router_v1.register("tags", TagViewSet, basename="tags")
router_v1.register("recipes", RecipeViewSet, basename="recipes")
router_v1.register(
    r"recipes/(?P<recipe_id>\d+)/favorite",
    FavoriteViewSet,
    basename="favorite",
)
router_v1.register(
    r"recipes/(?P<recipe_id>\d+)/shopping_cart",
    ShoppingCartViewSet,
    basename="shopping_cart",
)
router_v1.register(
    r"users/(?P<author_id>\d+)/subscribe",
    SubscribeViewSet,
    basename="subscribe",
)

djoser_urlpatterns = [
    path("auth/", include("djoser.urls.authtoken")),
    path(
        "users/set_password/",
        UserViewSet.as_view({"post": "set_password"}),
        name="set_password",
    ),
    path(
        "users/me/",
        UserViewSet.as_view({"get": "me"}),
        name="users_me",
    ),
]

urlpatterns = [
    *djoser_urlpatterns,
    path("", include(router_v1.urls)),
]
