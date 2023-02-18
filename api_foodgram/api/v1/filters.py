"""Custom filters."""

from django.db.models import Case, IntegerField, Value, When
from django_filters import rest_framework
from rest_framework import filters

from recipes.models import Recipe, Tag


class RecipeFilter(rest_framework.FilterSet):
    """Filter for 'Recipes' resource."""

    is_in_shopping_cart = rest_framework.BooleanFilter(
        label="In shopping cart"
    )
    is_favorited = rest_framework.BooleanFilter(label="In favorites")
    author = rest_framework.NumberFilter()
    tags = rest_framework.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name="tags__slug",
        to_field_name="slug",
    )

    class Meta:
        model: Recipe
        fields = ("author", "is_favorited", "is_in_shopping_cart", "tags")


class IngredientSearchFilter(filters.SearchFilter):
    """Filter for 'Ingredients' resource."""

    search_param = "name"

    def filter_queryset(self, request, queryset, view):
        name = request.query_params.get(self.search_param)
        if name is not None:
            queryset = queryset.annotate(
                ingredient_order=Case(
                    When(name__istartswith=name, then=Value(1)),
                    When(name__icontains=name, then=Value(2)),
                    default=0,
                    output_field=IntegerField(),
                )
            ).exclude(ingredient_order=0).order_by("ingredient_order", "name")
        return queryset
