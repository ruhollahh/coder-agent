import os
import config


def get_file_content(working_directory, file_path):
    try:
        abs_working_dir = os.path.abspath(working_directory)
        target_file_path = os.path.normpath(os.path.join(abs_working_dir, file_path))
        if os.path.commonpath([abs_working_dir, target_file_path]) != abs_working_dir:
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
        if not os.path.isfile(target_file_path):
            return f'Error: File not found or is not a regular file: "{file_path}"'
        content = ""
        with open(target_file_path, "r") as f:
            content = f.read(config.MAX_FILE_READ_CHARS)
            if f.read(1) != "":
                content += f'[...File "{file_path}" truncated at {config.MAX_FILE_READ_CHARS} characters]'
        return content
    except Exception as e:
        return f"Error: failed to get content: {e}"
