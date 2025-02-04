from venv import logger
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import json5
import os
import docx
import logging
import asyncio
from deepgram import Deepgram
from dotenv import load_dotenv
from openai import OpenAI
from accounts.forms import UserProfileForm
from .models import Chat, Message
import openai

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")

logger = logging.getLogger(__name__)

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


openai.api_key = OPENAI_API_KEY

def get_chatgpt_response(question):
    try:
        client = OpenAI()

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Выводи ответ для markdown."},
                {"role": "user", "content": question},
            ],
            stream=True,
            max_tokens=1000,
            temperature=0.7
        )


        def stream_generator():
            accumulated_text = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    """ yield chunk.choices[0].delta.content """
                    content = chunk.choices[0].delta.content
                    accumulated_text += content
                    yield content
            

            print(accumulated_text)

        return StreamingHttpResponse(stream_generator(), content_type='text/plain')

    except Exception as e:
        print(f"Ошибка при запросе к OpenAI API: {e}")
        return StreamingHttpResponse(f"Ошибка сервера: {e}", content_type='text/plain')
    

def save_to_database(bot_response, chat, sequence_number):
    try:

        Message.objects.create(
            chat=chat,
            sender=None,
            content=bot_response,
            is_bot=True,
            sequence=sequence_number + 1
        )
    except Exception as e:
        print(f"Ошибка при сохранении в базу данных: {e}")

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
        if request.FILES.get('document'):
            uploaded_file = request.FILES['document']
            file_path = default_storage.save(uploaded_file.name, ContentFile(uploaded_file.read()))
            full_path = default_storage.path(file_path)

            extracted_text = extract_text_from_docx(full_path)
            request.session['extracted_text'] = extracted_text

            return JsonResponse({'message': 'Документ успешно обработан', 'extracted_text': extracted_text}, status=200)

        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            subject = data.get('subject', '')
            chat_id = data.get('chat_id', None)

            if not user_message or not subject:
                return JsonResponse({'error': 'Пустое сообщение или не выбран предмет'}, status=400)
            
            if chat_id:
                chat = get_object_or_404(Chat, id=chat_id, user=request.user)
            else:

                chat = Chat.objects.create(user=request.user, subject=subject)
                
            sequence_number = chat.messages.count() + 1

            Message.objects.create(
                chat=chat,
                sender=request.user,
                content=user_message,
                is_bot=False,
                sequence=sequence_number
            )

            prompt_templates = load_prompts()

            extracted_text = request.session.get('extracted_text', '')

            if not extracted_text:
                return JsonResponse({'error': 'Документ не был загружен или обработан'}, status=400)

            template = prompt_templates.get(subject, "{question}")

            chat = Chat.objects.get(id=chat_id)
            sequence_number = chat.messages.count()
            question = template.format(question=user_message, document=extracted_text)
            bot_response = get_chatgpt_response(question)

            Message.objects.create(
                chat=chat,
                sender=None,
                content=bot_response,
                is_bot=True,
                sequence=sequence_number + 1
            )

            return bot_response
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Некорректные данные'}, status=400)
        
    chats = Chat.objects.filter(user=request.user).order_by('-created_at')    
    return render(request, 'chatapp/chat_page.html', {'chats': chats})


logger = logging.getLogger(__name__)
DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')
deepgram = Deepgram(DEEPGRAM_API_KEY)

async def transcribe_audio(file_path: str, language: str, model: str) -> str:

    with open(file_path, 'rb') as audio_file:
        audio_data = audio_file.read()

    try:
        response = await deepgram.transcription.prerecorded(
            {'buffer': audio_data, 'mimetype': 'audio/mpeg'},
             {'language': 'ru', 'model': 'nova-2'}# Укажите MIME тип для вашего файла
        )

        transcript = response['results']['channels'][0]['alternatives'][0]['transcript']
        return transcript
    except Exception as e:
        logger.error(f"Ошибка транскрипции: {str(e)}")
        raise

def transcribe_audio_sync(file_path: str) -> str:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(transcribe_audio(file_path, 'ru', 'nova-2'))

@login_required
@csrf_exempt
def page_one(request):
    if request.method == "POST" and request.FILES.get('media-file'):
        uploaded_file = request.FILES['media-file']


        file_path = default_storage.save(f"uploads/{uploaded_file.name}", ContentFile(uploaded_file.read()))
        full_path = default_storage.path(file_path)
        logger.info(f"Файл сохранен по пути: {full_path}")

        try:

            transcript = transcribe_audio_sync(full_path)
            os.remove(full_path)

            if 'transcribed_text' in request.session:
                del request.session['transcribed_text']
                request.session.modified = True

            request.session['transcribed_text'] = transcript
            print(f"Сохранён транскрибированный текст в сессии: {request.session.get('transcribed_text')}")

            return JsonResponse({"success": True, "transcription": transcript}, status=200)

        except Exception as e:
            logger.error(f"Ошибка обработки: {e}")
            os.remove(full_path)
            return JsonResponse({"success": False, "error": f"Ошибка: {str(e)}"}, status=500)

    if request.method == "POST" and request.body:
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            subject = data.get('subject', '')

            if not user_message or not subject:
                return JsonResponse({'error': 'Пустое сообщение или не выбран предмет'}, status=400)

            prompt_templates = load_prompts()

            transcribed_text = request.session.get('transcribed_text', '')

            if not transcribed_text:
                return JsonResponse({'error': 'Аудиофайл не был загружен или обработан'}, status=400)

            template = prompt_templates.get(subject, "{question}")
            question = template.format(question=user_message, document=transcribed_text)

            bot_response = get_chatgpt_response(question)
            return JsonResponse({'reply': bot_response}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Некорректные данные'}, status=400)

    return render(request, 'chatapp/audio_page.html')

@login_required
def page_two(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            question_count = data.get('question_count')
            topic = data.get('topic')
            keywords = data.get('keywords')
            difficulty = data.get('difficulty')
            single_choice_count = data.get('single_choice_count')
            multiple_choice_count = data.get('multiple_choice_count')
            gap_fill_count = data.get('gap_fill_count')

            if not all([question_count, topic, keywords, difficulty, single_choice_count, multiple_choice_count, gap_fill_count]):
                return JsonResponse({'error': 'Пожалуйста, заполните все поля.'}, status=400)

            prompt_templates = load_prompts2()

            prompt_template = prompt_templates.get("Математика", "{question}")

            question = prompt_template.format(question=f"Создать тест с {question_count} вопросами по теме {topic} с ключевыми словами: {keywords}, сложность: {difficulty}, количество одиночных вопросов: {single_choice_count}, для множественного выбора: {multiple_choice_count}, для теста с пропусками: {gap_fill_count}")

            bot_response = get_chatgpt_response(question)
            return JsonResponse({'reply': bot_response}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Некорректные данные'}, status=400)

    return render(request, 'chatapp/page_two.html')

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user.profile)

    return render(request, 'chatapp/profile.html', {'form': form})

@login_required
@csrf_exempt
def new_chat(request):
    if request.method == "POST":
        chat = Chat.objects.create(user=request.user, subject="Новый чат")
        return JsonResponse({"chat_id": chat.id, "subject": chat.subject})
    return JsonResponse({"error": "Метод не поддерживается"}, status=400)

@login_required
def get_chat_history(request, chat_id):
    try:
        chat = Chat.objects.get(id=chat_id, user=request.user)
        messages = chat.messages.order_by("timestamp")

        message_list = [
            {"sender": "bot" if msg.is_bot else "user", "content": msg.content}
            for msg in messages
        ]

        return JsonResponse({"messages": message_list})
    except Chat.DoesNotExist:
        return JsonResponse({"error": "Чат не найден"}, status=404)
