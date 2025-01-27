import logging
from urllib import request
from venv import logger

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import requests
import json
import json5
import os
import docx
from django.conf import settings
import logging
from deepgram import Deepgram
import asyncio
from decouple import config
from deepgram import Deepgram
import io
from typing import Optional
from concurrent.futures import ThreadPoolExecutor
from moviepy import *

from accounts.forms import UserProfileForm
from accounts.models import UserProfile

# Получение API-ключа из переменных окружения
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")

# Логгер
logger = logging.getLogger(__name__)

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


def load_prompts2():
    try:
        data = json5.load(open('configs/prompts2.json5', encoding='utf-8'))
        prompts = {}
        for k, v in data.items():
            prompts[k] = "\n".join(v) if isinstance(v, list) else v
        return prompts
    except Exception as e:
        print(f"Ошибка при загрузке шаблонов: {e}")
        return {}


import requests


def get_chatgpt_response(question):
    api_url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-4o",  # Используйте модель, доступную для вашего ключа
        "messages": [{"role": "user", "content": question}],
        "max_tokens": 150,
        "temperature": 0.7,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0,
    }

    try:
        # Отправка запроса
        response = requests.post(api_url, headers=headers, json=payload)

        # Проверка статуса ответа
        response.raise_for_status()

        # Преобразование ответа в JSON и извлечение данных
        data = response.json()

        # Извлечение ответа
        answer = data['choices'][0]['message']['content']
        return answer
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к OpenAI API: {e}")
        return "Произошла ошибка при обращении к API OpenAI."
    except Exception as e:
        print(f"Общая ошибка: {e}")
        return "Произошла ошибка."

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

@login_required
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
            bot_response = get_chatgpt_response(question)
            return JsonResponse({'reply': bot_response}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Некорректные данные'}, status=400)
    return render(request, 'chatapp/chatbot.html')


# Инициализация логирования
logger = logging.getLogger(__name__)

# Получение ключа из переменной окружения
DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')

# Инициализация клиента Deepgram
deepgram = Deepgram(DEEPGRAM_API_KEY)

# Асинхронная функция для транскрипции
async def transcribe_audio(file_path: str, language: str, model: str) -> str:
    """Транскрипция аудиофайла асинхронно."""
    # Чтение файла
    with open(file_path, 'rb') as audio_file:
        audio_data = audio_file.read()

    try:
        # Отправляем запрос для транскрипции
        response = await deepgram.transcription.prerecorded(
            {'buffer': audio_data, 'mimetype': 'audio/mpeg'},
             {'language': 'ru', 'model': 'nova-2'}# Укажите MIME тип для вашего файла
        )

        # Извлекаем транскрипт из ответа
        transcript = response['results']['channels'][0]['alternatives'][0]['transcript']
        return transcript
    except Exception as e:
        logger.error(f"Ошибка транскрипции: {str(e)}")
        raise

# Синхронная обёртка для асинхронной транскрипции
def transcribe_audio_sync(file_path: str) -> str:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(transcribe_audio(file_path, 'ru', 'nova-2'))

def video_to_audio(video_path):
    """Преобразует MP4 в MP3"""
    video_clip = VideoFileClip(video_path)
    audio_path = video_path.replace(".mp4", ".mp3")
    video_clip.audio.write_audiofile(audio_path)
    video_clip.close()
    return audio_path

# Обработка загрузки файла пользователем
@login_required
@csrf_exempt
def page_one(request):
    """Обработка загрузки файла пользователем и отправка запросов в LLM."""
    if request.method == "POST" and request.FILES.get('media-file'):
        uploaded_file = request.FILES['media-file']

        # Сохранение файла
        file_path = default_storage.save(f"uploads/{uploaded_file.name}", ContentFile(uploaded_file.read()))
        full_path = default_storage.path(file_path)
        logger.info(f"Файл сохранен по пути: {full_path}")

        try:
            # Вызов синхронной функции транскрипции
            transcript = transcribe_audio_sync(full_path)
            os.remove(full_path)  # Удаление временного файла

            # Очистить старое значение перед сохранением нового
            if 'transcribed_text' in request.session:
                del request.session['transcribed_text']
                request.session.modified = True
            # Сохраняем транскрибированный текст в сессии
            request.session['transcribed_text'] = transcript
            print(f"Сохранён транскрибированный текст в сессии: {request.session.get('transcribed_text')}")

            return JsonResponse({"success": True, "transcription": transcript}, status=200)

        except Exception as e:
            logger.error(f"Ошибка обработки: {e}")
            os.remove(full_path)  # Удаление временного файла при ошибке
            return JsonResponse({"success": False, "error": f"Ошибка: {str(e)}"}, status=500)

    # Обработка запросов от пользователя
    if request.method == "POST" and request.body:
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            subject = data.get('subject', '')  # Получаем выбранный предмет

            if not user_message or not subject:
                return JsonResponse({'error': 'Пустое сообщение или не выбран предмет'}, status=400)

            # Загрузка шаблонов промтов
            prompt_templates = load_prompts()

            # Получаем транскрибированный текст из сессии
            transcribed_text = request.session.get('transcribed_text', '')

            if not transcribed_text:
                return JsonResponse({'error': 'Аудиофайл не был загружен или обработан'}, status=400)

            # Формирование запроса с учётом выбранного предмета
            template = prompt_templates.get(subject, "{question}")
            question = template.format(question=user_message, document=transcribed_text)

            # Получение ответа от Perplexity API
            bot_response = get_chatgpt_response(question)
            return JsonResponse({'reply': bot_response}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Некорректные данные'}, status=400)

    # Возврат HTML-страницы для GET-запроса
    return render(request, 'chatapp/page_one.html')

@login_required
def page_two(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Получаем данные из тела запроса
            question_count = data.get('question_count')
            topic = data.get('topic')
            keywords = data.get('keywords')
            difficulty = data.get('difficulty')
            single_choice_count = data.get('single_choice_count')
            multiple_choice_count = data.get('multiple_choice_count')
            gap_fill_count = data.get('gap_fill_count')

            if not all([question_count, topic, keywords, difficulty, single_choice_count, multiple_choice_count, gap_fill_count]):
                return JsonResponse({'error': 'Пожалуйста, заполните все поля.'}, status=400)

            # Загрузка шаблонов промтов
            prompt_templates = load_prompts2()

            # В данном случае, не зависит от subject, просто используем шаблон по умолчанию
            prompt_template = prompt_templates.get("Математика", "{question}")

            # Формируем запрос на основе шаблона и сообщения пользователя
            question = prompt_template.format(question=f"Создать тест с {question_count} вопросами по теме {topic} с ключевыми словами: {keywords}, сложность: {difficulty}, количество одиночных вопросов: {single_choice_count}, для множественного выбора: {multiple_choice_count}, для теста с пропусками: {gap_fill_count}")

            # Получаем ответ от Perplexity API
            bot_response = get_chatgpt_response(question)
            return JsonResponse({'reply': bot_response}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Некорректные данные'}, status=400)

    # Если метод GET, возвращаем HTML-страницу
    return render(request, 'chatapp/page_two.html')


@login_required
def profile(request):
    """Представление для редактирования профиля"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()  # Сохраняем форму
            return redirect('profile')  # Перенаправляем на ту же страницу
    else:
        form = UserProfileForm(instance=request.user.profile)

    return render(request, 'chatapp/profile.html', {'form': form})


