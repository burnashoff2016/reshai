from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import requests
import json

# Ваш API-ключ Perplexity
PERPLEXITY_API_KEY = "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"

# Функция для отправки запроса к Perplexity API
def get_perplexity_response(question):
    api_url = "https://api.perplexity.ai/chat/completions"  # Новый URL для чатов
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.1-sonar-large-128k-online",
        "messages": [{"content": question, "role": "user"}],
        "max_tokens": 0,
        "temperature": 0.2,
        "top_p": 0.9,
        "top_k": 0,
        "stream": False,
        "presence_penalty": 0,
        "frequency_penalty": 1
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        answer = data.get('choices', [{}])[0].get('message', {}).get('content', "К сожалению, я не смог найти ответ.")
        return answer
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к Perplexity API: {e}")
        return "Произошла ошибка при обращении к API Perplexity."

@csrf_exempt
def chatbot_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            subject = data.get('subject', '')  # Получаем выбранный предмет

            if not user_message or not subject:
                return JsonResponse({'error': 'Пустое сообщение или не выбран предмет'}, status=400)

            # Добавляем контекст предмета в запрос
            question = f"[{subject}] {user_message}"

            bot_response = get_perplexity_response(question)
            return JsonResponse({'reply': bot_response}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Некорректные данные'}, status=400)
    return render(request, 'chatapp/chatbot.html')
