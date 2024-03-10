from openai import OpenAI

class GPT:
	MODEL_DICT = {
		'GPT-3.5-Turbo': "gpt-3.5-turbo-0125",
		'GPT-4-Turbo': "gpt-4-0125-preview"
	}
	def __init__(self, model_id='GPT-3.5-Turbo'):
		self.client = OpenAI()
		self.model_id = model_id
		self.model = self.MODEL_DICT[model_id]

	def Answer(self, text):
		completion = self.client.chat.completions.create(
			model=self.model,
			messages=[
				{"role": "system", "content": "根據問題，回答最可能的答案。（只要回答選項文字。）"},
				{"role": "user", "content": text}
			],
			timeout=5
		)
		return completion.choices[0].message.content
