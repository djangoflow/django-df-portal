from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Username", "class": "form-control"}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Password", "class": "form-control"}
        )
    )


def login_view(request, site, **kwargs):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(site.views.home_name)
            else:
                msg = "Invalid credentials"
        else:
            msg = "Error validating the form"

    return render(
        request, f"portal/{site.theme}/login.html", {"form": form, "msg": msg}
    )


def logout_view(request, site, **kwargs):
    logout(request)
    return redirect(site.views.login_name)


def home_view(request, site):
    for viewset in site._registry.values():
        if request.user.has_perm(viewset.views.index_permission):
            return redirect(viewset.views.index_name)

    return HttpResponse("Please contact your administrator")
