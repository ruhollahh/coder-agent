import os

schema_get_files_info = {
    "type": "function",
    "function": {
        "name": "get_files_info",
        "description": "Lists files in a specified directory relative to the working directory, providing file size and directory status",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Directory path to list files from, relative to the working directory (default is the working directory itself)",
                }
            },
        },
    },
}

def get_files_info(working_directory, directory="."):
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_dir = os.path.normpath(os.path.join(working_dir_abs, directory))
        valid_target_dir = (
            os.path.commonpath([working_dir_abs, target_dir]) == working_dir_abs
        )
        if not valid_target_dir:
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
        if not os.path.isdir(target_dir):
            return f'Error: "{directory}" is not a directory'
        entries_detail = []
        entries = os.listdir(target_dir)
        for entry in entries:
            entry_path = os.path.join(target_dir, entry)
            entries_detail.append(
                f"- {entry}: file_size={os.path.getsize(entry_path)} bytes, is_dir={os.path.isdir(entry_path)}"
            )
        return "\n".join(entries_detail)
    except Exception as e:
        return f"Error: failed to list files: {e}"
