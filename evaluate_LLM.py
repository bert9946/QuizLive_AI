import json
import time
from termcolor import colored
import asyncio

from src.util import *
from LLMs import Answer, vote

async def main() -> None:
	start_time = time.time()
	with open('data/data.jsonl', 'r', encoding='utf8') as file:
		data = [json.loads(line) for line in file]


	correct_count = 0
	number = 50
	for i in range(number):
		item = randomPickItem(data)
		if not isItemValid(item):
			i -= 1
			continue
		text = item['question'] + '\n' + '\n'.join(item['options'])
		real_ans_index = item['real_ans']

		print(f'#{i}', text)

		single_start_time = time.time()
		try:
			responses = await Answer(text)
		except:
			break
		for response in responses:
			print(format(response['model'], '16s'), format(response['text'], '8s'), format(response['time_elapsed'], '4d'), 'ms')
		ans_index = vote(responses, item['options'])
		ans_text = item['options'][ans_index-1]
		ans = str(ans_index) + '. ' + ans_text

		single_end_time = time.time()


		print(colored(ans, 'cyan'), end=' / ')

		print(str(real_ans_index) + '. ' + item['options'][real_ans_index-1])
		if ans_index == real_ans_index:
			print(colored('Correct', 'green'), end=' ')
			correct_count += 1
		else:
			print(colored('Wrong', 'red'), end=' ')
		single_execution_time = calculateExecutionTime(single_start_time, single_end_time)
		print(f'{single_execution_time}ms')
		print('====================')

	total_count = i+1
	print(f'Correct: {correct_count}/{total_count}')
	print(correct_count/total_count*100, '%')


	end_time = time.time()
	print("average time:", calculateExecutionTime(start_time, end_time) / total_count, 'ms')

if __name__ == '__main__':
	asyncio.run(main())