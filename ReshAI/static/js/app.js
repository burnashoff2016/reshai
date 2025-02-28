document.addEventListener("DOMContentLoaded", function () {
    const chatList = document.getElementById("chat-list");
    const chatBox = document.getElementById("chat-box");
    const newChatBtn = document.getElementById("new-chat-btn");

    chatList.addEventListener("click", function (event) {
        if (event.target.classList.contains("chat-item")) {
            const chatId = event.target.dataset.chatId;
            window.currentChatId = chatId;
            loadChatHistory(chatId);
        }
    });

    newChatBtn.addEventListener("click", function () {
        fetch("/new_chat/", {
            method: "POST",
            headers: { "X-CSRFToken": getCSRFToken() }
        })
        .then(response => response.json())
        .then(data => {
            if (data.chat_id) {
                window.currentChatId = data.chat_id;
                chatBox.innerHTML = "";

                const newChatItem = document.createElement("li");
                newChatItem.classList.add("chat-item", "text-white", "d-flex", "justify-content-between", "align-items-center");
                newChatItem.dataset.chatId = data.chat_id;
                newChatItem.innerHTML = `
                    <div>
                        <i class="fas fa-comments me-2"></i> ${data.subject || "Без названия"}
                    </div>
                    <div class="dropdown">
                                        <button class="btn btn-link text-white p-0" onclick="toggleChatMenu(event, '{{ chat.id }}')">
                                            <i class="fas fa-ellipsis-h"></i>
                                        </button>
                                    </div>
                `;
                chatList.prepend(newChatItem);
                // Инициализируем dropdown для нового чата
                let newDropdown = newChatItem.querySelector('.dropdown-toggle');
                new bootstrap.Dropdown(newDropdown);
            }
        })
        .catch(error => console.error("Ошибка создания чата:", error));
    });

function loadChatHistory(chatId) {
    fetch(`/get_chat_history/${chatId}/`)
        .then(response => response.json())
        .then(data => {
            chatBox.innerHTML = "";
            data.messages.forEach(msg => {
                const messageDiv = document.createElement("div");
                messageDiv.className = msg.sender === "bot" ? "chat-message bot" : "chat-message user";
                messageDiv.innerHTML = `<strong>${msg.sender}:</strong> ${msg.content}`;
                chatBox.appendChild(messageDiv);
            });
        })
        .catch(error => console.error("Ошибка загрузки истории:", error));
}

function getCSRFToken() {
    return document.querySelector("[name=csrfmiddlewaretoken]").value;
}
});



let selectedSubject = null;
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

window.addEventListener('load', function() {
    document.body.classList.add('loaded');
});

const openModal = document.getElementById('open-upload-modal');
const uploadModal = document.getElementById('upload-modal');
const closeModal = document.querySelector('.close-modal');

openModal.addEventListener('click', () => {
    uploadModal.classList.add('show');
});

closeModal.addEventListener('click', () => {
    uploadModal.classList.remove('show');
});

window.addEventListener('click', (e) => {
    if (e.target === uploadModal) {
        uploadModal.classList.remove('show');
    }
});

function showNotification(message,type = 'success') {
    const notificationContainer = document.getElementById('notification-container');

    const notification = document.createElement('div');
    notification.classList.add('notification');
    notification.textContent = message;

    if (type == 'error') {
        notification.style.backgroundColor = '#dc3545';
    } else {
        notification.style.backgroundColor = '#28a745';
    }

    notificationContainer.appendChild(notification);

    setTimeout(() => {
        notificationContainer.removeChild(notification);
    }, 3500);
}

function toggleChatMenu(event, chatId) {
    const globalMenu = document.getElementById('global-menu-container');
    
    // Если меню уже открыто для этого чата — закрыть его
    if (globalMenu.dataset.chatId === chatId && !globalMenu.classList.contains('hidden')) {
        globalMenu.classList.add('hidden');
        return;
    }
    
    // Задаём ID чата
    globalMenu.dataset.chatId = chatId;
    
    // Формируем контент меню (HTML)
    globalMenu.innerHTML = `
        <div class="global-dropdown-menu">
            <ul class="dropdown-menu dropdown-menu-end show" style="position: static; display: block;">
                <li>
                    <a class="dropdown-item d-flex gap-2 align-items-center" href="#">
                        <svg class="bi" width="16" height="16"><use xlink:href="/media/images/icons_menu.svg#export"/></svg>
                        Экспорт
                    </a>
                </li>
                <li>
                    <a class="dropdown-item d-flex gap-2 align-items-center" href="#">
                        <svg class="bi" width="16" height="16"><use xlink:href="/media/images/icons_menu.svg#share"/></svg>
                        Поделиться
                    </a>
                </li>
                <li>
                    <a class="dropdown-item d-flex gap-2 align-items-center" href="#">
                        <svg class="bi" width="16" height="16"><use xlink:href="/media/images/icons_menu.svg#rename"/></svg>
                        Переименовать
                    </a>
                </li>
                <li><hr class="dropdown-divider"></li>
                <li>
                    <a class="dropdown-item dropdown-item-danger d-flex gap-2 align-items-center text-danger" href="#" onclick="deleteChat(event)">
                        <svg class="bi" width="16" height="16" fill="currentColor"><use xlink:href="/media/images/icons_menu.svg#trash"/></svg>
                        Удалить
                    </a>
                </li>
            </ul>
        </div>
    `;

    // Позиционируем глобальное меню
    // 1) Получаем координаты кнопки, на которую кликнули
    const rect = event.target.getBoundingClientRect();

    // 2) Устанавливаем стили глобального контейнера
    globalMenu.style.position = 'absolute';
    globalMenu.style.top = (rect.bottom + window.scrollY) + 'px';
    globalMenu.style.left = (rect.left + window.scrollX) + 'px';
    globalMenu.style.zIndex = '9999';

    // 3) Показываем контейнер
    globalMenu.classList.remove('hidden');
}

function getCSRFToken() {
    return document.querySelector("[name=csrfmiddlewaretoken]").value;
}


function deleteChat(event) {
    event.preventDefault(); // Отменяем действие ссылки
    const globalMenu = document.getElementById('global-menu-container');
    const chatId = globalMenu.dataset.chatId;

    if (!chatId) {
        console.error("Chat ID не найден");
        return;
    }
    
    // Подтверждение удаления (опционально)
    if (!confirm("Вы уверены, что хотите удалить чат?")) {
        return;
    }
    
    fetch(`/delete_chat/${chatId}/`, {
        method: "POST", // или DELETE, в зависимости от настройки сервера
        headers: {
            "X-CSRFToken": getCSRFToken(), // функция для получения CSRF-токена
            "Content-Type": "application/json"
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Удаляем элемент чата из DOM
            const chatElement = document.querySelector(`.chat-item[data-chat-id="${chatId}"]`);
            if (chatElement) {
                chatElement.remove();
            }
            // Скрываем глобальное меню
            globalMenu.classList.add("hidden");
            showNotification("Чат успешно удалён", "success");
        } else {
            showNotification("Ошибка удаления чата", "error");
        }
    })
    .catch(error => {
        console.error("Ошибка удаления чата:", error);
        showNotification("Ошибка удаления чата", "error");
    });
}



// Закрытие меню при клике вне его
document.addEventListener('click', function(e) {
    const globalContainer = document.getElementById('global-menu-container');
    if (!globalContainer.contains(e.target) && !e.target.closest('.dropdown')) {
        globalContainer.classList.add('hidden');
    }
});


function selectSubject(button, subject) {

    document.querySelectorAll("#subjects-container button").forEach(btn => {
        btn.classList.remove("btn-primary");
        btn.classList.add("btn-secondary");
    });

    button.classList.remove("btn-secondary");
    button.classList.add("btn-primary");

    selectedSubject = subject;

    const chatBox = document.getElementById("chat-box");
    chatBox.innerHTML = '';

    const messageDiv = document.createElement('div');
    messageDiv.classList.add('system-message');
    messageDiv.textContent = `Вы выбрали предмет: ${subject}`;
    chatBox.appendChild(messageDiv);

    const allSubjects = document.querySelectorAll('.subjects-menu ul li');
    allSubjects.forEach(li => li.classList.remove('selected'));

    allSubjects.forEach(li => {
        if (li.textContent.trim() === subject) {
            li.classList.add('selected');
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

        const userMessageDiv = document.createElement('div');
        userMessageDiv.className = "chat-message user";
        userMessageDiv.innerHTML = `<strong>Вы:</strong> ${message}`;
        chatBox.appendChild(userMessageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
        scrollToBottom();
        document.getElementById("user-message").value = "";

        const typingIndicator = document.createElement('div');
        typingIndicator.className = "chat-message bot typing-indicator";
        typingIndicator.innerHTML = "<strong>Бот:</strong><span style='margin-left: 5px;'>Печатает </span>";
        chatBox.appendChild(typingIndicator);
        chatBox.scrollTop = chatBox.scrollHeight;
        scrollToBottom();

        const chatId = window.currentChatId || null;

        fetch("/", {
            method: "POST",
            headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
    },
            body: JSON.stringify({ subject: selectedSubject, message, chat_id:chatId }),
        })
        .then(response => {
            if (!response.body) {
                throw new Error("Ответ не содержит тела.");
            }

            typingIndicator.remove();

            scrollToBottom();

            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");

            const botMessageDiv = document.createElement('div');
            botMessageDiv.className = "chat-message bot";
            chatBox.appendChild(botMessageDiv);

            let accumulatedText = '';
            let htmlContent = '';

            const processStream = ({ done, value }) => {
                if (done) {
                    htmlContent = marked.parse(accumulatedText);
                    botMessageDiv.innerHTML = htmlContent;
                    chatBox.scrollTop = chatBox.scrollHeight;
                    return;
                }

                const chunk = decoder.decode(value, { stream: true });
                console.log("Полученный фрагмент:", chunk);

                accumulatedText += chunk;

                htmlContent = marked.parse(accumulatedText);

                botMessageDiv.innerHTML = htmlContent;

                chatBox.scrollTop = chatBox.scrollHeight;

                reader.read().then(processStream);
            };

            reader.read().then(processStream);
        })
        .catch(error => {
            console.error("Ошибка:", error);
            alert("Произошла ошибка при отправке сообщения.");
        });
    }

//    function animateTypingWithCleanText(element, text) {
//        const cleanedText = text.replace(/###|##|\r|\n/g, '\n').trim();
//        const paragraphs = cleanedText.split(/\n{2,}/).map(part => part.trim()).filter(part => part.length > 0);
//
//        let currentParagraphIndex = 0;
//        let currentTextIndex = 0;
//        let currentParagraph = document.createElement('p');
//        element.appendChild(currentParagraph);
//
//        const interval = 25;
//
//        function typeNextChar() {
//            if (currentParagraphIndex < paragraphs.length) {
//                const paragraphText = paragraphs[currentParagraphIndex];
//
//                if (currentTextIndex < paragraphText.length) {
//                    currentParagraph.innerHTML += paragraphText[currentTextIndex++];
//                    scrollToBottom();
//                } else {
//                    currentParagraphIndex++;
//                    currentTextIndex = 0;
//
//                    if (currentParagraphIndex < paragraphs.length) {
//                        currentParagraph = document.createElement('p');
//                        element.appendChild(currentParagraph);
//                    }
//                }
//
//                element.scrollTop = element.scrollHeight;
//                setTimeout(typeNextChar, interval);
//                scrollToBottom();
//            }
//        }
//
//        typeNextChar();
//    }

    function scrollToBottom() {
    const chatBox = document.getElementById("chat-box");
    chatBox.scrollTop = chatBox.scrollHeight;
}


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
            uploadModal.classList.add('hidden');
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

document.addEventListener('DOMContentLoaded', () => {
    const inputField = document.getElementById('user-message');

    if (inputField) {
        inputField.addEventListener('keydown', function (event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendMessage();
            }
        });
    } else {
        console.error("Элемент с id 'user-message' не найден.");
    }
});
