document.getElementById('upload-form').addEventListener('submit', async function (event) {
    event.preventDefault(); // Отменяем стандартное поведение формы

    const fileInput = document.getElementById('media-file'); // Используем правильный id
    const formData = new FormData();

    if (!fileInput.files[0]) {
        alert("Пожалуйста, выберите аудио или видео файл для загрузки.");
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
