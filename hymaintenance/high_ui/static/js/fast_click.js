function preventFastClick () {
    var forms = document.querySelectorAll("form");
    for (var i = 0; i < forms.length; ++i) {
        var form = forms[i];
        form.addEventListener("submit", function (e) {
            if (!form.classList.contains('is-form-submitting')) {
                form.classList.add('is-form-submitting');
            } else {
                e.preventDefault();
            }
        });
    }
}
preventFastClick();
