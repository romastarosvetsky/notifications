from django.core.mail import EmailMessage

from central.email.email_formatter import FileEmailFormatter, SimpleEmailFormatter


class Email:

    def __init__(self, subject='', from_email=None, to=None, text=None, file=None, email_body_context=None):
        if text is not None:
            self.formatter = SimpleEmailFormatter(text)
        else:
            self.formatter = FileEmailFormatter(file)
        self.subject = subject
        self.from_email = from_email
        self.to = to or []
        self.email_body_context = email_body_context or {}

    def _get_formatted_message(self):
        return self.formatter.get_formatted_email(**self.email_body_context)

    def _get_email_instance(self):
        return EmailMessage(
            subject=self.subject, body=self._get_formatted_message(), from_email=self.from_email, to=self.to
        )

    def send(self):
        self._get_email_instance().send()
