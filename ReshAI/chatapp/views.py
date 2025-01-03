import logging
from urllib import request
from venv import logger

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import requests
import json
import json5
import os
import docx
import whisper
from django.conf import settings
import logging
import torch


# Получение API-ключа из переменных окружения
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")


# Функция для загрузки шаблонов промтов
def load_prompts():
    try:
        data = json5.load(open('configs/prompts.json5', encoding='utf-8'))
        prompts = {}
        for k, v in data.items():
            prompts[k] = "\n".join(v) if isinstance(v, list) else v
        return prompts
    except Exception as e:
        print(f"Ошибка при загрузке шаблонов: {e}")
        return {}


# Функция для отправки запроса к Perplexity API
def get_perplexity_response(question):
    api_url = "https://api.perplexity.ai/chat/completions"
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


# Функция для извлечения текста из Word-документа
def extract_text_from_docx(file_path):
    try:
        doc = docx.Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()])
    except Exception as e:
        print(f"Ошибка при обработке документа: {e}")
        return "Ошибка при обработке документа."


@csrf_exempt
def chatbot_view(request):
    if request.method == "POST":
        if request.FILES.get('document'):  # Если загружен файл
            uploaded_file = request.FILES['document']
            file_path = default_storage.save(uploaded_file.name, ContentFile(uploaded_file.read()))
            full_path = default_storage.path(file_path)

            # Извлечение текста из документа
            extracted_text = extract_text_from_docx(full_path)

            # Сохраняем текст в сессии
            request.session['extracted_text'] = extracted_text

            return JsonResponse({'message': 'Документ успешно обработан', 'extracted_text': extracted_text}, status=200)

        # Обработка сообщений от пользователя
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            subject = data.get('subject', '')  # Получаем выбранный предмет

            if not user_message or not subject:
                return JsonResponse({'error': 'Пустое сообщение или не выбран предмет'}, status=400)

            # Загрузка шаблонов промтов
            prompt_templates = load_prompts()

            # Получаем ранее извлечённый текст из сессии
            extracted_text = request.session.get('extracted_text', '')

            if not extracted_text:
                return JsonResponse({'error': 'Документ не был загружен или обработан'}, status=400)

            # Формирование запроса с учётом выбранного предмета
            template = prompt_templates.get(subject, "{question}")
            question = template.format(question=user_message, document=extracted_text)

            # Получение ответа от Perplexity API
            bot_response = get_perplexity_response(question)
            return JsonResponse({'reply': bot_response}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Некорректные данные'}, status=400)
    return render(request, 'chatapp/chatbot.html')


# Логгер
logger = logging.getLogger(__name__)

@csrf_exempt
def page_one(request):
    if request.method == "POST" and request.FILES.get('media-file'):
        uploaded_file = request.FILES['media-file']
        file_path = default_storage.save(f"uploads/{uploaded_file.name}", ContentFile(uploaded_file.read()))
        full_path = default_storage.path(file_path)
        logger.info(f"File saved at: {full_path}")

        try:
            # Определяем устройство
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Using device: {device}")

            # Загружаем модель на указанное устройство
            model = whisper.load_model("base", device=device)

            # Указываем точность для GPU
            if device == "cuda":
                options = {"fp16": True}
            else:
                options = {"fp16": False}

            result = model.transcribe(full_path, **options)
            logger.info(f"Transcription result: {result['text']}")

            os.remove(full_path)
            return JsonResponse({"success": True, "transcription": result['text']}, status=200)

        except Exception as e:
            logger.error(f"Error during transcription: {str(e)}")
            return JsonResponse({"success": False, "error": f"Ошибка транскрипции: {str(e)}"}, status=500)

    return render(request, 'chatapp/page_one.html')

def page_two(request):
    if request.method == "POST":
        if request.FILES.get('document'):  # Если загружен файл
            uploaded_file = request.FILES['document']
            file_path = default_storage.save(uploaded_file.name, ContentFile(uploaded_file.read()))
            full_path = default_storage.path(file_path)

            # Извлечение текста из документа
            extracted_text = extract_text_from_docx(full_path)

            # Сохраняем текст в сессии
            request.session['extracted_text'] = extracted_text

            return JsonResponse({'message': 'Документ успешно обработан', 'extracted_text': extracted_text}, status=200)

        # Обработка сообщений от пользователя
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            subject = data.get('subject', '')  # Получаем выбранный предмет

            if not user_message or not subject:
                return JsonResponse({'error': 'Пустое сообщение или не выбран предмет'}, status=400)

            # Загрузка шаблонов промтов
            prompt_templates = load_prompts()

            # Получаем ранее извлечённый текст из сессии
            extracted_text = request.session.get('extracted_text', '')

            if not extracted_text:
                return JsonResponse({'error': 'Документ не был загружен или обработан'}, status=400)

            # Формирование запроса с учётом выбранного предмета
            template = prompt_templates.get(subject, "{question}")
            question = template.format(question=user_message, document=extracted_text)

            # Получение ответа от Perplexity API
            bot_response = get_perplexity_response(question)
            return JsonResponse({'reply': bot_response}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Некорректные данные'}, status=400)
    return render(request, 'chatapp/page_two.html')
