"""URLs request handlers of the 'api' application."""

from django.db.models import (
    Count,
    Exists,
    OuterRef,
    Sum,
)
from django.http.response import HttpResponse
from django_filters import rest_framework
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.pagination import PageNumberLimitPagination
from api.v1.filters import IngredientSearchFilter, RecipeFilter
from api.v1.permissions import IsAuthorOrReadOnly
from api.v1.serializers import (
    CustomUserCreateSerializer,
    CustomUserSerializer,
    FavoriteSerializer,
    GetRecipeSerializer,
    IngredientSerializer,
    PostPatchRecipeSerializer,
    ShoppingCartSerializer,
    SubscribeSerializer,
    SubscriptionsSerializer,
    TagSerializer,
)
from api.viewsets import (
    CustomCreateDestroyViewSet,
    GetPostPatchDeleteViewSet,
    GetPostViewSet,
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


class CustomUserViewSet(GetPostViewSet):
    """URL requests handler to 'Users' resource endpoints."""

    permission_classes = (AllowAny,)
    pagination_class = PageNumberLimitPagination

    def get_queryset(self):
        if self.action == "subscriptions":
            return User.objects.filter(
                subscription__user=self.request.user
            ).annotate(recipes_count=(Count("recipes")))
        queryset = User.objects.all()
        user = self.request.user
        if self.request.method == "GET" and user.is_authenticated:
            subquery = Subscription.objects.filter(
                user=user, author=OuterRef("pk")
            )
            queryset = queryset.annotate(is_subscribed=(Exists(subquery)))
        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return CustomUserCreateSerializer
        elif self.action == "subscriptions":
            return SubscriptionsSerializer
        return CustomUserSerializer

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def me(self, request):
        return Response(self.get_serializer(request.user).data)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        return super().list(self, request)


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

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
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


class FavoriteViewSet(CustomCreateDestroyViewSet):
    """URL requests handler to 'Favorites' resource endpoints."""

    serializer_class = FavoriteSerializer
    model = Favorite
    request_instance_field = "recipe"
    request_kwarg = "recipe_id"
    error_message = "Recipe was not in the favorites."


class ShoppingCartViewSet(CustomCreateDestroyViewSet):
    """URL requests handler to 'Shopping list' resource endpoints."""

    serializer_class = ShoppingCartSerializer
    model = ShoppingCart
    request_instance_field = "recipe"
    request_kwarg = "recipe_id"
    error_message = "Recipe was not in the shopping list."


class SubscribeViewSet(CustomCreateDestroyViewSet):
    """URL requests handler to  endpoints of 'Subscriptions' resource."""

    serializer_class = SubscribeSerializer
    model = Subscription
    request_instance_field = "author"
    request_kwarg = "author_id"
    error_message = "There was no subscription to this author."
