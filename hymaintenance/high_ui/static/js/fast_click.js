function ForbiddenFastClick (document) {
    var buttons = document.querySelectorAll('form button[type="submit"]');
    for (var button of buttons) {
        button.addEventListener("click", function (e) {
            if (!button.classList.contains('is-form-submitting')) {
                button.classList.add('is-form-submitting');
            } else {
                e.preventDefault();
            }
        })
    }

    forms = document.querySelectorAll("form");
    for (var form of forms) {
        form.addEventListener("submit", function (e) {
            form.querySelector('form button[type="submit"]').classList.add('is-form-submitting');
        });
    }
}
