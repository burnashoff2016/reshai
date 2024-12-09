from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import requests
import json

# Ваш API-ключ Perplexity (замените на реальный ключ)
PERPLEXITY_API_KEY = "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"

# Функция для отправки запроса к Perplexity API
def get_perplexity_response(question):
    api_url = "https://api.perplexity.ai/chat/completions"  # Новый URL для чатов
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.1-sonar-small-128k-online",  # Используем модель, указанную вами
        "messages": [{"content": question, "role": "user"}],  # Структура сообщений для чата
        "max_tokens": 0,  # Можно настроить, если нужно ограничение на количество токенов
        "temperature": 0.2,  # Параметры для управления креативностью
        "top_p": 0.9,
        "top_k": 0,
        "stream": False,
        "presence_penalty": 0,
        "frequency_penalty": 1
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()  # Проверка на успешный запрос

        # Распарсить ответ от API
        data = response.json()

        # Поскольку Perplexity API теперь возвращает в формате сообщений, извлекаем ответ
        answer = data.get('choices', [{}])[0].get('message', {}).get('content', "К сожалению, я не смог найти ответ.")
        return answer

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к Perplexity API: {e}")
        return "Произошла ошибка при обращении к API Perplexity."

@csrf_exempt
def chatbot_view(request):
    if request.method == "POST":
        try:
            # Парсим данные из запроса
            data = json.loads(request.body)
            user_message = data.get('message', '')

            if not user_message:
                return JsonResponse({'error': 'Пустое сообщение'}, status=400)

            # Получаем ответ от Perplexity API
            bot_response = get_perplexity_response(user_message)

            return JsonResponse({'reply': bot_response}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Некорректные данные'}, status=400)

    # Для GET-запросов возвращаем страницу с чатом
    return render(request, 'chatapp/chatbot.html')
