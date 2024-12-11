from turtledemo.clock import datum

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import requests
import json
import json5
import os

# Ваш API-ключ Perplexity


# Функция для загрузки шаблонов промтов
# def load_prompts():
#     prompts = {}
#     base_dir = os.path.join(os.path.dirname(__file__), "..", "prompts")
#     subjects = {
#         "Математика": "matematika.txt",
#         "Физика": "fizika.txt",
#         "История": "istoriya.txt",
#         "Химия": "khimiya.txt",
#         "Биология": "biologiya.txt",
#     }
#     for subject, filename in subjects.items():
#         filepath = os.path.join(base_dir, filename)
#         try:
#             with open(filepath, "r", encoding="utf-8") as file:
#                 prompts[subject] = file.read().strip()
#         except FileNotFoundError:
#             print(f"Файл {filename} не найден.")
#             prompts[subject] = f"Шаблон для {subject} отсутствует."
#     return prompts

def load_prompts():
    data = json5.load(open('configs/prompts.json5', encoding='utf-8'))
    prompts = {}
    for k, v in data.items():
        prompts[k] = "\n".join(v) if isinstance(v, list) else v
    return prompts


# Функция для отправки запроса к Perplexity API
def get_perplexity_response(question):
    api_url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.getenv("PERPLEXITY_API_KEY", "")}",
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
    # print(payload)
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

            # Загрузка промтов из файлов
            prompt_templates = load_prompts()

            # Добавляем контекст предмета в запрос
            template = prompt_templates.get(subject, "{question}")
            question = template.format(question=user_message)

            bot_response = get_perplexity_response(question)
            return JsonResponse({'reply': bot_response}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Некорректные данные'}, status=400)
    return render(request, 'chatapp/chatbot.html')
