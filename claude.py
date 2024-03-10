import os
import time
import aiohttp
class Claude:
	MODEL_DICT = {
		'Claude-3-Opus': "claude-3-opus-20240229",
		'Claude-3-Sonnet': "claude-3-sonnet-20240229"
	}

	def __init__(self, model_id='Claude-3-Opus'):
		self.model_id = model_id
		self.model = self.MODEL_DICT[model_id]
		self.ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')

	async def answer(self, text):
		start_time = time.time()
		url = "https://api.anthropic.com/v1/messages"
		headers = {
			"x-api-key": self.ANTHROPIC_API_KEY,
			"anthropic-version": "2023-06-01",
			"content-type": "application/json",
		}
		data = {
			"model": self.MODEL_DICT[self.model_id],
			"stop_sequences": ["。"],
			"max_tokens": 100,
			"temperature": 0.0,
			"system": "你是問答遊戲的 AI。根據問題，簡短回答最可能的答案。（不要解釋原因，只要回答選項文字）",
			"messages": [
				{"role": "user", "content": text}
			]
		}

		timeout = aiohttp.ClientTimeout(total=3)
		try:
			async with aiohttp.ClientSession(timeout=timeout) as session:
				async with session.post(url, headers=headers, json=data) as response:
					response_data = await response.json()
					response_text = response_data['content'][0]['text']
		except:
			response_text = "None"

		end_time = time.time()

		result = {
			'model': self.model_id,
			'text': response_text,
			'time_elapsed': int((end_time - start_time) * 1000)
		}
		return result
