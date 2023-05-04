"""Serializers of the 'api' application."""

from django.db import IntegrityError, transaction
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.pagination import LimitPagination
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.models import Subscription, User


class CustomUserCreateSerializer(UserCreateSerializer):
    """Serializer for POST request to endpoint of 'Users' resource."""

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


class CustomUserSerializer(serializers.ModelSerializer):
    """Serializer for GET requests to endpoints of 'Users' resource."""

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
        model = RecipeIngredient
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
        model = RecipeIngredient
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
            "recipe",
            "ingredients",
        )


class GetRecipeSerializer(serializers.ModelSerializer):
    """Serializer for Get requests to endpoints of 'Recipes' resource."""

    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientsSerializer(
        many=True, read_only=True, source="recipe_ingredient"
    )
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


class PostPatchRecipeSerializer(GetRecipeSerializer):
    """Serializer for Post Patch requests to endpoints of Recipes resource."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    author = CustomUserSerializer(default=serializers.CurrentUserDefault())
    ingredients = IngredientAmountSerializer(many=True)

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

    @staticmethod
    def extract_tags_ingredients(data):
        return data.pop("tags"), data.pop("ingredients")

    @staticmethod
    def add_ingredients_to_recipe(recipe, ingredients):
        try:
            RecipeIngredient.objects.bulk_create(
                [
                    RecipeIngredient(
                        recipe=recipe,
                        ingredient=ingredient["id"],
                        amount=ingredient["amount"],
                    )
                    for ingredient in ingredients
                ],
            )
        except IntegrityError:
            raise serializers.ValidationError(
                {"ingredients_id": "This field must be unique."}
            )
        return recipe

    @transaction.atomic
    def create(self, validated_data, update_obj_id=None):
        tags, ingredients = self.extract_tags_ingredients(validated_data)
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        return self.add_ingredients_to_recipe(recipe, ingredients)

    @transaction.atomic
    def update(self, instance, validated_data):
        tags, ingredients = self.extract_tags_ingredients(validated_data)
        super().update(instance, validated_data)
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        return self.add_ingredients_to_recipe(instance, ingredients)

    def to_representation(self, instance):
        return GetRecipeSerializer(
            instance, context={"request": self.context.get("request")}
        ).data


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


class FavoriteSerializer(serializers.ModelSerializer):
    """Serializer for requests to endpoints of 'Favorites' resource."""

    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = Favorite
        fields = ("user", "recipe")
        validators = (
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=("user", "recipe"),
                message="Recipe was added to favorites earlier.",
            ),
        )

    def to_representation(self, instance):
        return RecipeBriefSerializer(
            instance.recipe, context={"request": self.context.get("request")}
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Serializer for requests to endpoints of 'Shopping list' resource."""

    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = ShoppingCart
        fields = ("user", "recipe")
        validators = (
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=("user", "recipe"),
                message="Recipe was added to the shopping list earlier.",
            ),
        )

    def to_representation(self, instance):
        return RecipeBriefSerializer(
            instance.recipe, context={"request": self.context.get("request")}
        ).data


class SubscribeSerializer(serializers.ModelSerializer):
    """Serializer for Post request to endpoint of 'Subscriptions' resource."""

    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Subscription
        fields = ("user", "author")
        validators = (
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=("user", "author"),
                message="Subscription to this author was created earlier.",
            ),
        )

    def validate_author(self, value):
        if self.context["request"].user == value:
            raise serializers.ValidationError(
                {"errors": "Subscribing to yourself is not allowed."}
            )
        return value

    def to_representation(self, instance):
        author = instance.author
        author.recipes_count = author.recipes.values().count()
        return SubscriptionsSerializer(
            author, context={"request": self.context.get("request")}
        ).data


class SubscriptionsSerializer(CustomUserSerializer):
    """Serializer for requests to users/subscriptions/ endpoint."""

    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.BooleanField(default=True)
    recipes_count = serializers.IntegerField()

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
        request = self.context.get("request")
        queryset = obj.recipes.all()
        if request.query_params.get("recipes_limit") is not None:
            queryset = LimitPagination().paginate_queryset(queryset, request)
        return RecipeBriefSerializer(
            queryset, many=True, context={"request": request}
        ).data
