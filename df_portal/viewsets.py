from dataclasses import dataclass
from functools import cached_property
from typing import Type, Optional

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Model
from django.forms import ModelForm
from django.urls import reverse, path
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView, RedirectView
from django.views.generic.list import MultipleObjectMixin
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from df_portal.forms import BaseFilterFormHelper
from df_portal.sites import PortalSite


def view_meta(*, action: str, permission_verb: str, pk_in_url: bool = False):
    meta = ViewMeta(
        action=action,
        permission_verb=permission_verb,
        pk_in_url=pk_in_url,
    )

    def wrapper(method):
        method.meta = meta
        return method

    return wrapper


class ViewsetViewInfo:
    index_name: str
    index_permission: str
    update_name: str
    update_permission: str
    create_name: str
    create_permission: str
    delete_name: str
    delete_permission: str
    detail_name: str
    detail_permission: str
    customaction_name: str
    customaction_permission: str


@dataclass
class ViewMeta:
    action: str
    permission_verb: str
    pk_in_url: bool = False

    def view_route(self, model):
        pk_part = "<pk>/" if self.pk_in_url else ""
        return f"{model._meta.model_name}/{pk_part}{self.action}"

    def view_name(self, model):
        return f"{model._meta.model_name}/{self.action}"

    def permission(self, model):
        return f"{model._meta.app_label}.{self.permission_verb}_{model._meta.model_name}"


class PortalBaseMixin(LoginRequiredMixin):
    meta: ViewMeta
    site: PortalSite
    model: Type[Model]

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return self.handle_no_permission()

        if not request.user.has_perm(self.meta.permission):
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)

    def get_login_url(self):
        return reverse(f"{self.site.name}:login")

    def get_template_names(self):
        return [
            f"portal/{self.model._meta.model_name}/{self.meta.action}.html",
            f"portal/{self.meta.action}.html",
            f"portal/{self.site.theme}/{self.meta.action}.html",
        ]

class PortalViewSet:
    model = None
    model_verbose_name = ""
    model_verbose_name_plural = ""

    table_class = None
    form_helper_class = BaseFilterFormHelper
    filterset_class = None
    paginate_by = 25

    create_form_class = None
    update_form_class = None
    default_form_fields = "__all__"
    default_form_widgets = {}
    form_prepopulate_from_params = True

    custom_actions = {}

    def __init__(self, site: PortalSite):
        self.site = site

    def get_create_form_class(self):
        return self.create_form_class or self.default_form_class()

    def get_update_form_class(self):
        return self.create_form_class or self.default_form_class()

    def default_form_class(self):
        class DynamicForm(ModelForm):
            class Meta:
                model = self.model
                fields = self.default_form_fields
                widgets = self.default_form_widgets

        return DynamicForm

    @property
    def model_meta(self):
        return self.model._meta

    def get_model_verbose_name(self):
        return self.model_verbose_name or self.model_meta.verbose_name

    def get_model_verbose_name_plural(self):
        return self.model_verbose_name_plural or self.model_meta.verbose_name_plural

    def change_form_valid(self, request, form, *, created: bool):
        messages.success(request, "Data saved")

    def additional_context(self, request):
        return {
            "site": self.site,
            "sidebar": self.site.sidebar(request),

            "model_meta": self.model_meta,
            "model_verbose_name": self.get_model_verbose_name(),
            "model_verbose_name_plural": self.get_model_verbose_name_plural(),

            "index_view_url": self.index_view.meta,
            "index_view_permissiom": self.index_view.meta,
            "update_view_meta": self.index_view.meta,
            "create_view_meta": self.index_view.meta,
            "delete_view_meta": self.index_view.meta,
        }

    @property
    def views(self):
        info = ViewsetViewInfo()

        for view in self.view_methods:
            setattr(info, f"{view.meta.action}_name", f"{self.site.name}:{self.index_view.meta.view_name(self.model)}")
            setattr(info, f"{view.meta.action}_permission", self.index_view.meta.permission(self.model))

        return info

    @cached_property
    def view_methods(self):
        views = []
        for method_name in dir(self):
            if method_name in ["view_methods", "views"] or method_name.startswith('__'):
                continue
            method = getattr(self, method_name)
            meta = getattr(method, "meta", None)
            if not isinstance(meta, ViewMeta):
                continue

            views.append(method)

        return views

    def get_urls(self):
        return [path(
            view.meta.view_route(self.model),
            view().as_view(),
            name=view.meta.view_name(self.model),
        ) for view in self.view_methods]

    @view_meta(action="index", permission_verb="view")
    def index_view(self):
        viewset = self

        class BaseListView(PortalBaseMixin, SingleTableMixin, FilterView):
            meta = self.index_view.meta
            site = self.site
            model = self.model

            formhelper_class = self.form_helper_class
            paginate_by = self.paginate_by
            filterset_class = self.filterset_class
            table_class = self.table_class

            def get_filterset(self, filterset_class):
                kwargs = self.get_filterset_kwargs(filterset_class)
                filterset = filterset_class(**kwargs)
                filterset.form.helper = self.formhelper_class(filterset.form)
                return filterset

            def get_context_data(self, **kwargs):
                return {
                    **super().get_context_data(**kwargs),
                    **viewset.additional_context(self.request),
                }

        return BaseListView

    @view_meta(action="create", permission_verb="add")
    def create_view(self):
        viewset = self

        class BaseCreateView(PortalBaseMixin, CreateView):
            meta = self.create_view.meta
            site = self.site
            model = self.model

            form_class = self.get_create_form_class()

            def get_context_data(self, **kwargs):
                return {
                    **super().get_context_data(**kwargs),
                    **viewset.additional_context(self.request),
                }

            def form_valid(self, form):
                response = super().form_valid(form)
                viewset.change_form_valid(self.request, form, created=True)
                return response

            def get_form_kwargs(self):
                kwargs = super().get_form_kwargs()
                kwargs["request"] = self.request
                if self.request.method == "GET" and viewset.form_prepopulate_from_params:
                    kwargs["initial"] = dict(self.request.GET)
                return kwargs

            # def get_success_url(self):
            #     if self.request.user.has_perm(viewset.)
            #
            #     if "update" in cls.enabled_actions:
            #         return (
            #                 reverse(
            #                     f"{cls.app_label}:{cls.model_name()}/update",
            #                     args=[self.object.id],
            #                 )
            #                 + self.user_query_param()
            #         )
            #     return super().get_success_url()

        return BaseCreateView

    @view_meta(action="update", permission_verb="change", pk_in_url=True)
    def update_view(self):
        viewset = self

        class BaseUpdateView(PortalBaseMixin, UpdateView):
            meta = self.update_view.meta
            site = self.site
            model = self.model

            form_class = self.get_update_form_class()

            def form_valid(self, form):
                response = super().form_valid(form)
                viewset.change_form_valid(self.request, form, created=False)
                return response

            def get_context_data(self, **kwargs):
                return {
                    **super().get_context_data(**kwargs),
                    **viewset.additional_context(self.request),
                }

            def get_form_kwargs(self):
                return {
                    **super().get_form_kwargs(),
                    "request": self.request,
                }

            # def get_success_url(self):
            #     return (
            #         reverse(
            #             f"{self.site.name}:{self.meta.view_name(self.model)}",
            #             args=[self.object.id],
            #         )
            #         + self.user_query_param()
            #     )

        return BaseUpdateView

    @view_meta(action="detail", permission_verb="view", pk_in_url=True)
    def detail_view(self):
        viewset = self

        class BaseDetailView(PortalBaseMixin, DetailView):
            meta = self.index_view.meta
            site = self.site
            model = self.model

            def get_context_data(self, **kwargs):
                return {
                    **super().get_context_data(**kwargs),
                    **viewset.additional_context(self.request),
                }

        return BaseDetailView

    @view_meta(action="delete", permission_verb="remove", pk_in_url=True)
    def delete_view(self):
        viewset = self

        class BaseDeleteView(PortalBaseMixin, DeleteView):
            meta = self.index_view.meta
            site = self.site
            model = self.model

            def get_context_data(self, **kwargs):
                return {
                    **super().get_context_data(**kwargs),
                    **viewset.additional_context(self.request),
                }

        return BaseDeleteView

    @view_meta(action="customaction", permission_verb="change", pk_in_url=True)
    def customaction_view(self):
        viewset = self

        class CustomActionView(PortalBaseMixin, MultipleObjectMixin, RedirectView):
            meta = self.index_view.meta
            site = self.site
            model = self.model

            def get_redirect_url(self, *args, **kwargs):
                action = self.request.POST.get("action")
                if action not in viewset.custom_actions:
                    raise ValueError(f"Invalid custom action {action}")

                handler = viewset.custom_actions[action]
                pk_list = self.request.POST.getlist("checkbox")
                queryset = self.get_queryset().filter(pk__in=pk_list)
                handler(queryset, self)
                return reverse(viewset.views.index_name)

        return CustomActionView
