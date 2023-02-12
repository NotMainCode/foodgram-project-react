"""Serializers of the 'api' application."""

from django.db import IntegrityError, transaction
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

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
        recipe_ingredients = RecipeIngredient.objects.filter(recipe=obj)
        serializer = RecipeIngredientsSerializer(
            instance=recipe_ingredients, many=True
        )
        return serializer.data


class PostPatchRecipeSerializer(GetRecipeSerializer):
    """Serializer for Post Patch requests to endpoints of Recipes resource."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
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

    @transaction.atomic
    def create(self, validated_data, update_obj_id=None):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        instance_data = validated_data
        instance_data["author"] = self.context["request"].user
        recipe, created = Recipe.objects.update_or_create(
            id=update_obj_id,
            defaults=instance_data,
        )
        recipe.tags.set(tags)
        for ingredient in ingredients:
            ingredient["id"] = ingredient["id"].id
        data = {"recipe": recipe.id, "ingredients": ingredients}
        serializer = RecipeIngredientsSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        if not created:
            RecipeIngredient.objects.filter(recipe=recipe).delete()
        try:
            RecipeIngredient.objects.bulk_create(
                [
                    RecipeIngredient(
                        recipe=serializer.validated_data["recipe"],
                        ingredient=ingredient["id"],
                        amount=ingredient["amount"],
                    )
                    for ingredient in serializer.validated_data["ingredients"]
                ],
            )
        except IntegrityError:
            raise serializers.ValidationError(
                {"ingredients_id": "This field must be unique."}
            )
        return recipe

    def update(self, instance, validated_data):
        recipe = self.create(validated_data, update_obj_id=instance.id)
        return recipe

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

    class Meta:
        model = Favorite
        fields = ("user", "recipe")

    def validate(self, attrs):
        recipe_id = attrs["recipe"].id
        if Favorite.objects.filter(
            user=self.context["request"].user, recipe_id=recipe_id
        ).exists():
            message = (
                f"The recipe with id={recipe_id} "
                f"was added to favorites earlier."
            )
            raise serializers.ValidationError({"errors": message})
        return attrs

    def to_representation(self, instance):
        return RecipeBriefSerializer(
            instance.recipe, context={"request": self.context.get("request")}
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Serializer for requests to endpoints of 'Shopping list' resource."""

    class Meta:
        model = ShoppingCart
        fields = ("user", "recipe")

    def validate(self, attrs):
        recipe_id = attrs["recipe"].id
        if ShoppingCart.objects.filter(
            user=self.context["request"].user, recipe_id=recipe_id
        ).exists():
            message = (
                f"The recipe with id={recipe_id} "
                f"was added to the shopping list earlier."
            )
            raise serializers.ValidationError({"errors": message})
        return attrs

    def to_representation(self, instance):
        request = self.context.get("request")
        return RecipeBriefSerializer(
            instance.recipe, context={"request": request}
        ).data


class SubscribeSerializer(serializers.ModelSerializer):
    """Serializer for Post request to endpoint of 'Subscriptions' resource."""

    class Meta:
        model = Subscription
        fields = ("user", "author")

    def validate(self, attrs):
        user = self.context["request"].user
        author = attrs["author"]
        if Subscription.objects.filter(user=user, author=author).exists():
            message = (
                f"The subscription to the author with id={author.id} "
                f"was created earlier."
            )
            raise serializers.ValidationError({"errors": message})
        if user == author:
            raise serializers.ValidationError(
                {"errors": "Subscribing to yourself is not allowed."}
            )
        return attrs

    def to_representation(self, instance):
        author = instance.author
        author.recipes_count = author.recipes.values().count()
        return SubscriptionsSerializer(
            author, context={"request": self.context.get("request")}
        ).data


class SubscriptionsSerializer(UserSerializer):
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
        serializer = RecipeBriefSerializer(
            LimitPagination().paginate_queryset(obj.recipes.all(), request),
            many=True,
            context={"request": request},
        )
        return serializer.data
