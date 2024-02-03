import smtplib


class EmailSenderClient(smtplib.SMTP):
    def __init__(self, smtp_server, smtp_port):
        super().__init__(smtp_server, smtp_port)
        self.sender_email_address = None

    def set_sender_email_address(self, email_address: str):
        self.sender_email_address = email_address

    def get_sender_email_address(self) -> str:
        return self.sender_email_address
