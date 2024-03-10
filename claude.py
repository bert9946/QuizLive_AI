import anthropic
from timeout_decorator import timeout

@timeout(5)
def Answer(text, model_id='Opus'):
    client = anthropic.Anthropic()
    if model_id == 'Opus':
        model = "claude-3-opus-20240229"
    if model_id == 'Sonnet':
        model = "claude-3-sonnet-20240229"

    message = client.messages.create(
        model=model,
        stop_sequences=["。"],
        max_tokens=100,
        temperature=0.0,
        system="你是問答遊戲的 AI。根據問題，簡短回答最可能的答案。（不用解釋原因，只要回答選項文字）",
        messages=[
            {"role": "user", "content": text}
        ]
    )

    return message.content[0].text
