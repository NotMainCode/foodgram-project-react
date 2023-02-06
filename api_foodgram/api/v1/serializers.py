"""Serializers of the 'api' application."""

from django.db import IntegrityError
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


class IngredientsAmountSerializer(serializers.ModelSerializer):
    """Nested serializer for RecipeIngredientsSerializer."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), write_only=True
    )

    class Meta:
        model = RecipeIngredients
        fields = (
            "id",
            "amount",
        )


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    """Add serializer for requests to endpoints of 'Recipes' resource."""

    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )
    amount = serializers.SerializerMethodField()
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(), write_only=True
    )
    ingredients = IngredientsAmountSerializer(many=True, write_only=True)

    class Meta:
        model = RecipeIngredients
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
            "recipe",
            "ingredients",
        )

    def get_amount(self, obj):
        if obj.ingredient.measurement_unit in EDITABLE_INGREDIENTS_AMOUNT:
            return ""
        return obj.amount


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for requests to endpoints of 'Recipes' resource."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.context["request"].method in ("GET",):
            self.fields["tags"] = TagSerializer(many=True, read_only=True)

    def get_ingredients(self, obj):
        recipe_ingredients = RecipeIngredients.objects.filter(recipe=obj)
        serializer = RecipeIngredientsSerializer(
            instance=recipe_ingredients, many=True
        )
        return serializer.data

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(
            author=self.context["request"].user, **validated_data
        )
        recipe.tags.set(tags)
        self.initial_data["recipe"] = recipe.id
        serializer = RecipeIngredientsSerializer(data=self.initial_data)
        serializer.is_valid(raise_exception=True)
        try:
            RecipeIngredients.objects.bulk_create(
                [
                    RecipeIngredients(
                        recipe=serializer.validated_data["recipe"],
                        ingredient=ingredient["id"],
                        amount=ingredient["amount"],
                    )
                    for ingredient in serializer.validated_data["ingredients"]
                ],
            )
        except IntegrityError:
            recipe.delete()
            raise serializers.ValidationError(
                {
                    "ingredients_id": "There cannot be two or more of the same ingredient id."
                }
            )
        return recipe


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
