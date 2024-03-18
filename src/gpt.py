from time import perf_counter
from openai import OpenAI, AsyncOpenAI
from enum import Enum
import re
import asyncio


class GPT_Model(Enum):
	GPT_3_5_TURBO = "gpt-3.5-turbo-0125"
	GPT_4_TURBO = "gpt-4-0125-preview"

	def __str__(self):
		name = re.sub(r'(\d)_(\d)', r'\1.\2', self.name)
		name = '-'.join(x.capitalize() for x in name.split('_'))
		name = name.replace('Gpt', 'GPT')
		return name

class GPT:
	SYSTEM_TEXT = "你是問答遊戲的 AI。根據問題，簡短回答最可能的答案。（不用解釋原因，只要回答選項文字）"
	def __init__(self, model_id=GPT_Model.GPT_3_5_TURBO):
		self.client = AsyncOpenAI()
		self.model_id = model_id
		self.model = self.model_id.value

	async def answer(self, text, timeout: float = 3.0):
		start_time = perf_counter()
		success = True
		try:
			completion = await self.client.chat.completions.create(
				model=self.model,
				messages=[
					{"role": "system", "content": self.SYSTEM_TEXT},
					{"role": "user", "content": text}
				],
				timeout=timeout
			)
			response_text = completion.choices[0].message.content
		except asyncio.CancelledError:
			response_text = "CANCELLED"
			success = False
		finally:
			end_time = perf_counter()
			result = {
				'model': str(self.model_id),
				'success': success,
				'text': response_text,
				'time_elapsed': int((end_time - start_time) * 1000)
			}
			return result