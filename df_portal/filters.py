from copy import deepcopy

import django_filters
from django import forms
from django.db import models
from django.db.models import Q
from django.utils.text import smart_split
from django_filters.filterset import FILTER_FOR_DBFIELD_DEFAULTS
from django_select2 import forms as s2forms
from df_portal.sites import site


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


FILTER_DEFAULTS = deepcopy(FILTER_FOR_DBFIELD_DEFAULTS)

WIDGET_MAP = {
    models.OneToOneField: s2forms.ModelSelect2Widget,
    models.ForeignKey: s2forms.ModelSelect2Widget,
    models.ManyToManyField: s2forms.ModelSelect2MultipleWidget,
    models.OneToOneRel: s2forms.ModelSelect2Widget,
    models.ManyToOneRel: s2forms.ModelSelect2MultipleWidget,
    models.ManyToManyRel: s2forms.ModelSelect2MultipleWidget,
}

for field in WIDGET_MAP:
    try:
        extra = FILTER_DEFAULTS[field]["extra"]

        def extra_(f):
            viewset = site.viewset(f.model)
            return {
                **extra(f),
                "widget": WIDGET_MAP[f.__class__](
                    search_fields=viewset.filterset_search_fields,
                    attrs={"data-placeholder": viewset.get_model_verbose_name().title()},
                ),
            }

        FILTER_DEFAULTS[field]["extra"] = extra_
    except ValueError:
        pass


class BaseFilterSet(django_filters.FilterSet):
    FILTER_DEFAULTS = FILTER_DEFAULTS


class BaseSearchFilterSet(BaseFilterSet, SearchMixin):
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
