from openai import OpenAI

def Anwser(text):
  client = OpenAI()
  completion = client.chat.completions.create(
    model="gpt-3.5-turbo-0125",
    messages=[
      {"role": "system", "content": "根據問題，回答最可能的答案。（只要回答選項文字。）"},
      {"role": "user", "content": text}
    ]
  )
  return completion.choices[0].message.content
