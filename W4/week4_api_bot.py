import os
from openai import OpenAI

api_key = ""



client = OpenAI(
    api_key=api_key,
    base_url="https://open.bigmodel.cn/api/paas/v4"
)

def chat(prompt: str):
    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: py week04_API/week4_api_bot.py \"你的问题\"")
    else:
        question = sys.argv[1]
        res = chat(question)
        print("\n-----回答-----\n")
        print(res)
        with open("chat_log.txt","w",encoding="utf-8") as f:
            f.write(res)
