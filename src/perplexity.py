import os
import aiohttp
import asyncio
from enum import Enum
from time import perf_counter

from src.gpt import GPT


class Perplexity_Model(Enum):
	SONAR_SMALL_CHAT = "sonar-small-chat"
	SONAR_MEDIUM_CHAT = "sonar-medium-chat"

	def __str__(self):
		name = self.name
		name = '-'.join(x.capitalize() for x in name.split('_'))
		name = name.replace('Gpt', 'GPT')
		return name

class Perplexity(GPT):
	SYSTEM_TEXT = "你是問答遊戲的 AI。根據提供的問題和選項，簡短回答最可能的選項。（不用解釋原因，只要回答選項文字）"
	def __init__(self, model_id=Perplexity_Model.SONAR_SMALL_CHAT):
		self.model_id = model_id
		self.model = self.model_id.value

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
		api_key = os.environ.get('PERPLEXITY_API_KEY')
		url = "https://api.perplexity.ai/chat/completions"
		payload = {
			"model": self.model,
			"messages": [
				{
					"role": "system",
					"content": self.SYSTEM_TEXT
				},
				{
					"role": "user",
					"content": text
				}
			],
			"temperature": 0.3,
		}
		headers = {
			"accept": "application/json",
			"content-type": "application/json",
			"authorization": f"Bearer {api_key}"
		}

		timeout_ = aiohttp.ClientTimeout(total=timeout)

		async with aiohttp.ClientSession(timeout=timeout_) as session:
			async with session.post(url, headers=headers, json=payload) as response:
				response_data = await response.json()
		return response_data


	def parseResponseData(self, response_data):
		is_error = False
		response_text = response_data['choices'][0]['message']['content']
		return response_text, is_error