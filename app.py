from config import config
from app import app_email_listener

if __name__ == "__main__":
    print(f"hello world on {config.env}")
    app_email_listener.run()