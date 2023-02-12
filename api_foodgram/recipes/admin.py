"""Admin site settings of the 'Recipes' application."""

from django.contrib import admin
from django.db.models import Count

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
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
    prepopulated_fields = {"slug": ("name",)}


class RecipeIngredientsInline(admin.TabularInline, StaffAllowedBaseModelAdmin):
    """Table settings for 'RecipeIngredients' model on the admin site."""

    model = RecipeIngredient
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
        "in_favorite",
    )
    readonly_fields = ("in_favorite",)
    inlines = [
        RecipeIngredientsInline,
    ]
    filter_horizontal = ("tags",)
    search_fields = ("author", "name", "tags")
    list_filter = ("author", "name", "tags")

    @staticmethod
    def in_favorite(obj):
        return obj.in_favorite

    def get_queryset(self, request):
        """Annotating objects with "in_favorite" value."""
        qs = Recipe.objects.annotate(in_favorite=Count("favorites"))
        ordering = self.get_ordering(request)
        if ordering:
            qs.order_by(*ordering)
        return qs


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
