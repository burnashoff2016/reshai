document.addEventListener("DOMContentLoaded", function () {
     window.selectSubject = selectSubject;
     window.sendMessage = sendMessage;
     window.scrollToBottom = scrollToBottom;

    const resizeHandle = document.querySelector('.resize-handle');
    const uploadSection = document.querySelector('.upload-section');
    let isResizing = false;


    // Функция для обработки изменения размера
    function handleResize(e) {
        if (isResizing) {
            const newWidth = e.clientX - uploadSection.getBoundingClientRect().left;
            if (newWidth > 250) { // Минимальная ширина
                uploadSection.style.width = `${newWidth}px`;
            }
        }
    }

    // Остановка перетаскивания
    function stopResize() {
        isResizing = false;
        document.body.style.cursor = 'default';
        document.removeEventListener('mousemove', handleResize);
        document.removeEventListener('mouseup', stopResize);
    }

    // Начало перетаскивания
    resizeHandle.addEventListener('mousedown', (e) => {
        isResizing = true;
        document.body.style.cursor = 'ew-resize';
        e.preventDefault();
        document.addEventListener('mousemove', handleResize);
        document.addEventListener('mouseup', stopResize);
    });

    function selectSubject(subject) {
        selectedSubject = subject;
        const chatBox = document.getElementById("chat-box");
        chatBox.innerHTML = `<div class="system-message">Вы выбрали предмет: ${subject}</div>`;
        const allSubjects = document.querySelectorAll('.subjects-menu ul li');
        allSubjects.forEach(li => li.classList.remove('selected'));
        const selectedLi = document.querySelector(`#subject-${subject.toLowerCase()}`);
        if (selectedLi) {
            selectedLi.classList.add('selected');
        }
    }

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

        fetch("/chat/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
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
        const cleanedText = text.replace(/###|\r|\n/g, '\n').trim();
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
});
