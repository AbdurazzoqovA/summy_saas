import pprint
import google.generativeai as palm
import markdown
import openai
import os
from dotenv import load_dotenv


load_dotenv()

# Load environment variables from .env file


palm.configure(api_key="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")


def summarizer(
    text,
    mode,
    range_value,
):

    # summary_length_tokens = 100
    word_count = len(text.split())

    summaryLen = int(word_count*0.9)

    model = "models/text-bison-001"
    range_value = int(range_value)

    if range_value == 3:
        summaryLen = int(word_count/3)
    elif range_value == 2:
        summaryLen = int(word_count/2)
    elif range_value == 1:
        summaryLen = int(word_count/1.5)

    #  Summarize the text and shorten it by {range_percentage}, text:
    if mode == "Paragraph":
        prompt = f"""
        Summarize the following text in {summaryLen} words, do not stop until complete:
        {text}

        """
    else:
        prompt = f"""
       summarize the text and present it in bullet points important, Also format the output text nicely, use headings. text:
        {text}
        """

    try:
        openai_api_key = os.environ.get("OPEN_AI_KEY")
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",  # Experiment with different models as needed
            messages=[
                {
                    "role": "system",
                    "content": f"you are expert to summarize texts, summarize given text and return only markdown result no extra.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            max_tokens=4000,
            temperature=0.9,
        )

        return response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
