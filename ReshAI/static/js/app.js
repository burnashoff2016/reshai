let selectedSubject = "";

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
    chatBox.innerHTML += `<div class="chat-message user"><strong>Вы:</strong> ${message}</div>`;
    chatBox.scrollTop = chatBox.scrollHeight;
    document.getElementById("user-message").value = "";

    fetch("/chat/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ subject: selectedSubject, message }),
    })
    .then(response => response.json())
    .then(data => {
        const botMessageDiv = document.createElement('div');
        botMessageDiv.className = "chat-message bot";
        chatBox.appendChild(botMessageDiv);
        animateTypingWithCleanText(botMessageDiv, data.reply);
    })
    .catch(error => {
        console.error("Ошибка:", error);
        alert("Произошла ошибка при отправке сообщения.");
    });
}

function animateTypingWithCleanText(element, text) {
    // Очищаем текст: удаляем ### и лишние переносы строк
    const cleanedText = text.replace(/###|\r|\n/g, '\n').trim();
    const paragraphs = cleanedText.split(/\n{2,}/).map(part => part.trim()).filter(part => part.length > 0);

    let currentParagraphIndex = 0;
    let currentTextIndex = 0;
    let currentParagraph = document.createElement('p');
    element.appendChild(currentParagraph);

    const interval = 25; // Скорость печати (в миллисекундах)

    function typeNextChar() {
        if (currentParagraphIndex < paragraphs.length) {
            const paragraphText = paragraphs[currentParagraphIndex];

            if (currentTextIndex < paragraphText.length) {
                currentParagraph.innerHTML += paragraphText[currentTextIndex++];
            } else {
                currentParagraphIndex++;
                currentTextIndex = 0;

                if (currentParagraphIndex < paragraphs.length) {
                    currentParagraph = document.createElement('p');
                    element.appendChild(currentParagraph);
                }
            }

            element.scrollTop = element.scrollHeight; // Прокрутка вниз
            setTimeout(typeNextChar, interval);
        }
    }

    typeNextChar();
}
