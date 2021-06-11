from email_listener import EmailListener
from imapclient import IMAPClient, SEEN
from config import config


class EmailListenerRunner(EmailListener):
    def __init__(self, email, app_password, folder, attachment_dir, host):
        super(EmailListenerRunner, self).__init__(email, app_password, folder, attachment_dir)
        self.host = host
        self.email = email
        self.password = app_password
        self.folder = folder
        self.attachment_dir = attachment_dir
        self.server = IMAPClient(host)
    
    def login(self):
        self.server.login(self.email, self.password)
        self.server.select_folder(self.folder, readonly=False)
        

def run():
    
    # Set your email, password, what folder you want to listen to, and where to save attachments
    host = config.EMAIL_HOST
    email = config.EMAIL
    app_password = config.EMAIL_PASSWORD
    folder = config.FOLDER
    attachment_dir = config.ATTACHMENTS_DIR
    el = EmailListenerRunner(email, app_password, folder, attachment_dir, host)

    # Log into the IMAP server
    el.login()

    # Get the emails currently unread in the inbox
    messages = el.scrape()
    print(messages)

    # Start listening to the inbox and timeout after an hour
    timeout = 60
    el.listen(timeout)


