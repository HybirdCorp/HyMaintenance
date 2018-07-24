from django.utils import translation


class SetDjangoLanguage:
    def __init__(self, language_code):
        self.language = language_code

    def __enter__(self):
        self.current_language = translation.get_language()
        translation.activate(self.language)

    def __exit__(self, type, value, traceback):
        translation.activate(self.current_language)
