import pprint
import google.generativeai as palm
import markdown
import openai
import os
from dotenv import load_dotenv

load_dotenv()


palm.configure(api_key="AIzaSyAxFzWVjI7vyJH2t3hUB1JAqjLOilSTYqs")


def summarizer(
    text,
    mode,
    range_value,
):
    
    summary_length_tokens = 100

    model = "models/text-bison-001"
    range_value = int(range_value)

    range_percentage = '1%'

    if range_value == 5:
        summary_length_tokens = 90
    elif range_value == 4:
        summary_length_tokens = 65
    elif range_value == 3:
        summary_length_tokens = 50
    elif range_value == 2:
        summary_length_tokens = 30
    elif range_value == 1:
        summary_length_tokens = 10

    if mode == "Paragraph":
        prompt = f"""
        Summarize the text and shorten it by {range_percentage}, text:
        {text}

        """
    else:
        prompt = f"""
       summarize the text and present it in bullet points important, text:
        {text}
        """

    try:
        openai_api_key = os.environ.get("OPEN_AI_KEY")
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",  # Experiment with different models as needed
            max_tokens=summary_length_tokens,
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
        )

        return response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
