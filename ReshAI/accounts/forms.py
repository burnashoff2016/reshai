from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from accounts.models import CustomUser
from .models import UserProfile

class LoginForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'password')

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

        # Устанавливаем атрибуты для полей
        self.fields['username'].widget.attrs.update({'id': 'username', 'placeholder': 'Username'})
        self.fields['password'].widget.attrs.update({'id': 'password', 'placeholder': 'Password'})

        # Добавление дебага для проверки атрибутов
        self.fields['username'].label = "Имя пользователя"
        self.fields['password'].label = "Пароль"


class SignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        # Устанавливаем уникальные id для полей формы
        self.fields['username'].widget.attrs.update({'id': 'username', 'placeholder': 'Логин'})
        self.fields['email'].widget.attrs.update({'id': 'email', 'placeholder': 'Почта'})
        self.fields['password1'].widget.attrs.update({'id': 'password1', 'placeholder': 'Пароль'})
        self.fields['password2'].widget.attrs.update({'id': 'password2', 'placeholder': 'Повторите пароль'})

        # Устанавливаем метки
        self.fields['username'].label = "Имя пользователя"
        self.fields['email'].label = "Ваша электронная почта"
        self.fields['password1'].label = "Пароль"
        self.fields['password2'].label = "Подтверждение пароля"


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'date_of_birth', 'location']



