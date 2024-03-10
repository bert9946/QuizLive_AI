import os
import time
import aiohttp


class Gemini:
	SAFETY_SETTINGS = [
		{
			"category": "HARM_CATEGORY_DANGEROUS",
			"threshold": "BLOCK_NONE",
		},
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
		},
	]
	MODEL_DICT = {
		'Gemini-Pro': "gemini-pro"
	}

	def __init__(self, model_id='Gemini-Pro'):
		GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
		self.model_id = model_id
		self.model_name = self.MODEL_DICT[self.model_id]
		self.__url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GOOGLE_API_KEY}"

	async def answer(self, text):
		headers = {
			"Content-Type": "application/json"
		}
		data = {
			"contents": [{
				"parts": [{
					"text": text
				}]
			}]
		}

		start_time = time.time()

		timeout = aiohttp.ClientTimeout(total=3)

		try:
			async with aiohttp.ClientSession(timeout=timeout) as session:
				async with session.post(self.__url, headers=headers, json=data) as response:
					response_data = await response.json()
					response_text = response_data['candidates'][0]['content']['parts'][0]['text']
		except:
			response_text = "None"
		end_time = time.time()
		result = {
			'model': self.model_id,
			'text': response_text,
			'time_elapsed': int((end_time - start_time) * 1000)
		}

		return result
