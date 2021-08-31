import logging
from datetime import datetime
import json
from shared.file_util import file_util

logger = logging.getLogger(__name__)

class DateTimeEncoder(json.JSONEncoder):
    def default(self, z):
        if isinstance(z, datetime):
            return (str(z))
        else:
            return super().default(z)

def to_json_file(metadata, filename, dest_dir):
    logger.debug(f"trying to write json to file={filename} with uid={metadata['uid']}")
    json_obj = json.dumps(metadata, indent=4, cls=DateTimeEncoder)
    file_path = file_util.write_to_file(json_obj, filename, dest_dir)
    return file_path
