import openai
import os
from dotenv import load_dotenv


def execute(prompt: str) -> str:
    load_dotenv()

    openai.api_key = os.getenv("CHATGPT_API_KEY")

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return response['choices'][0]['message']['content']
