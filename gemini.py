import os
from timeout_decorator import timeout

import google.generativeai as genai


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
	def __init__(self, model_id='gemini-pro'):
		GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
		genai.configure(api_key=GOOGLE_API_KEY)
		self.model_id = model_id
		self.model = genai.GenerativeModel(self.model_id, safety_settings=self.SAFETY_SETTINGS)

	@timeout(5)
	def Answer(self, text):
		response = self.model.generate_content(text)
		return response.text
