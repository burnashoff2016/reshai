window.addEventListener('load', function() {
    document.body.classList.add('loaded');
});

document.getElementById('upload-form').addEventListener('submit', async function (event) {
    event.preventDefault(); // Отменяем стандартное поведение формы

    const fileInput = document.getElementById('media-file'); // Используем правильный id
    const formData = new FormData();

    if (!fileInput.files[0]) {
        alert("Пожалуйста, выберите аудио файл для загрузки.");
        return;
    }

    formData.append('media-file', fileInput.files[0]); // Используем правильное имя поля для файла

    try {
        const response = await fetch('/page_one/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
        });

        const data = await response.json();

        if (data.success) {
            // Если транскрипция успешна, выводим её
            const transcriptionOutput = document.querySelector('.transcribed-output');
            if (transcriptionOutput) {
                transcriptionOutput.textContent = data.transcription;
            } else {
                console.error("Элемент для вывода транскрипции не найден.");
            }
        } else {
            alert(`Ошибка: ${data.error}`);
        }
    } catch (error) {
        console.error('Ошибка загрузки файла:', error);
        alert('Произошла ошибка при обработке файла.');
    }
});

    const menuToggle = document.getElementById("menu-toggle");
    const sidebarMenu = document.getElementById("sidebar-menu");

    // Обработчик клика по кнопке меню
    menuToggle.addEventListener("click", function() {
        sidebarMenu.classList.toggle("open"); // Переключаем класс для открытия/закрытия меню
    });

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

        fetch("/page_one/", {
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
                scrollToBottom();
            }
        }

        typeNextChar();
    }

    function scrollToBottom() {
    const chatBox = document.getElementById("chat-box");
    chatBox.scrollTop = chatBox.scrollHeight;
}


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


