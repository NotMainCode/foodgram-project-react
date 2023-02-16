# Generated by Django 2.2.28 on 2023-02-14 04:29

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models

import recipes.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Favorite",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
            options={
                "verbose_name": "favorites",
                "verbose_name_plural": "favorites",
                "ordering": ("recipe__name",),
            },
        ),
        migrations.CreateModel(
            name="Ingredient",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        db_index=True,
                        help_text="Enter ingredient name",
                        max_length=200,
                        verbose_name="ingredient name",
                    ),
                ),
                (
                    "measurement_unit",
                    models.CharField(
                        help_text="Enter measurement unit of ingredient",
                        max_length=200,
                        verbose_name="measurement unit",
                    ),
                ),
            ],
            options={
                "verbose_name": "ingredient",
                "verbose_name_plural": "ingredients",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="Recipe",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        db_index=True,
                        help_text="Enter recipe name",
                        max_length=200,
                        verbose_name="name",
                    ),
                ),
                (
                    "cooking_time",
                    models.PositiveSmallIntegerField(
                        help_text="Enter cooking time in minutes (at least 1 min)",
                        validators=[
                            django.core.validators.MinValueValidator(
                                1,
                                "Cooking time cannot be less than one minute.",
                            )
                        ],
                        verbose_name="cooking time",
                    ),
                ),
                (
                    "text",
                    models.TextField(
                        help_text="Enter description",
                        verbose_name="description",
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        help_text="Add recipe image",
                        upload_to="recipes/images/",
                        verbose_name="recipe image",
                    ),
                ),
                (
                    "pub_date",
                    models.DateTimeField(auto_now_add=True, db_index=True),
                ),
            ],
            options={
                "verbose_name": "recipe",
                "verbose_name_plural": "recipes",
                "ordering": ("-pub_date",),
            },
        ),
        migrations.CreateModel(
            name="RecipeIngredient",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "amount",
                    models.PositiveSmallIntegerField(
                        help_text="Enter amount of ingredient",
                        validators=[
                            django.core.validators.MinValueValidator(
                                1, "Amount cannot be less than one piece."
                            )
                        ],
                        verbose_name="amount",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Enter tag",
                        max_length=200,
                        unique=True,
                        verbose_name="Tag",
                    ),
                ),
                (
                    "color",
                    models.CharField(
                        help_text="Enter color in HEX format",
                        max_length=7,
                        unique=True,
                        validators=[
                            recipes.validators.validate_hex_format_color
                        ],
                        verbose_name="color in HEX format",
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        help_text="Enter tag URL (slug)",
                        max_length=200,
                        unique=True,
                        verbose_name="tag URL (slug)",
                    ),
                ),
            ],
            options={
                "verbose_name": "tag",
                "verbose_name_plural": "tags",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="ShoppingCart",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "recipe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="carts",
                        to="recipes.Recipe",
                        verbose_name="recipe",
                    ),
                ),
            ],
            options={
                "verbose_name": "shopping cart",
                "verbose_name_plural": "shopping carts",
                "ordering": ("id",),
            },
        ),
    ]
