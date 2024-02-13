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
    
    summary_length_tokens = 10 
    model = "models/text-bison-001"
    range_value = int(range_value)
    if range_value == 5:
        range_percentage = "20%"
    elif range_value == 4:
        range_percentage = "40%"
    elif range_value == 3:
        range_percentage = "50%"
    elif range_value == 2:
        range_percentage = "70%"
    elif range_value == 1:
        range_percentage = "90%"

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
