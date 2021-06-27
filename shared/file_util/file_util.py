import os
import logging

logger = logging.getLogger(__name__)

def write_to_file(content, filename, dest_dir):
    file_path = os.path.join(dest_dir, filename)
    if os.path.exists(file_path):
        logger.warning(f"File={file_path} has already been created.")
        raise ValueError(f"file={filename} already existed")

    logger.info(f"write to json file {file_path}")
    with open(file_path, "w") as file:
        file.write(content)

    return file_path
