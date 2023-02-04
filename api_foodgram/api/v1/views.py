"""URLs request handlers of the 'api' application."""

from django.db.models import (
    Case,
    Exists,
    IntegerField,
    OuterRef,
    Sum,
    Value,
    When
)
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.mixins import CreateDestroyViewSet
from api.pagination import PageNumberLimitPagination
from api.v1.serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    TagSerializer,
)
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingCart,
    Tag,
)
from users.models import Subscription, User


class CustomUserViewSet(UserViewSet):
    """URL requests handler to 'Users' resource endpoints."""

    http_method_names = ("get", "post", "head")

    def get_queryset(self):
        qs = User.objects.all()
        user = self.request.user
        if self.request.method == "GET" and (isinstance(user, User)):
            subquery = Subscription.objects.filter(
                subscriber=user, author=OuterRef("pk")
            )
            qs = qs.annotate(is_subscribed=(Exists(subquery)))
        return qs


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """URL requests handler to 'Ingredients' resource endpoints."""

    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny,)

    def get_queryset(self):
        qs = Ingredient.objects.all()
        name = self.request.query_params.get("name")
        if name is not None:
            qs = (
                qs.annotate(
                    ingredient_order=Case(
                        When(name__istartswith=name, then=Value(1)),
                        When(name__icontains=name, then=Value(2)),
                        default=0,
                        output_field=IntegerField(),
                    )
                )
                .exclude(ingredient_order=0)
                .order_by("ingredient_order")
            )
        return qs


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """URL requests handler to 'Tags' resource endpoints."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """URL requests handler to 'Recipes' resource endpoints."""

    serializer_class = RecipeSerializer
    permission_classes = (AllowAny,)
    pagination_class = PageNumberLimitPagination

    def get_queryset(self):
        qs = Recipe.objects.select_related("author").prefetch_related(
            "tags", "ingredients"
        )
        if (self.request.method == "GET") and (
            isinstance(self.request.user, User)
        ):
            subquery_subscription = Subscription.objects.filter(
                subscriber=self.request.user, author=OuterRef("pk")
            )
            subquery_favorite = Favorite.objects.filter(
                user=self.request.user, recipe=OuterRef("pk")
            )
            subquery_shopping_cart = ShoppingCart.objects.filter(
                user=self.request.user, recipe=OuterRef("pk")
            )
            qs = qs.annotate(
                is_subscribed=(Exists(subquery_subscription)),
                is_favorited=(Exists(subquery_favorite)),
                is_in_shopping_cart=(Exists(subquery_shopping_cart)),
            )
            if self.action == "list":
                is_in_shopping_cart = self.request.query_params.get(
                    "is_in_shopping_cart"
                )
                if is_in_shopping_cart is not None:
                    qs = qs.filter(
                        is_in_shopping_cart=bool(is_in_shopping_cart)
                    )
                    return qs
                tags = self.request.query_params.getlist("tags")
                qs = qs.filter(tags__slug__in=tags)
                is_favorited = self.request.query_params.get("is_favorited")
                if is_favorited is not None:
                    qs = qs.filter(is_favorited=bool(is_favorited))
                author_id = self.request.query_params.get("author")
                if author_id is not None:
                    qs = qs.filter(author_id=author_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class FavoriteViewSet(CreateDestroyViewSet):
    """URL requests handler to 'Favorites' resource endpoints."""

    serializer_class = FavoriteSerializer

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        recipe_id = self.kwargs["recipe_id"]
        if Favorite.objects.filter(user=user, recipe_id=recipe_id).exists():
            raise serializers.ValidationError(
                {"errors": "Recipe added to favorites earlier."}
            )
        serializer.save(
            user=user,
            recipe=get_object_or_404(Recipe, id=recipe_id),
        )

    @action(methods=("delete",), detail=False)
    def delete(self, request, recipe_id):
        get_object_or_404(
            Favorite, user=request.user, recipe_id=recipe_id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(CreateDestroyViewSet):
    """URL requests handler to 'Shopping cart' resource endpoints."""

    serializer_class = ShoppingCartSerializer

    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        recipe_id = self.kwargs["recipe_id"]
        if ShoppingCart.objects.filter(
            user=user, recipe_id=recipe_id
        ).exists():
            raise serializers.ValidationError(
                {"errors": "Recipe added to shopping cart earlier."}
            )
        serializer.save(
            user=user,
            recipe=get_object_or_404(Recipe, id=recipe_id),
        )

    @action(methods=("delete",), detail=False)
    def delete(self, request, recipe_id):
        get_object_or_404(
            ShoppingCart, user=request.user, recipe_id=recipe_id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(("GET",))
@permission_classes((IsAuthenticated,))
def download_shopping_cart(request):
    """URL requests handler to recipes/download_shopping_cart/ endpoint."""
    items = [
        *RecipeIngredients.objects.filter(recipe__order__user=request.user)
        .select_related("ingredient")
        .values_list(
            "ingredient__name",
            "ingredient__measurement_unit",
        )
        .annotate(Sum("amount"))
        .order_by("ingredient__name")
    ]
    shopping_list = ""
    for item in items:
        shopping_list += " ".join((str(el) for el in item)) + "\n"
    return HttpResponse(
        shopping_list, content_type="text/plain", status=status.HTTP_200_OK
    )
