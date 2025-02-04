document.addEventListener("DOMContentLoaded", function () {
    const menuToggle = document.getElementById("menu-toggle");
    const sidebarMenu = document.getElementById("sidebar-menu");

    menuToggle.addEventListener("click", function() {
        sidebarMenu.classList.toggle("open");
    });

    window.sendMessage = sendMessage;
    window.scrollToBottom = scrollToBottom;

    const resizeHandle = document.querySelector('.resize-handle');
    const uploadSection = document.querySelector('.upload-section');
    let isResizing = false;

    function handleResize(e) {
        if (isResizing) {
            const newWidth = e.clientX - uploadSection.getBoundingClientRect().left;
            if (newWidth > 250) {
                uploadSection.style.width = `${newWidth}px`;
            }
        }
    }

    function getCSRFToken() {
        let csrfToken = null;
        const cookies = document.cookie.split(';');
        cookies.forEach(cookie => {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                csrfToken = value;
            }
        });
        return csrfToken;
    }

    function sendMessage() {
    const form = document.querySelector(".prompt-builder");
    const questionCount = form.querySelector("#question-count").value;
    const topic = form.querySelector("#topic").value;
    const keywords = form.querySelector("#keywords").value;
    const difficulty = form.querySelector("#difficulty-level").value;
    const singleChoiceCount = form.querySelector("#single-choice-count").value;
    const multipleChoiceCount = form.querySelector("#multiple-choice-count").value;
    const gapFillCount = form.querySelector("#gap-fill-count").value; // исправление ID

    if (!questionCount || !topic || !keywords || !difficulty || !singleChoiceCount || !multipleChoiceCount || !gapFillCount) {
        alert("Пожалуйста, заполните все поля.");
        return;
    }

    const chatBox = document.getElementById("chat-box");

    const userMessageDiv = document.createElement('div');
    userMessageDiv.className = "chat-message user";
    userMessageDiv.innerHTML = `<strong>Вы:</strong> Создать тест с ${questionCount} вопросами по теме "${topic}" с ключевыми словами: ${keywords}, сложность: ${difficulty}, количество вопросов для одиночного выбора: ${singleChoiceCount}, для множественного выбора: ${multipleChoiceCount}, для теста с пропусками: ${gapFillCount}.`;
    chatBox.appendChild(userMessageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    scrollToBottom();

    const typingIndicator = document.createElement('div');
    typingIndicator.className = "chat-message bot typing-indicator";
    typingIndicator.innerHTML = "<strong>ИИ:</strong><span style='margin-left: 5px;'>Печатает </span>";
    chatBox.appendChild(typingIndicator);
    chatBox.scrollTop = chatBox.scrollHeight;
    scrollToBottom();

    const csrfToken = getCSRFToken();

    if (!csrfToken) {
        console.error("CSRF токен не найден!");
        return;
    }

    fetch("/page_two/", {
    method: "POST",
    headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken
    },
    body: JSON.stringify({
        question_count: questionCount,
        topic: topic,
        keywords: keywords,
        difficulty: difficulty,
        single_choice_count: singleChoiceCount,
        multiple_choice_count: multipleChoiceCount,
        gap_fill_count: gapFillCount
    }),
})
    .then(response => response.json())
    .then(data => {
        typingIndicator.remove();

        if (data && data.reply) {
            const botMessageDiv = document.createElement('div');
            botMessageDiv.className = "chat-message bot";
            chatBox.appendChild(botMessageDiv);
            animateTypingWithCleanText(botMessageDiv, data.reply);
        } else {
            console.error("Ответ от бота не получен или не содержит текста.");
        }

        scrollToBottom();
    })
    .catch(error => {
        console.error("Ошибка:", error);
        alert("Произошла ошибка при отправке сообщения.");
    });
}

function animateTypingWithCleanText(element, text) {
    if (!text) {
        console.error("Нет текста для анимации.");
        return;
    }

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

    console.log('app3.js loaded');

    const generateTestButton = document.getElementById("generate-test");
    if (generateTestButton) {
        generateTestButton.addEventListener("click", function(event) {
            event.preventDefault();
            sendMessage();
        });
    } else {
        console.error("Кнопка 'Составить тест' не найдена.");
    }
});
