document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector('form');
  const inputs = document.querySelectorAll('input');
  const errorMessages = document.querySelectorAll('.error-message');

  // Обработчик нажатия на кнопку отправки формы
  form.addEventListener('submit', function(event) {
    let isValid = true;

    // Проверка валидности полей
    inputs.forEach(input => {
      if (!input.validity.valid) {
        input.classList.add('invalid');
        isValid = false;
      } else {
        input.classList.remove('invalid');
      }
    });

    // Если форма невалидна, предотвратить отправку
    if (!isValid) {
      event.preventDefault();
    }
  });

  // Прячем/отображаем ошибки при вводе
  inputs.forEach(input => {
    input.addEventListener('input', function () {
      const errorMessage = this.nextElementSibling;

      // Если поле валидно, скрываем ошибку
      if (this.validity.valid) {
        this.classList.remove('invalid');
        if (errorMessage) {
          errorMessage.classList.add('hidden');
        }
      } else {
        this.classList.add('invalid');
        if (errorMessage) {
          errorMessage.classList.remove('hidden');
        }
      }
    });
  });
});
