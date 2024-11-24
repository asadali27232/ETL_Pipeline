import google.generativeai as genai

# Access the API key and other variables
api_key = ""

# Initialize Groq client
genai.configure(api_key=api_key)


def summarize_text(contents):
    """Summarize the text content using the provided summary format."""

    # Read a INSTRUCTIONS from a txt file
    with open('prompt.json', 'r', encoding='utf-8') as file:
        instructions = file.read()

    prompt = "\n\nDEGREE/COURSE DETAILS FROM University Website:\n\n" + \
        contents + "\n\n" + "Instructions to fill up JSON" + instructions + "\n\n" + \
        "Please summarize the above detailed text into JSON format according to the instructions provided as value for every key."

    # Create the model
    generation_config = {
        "temperature": 1,
        "top_p": 1,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "application/json",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )

    chat_session = model.start_chat(
        history=[
        ]
    )

    response = chat_session.send_message(prompt)
    return response.text


if __name__ == '__main__':
    summary = summarize_text("Example text to summarize")

    # Write the summary to a JSON file
    with open('summary.json', 'w', encoding='utf-8') as file:
        file.write(summary)
