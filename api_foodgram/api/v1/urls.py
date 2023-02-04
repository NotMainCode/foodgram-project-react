"""URLs configuration of the 'api' application v1."""

from django.urls import include, path

from api.routers import CustomDefaultRouter
from api.v1.views import (
    CustomUserViewSet,
    download_shopping_cart,
    FavoriteViewSet,
    IngredientViewSet,
    RecipeViewSet,
    ShoppingCartViewSet,
    TagViewSet,
)

router_v1 = CustomDefaultRouter()

router_v1.register("users", CustomUserViewSet)
router_v1.register("ingredients", IngredientViewSet, basename="ingredients")
router_v1.register("tags", TagViewSet, basename="tags")
router_v1.register("recipes", RecipeViewSet, basename="recipes")
router_v1.register(
    "recipes/(?P<recipe_id>\d+)/favorite", FavoriteViewSet, basename="favorite"
)
router_v1.register(
    "recipes/(?P<recipe_id>\d+)/shopping_cart",
    ShoppingCartViewSet,
    basename="shopping_cart",
)


urlpatterns = [
    path("auth/", include("djoser.urls.authtoken")),
    path(
        "recipes/download_shopping_cart/",
        download_shopping_cart,
        name="download_shopping_cart",
    ),
    path("", include(router_v1.urls)),
]
