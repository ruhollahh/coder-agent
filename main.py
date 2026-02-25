import os
from dotenv import load_dotenv
import argparse
import prompts
import functions.call_function as call_function

# from google import genai
import cerebras.cloud.sdk as cerebrassdk


def main():
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    load_dotenv()
    api_key = os.environ.get("CEREBRAS_API_KEY")
    if api_key == None:
        raise RuntimeError("no api key provided in .env file")
    # boot.dev tests:
    # client = genai.Client(api_key=api_key)
    # response = client.models.generate_content(model="gemini-2.5-flash", contents="")
    # response.text
    # parts=[
    # role="user"
    client = cerebrassdk.Cerebras(api_key=api_key)

    user_prompt = args.user_prompt
    chat_completion = None
    try:
        chat_completion = client.chat.completions.create(
            model="gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": prompts.system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
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

    if chat_completion == None or len(chat_completion.choices) < 1:
        raise RuntimeError(f"empty response: {chat_completion}")

    if args.verbose:
        print(f"User prompt: {user_prompt}")
        print(f"Prompt tokens: {chat_completion.usage.prompt_tokens}")
        print(f"Response tokens: {chat_completion.usage.completion_tokens}")

    print(f"Response:\n{chat_completion.choices[0].message.content}")

    tool_calls = chat_completion.choices[0].message.tool_calls
    if tool_calls == None:
        return

    for tool_call in tool_calls:
        function_call_result = call_function.call_function(tool_call, args.verbose)
        if args.verbose:
            print(f"-> {function_call_result["content"]}")


if __name__ == "__main__":
    main()
