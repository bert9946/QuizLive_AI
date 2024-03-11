import os
import time
import aiohttp
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
		start_time = time.time()
		response_data = await self.sendRequest(text, timeout=timeout)
		response_text = response_data['candidates'][0]['content']['parts'][0]['text']
		end_time = time.time()
		result = {
			'model': str(self.model_id),
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
					"text": self.SYSTEM_PROMPT,
					"text": text
				}]
			}],
			"safetySettings": self.SAFETY_SETTINGS,
			"generationConfig": self.GENERATION_CONFIG
		}

		timeout_ = aiohttp.ClientTimeout(total=timeout)

		try:
			async with aiohttp.ClientSession(timeout=timeout_) as session:
				async with session.post(self.__url, headers=headers, json=data) as response:
					response_data = await response.json()
		except Exception as e:
			response_text = "None"
		return response_data

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