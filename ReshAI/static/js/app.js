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
function showNotification(message) {
    const notificationContainer = document.getElementById('notification-container');

    // Создаём новый элемент уведомления
    const notification = document.createElement('div');
    notification.classList.add('notification');
    notification.textContent = message;

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

    const selectedLi = document.querySelector(`#subject-${subject.toLowerCase()}`);
    if (selectedLi) {
        selectedLi.classList.add('selected');
    }
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
            alert("Пожалуйста, выберите предмет перед отправкой сообщения!");
            return;
        }

        if (!message) {
            alert("Сообщение не может быть пустым!");
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
        .then(response => response.json())
        .then(data => {
            // Убираем индикатор "печатает..."
            typingIndicator.remove();

           // Создаём новое сообщение от бота и анимируем его
            const botMessageDiv = document.createElement('div');
            botMessageDiv.className = "chat-message bot";
            chatBox.appendChild(botMessageDiv);
            animateTypingWithCleanText(botMessageDiv, data.reply);

            scrollToBottom();
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
            showNotification('Документ успешно загружен!');
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
