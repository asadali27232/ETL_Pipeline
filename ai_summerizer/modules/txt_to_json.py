import random
import json
import time
from google import genai

with open("./ai_summerizer/modules/helpers/.env", "r", encoding="utf-8") as f:
    api_keys = f.readlines()

client = genai.Client(api_key=random.choice(api_keys))


def summarize_text(contents, response_schema=None):
    """Summarize the text content using the provided summary format."""

    with open("./ai_summerizer/modules/helpers/response_schema.json", "r", encoding="utf-8") as f:
        response_schema = json.load(f)

    # ------------ Prepare Prompt ------------
    prompt = f"DEGREE/COURSE DETAILS:\n\n{contents}\n\nAnswer the in a way that we can upload this json directly to our live website. Don't make such sentences that are just to read by human like 'no such thing is provided in text' etc. Do not say things like 'The provided text does not contain' or 'no information found'. Simply say 'NA' if not found or not applicable!"

    # ------------ Call the API with timer ------------
    start_time = time.time()
    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": response_schema
        }
    )
    end_time = time.time()
    elapsed = round(end_time - start_time, 2)

    print(f"✅ Done in {elapsed} seconds")

    return response.text


if __name__ == '__main__':
    summary = summarize_text("Example text to summarize")

    # Write the summary to a JSON file
    with open('gemini_test.json', 'w', encoding='utf-8') as file:
        file.write(summary)
