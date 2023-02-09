"""Serializers of the 'api' application."""

from django.db import IntegrityError
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredients,
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


class IngredientAmountSerializer(serializers.ModelSerializer):
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
    """Nested serializer for RecipeSerializer."""

    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )
    amount = serializers.ReadOnlyField()
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(), write_only=True
    )
    ingredients = IngredientAmountSerializer(many=True, write_only=True)

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
                {"ingredients_id": "This field must be unique."}
            )
        return recipe

    def update(self, instance, validated_data):
        recipe = self.create(validated_data)
        instance.delete()
        return recipe


class RecipeBriefSerializer(serializers.ModelSerializer):
    """Brief information about the recipe."""

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class SubscriptionSerializer(UserSerializer):
    """Serializer for requests to endpoints of 'Subscriptions' resource."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj)
        recipes_limit = self.context["request"].query_params.get(
            "recipes_limit"
        )
        if recipes_limit is not None:
            try:
                recipes = recipes[: int(recipes_limit)]
            except (ValueError, AssertionError):
                message = (
                    f"Invalid query parameter value: "
                    f"recipes_limit={recipes_limit}."
                )
                raise serializers.ValidationError({"errors": message})
        serializer = RecipeBriefSerializer(instance=recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()
