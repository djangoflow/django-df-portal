import django_filters
from django import forms
from django.db.models import Q
from django.utils.text import smart_split

from tests.test_app.models import Product


class SearchMixin:
    search_fields = []

    def search_filter(self, queryset, name, value):
        if not self.search_fields:
            return queryset

        for term in smart_split(value):
            cond = Q(pk__in=[])
            for field in self.search_fields:
                cond |= Q(**{field: term})
            queryset = queryset.filter(cond)

        return queryset


class BaseSearchFilterSet(django_filters.FilterSet, SearchMixin):
    q = django_filters.CharFilter(
        method="search_filter",
        label="Search",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Search . . .",
                "style": "width: 90px;",
            }
        ),
    )


class ProductFilter(BaseSearchFilterSet):
    search_fields = ["title"]

    class Meta:
        model = Product
        fields = ["q"]
