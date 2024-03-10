import anthropic
from timeout_decorator import timeout


class Claude:
    MODEL_DICT = {
        'Claude-3-Opus': "claude-3-opus-20240229",
        'Claude-3-Sonnet': "claude-3-sonnet-20240229"
    }
    def __init__(self, model_id='Claude-3-Opus'):
        self.client = anthropic.Anthropic()
        self.model_id = model_id
        self.model = self.MODEL_DICT[model_id]

    @timeout(5)
    def Answer(self, text):
        message = self.client.messages.create(
            model=self.model,
            stop_sequences=["。"],
            max_tokens=100,
            temperature=0.0,
            system="你是問答遊戲的 AI。根據問題，簡短回答最可能的答案。（不用解釋原因，只要回答選項文字）",
            messages=[
                {"role": "user", "content": text}
            ]
        )
        return message.content[0].text
