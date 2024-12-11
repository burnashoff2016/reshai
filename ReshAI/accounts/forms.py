from django import forms
from django.contrib.auth.forms import UserCreationForm

from accounts.models import CustomUser


class SignUpForm(UserCreationForm):
    # email = forms.EmailField(max_length=254, help_text='Обязательное поле. Введите действующий email.')
    # phone_number = forms.CharField(max_length=15, required=False, help_text='Необязательное поле.')

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')