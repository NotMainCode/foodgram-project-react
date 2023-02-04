"""Serializers of the 'api' application."""

from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from api_foodgram.settings import EDITABLE_INGREDIENTS_AMOUNT
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingCart,
    Tag,
)
from users.models import User


class CustomUserCreateSerializer(UserCreateSerializer):
    """Modified Djoser UserCreateSerializer ('Users' resource)."""

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "id",
            "username",
            "first_name",
            "last_name",
        )


class UserSerializer(serializers.ModelSerializer):
    """Serializer for requests to endpoints of 'Users' resource."""

    is_subscribed = serializers.BooleanField(read_only=True, default=False)

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for requests to endpoints of 'Ingredients' resource."""

    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
            "measurement_unit",
        )


class TagSerializer(serializers.ModelSerializer):
    """Serializer for requests to endpoints of 'Tags' resource."""

    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "color",
            "slug",
        )


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    """Add serializer for requests to endpoints of 'Recipes' resource."""

    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )
    amount = serializers.SerializerMethodField()

    class Meta:
        model = RecipeIngredients
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )

    def get_amount(self, obj):
        if obj.ingredient.measurement_unit in EDITABLE_INGREDIENTS_AMOUNT:
            return ""
        return obj.amount


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for requests to endpoints of 'Recipes' resource."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.BooleanField(read_only=True, default=False)
    is_in_shopping_cart = serializers.BooleanField(
        read_only=True, default=False
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_ingredients(self, obj):
        recipes = RecipeIngredients.objects.filter(recipe_id=obj.id)
        serializer = RecipeIngredientsSerializer(instance=recipes, many=True)
        return serializer.data


class FavoriteSerializer(serializers.ModelSerializer):
    """Serializer for requests to endpoints of 'Favorites' resource."""

    id = serializers.ReadOnlyField(source="recipe.id")
    name = serializers.ReadOnlyField(source="recipe.name")
    image = serializers.CharField(source="recipe.image", read_only=True)
    cooking_time = serializers.ReadOnlyField(source="recipe.cooking_time")

    class Meta:
        model = Favorite
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Serializer for requests to endpoints of 'Shopping list' resource."""

    id = serializers.ReadOnlyField(source="recipe.id")
    name = serializers.ReadOnlyField(source="recipe.name")
    image = serializers.CharField(source="recipe.image", read_only=True)
    cooking_time = serializers.ReadOnlyField(source="recipe.cooking_time")

    class Meta:
        model = ShoppingCart
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )
