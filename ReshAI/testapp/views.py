import os
from datetime import date, datetime, time

from django.contrib.auth.decorators import login_required, login_not_required
from django.views.generic import ListView
# from .models import ToDoItem
from django.shortcuts import redirect, render
from .forms import ToDoItemForm, MessageForm

from pymongo import MongoClient


def get_db_handle():
    client = MongoClient(host=os.environ.get('MONGODB_CONNECTION_STRING'), port=27017)
    db_handle = client.djangoTutorial.to_do_item
    return db_handle


@login_not_required
class AllToDos(ListView):
    template_name = "test/index.html"

    def get_queryset(self):
        db = get_db_handle()
        results = db.find()
        return results


@login_not_required
class TodayToDos(ListView):
    template_name = "test/today.html"

    def get_queryset(self):
        db = get_db_handle()
        today = datetime.combine(date.today(), time())
        results = db.find({"due_date": today}).sort("due_date")
        return results

@login_required
def add_todo(request):
    if request.method == "POST":
        form = ToDoItemForm(request.POST)
        if form.is_valid():
            new_todo = {
                "text": form.cleaned_data["text"],
                "due_date": datetime.combine(form.cleaned_data["due_date"], time())
            }
            db = get_db_handle()
            db.insert_one(new_todo)
            return redirect('today')
    else:
        form = ToDoItemForm()
    return render(request, "test/add.html", {"form": form})


def chat(request):
    reply = ""
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']
            # response = requests.post(
            #     "https://api.openai.com/v1/chat/completions",
            #     headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
            #     json={
            #         "model": "gpt-3.5-turbo",
            #         "messages": [{"role": "user", "content": message}]
            #     }
            # ).json()
            # reply = response['choices'][0]['message']['content']
            reply = f"this is annswer on your message [{message}]"
    else:
        form = MessageForm()

    return render(request, 'test/chat.html', {'form': form, 'reply': reply})
