from domain.fetched_email import FetchedEmail
from shared.json_util.json_util import to_json_file
from infrastructure.email import email_parser
from shared.decorators.pipe import Pipe
from config import logger, config

logger = logger.logger(__name__, config.LOG_LEVEL)

@Pipe
def scrape(data, config):
    return data \
        | parse_emails() \
        | parse_emails_body() \
        | parse_email_attachments(config.attachment_dir) \
        | summary_to_json_file(config.attachment_dir)

@Pipe
def parse_emails(emails_with_envelopes):
    logger.debug("parse emails with raw_emails_with_envelopes")
    emails_with_metadata = []
    for email in emails_with_envelopes:
        if type(email) == FetchedEmail:
            date = email.envelop.date#.strftime('%Y%m%d_%H%M')

            email_from = email_parser.get_from(email.message)
            email_subject = email_parser.get_subject(email.message).strip()
            logger.info(f"processing: email UID={email.uid} from {email_from} @ {date} -> {email_subject}")

            email.metadata = {
                'uid': email.uid,
                'from': email_from,
                'subject': email_subject,
                'date': date
            }

            emails_with_metadata.append(email)
    return emails_with_metadata

@Pipe
def parse_emails_body(emails_with_metadata):
    logger.debug("parse emails body with parsed_messages")
    emails_with_body = []
    for email in emails_with_metadata:
        logger.debug(f"parsing email body for UID={email.uid}")
        email.metadata['body'] = email_parser.parse_body(email.message)
        emails_with_body.append(email)
    return emails_with_body

@Pipe
def parse_email_attachments(emails_with_body, attachment_dir):
    logger.debug("parse emails attachments with parsed_messages")
    emails_with_attachments = []
    for email in emails_with_body:
        logger.debug(f"parsing email attachments for UID={email.uid}")
        email_attachments = email_parser.save_attachments(email.message, attachment_dir)
        email.metadata['attachments'] = email_attachments
        emails_with_attachments.append(email)
    return emails_with_attachments

@Pipe
def summary_to_json_file(emails_with_body, dest_dir):
    logger.info("write summary to json file with metadatas")
    file_list = []
    for email in emails_with_body:
        try:
            logger.debug('metadata %s', email.metadata)
            filename = f"{email.metadata['from']}-{email.metadata['date']}-{email.metadata['uid']}.json"
            file_path = to_json_file(email.metadata, filename, dest_dir)
            file_list.append(file_path)
        except ValueError:
            logger.error(f"an error occured while dumping metadata into json for message uid={email.metadata['uid']}")
            continue

    return file_list
