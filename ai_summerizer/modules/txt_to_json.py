import random
import json
from google import genai

with open(".env", "r", encoding="utf-8") as f:
    api_keys = f.readlines()

client = genai.Client(api_key=random.choice(api_keys))


def summarize_text(contents, response_schema=None):
    """Summarize the text content using the provided summary format."""

    with open("./helpers_response_schema.json", "r", encoding="utf-8") as f:
        response_schema = json.load(f)

    # ------------ Prepare Prompt ------------

    prompt = f"DEGREE/COURSE DETAILS FROM University Website:\n\n{contents}\n\nPlease try to stick to given context. Write the content in a way that we can upload this json directly to our live webiste don't make such sentences that are just to read by human like no such thing is provided in text etc. Do not say this; The provided text does not contain and no information found, etc. Simply say NA is not found or not applicable!"

    # ------------ Call the API ------------

    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": response_schema
        }
    )

    return response.text


if __name__ == '__main__':
    summary = summarize_text("Example text to summarize")

    # Write the summary to a JSON file
    with open('gemini_test.json', 'w', encoding='utf-8') as file:
        file.write(summary)
