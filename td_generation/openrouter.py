import requests
import json
import os
from pathlib import Path
import dotenv
from td_generation.prompt_creation import compose_prompt
dotenv.load_dotenv()

prompt = compose_prompt(configuration="GUIDED", input_file=Path("../ner_output/TV_block.json"))
key = os.getenv("OPENROUTER_API_KEY")

response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
    "Authorization": "Bearer " + key,
    "Content-Type": "application/json"
  },
  data=json.dumps({
    "model": "mistralai/devstral-2512:free",
    "messages": [
      {
        "role": "user",
        "content": prompt}
    ]
  })
)

print(response.json())