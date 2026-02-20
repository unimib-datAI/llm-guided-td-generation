import os
from pathlib import Path
import dotenv
dotenv.load_dotenv()
from openai import AzureOpenAI
from prompt_creation import compose_prompt

endpoint = os.getenv("ENDPOINT_URL")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")

client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=subscription_key,
    api_version="2025-01-01-preview",
)

prompt = compose_prompt(configuration="GUIDED", input_file=Path("../ner_output/TV_block.json"))

chat_prompt = [
    {
        "role": "developer",
        "content": [
            {
                "type": "text",
                "text": prompt
           }
        ]
    }
]

messages = chat_prompt

completion = client.chat.completions.create(
    model="gpt-5-mini",
    messages=messages,
    max_completion_tokens=6553,
    stop=None,
    stream=False
)

print(completion.to_json())