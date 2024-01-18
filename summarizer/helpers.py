import pprint
import google.generativeai as palm
import markdown

palm.configure(api_key="AIzaSyAxFzWVjI7vyJH2t3hUB1JAqjLOilSTYqs")


def summarizer(
    text,
    mode,
    range_value,
):
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

    completion = palm.generate_text(
        model=model,
        prompt=prompt,
        temperature=1,
        # The maximum length of the response
        max_output_tokens=800,
        candidate_count=1,
    )

    return markdown.markdown(completion.result)
