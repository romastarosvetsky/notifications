import os

import jinja2


class SimpleEmailFormatter:

    def __init__(self, text=''):
        self.text = text

    def get_template(self):
        return jinja2.Template(self.text)

    def get_formatted_email(self, *args, **kwargs):
        template = self.get_template()
        return template.render(**kwargs)


class FileEmailFormatter(SimpleEmailFormatter):

    default_email_file_name = 'base_email.html'
    default_email_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), default_email_file_name)

    def __init__(self, file_path=None):
        self.file_path = file_path or self.default_email_file_path
        with open(self.file_path) as file:
            super().__init__(text=file.read())
