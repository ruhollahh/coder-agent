import json
import config
from functions.get_files_info import schema_get_files_info, get_files_info
from functions.get_file_content import schema_get_file_content, get_file_content
from functions.run_python_file import schema_run_python_file, run_python_file
from functions.write_file import schema_write_file, write_file


def call_function(function_call, verbose=False):
    try:
        function_name = function_call.function.name or ""
        args = (
            json.loads(function_call.function.arguments)
            if function_call.function.arguments
            else {}
        )
        if verbose:
            print(f"Calling function: {function_name}({args})")
        else:
            print(f" - Calling function: {function_name}")
        if function_name not in function_map:
            return {
                "role": "tool",
                "tool_call_id": function_call.id,
                "content": f"Unknown function: {function_name}",
            }
        args["working_directory"] = config.WORKING_DIRECTORY
        function_result = function_map[function_name](**args)
        return {
            "role": "tool",
            "tool_call_id": function_call.id,
            "content": function_result,
        }
    except Exception as e:
        return {
            "role": "tool",
            "tool_call_id": function_call.id,
            "content": f"failed to call function: {e}",
        }


function_map = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "run_python_file": run_python_file,
    "write_file": write_file,
}

available_functions = [
    schema_get_files_info,
    schema_get_file_content,
    schema_run_python_file,
    schema_write_file,
]
