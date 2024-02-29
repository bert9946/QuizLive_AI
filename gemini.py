import os
from timeout_decorator import timeout

import google.generativeai as genai


class Gemini:
	def __init__(self) -> None:
		GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
		genai.configure(api_key=GOOGLE_API_KEY)

		safety_settings=[
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
		self.model = genai.GenerativeModel('gemini-pro', safety_settings=safety_settings)

	@timeout(5)
	def Answer(self, text):
		response = self.model.generate_content(text)
		return response.text
