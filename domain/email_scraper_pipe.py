import logging
from infrastructure.email.email_client_pipe import get_from, get_subject, parse_body, save_attachments, to_json_file
from shared.decorators.pipe import Pipe

logger = logging.getLogger(__name__)


@Pipe
def scrape(data, config):
    data \
        | parse_emails() \
        | parse_emails_body() \
        | parse_email_attachments(config.attachment_dir) \
        | summary_to_json_file(config.attachment_dir)

@Pipe
def parse_emails(raw_emails_with_envelopes):
    logger.debug("parse emails with raw_emails_with_envelopes")
    messages = []
    for (uid, message, envelop) in raw_emails_with_envelopes:
        date = envelop.date.strftime('%Y%m%d_%H%M')

        email_from = get_from(message)
        email_subject = get_subject(message).strip()
        logger.info(f"processing: email UID={uid} from {email_from} @ {date} -> {email_subject}")

        metadata = {
            'uid': uid,
            'from': email_from,
            'subject': email_subject,
            'date': date
        }

        messages.append((uid, metadata, message))
    return messages

@Pipe
def parse_emails_body(parsed_messages):
    logger.debug("parse emails body with parsed_messages")
    messages = []
    for (uid, metadata, message) in parsed_messages:
        logger.debug(f"parsing email body for UID={uid}")
        metadata['body'] = parse_body(message)
        messages.append((uid, metadata, message))
    return messages

@Pipe
def parse_email_attachments(parsed_messages, attachment_dir):
    logger.debug("parse emails attachments with parsed_messages")
    messages = []
    for (uid, metadata, message) in parsed_messages:
        logger.debug(f"parsing email attachments for UID={uid}")
        email_attachments = save_attachments(message, attachment_dir)
        metadata['attachments'] = email_attachments
        messages.append((uid, metadata, message))
    return messages

@Pipe
def summary_to_json_file(parsed_messages, dest_dir):
    logger.info("write summary to json file with metadatas")
    file_list = []
    for (uid, metadata, message) in parsed_messages:
        try:
            filename = f"{metadata['from']}-{metadata['date']}-{metadata['uid']}.json"
            file_path = to_json_file(metadata, filename, dest_dir)
            file_list.append(file_path)
        except ValueError:
            logger.error(f"an error occured while dumping metadata into json for message uid={metadata['uid']}")
            continue

    return file_list
