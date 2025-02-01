let selectedSubject = null; // Инициализация переменной выбранного предмета
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

window.addEventListener('load', function() {
    document.body.classList.add('loaded');
});

const openModal = document.getElementById('open-upload-modal');
const uploadModal = document.getElementById('upload-modal');
const closeModal = document.querySelector('.close-modal');

// Открытие модального окна
openModal.addEventListener('click', () => {
    uploadModal.classList.add('show');
});

// Закрытие модального окна
closeModal.addEventListener('click', () => {
    uploadModal.classList.remove('show');
});

// Закрытие окна при клике вне области модального окна
window.addEventListener('click', (e) => {
    if (e.target === uploadModal) {
        uploadModal.classList.remove('show');
    }
});

// Функция для создания уведомления
function showNotification(message,type = 'success') {
    const notificationContainer = document.getElementById('notification-container');

    // Создаём новый элемент уведомления
    const notification = document.createElement('div');
    notification.classList.add('notification');
    notification.textContent = message;

    if (type == 'error') {
        notification.style.backgroundColor = '#dc3545';
    } else {
        notification.style.backgroundColor = '#28a745';
    }

    // Добавляем уведомление в контейнер
    notificationContainer.appendChild(notification);

    // Удаляем уведомление через 3.5 секунды
    setTimeout(() => {
        notificationContainer.removeChild(notification);
    }, 3500);
}

function selectSubject(subject) {
    selectedSubject = subject; // Обновляем выбранный предмет

    const chatBox = document.getElementById("chat-box");
    chatBox.innerHTML = ''; // Очищаем текущее содержимое chat-box

    const messageDiv = document.createElement('div');
    messageDiv.classList.add('system-message');
    messageDiv.textContent = `Вы выбрали предмет: ${subject}`;
    chatBox.appendChild(messageDiv);

    const allSubjects = document.querySelectorAll('.subjects-menu ul li');
    allSubjects.forEach(li => li.classList.remove('selected'));

    allSubjects.forEach(li => {
        if (li.textContent.trim() === subject) {
            li.classList.add('selected');  // Добавляем класс для выбранного предмета
        }
    });
}




     window.selectSubject = selectSubject;
     window.sendMessage = sendMessage;
     window.scrollToBottom = scrollToBottom;

    const resizeHandle = document.querySelector('.resize-handle');
    const uploadSection = document.querySelector('.upload-section');
    let isResizing = false;



    function sendMessage() {
        const message = document.getElementById("user-message").value.trim();

        if (!selectedSubject) {
            showNotification('Пожалуйста, выберите предмет перед отправкой сообщения!', 'error');
            return;
        }

        if (!message) {
            showNotification('Сообщение не может быть пустым!', 'error');
            return;
        }



        const chatBox = document.getElementById("chat-box");

        /// Отправляем сообщение пользователя в чат
        const userMessageDiv = document.createElement('div');
        userMessageDiv.className = "chat-message user";
        userMessageDiv.innerHTML = `<strong>Вы:</strong> ${message}`;
        chatBox.appendChild(userMessageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
        scrollToBottom();
        document.getElementById("user-message").value = "";

         // Добавляем индикатор "печатает..."
        const typingIndicator = document.createElement('div');
        typingIndicator.className = "chat-message bot typing-indicator";
        typingIndicator.innerHTML = "<strong>Бот:</strong><span style='margin-left: 5px;'>Печатает </span>";
        chatBox.appendChild(typingIndicator);
        chatBox.scrollTop = chatBox.scrollHeight;
        scrollToBottom();

        fetch("/", {
            method: "POST",
            headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,  // Добавляем токен
    },
            body: JSON.stringify({ subject: selectedSubject, message }),
        })
        .then(response => {
            if (!response.body) {
                throw new Error("Ответ не содержит тела.");
            }
    
            // Убираем индикатор "печатает..."
            typingIndicator.remove();
    
            scrollToBottom();
    
            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");
                
            // Получаем элемент, куда будем анимировать текст
            const botMessageDiv = document.createElement('div');
            botMessageDiv.className = "chat-message bot";
            chatBox.appendChild(botMessageDiv);

            let accumulatedText = ''; // Переменная для накопления текста
            let htmlContent = ''; // Переменная для накопленного HTML контента
    
            const processStream = ({ done, value }) => {
                if (done) {
                    // Когда все данные получены, обрабатываем их
                    htmlContent = marked.parse(accumulatedText);
                    botMessageDiv.innerHTML = htmlContent;
                    chatBox.scrollTop = chatBox.scrollHeight;
                    return;
                }
        
                // Декодируем фрагмент данных
                const chunk = decoder.decode(value, { stream: true });
                console.log("Полученный фрагмент:", chunk);
        
                // Накопление текста
                accumulatedText += chunk;
        
                // Преобразуем накопленный текст в HTML с Markdown
                htmlContent = marked.parse(accumulatedText);
        
                // Выводим текст с применением Markdown
                botMessageDiv.innerHTML = htmlContent;
        
                // Прокручиваем чат вниз
                chatBox.scrollTop = chatBox.scrollHeight;
        
                // Читаем следующий блок данных
                reader.read().then(processStream);
            };
    
            reader.read().then(processStream);
        })
        .catch(error => {
            console.error("Ошибка:", error);
            alert("Произошла ошибка при отправке сообщения.");
        });
    }

    function animateTypingWithCleanText(element, text) {
        const cleanedText = text.replace(/###|##|\r|\n/g, '\n').trim();
        const paragraphs = cleanedText.split(/\n{2,}/).map(part => part.trim()).filter(part => part.length > 0);

        let currentParagraphIndex = 0;
        let currentTextIndex = 0;
        let currentParagraph = document.createElement('p');
        element.appendChild(currentParagraph);

        const interval = 25;

        function typeNextChar() {
            if (currentParagraphIndex < paragraphs.length) {
                const paragraphText = paragraphs[currentParagraphIndex];

                if (currentTextIndex < paragraphText.length) {
                    currentParagraph.innerHTML += paragraphText[currentTextIndex++];
                    scrollToBottom();
                } else {
                    currentParagraphIndex++;
                    currentTextIndex = 0;

                    if (currentParagraphIndex < paragraphs.length) {
                        currentParagraph = document.createElement('p');
                        element.appendChild(currentParagraph);
                    }
                }

                element.scrollTop = element.scrollHeight;
                setTimeout(typeNextChar, interval);
                scrollToBottom();
            }
        }

        typeNextChar();
    }

    function scrollToBottom() {
    const chatBox = document.getElementById("chat-box");
    chatBox.scrollTop = chatBox.scrollHeight;
}


    // Отправка формы загрузки документов
    document.getElementById('upload-form').addEventListener('submit', function (event) {
        event.preventDefault();

        const formData = new FormData(this);

        fetch('', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
        })
        .then(response => response.json())
        .then(data => {
        const uploadModal = document.getElementById('upload-modal');
            uploadModal.classList.remove('show');
            uploadModal.classList.add('hidden'); // Если нужно добавить скрытие через 'hidden'
            showNotification('Документ успешно загружен!', 'success');
            if (data.extracted_text) {
                const documentTextDiv = document.getElementById('document-text');
                documentTextDiv.textContent = data.extracted_text;
            } else {
                alert('Ошибка при обработке документа.');
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
        });
    });

    console.log('app.js loaded');

// Добавляем обработчик события на поле ввода
document.addEventListener('DOMContentLoaded', () => {
    const inputField = document.getElementById('user-message');

    if (inputField) {
        inputField.addEventListener('keydown', function (event) {
            // Проверяем, что нажата клавиша Enter и не удерживается Shift
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault(); // Предотвращаем добавление новой строки
                sendMessage(); // Вызываем функцию отправки сообщения
            }
        });
    } else {
        console.error("Элемент с id 'user-message' не найден.");
    }
});
