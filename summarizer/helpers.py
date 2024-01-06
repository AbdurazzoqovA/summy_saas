import pprint
import google.generativeai as palm

palm.configure(api_key="AIzaSyAxFzWVjI7vyJH2t3hUB1JAqjLOilSTYqs")


def summarizer(text):
    model = "models/text-bison-001"
    prompt = f"""
    Provide a short summary while keeping main points for the following text:
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
    return completion.result
