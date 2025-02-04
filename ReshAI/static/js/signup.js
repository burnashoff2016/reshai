document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector('form');
  const inputs = document.querySelectorAll('input');
  const errorMessages = document.querySelectorAll('.error-message');

  form.addEventListener('submit', function(event) {
    let isValid = true;

    inputs.forEach(input => {
      if (!input.validity.valid) {
        input.classList.add('invalid');
        isValid = false;
      } else {
        input.classList.remove('invalid');
      }
    });

    if (!isValid) {
      event.preventDefault();
    }
  });

  inputs.forEach(input => {
    input.addEventListener('input', function () {
      const errorMessage = this.nextElementSibling;

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
