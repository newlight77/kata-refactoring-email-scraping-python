from config import config
from app import app_email_listener, app_email_pipe

if __name__ == "__main__":
    print(f"running the email scraper on {config.env}")
    #app_email_listener.run()
    app_email_pipe.run()
