import time
from openai import OpenAI, AsyncOpenAI

class GPT:
	MODEL_DICT = {
		'GPT-3.5-Turbo': "gpt-3.5-turbo-0125",
		'GPT-4-Turbo': "gpt-4-0125-preview"
	}
	SYSTEM_TEXT = "你是問答遊戲的 AI。根據問題，簡短回答最可能的答案。（不用解釋原因，只要回答選項文字）"
	def __init__(self, model_id='GPT-3.5-Turbo'):
		self.client = OpenAI()
		self.model_id = model_id
		self.model = self.MODEL_DICT[model_id]

	async def answer(self, text):
		start_time = time.time()
		self.client = AsyncOpenAI()
		completion = await self.client.chat.completions.create(
			model=self.model,
			messages=[
				{"role": "system", "content": self.SYSTEM_TEXT},
				{"role": "user", "content": text}
			],
			timeout=5
		)
		end_time = time.time()
		result = {
			'model': self.model_id,
			'text': completion.choices[0].message.content,
			'time_elapsed': int((end_time - start_time) * 1000)
		}
		return result