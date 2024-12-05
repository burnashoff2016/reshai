
from django.contrib import auth
from django.utils import timezone
from django.http import JsonResponse

from django.shortcuts import render,redirect

# from openai import OpenAI

from .models import Chat

# openai_api_key = 'YOUR_API_KEY' # Replace YOUR_API_KEY with your openai apikey
# client = OpenAI(api_key=openai_api_key)

# def ask_openai(message):
#     response = client.chat.completions.create(
#         model = "gpt-3.5-turbo",
#         # prompt = message,
#         # max_tokens=150,
#         # n=1,
#         # stop=None,
#         # temperature=0.7,
#         messages=[
#             {"role": "system", "content": "You are an helpful assistant."},
#             {"role": "user", "content": message},
#         ]
#     )
#     answer = response.choices[0].message.content.strip()
#     return answer
def ask_openai(message):
    return f"Answer. Message: [{message}]"
# Create your views here.

def chatbot(request):
    chats = Chat.objects.filter(user=request.user)


    if request.method == 'POST':
        message = request.POST.get('message')
        response = ask_openai(message)

        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now)
        chat.save()
        return JsonResponse({'message': message, 'response': response})
    return render(request, 'test/chatbot.html', {'chats': chats})




def logout(request):
    auth.logout(request)
    return redirect('login')
