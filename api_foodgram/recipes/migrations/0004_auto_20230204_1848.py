# Generated by Django 2.2.28 on 2023-02-04 15:48

import re

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import recipes.validators


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0003_auto_20230202_0439"),
    ]

    operations = [
        migrations.AlterField(
            model_name="favorite",
            name="recipe",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="favorites",
                to="recipes.Recipe",
                verbose_name="recipe",
            ),
        ),
        migrations.AlterField(
            model_name="favorite",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="chooser",
                to=settings.AUTH_USER_MODEL,
                verbose_name="chooser",
            ),
        ),
        migrations.AlterField(
            model_name="ingredient",
            name="measurement_unit",
            field=models.CharField(
                help_text="Enter measurement unit of ingredient",
                max_length=200,
                verbose_name="measurement unit",
            ),
        ),
        migrations.AlterField(
            model_name="ingredient",
            name="name",
            field=models.CharField(
                db_index=True,
                help_text="Enter ingredient name",
                max_length=200,
                verbose_name="ingredient name",
            ),
        ),
        migrations.AlterField(
            model_name="recipe",
            name="author",
            field=models.ForeignKey(
                help_text="Choose author",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="recipes",
                to=settings.AUTH_USER_MODEL,
                verbose_name="author",
            ),
        ),
        migrations.AlterField(
            model_name="recipe",
            name="cooking_time",
            field=models.PositiveSmallIntegerField(
                help_text="Enter cooking time in minutes (at least 1 min)",
                validators=[
                    django.core.validators.MinValueValidator(
                        1, "Cooking time cannot be less than one minute."
                    )
                ],
                verbose_name="cooking time",
            ),
        ),
        migrations.AlterField(
            model_name="recipe",
            name="image",
            field=models.ImageField(
                help_text="Add recipe image",
                upload_to="recipes/images/",
                verbose_name="recipe image",
            ),
        ),
        migrations.AlterField(
            model_name="recipe",
            name="ingredients",
            field=models.ManyToManyField(
                help_text="Add ingredient",
                related_name="recipes",
                through="recipes.RecipeIngredients",
                to="recipes.Ingredient",
                verbose_name="ingredients",
            ),
        ),
        migrations.AlterField(
            model_name="recipe",
            name="name",
            field=models.CharField(
                db_index=True,
                help_text="Enter recipe name",
                max_length=200,
                verbose_name="name",
            ),
        ),
        migrations.AlterField(
            model_name="recipe",
            name="tags",
            field=models.ManyToManyField(
                help_text="Choose tag",
                related_name="recipes",
                to="recipes.Tag",
                verbose_name="tag",
            ),
        ),
        migrations.AlterField(
            model_name="recipe",
            name="text",
            field=models.TextField(
                help_text="Enter description", verbose_name="description"
            ),
        ),
        migrations.AlterField(
            model_name="recipeingredients",
            name="amount",
            field=models.PositiveSmallIntegerField(
                help_text="Enter amount of ingredient",
                validators=[
                    django.core.validators.MinValueValidator(
                        1, "Amount cannot be less than one piece."
                    )
                ],
                verbose_name="amount",
            ),
        ),
        migrations.AlterField(
            model_name="shoppingcart",
            name="recipe",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="order",
                to="recipes.Recipe",
                verbose_name="recipe",
            ),
        ),
        migrations.AlterField(
            model_name="shoppingcart",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="customer",
                to=settings.AUTH_USER_MODEL,
                verbose_name="customer",
            ),
        ),
        migrations.AlterField(
            model_name="tag",
            name="color",
            field=models.CharField(
                help_text="Enter color in HEX format",
                max_length=7,
                unique=True,
                validators=[recipes.validators.validate_hex_format_color],
                verbose_name="color in HEX format",
            ),
        ),
        migrations.AlterField(
            model_name="tag",
            name="slug",
            field=models.SlugField(
                help_text="Enter tag URL (slug)",
                max_length=200,
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        re.compile("^[-a-zA-Z0-9_]+\\Z"),
                        "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.",
                        "invalid",
                    )
                ],
                verbose_name="tag URL (slug)",
            ),
        ),
        migrations.AddConstraint(
            model_name="shoppingcart",
            constraint=models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_shopping_cart"
            ),
        ),
    ]