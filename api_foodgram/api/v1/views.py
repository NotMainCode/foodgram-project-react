"""URLs request handlers of the 'api' application."""

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import (
    Count,
    Exists,
    OuterRef,
    Sum,
)
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework
from djoser.views import UserViewSet
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.mixins import (
    CreateDestroyViewSet,
    GetPostPatchDeleteViewSet,
    ListViewSet,
)
from api.pagination import PageNumberLimitPagination
from api.v1.filters import IngredientSearchFilter, RecipeFilter
from api.v1.permissions import IsAuthorOrReadOnly
from api.v1.serializers import (
    FavoriteSerializer,
    GetRecipeSerializer,
    IngredientSerializer,
    PostPatchRecipeSerializer,
    ShoppingCartSerializer,
    SubscribeSerializer,
    SubscriptionsSerializer,
    TagSerializer,
)
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.models import Subscription, User


class CustomUserViewSet(UserViewSet):
    """URL requests handler to 'Users' resource endpoints."""

    http_method_names = ("get", "post", "head", "options")
    pagination_class = PageNumberLimitPagination

    def get_queryset(self):
        queryset = User.objects.all()
        user = self.request.user
        if self.request.method == "GET" and user.is_authenticated:
            subquery = Subscription.objects.filter(
                user=user, author=OuterRef("pk")
            )
            queryset = queryset.annotate(is_subscribed=(Exists(subquery)))
        return queryset


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """URL requests handler to 'Ingredients' resource endpoints."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (IngredientSearchFilter,)
    search_fields = ("name",)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """URL requests handler to 'Tags' resource endpoints."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class RecipeViewSet(GetPostPatchDeleteViewSet):
    """URL requests handler to 'Recipes' resource endpoints."""

    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = PageNumberLimitPagination
    filter_backends = (rest_framework.DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == "GET":
            return GetRecipeSerializer
        return PostPatchRecipeSerializer

    def get_queryset(self):
        queryset = Recipe.objects.select_related("author").prefetch_related(
            "tags", "ingredients"
        )
        if self.request.method == "GET" and self.request.user.is_authenticated:
            subquery_subscription = Subscription.objects.filter(
                user=self.request.user, author=OuterRef("pk")
            )
            subquery_favorite = Favorite.objects.filter(
                user=self.request.user, recipe=OuterRef("pk")
            )
            subquery_shopping_cart = ShoppingCart.objects.filter(
                user=self.request.user, recipe=OuterRef("pk")
            )
            queryset = queryset.annotate(
                is_subscribed=(Exists(subquery_subscription)),
                is_favorited=(Exists(subquery_favorite)),
                is_in_shopping_cart=(Exists(subquery_shopping_cart)),
            )
        return queryset


class FavoriteViewSet(CreateDestroyViewSet):
    """URL requests handler to 'Favorites' resource endpoints."""

    serializer_class = FavoriteSerializer

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs["recipe_id"])
        data = {"user": request.user.id, "recipe": recipe.id}
        serializer = self.get_serializer_class()(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=("delete",), detail=False)
    def delete(self, request, recipe_id):
        try:
            Favorite.objects.get(
                user=request.user, recipe_id=recipe_id
            ).delete()
        except ObjectDoesNotExist:
            return Response(
                {"errors": "Recipe was not in the favorites."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(CreateDestroyViewSet):
    """URL requests handler to 'Shopping list' resource endpoints."""

    serializer_class = ShoppingCartSerializer

    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs["recipe_id"])
        data = {"user": request.user.id, "recipe": recipe.id}
        serializer = self.get_serializer_class()(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=("delete",), detail=False)
    def delete(self, request, recipe_id):
        try:
            ShoppingCart.objects.get(
                user=request.user, recipe_id=recipe_id
            ).delete()
        except ObjectDoesNotExist:
            message = (
                f"The recipe with id={recipe_id} was not in the shopping list."
            )
            raise serializers.ValidationError({"errors": message})
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscribeViewSet(CreateDestroyViewSet):
    """URL requests handler to  endpoints of 'Subscriptions' resource."""

    serializer_class = SubscribeSerializer

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        author = get_object_or_404(User, id=kwargs["author_id"])
        data = {"user": request.user.id, "author": author.id}
        serializer = self.get_serializer_class()(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=("delete",), detail=False)
    def delete(self, request, author_id):
        try:
            Subscription.objects.get(
                user=request.user, author_id=author_id
            ).delete()
        except ObjectDoesNotExist:
            message = (
                f"There was no subscription to the author with id={author_id}."
            )
            raise serializers.ValidationError({"errors": message})
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionsViewSet(ListViewSet):
    """URL requests handler to users/subscriptions/ endpoint."""

    serializer_class = SubscriptionsSerializer
    pagination_class = PageNumberLimitPagination

    def get_queryset(self):
        return User.objects.filter(
            subscription__user=self.request.user
        ).annotate(recipes_count=(Count("recipes")))


@api_view()
def download_shopping_cart(request):
    """URL requests handler to recipes/download_shopping_cart/ endpoint."""
    ingredients = [
        *RecipeIngredient.objects.filter(
            recipe__carts__user=request.user
        ).select_related(
            "ingredient"
        ).values_list(
            "ingredient__name",
            "ingredient__measurement_unit",
        ).annotate(Sum("amount")).order_by("ingredient__name")
    ]
    shopping_list = (
        (" ".join((str(element) for element in ingredient)) + "\n")
        for ingredient in ingredients
    )
    return HttpResponse(
        shopping_list, content_type="text/plain", status=status.HTTP_200_OK
    )
