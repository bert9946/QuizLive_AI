import time
import asyncio

from gemini import Gemini
from gpt import GPT
from claude import Claude

from src.util import *


async def Answer(text):
	gemini = Gemini('Gemini-Pro')
	claude_opus = Claude('Claude-3-Opus')
	# claude_sonnet = Claude('Claude-3-Sonnet')
	# gpt_4 = GPT('GPT-4-Turbo')
	gpt_35 = GPT('GPT-3.5-Turbo')

	tasks = [
			gemini.answer(text),
			claude_opus.answer(text),
			# claude_sonnet.answer(text),
			# gpt_4.answer(text),
			gpt_35.answer(text),
		]
	results = await asyncio.gather(*tasks)
	return results

def vote(results, options) -> int:
	# answer_indices = [matchOption(result['text'], options) for result in results]
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
