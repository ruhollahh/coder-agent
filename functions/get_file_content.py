import os
import config
import config

schema_get_file_content = {
    "type": "function",
    "function": {
        "name": "get_file_content",
        "description": f"Retrieves the content (at most {config.MAX_FILE_READ_CHARS} characters) of a specified file within the working directory",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to read, relative to the working directory",
                }
            },
            "required": ["file_path"],
        },
    },
}


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
