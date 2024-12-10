let selectedSubject = "";

function selectSubject(subject) {
    selectedSubject = subject;
    const chatBox = document.getElementById("chat-box");
    chatBox.innerHTML = `<div class="system-message">Вы выбрали предмет: ${subject}</div>`;

    // Подсветка выбранного предмета
    const allSubjects = document.querySelectorAll('.subjects-menu ul li');
    allSubjects.forEach(li => {
        li.classList.remove('selected');
    });
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

    fetch("/chat/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ subject: selectedSubject, message }),
    })
    .then(response => response.json())
    .then(data => {
        const chatBox = document.getElementById("chat-box");
        chatBox.innerHTML += `<div><strong>Вы:</strong> ${message}</div>`;
        chatBox.innerHTML += `<div><strong>Бот:</strong> ${data.reply}</div>`;
        chatBox.scrollTop = chatBox.scrollHeight; // Прокрутка вниз
        document.getElementById("user-message").value = "";
    })
    .catch(error => {
        console.error("Ошибка:", error);
        alert("Произошла ошибка при отправке сообщения.");
    });
}
