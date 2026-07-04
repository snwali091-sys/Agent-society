import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

key = os.environ.get("DASHSCOPE_API_KEY")
print("Key found:", repr(key))

client = OpenAI(
    api_key=key,
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
)

try:
    response = client.chat.completions.create(
        model="qwen-plus",
        messages=[
            {"role": "user", "content": "Say hello in one sentence."}
        ],
        max_tokens=50,
    )
    print("SUCCESS:", response.choices[0].message.content)

except Exception as e:
    print("FAILED:", e)