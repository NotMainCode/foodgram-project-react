"""Database settings of the 'Recipes' application."""

from django.core.validators import MinValueValidator, validate_slug
from django.db import models

from recipes.validators import validate_hex_format_color
from users.models import User


class Ingredient(models.Model):
    """Table settings for ingredients of recipe."""

    name = models.CharField(
        max_length=200,
        verbose_name="ingredient name",
        help_text="Enter ingredient name",
        db_index=True,
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name="measurement unit",
        help_text="Enter measurement unit of ingredient",
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "ingredient"
        verbose_name_plural = "ingredients"
        constraints = (
            models.UniqueConstraint(
                fields=["name", "measurement_unit"], name="unique_ingredient"
            ),
        )

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"


class Tag(models.Model):
    """Table settings for tag of recipe."""

    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Tag",
        help_text="Enter tag",
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        verbose_name="color in HEX format",
        help_text="Enter color in HEX format",
        validators=(validate_hex_format_color,),
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name="tag URL (slug)",
        help_text="Enter tag URL (slug)",
        validators=(validate_slug,),
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "tag"
        verbose_name_plural = "tags"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Table settings for recipe."""

    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name="name",
        help_text="Enter recipe name",
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="recipes",
        verbose_name="tag",
        help_text="Choose tag",
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="cooking time",
        help_text="Enter cooking time in minutes (at least 1 min)",
        validators=(
            MinValueValidator(
                1, "Cooking time cannot be less than one minute."
            ),
        ),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="author",
        help_text="Choose author",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredients",
        related_name="recipes",
        verbose_name="ingredients",
        help_text="Add ingredient",
    )
    text = models.TextField(
        verbose_name="description",
        help_text="Enter description",
    )
    image = models.ImageField(
        upload_to="recipes/images/",
        verbose_name="recipe image",
        help_text="Add recipe image",
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "recipe"
        verbose_name_plural = "recipes"

    def __str__(self):
        return self.name


class RecipeIngredients(models.Model):
    """Intermediary model for amount of ingredient in recipe."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="amount",
        help_text="Enter amount of ingredient",
        validators=(
            MinValueValidator(1, "Amount cannot be less than one piece."),
        ),
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique_recipe_ingredient",
            ),
        )


class Favorite(models.Model):
    """Table settings for favorites recipes."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="chooser",
        verbose_name="chooser",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="recipe",
    )

    class Meta:
        ordering = ("recipe__name",)
        verbose_name = "favorites"
        verbose_name_plural = "favorites"
        constraints = (
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_favorite"
            ),
        )


class ShoppingCart(models.Model):
    """Table settings for user shopping cart."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="customer",
        verbose_name="customer",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="order",
        verbose_name="recipe",
    )

    class Meta:
        ordering = ("id",)
        verbose_name = "shopping cart"
        verbose_name_plural = "shopping carts"
        constraints = (
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_shopping_cart"
            ),
        )
