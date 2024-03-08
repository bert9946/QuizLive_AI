from openai import OpenAI

def Answer(text, model_id='GPT-3.5'):
  client = OpenAI()
  if model_id == 'GPT-3.5':
    model = "gpt-3.5-turbo-0125"
  elif model_id == 'GPT-4':
    model = "gpt-4-0125-preview"

  completion = client.chat.completions.create(
    model=model,
    messages=[
      {"role": "system", "content": "根據問題，回答最可能的答案。（只要回答選項文字。）"},
      {"role": "user", "content": text}
    ],
    timeout=5

  )
  return completion.choices[0].message.content
