import os

def write_to_file(content, filename, dest_dir):
    file_path = os.path.join(dest_dir, filename)
    if os.path.exists(file_path):
        print(f"File={file_path} has already been created.")
        raise ValueError(f"file={filename} already existed")

    print(f"write to json file {file_path}")
    with open(file_path, "w") as file:
        file.write(content)

    return file_path
