import os
from time import perf_counter
import aiohttp
import asyncio
from enum import Enum

class Gemini_Model(Enum):
	GEMINI_PRO = "gemini-pro"

	def __str__(self):
		name = '-'.join(x.capitalize() for x in self.name.split('_'))
		return name


class Gemini:
	SYSTEM_PROMPT = "你是問答遊戲的 AI。根據問題，簡短回答最可能的答案。（不要解釋原因，只要回答選項文字）"

	def __init__(self, model_id=Gemini_Model.GEMINI_PRO):
		GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
		self.model_id = model_id
		self.model_name = self.model_id.value
		self.__url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GOOGLE_API_KEY}"

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
		headers = {
			"Content-Type": "application/json"
		}
		data = {
			"contents": [{
				"parts": [{
					"text": self.SYSTEM_PROMPT
				},
				{
					"text": text
				}]
			}],
			"safetySettings": self.SAFETY_SETTINGS,
			"generationConfig": self.GENERATION_CONFIG
		}

		timeout_ = aiohttp.ClientTimeout(total=timeout)

		async with aiohttp.ClientSession(timeout=timeout_) as session:
			async with session.post(self.__url, headers=headers, json=data) as response:
				response_data = await response.json()

		return response_data

	def parseResponseData(self, response_data):
		if 'candidates' in response_data:
			response_text = response_data['candidates'][0]['content']['parts'][0]['text']
			is_error = False
		elif 'error' in response_data:
			response_text = response_data['error']['status']
			is_error = True
		return response_text, is_error

	GENERATION_CONFIG = {
		"temperature": 1.0,
		"maxOutputTokens": 100,
	}
	SAFETY_SETTINGS = [
		{
			"category": "HARM_CATEGORY_HARASSMENT",
			"threshold": "BLOCK_NONE",
		},
		{
			"category": "HARM_CATEGORY_HATE_SPEECH",
			"threshold": "BLOCK_NONE",
		},
		{
			"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
			"threshold": "BLOCK_NONE",
		},
		{
			"category": "HARM_CATEGORY_DANGEROUS_CONTENT",
			"threshold": "BLOCK_NONE",
		}
	]