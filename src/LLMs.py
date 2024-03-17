from time import perf_counter
import asyncio
import json
from collections import Counter

from src.gemini import Gemini, Gemini_Model
from src.gpt import GPT, GPT_Model
from src.claude import Claude, Claude_Model

from src.util import matchOption, randomPickItem, combineQuestionAndOptionsFromItem


async def Answer(text,
				options,
				models: list = [Gemini_Model.GEMINI_1_0_PRO, Claude_Model.CLAUDE_3_SONNET, GPT_Model.GPT_3_5_TURBO],
				timeout: float = 3.0):
	llms = []
	for model in models:
		llm = initLLM(model)
		llms.append(llm)

	tasks = [asyncio.create_task(llm.answer(text, timeout=timeout)) for llm in llms]
	results = []
	ans_indices = []
	pending_tasks = set(tasks)

	for fut in asyncio.as_completed(tasks):
		try:
			pending_tasks.discard(fut)
			result = await fut
			results.append(result)
			yield result

			if result['success']:
				ans_index = matchOption(result['text'], options)
			else:
				ans_index = 0
			ans_indices.append(ans_index)
			successed_ans_indices = [index for index in ans_indices if index != 0]

			if find_majority_element(successed_ans_indices, size=len(models)):
				for task in pending_tasks:
					try:
						task.cancel()
						result = await task
						if result not in results:
							results.append(result)
							yield result
					except asyncio.CancelledError:
						pass
				break
		except asyncio.CancelledError:
			pass

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
		if result['success']:
			answer_indices.append(matchOption(result['text'], options))
	try:
		index = max(set(answer_indices), key=answer_indices.count)
	except:
		index = 0
	return index

def find_majority_element(data, size):
	element_counts = Counter(data)
	for element, count in element_counts.items():
		if count > size // 2:
			return element

	return None

async def main() -> None:
	with open('data/data.jsonl', 'r', encoding='utf8') as file:
		data = [json.loads(line) for line in file]
	item = randomPickItem(data)
	text = combineQuestionAndOptionsFromItem(item)
	real_ans_index = item['real_ans']
	print(text)

	start_time = perf_counter()

	results = []
	async for result in Answer(text, item['options'], timeout=3.0, models=models):
		print(format(result['model'], '16s'), format(result['text'], '4s'), format(result['time_elapsed'], '4d'), 'ms')
		results.append(result)
	print('Vote:', vote(results, item['options']))

	end_time = perf_counter()
	print('Time:', int((end_time - start_time)*1000))

	print('Real answer:', str(real_ans_index) + '. ' + item['options'][real_ans_index-1])

if __name__ == '__main__':
	asyncio.run(main())
