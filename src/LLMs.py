import time
import asyncio
import json

from src.gemini import Gemini, Gemini_Model
from src.gpt import GPT, GPT_Model
from src.claude import Claude, Claude_Model

from src.util import matchOption, randomPickItem, combineQuestionAndOptionsFromItem


async def Answer(text,
				models: list = [Gemini_Model.GEMINI_PRO, Claude_Model.CLAUDE_3_SONNET, GPT_Model.GPT_3_5_TURBO],
				timeout: float = 3.0):
	llms = []
	for model in models:
		llm = initLLM(model)
		llms.append(llm)

	tasks = [llm.answer(text, timeout=timeout) for llm in llms]
	results = await asyncio.gather(*tasks)
	return results

def initLLM(model):
	if isinstance(model, Gemini_Model):
		return Gemini(model)
	elif isinstance(model, Claude_Model):
		return Claude(model)
	elif isinstance(model, GPT_Model):
		return GPT(model)
	else:
		raise ValueError('Invalid model')

def vote(results, options) -> int:
	answer_indices = []
	for result in results:
		if result['text'] != 'None':
			answer_indices.append(matchOption(result['text'], options))
	try:
		index = max(set(answer_indices), key=answer_indices.count)
	except:
		index = 0
	return index

async def main() -> None:
	with open('data/data.jsonl', 'r', encoding='utf8') as file:
		data = [json.loads(line) for line in file]
	item = randomPickItem(data)
	text = combineQuestionAndOptionsFromItem(item)
	real_ans_index = item['real_ans']
	print(text)

	start_time = time.time()

	results = await Answer(text)
	for result in results:
		print(format(result['model'], '16s'), format(result['text'], '4s'), format(result['time_elapsed'], '4d'), 'ms')
	print('Vote:', vote(results, item['options']))

	end_time = time.time()
	print('Time:', int((end_time - start_time)*1000))

	print('real', str(real_ans_index) + '. ' + item['options'][real_ans_index-1])

if __name__ == '__main__':
	asyncio.run(main())
