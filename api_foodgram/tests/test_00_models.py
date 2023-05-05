"""Model constraint tests."""

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
)
from recipes.validators import validate_hex_format_color
from users.models import Subscription, User


class ModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_author = User.objects.create_user(
            username="author", email="author@email.fake"
        )
        cls.ingredient = Ingredient.objects.create(
            name="ingredient_one", measurement_unit="measurement_unit"
        )
        cls.recipe = Recipe.objects.create(
            cooking_time=1,
            author=cls.user_author,
        )
        RecipeIngredient.objects.create(
            recipe=cls.recipe,
            ingredient=cls.ingredient,
            amount=1,
        )

    def test_subscription_model(self):
        """The 'Subscription' model has constraints."""
        user_subscriber = User.objects.create_user(username="subscriber")
        Subscription.objects.create(
            user=user_subscriber, author=self.user_author
        )
        user_message = {
            self.user_author: (
                "The 'Subscription' model "
                "does not include the constraint that "
                "a subscriber cannot subscribe to itself."
            ),
            user_subscriber: (
                "The 'Subscription' model does not contain the constraint: "
                "the subscriber and the author together must be unique."
            ),
        }
        for user, message in user_message.items():
            with self.subTest(msg=message, user=user, author=self.user_author):
                with transaction.atomic():
                    self.assertRaises(
                        IntegrityError,
                        Subscription.objects.create,
                        user=user,
                        author=self.user_author,
                    )

    def test_ingredient_model(self):
        """The 'Ingredient' model has constraints."""
        with self.assertRaises(
            IntegrityError,
            msg=(
                "The 'Ingredient' model does not contain the constraint: "
                "the name and the measurement_unit together must be unique."
            ),
        ):
            Ingredient.objects.create(
                name=self.ingredient.name,
                measurement_unit=self.ingredient.measurement_unit,
            )

    def test_tag_model(self):
        """Validator for "color" field of "Tag" model is working correctly."""
        invalid_hex_format_color = (
            "123",
            "#1",
            "#1a",
            "#1a2b",
            "#12345",
            "#1234567",
            "#abcdefa",
            "#ggg",
        )
        for color in invalid_hex_format_color:
            with self.subTest(
                msg=(
                    "The 'color' field validator of the 'Tag' model "
                    "does not work correctly."
                ),
                color=color,
            ):
                self.assertRaises(
                    ValidationError, validate_hex_format_color, color
                )

    def test_recipe_ingredient_through_model(self):
        """The 'RecipeIngredient' model has constraints."""
        with self.assertRaises(
            IntegrityError,
            msg=(
                "The 'RecipeIngredient' model "
                "does not contain the constraint: "
                "the recipe_id and the ingredient_id together must be unique."
            ),
        ):
            RecipeIngredient.objects.create(
                recipe=self.recipe,
                ingredient=self.ingredient,
                amount=1,
            )

    def test_favorite_model(self):
        """The 'Favorite' model has constraints."""
        favorite_item = Favorite.objects.create(
            user=self.user_author,
            recipe=self.recipe,
        )
        with self.assertRaises(
            IntegrityError,
            msg=(
                "The 'Favorite' model does not contain the constraint: "
                "the user and the recipe together must be unique."
            ),
        ):
            Favorite.objects.create(
                user=favorite_item.user,
                recipe=favorite_item.recipe,
            )

    def test_shopping_cart_model(self):
        """The 'ShoppingCart' model has constraints."""
        cart_item = ShoppingCart.objects.create(
            user=self.user_author,
            recipe=self.recipe,
        )
        with self.assertRaises(
            IntegrityError,
            msg=(
                "The 'ShoppingCart' model does not contain the constraint: "
                "the user and the recipe together must be unique."
            ),
        ):
            ShoppingCart.objects.create(
                user=cart_item.user,
                recipe=cart_item.recipe,
            )
