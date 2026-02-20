
import os
from pathlib import Path
import dotenv

from td_generation.prompt_creation import compose_prompt
dotenv.load_dotenv()
from openai import OpenAI
from prompt_creation import compose_prompt
import os

key=os.getenv("GROQ_API_KEY")

client = OpenAI(
    api_key=key,
    base_url="https://api.groq.com/openai/v1",
)
deployment = "qwen/qwen3-32b"

prompt = compose_prompt(configuration="GUIDED", input_file=Path("../ner_output/TV_block.json"))

chat_prompt = [
    {
        "role": "user",
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
    model=deployment,
    messages=messages,
    max_completion_tokens=6553,
    stop=None,
    stream=False
)

print(completion.to_json())
