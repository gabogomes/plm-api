import pytest
from unittest.mock import MagicMock, patch
from plm.services.email_service import EmailSenderClient
import smtplib


@patch.object(smtplib.SMTP, "connect")
def test_smtp_called_with_right_parameters(mock_connect):
    smtp_server = "mock.smtp.com"
    smtp_port = 25
    mock_connect.return_value = (220, b"SMTP Mock")
    client = EmailSenderClient(smtp_server, smtp_port)

    mock_connect.assert_called_once()


@patch.object(smtplib.SMTP, "connect")
def test_email_setter_and_getter(mock_connect):
    smtp_server = "mock.smtp.com"
    smtp_port = 25
    mock_connect.return_value = (220, b"SMTP Mock")
    client = EmailSenderClient(smtp_server, smtp_port)

    test_email = "test@example.com"

    client.set_sender_email_address(test_email)

    assert client.get_sender_email_address() == test_email
