from django.shortcuts import render, redirect

def index(request):
    return render(request, 'mainapp/index.html')

def about(request):
    return render(request, 'mainapp/about.html')

def contact(request):
    return render(request, 'mainapp/contact.html')

def chat_redirect(request):
    # Перенаправление на страницу chatapp
    return redirect('/chat/')
