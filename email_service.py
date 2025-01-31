import smtplib
from email.mime.text import MIMEText
from configparser import ConfigParser

class EmailService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmailService, cls).__new__(cls)
            cls._instance._initialize_email_config()
        return cls._instance

    def _initialize_email_config(self):
        config = ConfigParser()
        config.read("config.ini")
        self.smtp_server = config["EMAIL"]["SMTP_SERVER"]
        self.smtp_port = int(config["EMAIL"]["SMTP_PORT"])
        self.email_user = config["EMAIL"]["EMAIL_USER"]
        self.email_password = config["EMAIL"]["EMAIL_PASSWORD"]

    def send_email(self, to_email, subject, body):
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = self.email_user
        msg["To"] = to_email

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.sendmail(self.email_user, to_email, msg.as_string())
                if to_email != self.email_user:
                    print(f"Email notification sent to {to_email}")
        except Exception as e:
            print(f"Failed to send email: {e}")
