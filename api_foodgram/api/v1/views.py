"""URLs request handlers of the 'api' application."""

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import (
    Case,
    Exists,
    IntegerField,
    OuterRef,
    Sum,
    Value,
    When,
)
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api.mixins import ListViewSet, ModelViewSetWithoutPUT
from api.pagination import PageNumberLimitPagination
from api.v1.permissions import IsAuthorOrReadOnly
from api.v1.serializers import (
    IngredientSerializer,
    RecipeBriefSerializer,
    RecipeSerializer,
    SubscriptionSerializer,
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

    http_method_names = ("get", "post", "head", "options")
    pagination_class = PageNumberLimitPagination

    def get_queryset(self):
        qs = User.objects.all()
        user = self.request.user
        if self.request.method == "GET" and (isinstance(user, User)):
            subquery = Subscription.objects.filter(
                user=user, author=OuterRef("pk")
            )
            qs = qs.annotate(is_subscribed=(Exists(subquery)))
        return qs


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """URL requests handler to 'Ingredients' resource endpoints."""

    serializer_class = IngredientSerializer
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


class RecipeViewSet(ModelViewSetWithoutPUT):
    """URL requests handler to 'Recipes' resource endpoints."""

    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = PageNumberLimitPagination

    def get_queryset(self):
        qs = Recipe.objects.select_related("author").prefetch_related(
            "tags", "ingredients"
        )
        tags = self.request.query_params.getlist("tags")
        if tags != []:
            qs = qs.filter(tags__slug__in=tags).distinct()
        if (self.request.method == "GET") and (
            isinstance(self.request.user, User)
        ):
            subquery_subscription = Subscription.objects.filter(
                user=self.request.user, author=OuterRef("pk")
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
                author_id = self.request.query_params.get("author")
                if author_id is not None:
                    qs = qs.filter(author_id=author_id)
                is_in_shopping_cart = self.request.query_params.get(
                    "is_in_shopping_cart"
                )
                if is_in_shopping_cart is not None:
                    qs = qs.filter(
                        is_in_shopping_cart=bool(is_in_shopping_cart)
                    )
                is_favorited = self.request.query_params.get("is_favorited")
                if is_favorited is not None:
                    qs = qs.filter(is_favorited=bool(is_favorited))
        return qs


class FavoritePostDelAPIView(APIView):
    """URL requests handler to 'Favorites' resource endpoints."""

    def post(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs["recipe_id"])
        try:
            Favorite.objects.create(user=request.user, recipe=recipe)
        except IntegrityError:
            message = (
                f"The recipe with id={recipe.id} "
                f"was added to favorites earlier."
            )
            raise serializers.ValidationError({"errors": message})
        return Response(
            RecipeBriefSerializer(recipe).data, status=status.HTTP_201_CREATED
        )

    def delete(self, request, **kwargs):
        recipe_id = kwargs["recipe_id"]
        try:
            Favorite.objects.get(
                user=request.user, recipe_id=recipe_id
            ).delete()
        except ObjectDoesNotExist:
            message = f"The recipe with id={recipe_id} was not in favorites."
            return Response(
                {"errors": message}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartPostDelAPIView(APIView):
    """URL requests handler to 'Shopping list' resource endpoints."""

    def post(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs["recipe_id"])
        try:
            ShoppingCart.objects.create(user=request.user, recipe=recipe)
        except IntegrityError:
            message = (
                f"The recipe with id={recipe.id} "
                f"was added to the shopping list earlier."
            )
            raise serializers.ValidationError({"errors": message})
        return Response(
            RecipeBriefSerializer(recipe).data, status=status.HTTP_201_CREATED
        )

    def delete(self, request, **kwargs):
        recipe_id = kwargs["recipe_id"]
        try:
            ShoppingCart.objects.get(
                user=request.user, recipe_id=recipe_id
            ).delete()
        except ObjectDoesNotExist:
            message = (
                f"The recipe with id={recipe_id} was not in the shopping list."
            )
            return Response(
                {"errors": message}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscribePostDelAPIView(APIView):
    """URL requests handler to 'Subscriptions' resource endpoints."""

    def post(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs["author_id"])
        user = request.user
        if author == user:
            raise serializers.ValidationError(
                {"errors": "Subscribing to yourself is not allowed."}
            )
        try:
            Subscription.objects.create(user=user, author=author)
        except IntegrityError:
            message = (
                f"The subscription to the author with id={author.id} "
                f"was created earlier."
            )
            raise serializers.ValidationError({"errors": message})
        author.is_subscribed = True
        serializer = SubscriptionSerializer(author)
        serializer.context["request"] = request
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, **kwargs):
        author_id = kwargs["author_id"]
        try:
            Subscription.objects.get(
                user=request.user, author_id=author_id
            ).delete()
        except ObjectDoesNotExist:
            message = (
                f"There was no subscription to the author with id={author_id}."
            )
            return Response(
                {"errors": message}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionViewSet(ListViewSet):
    """URL requests handler to users/subscriptions/ endpoint."""

    serializer_class = SubscriptionSerializer
    pagination_class = PageNumberLimitPagination

    def get_queryset(self):
        return User.objects.filter(subscription__user=self.request.user)


@api_view(("GET",))
def download_shopping_cart(request):
    """URL requests handler to recipes/download_shopping_cart/ endpoint."""
    ingredients = [
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
    for ingredient in ingredients:
        shopping_list += " ".join((str(el) for el in ingredient)) + "\n"
    return HttpResponse(
        shopping_list, content_type="text/plain", status=status.HTTP_200_OK
    )
