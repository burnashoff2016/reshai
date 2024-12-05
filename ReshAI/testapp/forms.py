from django import forms
from datetime import datetime
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from django import forms



class MessageForm(forms.Form):
    message = forms.CharField(label='Ваше сообщение', max_length=1000)

class ToDoItemForm(forms.Form):
    text = forms.CharField(max_length=100)
    due_date = forms.DateField(initial=datetime.now)
