"""Admin site settings of the 'Recipes' application."""

from django.contrib import admin

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingCart,
    Tag,
)
from users.admin_site_permissions import (
    StaffAllowedBaseModelAdmin,
    StaffAllowedModelAdmin,
)


@admin.register(Ingredient)
class IngredientAdmin(StaffAllowedModelAdmin):
    """Table settings for resource 'Ingredient' on the admin site."""

    list_display = (
        "pk",
        "name",
        "measurement_unit",
    )
    search_fields = ("name",)
    list_filter = ("name",)


@admin.register(Tag)
class TagAdmin(StaffAllowedModelAdmin):
    """Table settings for resource 'Tag' on the admin site."""

    list_display = (
        "pk",
        "name",
        "color",
        "slug",
    )
    search_fields = ("name",)


class RecipeIngredientsInline(admin.TabularInline, StaffAllowedBaseModelAdmin):
    """Table settings for 'RecipeIngredients' model on the admin site."""

    model = RecipeIngredients
    min_num = 1
    extra = 5


@admin.register(Recipe)
class RecipeAdmin(StaffAllowedModelAdmin):
    """Table settings for resource 'Recipe' on the admin site."""

    list_display = (
        "pk",
        "author",
        "name",
        "cooking_time",
    )
    inlines = [
        RecipeIngredientsInline,
    ]
    filter_horizontal = ("tags",)
    search_fields = ("author", "name", "tags")
    list_filter = ("author", "name", "tags")


@admin.register(Favorite)
class FavoriteAdmin(StaffAllowedModelAdmin):
    """Table settings for resource 'Favorite' on the admin site."""

    list_display = (
        "pk",
        "user",
        "recipe",
    )
    search_fields = ("user__username",)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(StaffAllowedModelAdmin):
    """Table settings for resource 'Shopping cart' on the admin site."""

    list_display = (
        "pk",
        "user",
        "recipe",
    )
    search_fields = ("user__username",)
