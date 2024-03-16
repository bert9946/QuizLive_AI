from enum import Enum
import os
from time import perf_counter
import aiohttp
import asyncio

class Claude_Model(Enum):
	CLAUDE_3_OPUS = "claude-3-opus-20240229"
	CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
	CLAUDE_3_HAIKU = "claude-3-haiku-20240307"

	def __str__(self):
		name = '-'.join(x.capitalize() for x in self.name.split('_'))
		return name

class Claude:
	def __init__(self, model_id=Claude_Model.CLAUDE_3_OPUS):
		self.model_id = model_id
		self.model = self.model_id.value
		self.__ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')

	async def answer(self, text, timeout: float = 3.0):
		start_time = perf_counter()
		success = True
		try:
			response_data = await self.sendRequest(text, timeout=timeout)
			response_text, is_error = self.parseResponseData(response_data)
			if is_error:
				success = False
		except asyncio.CancelledError:
			response_text = "CANCELLED"
			success = False
		except asyncio.exceptions.TimeoutError:
			response_text = "TIMEOUT"
			success = False
		except Exception:
			response_text = "ERROR"
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

	async def sendRequest(self, text, timeout: float = 3.0):
		url = "https://api.anthropic.com/v1/messages"
		headers = {
			"x-api-key": self.__ANTHROPIC_API_KEY,
			"anthropic-version": "2023-06-01",
			"content-type": "application/json",
		}
		data = {
			"model": self.model,
			"stop_sequences": ["。"],
			"max_tokens": 100,
			"temperature": 0.5,
			"system": "你是問答遊戲的 AI。根據問題，簡短回答最可能的答案。（不要解釋原因，只要回答選項文字）",
			"messages": [
				{"role": "user", "content": text}
			]
		}
		timeout_ = aiohttp.ClientTimeout(total=timeout)
		async with aiohttp.ClientSession(timeout=timeout_) as session:
			async with session.post(url, headers=headers, json=data) as response:
				response_data = await response.json()
		return response_data

	def parseResponseData(self, response_data):
		if response_data['type'] == 'message':
			response_text = response_data['content'][0]['text']
			is_error = False
		elif response_data['type'] == 'error':
			response_text = response_data['error']['type'].upper()
			is_error = True
		return response_text, is_error
