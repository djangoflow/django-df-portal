from django import forms
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render


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


def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("portal:userprofile/index")
            else:
                msg = "Invalid credentials"
        else:
            msg = "Error validating the form"

    return render(request, "portal/datta-able/login.html", {"form": form, "msg": msg})


def logout_view(request):
    logout(request)
    return redirect("portal:login")
