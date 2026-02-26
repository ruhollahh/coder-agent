import os
import sys
from dotenv import load_dotenv
import argparse
import prompts
import functions.call_function as call_function
import cerebras.cloud.sdk as cerebrassdk


def main():
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    load_dotenv()
    api_key = os.environ.get("CEREBRAS_API_KEY")
    if api_key == None:
        print("no api key provided in .env file")
        sys.exit(1)

    client = cerebrassdk.Cerebras(api_key=api_key)
    user_prompt = args.user_prompt
    if args.verbose:
        print(f"User prompt: {user_prompt}")

    messages = [
        {
            "role": "system",
            "content": prompts.system_prompt,
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ]

    for i in range(0, 20):
        chat = None
        try:
            chat = client.chat.completions.create(
                model="gpt-oss-120b",
                messages=messages,
                tools=call_function.available_functions,
                tool_choice="auto",
                temperature=0.1,
            )
        except cerebrassdk.APIConnectionError as e:
            print("The server could not be reached")
            print(e.__cause__)  # an underlying Exception, likely raised within httpx.
        except cerebrassdk.RateLimitError as e:
            print("A 429 status code was received; we should back off a bit.")
        except cerebrassdk.APIStatusError as e:
            print(f"Another non-200-range status code was received: {e}")
            print(e.status_code)
            print(e.response)
        except Exception as e:
            print(f"failed to create chat completion: {e}")

        if chat == None or len(chat.choices) < 1:
            print(f"failed to create chat: {chat}")
            sys.exit(1)

        response = chat.choices[0]

        messages.append(response.message)

        if args.verbose:
            print(f"Prompt tokens: {chat.usage.prompt_tokens}")
            print(f"Response tokens: {chat.usage.completion_tokens}")

        tool_calls = response.message.tool_calls or []

        if len(tool_calls) < 1:
            print(f"Response:\n{response.message.content}")
            return

        for tool_call in tool_calls:
            function_call_result = call_function.call_function(tool_call, args.verbose)
            if args.verbose:
                print(f"-> {function_call_result["content"]}")
            messages.append(function_call_result)

    print(f"Feedback loop exceeds {20} iterations")
    sys.exit(1)


if __name__ == "__main__":
    main()
