"""URLs configuration of the 'api' application v1."""

from django.urls import include, path, re_path

from api.routers import CustomDefaultRouter
from api.v1.views import (
    CustomUserViewSet,
    download_shopping_cart,
    FavoritePostDelAPIView,
    IngredientViewSet,
    RecipeViewSet,
    ShoppingCartPostDelAPIView,
    SubscribePostDelAPIView,
    SubscriptionViewSet,
    TagViewSet,
)

router_v1 = CustomDefaultRouter()

router_v1.register(
    "users/subscriptions", SubscriptionViewSet, basename="subscriptions"
)
router_v1.register("users", CustomUserViewSet)
router_v1.register("ingredients", IngredientViewSet, basename="ingredients")
router_v1.register("tags", TagViewSet, basename="tags")
router_v1.register("recipes", RecipeViewSet, basename="recipes")

urlpatterns = [
    path("auth/", include("djoser.urls.authtoken")),
    path(
        "recipes/download_shopping_cart/",
        download_shopping_cart,
        name="download_shopping_cart",
    ),
    re_path(
        "recipes/(?P<recipe_id>\d+)/favorite/",
        FavoritePostDelAPIView.as_view(),
        name="favorite",
    ),
    re_path(
        "recipes/(?P<recipe_id>\d+)/shopping_cart/",
        ShoppingCartPostDelAPIView.as_view(),
        name="shopping_cart",
    ),
    re_path(
        "users/(?P<author_id>\d+)/subscribe/",
        SubscribePostDelAPIView.as_view(),
        name="subscribe",
    ),
    path("", include(router_v1.urls)),
]
