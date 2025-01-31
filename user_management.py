import bcrypt
import re
from src.database_connection import DatabaseConnection
from email.mime.text import MIMEText
import smtplib
from configparser import ConfigParser

def validate_password(password):
    if len(password) < 8:
        return False
    if not re.search(r'[A-Za-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    return True

def create_user(role='user'):
    username = input("Enter username: ")
    email = input("Enter email: ")
    password = input("Enter password: ")

    if not validate_password(password):
        print("Error: Password must be at least 8 characters long and include both letters and numbers.")
        return

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    db_conn = DatabaseConnection().get_connection()
    cursor = db_conn.cursor()

    try:
        cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
        user = cursor.fetchone()

        if user:
            print("Error: Username or email already exists. Please choose a different username or email.")
            return

        cursor.execute("INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
                       (username, email, hashed_password.decode("utf-8"), role))
        db_conn.commit()

        if role == 'user':
            print(f"User '{username}' registered successfully!")

            email_service = EmailService()
            email_service.send_email(
                email,
                "Registration Successful",
                f"Dear {username},\n\nYou have successfully registered to the Car Rental System.\n\n"
                f"Your username: {username}\n"
                f"Your email: {email}\n\n"
                f"Thank you for joining us!\n\n"
                f"Regards,\nCar Rental System"
            )
            print(f"Registration confirmation email sent to {email}.")

        elif role == 'admin':
            print(f"Admin '{username}' registered successfully!")
    except Exception as e:
        print(f"Error during registration: {e}")
    finally:
        cursor.close()

def authenticate_user(role='user'):
    username = input("Enter username: ")
    password = input("Enter password: ")

    db_conn = DatabaseConnection().get_connection()
    cursor = db_conn.cursor()

    try:
        cursor.execute("SELECT * FROM users WHERE username = %s AND role = %s", (username, role))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(password.encode("utf-8"), user[2].encode("utf-8")):
            print(f"Welcome, {username}!")
            return user
        else:
            print("Invalid credentials or role.")
            return None
    except Exception as e:
        print(f"Error authenticating {role}: {e}")
        return None
    finally:
        cursor.close()

def create_admin():
    print("Only authenticated admins can register new admins.")
    current_admin = authenticate_admin()

    if not current_admin:
        print("Error: You must be logged in as an admin to register a new admin.")
        return

    username = input("Enter new admin username: ")
    password = input("Enter new admin password: ")

    if not validate_password(password):
        print("Error: Password must be at least 8 characters long and include both letters and numbers.")
        return

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    db_conn = DatabaseConnection().get_connection()
    cursor = db_conn.cursor()

    try:
        cursor.execute("SELECT * FROM admins WHERE username = %s", (username,))
        existing_admin = cursor.fetchone()

        if existing_admin:
            print("Error: Admin username already exists. Please choose a different username.")
            return

        cursor.execute("INSERT INTO admins (username, password) VALUES (%s, %s)",
                       (username, hashed_password.decode("utf-8")))
        db_conn.commit()
        print(f"Admin '{username}' registered successfully!")
    except Exception as e:
        print(f"Error during admin registration: {e}")
    finally:
        cursor.close()

def authenticate_admin():
    username = input("Enter admin username: ")
    password = input("Enter admin password: ")

    db_conn = DatabaseConnection().get_connection()
    cursor = db_conn.cursor()

    try:
        cursor.execute("SELECT id, username, password FROM admins WHERE username = %s", (username,))
        admin = cursor.fetchone()

        if not admin:
            print("Error: Admin not found.")
            return None

        stored_password = admin[2]
        if bcrypt.checkpw(password.encode("utf-8"), stored_password.encode("utf-8")):
            print(f"Welcome, Admin {username}!")
            return admin
        else:
            print("Error: Invalid password.")
            return None
    except Exception as e:
        print(f"Error authenticating admin: {e}")
        return None
    finally:
        cursor.close()

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