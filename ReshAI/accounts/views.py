
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import FormView

from accounts import forms


class SignUpView(generic.CreateView):
    form_class = forms.SignUpForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

    # def dispatch(self, request, *args, **kwargs):
    #     return render(request, 'registration/403_signup.html')

class LoginView(FormView):
    form_class = forms.LoginForm
    template_name = 'registration/login.html'
    success_url = reverse_lazy('/')


