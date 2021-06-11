"""[summary]
Email scraper based on Email-listeneer aiming to connect to
an email account, read emails and save attachments into a directory
"""

from email_listener import EmailListener
from imapclient import IMAPClient
from config import config


class EmailScraper(EmailListener):
    """
    Email scraper based on Email-listeneer
    """

    # pylint: disable=too-many-arguments
    def __init__(self, email, password, folder, attachment_dir, host):
        super().__init__(email, password, folder, attachment_dir)
        self.host = host
        self.email = email
        self.password = password
        self.folder = folder
        self.attachment_dir = attachment_dir
        self.server = IMAPClient(host)

    def login(self):
        self.server.login(self.email, self.password)
        self.server.select_folder(self.folder, readonly=False)


def run():
    """
    Running the Email scraper based on Email-listeneer
    """

    # pylint: disable=no-member
    host = config.EMAIL_HOST
    email = config.EMAIL
    app_password = config.EMAIL_PASSWORD
    folder = config.FOLDER
    attachment_dir = config.ATTACHMENTS_DIR
    listener = EmailScraper(email, app_password, folder, attachment_dir, host)

    # Log into the IMAP server
    listener.login()

    # Get the emails currently unread in the inbox
    messages = listener.scrape()
    print(messages)

    # Start listening to the inbox and timeout after an hour
    timeout = 60
    listener.listen(timeout)
