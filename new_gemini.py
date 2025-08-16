import random
import json
from google import genai

with open(".env", "r", encoding="utf-8") as f:
    api_keys = f.readlines()

client = genai.Client(api_key=random.choice(api_keys))

# ------------ Simple Test ------------

# response = client.models.generate_content(
#     model="gemini-2.5-flash",
#     contents="Explain how AI works in a few words"
# )
# print(response.text)

# ------------ Load Schema ------------

with open("response_schema.json", "r", encoding="utf-8") as f:
    response_schema = json.load(f)

# ------------ Prepare Prompt ------------

with open('contents.txt', 'r', encoding='utf-8') as file:
    contents = file.read()

prompt = f"DEGREE/COURSE DETAILS FROM University Website:\n\n{contents}\n\nPlease summarize the above detailed text into JSON format according to the instructions provided as value for every key. Write the content in a way that we can upload this json directly to our live webiste don't make such sentences that are just to read by human like no such thing is provided in text etc. Do not say this; The provided text does not contain and no information found, etc. Simply say NA is not found or not applicable!"

# ------------ Call the API ------------

response = client.models.generate_content(
    model="gemini-2.5-pro",
    contents=prompt,
    config={
        "response_mime_type": "application/json",
        "response_schema": response_schema
    }
)

# ------------ Output ------------

try:
    data = json.loads(response.text)   # convert string → dict
except json.JSONDecodeError:
    print("⚠️ Response was not valid JSON, saving raw text instead.")
    data = response.text

# Save to response.json
with open("response.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("✅ Saved response to response.json")
