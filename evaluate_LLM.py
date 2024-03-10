import json
import time
from termcolor import colored

from src.util import *
from gpt import GPT
from gemini import Gemini
from claude import Claude


start_time = time.time()
with open('data/data.jsonl', 'r', encoding='utf8') as file:
	data = [json.loads(line) for line in file]

gemini = Gemini()
# claude = Claude('Opus')
# gpt = GPT('GPT-4-Turbo')


correct_count = 0
number = 5

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
		# response = gpt.Answer(text)
		# response = claude.Answer(text)
		response = gemini.Answer(text)
	except Exception as e:
		print("An error occurred:", e)
		response = None
		
	single_end_time = time.time()


	if response:
		ans_index = matchOption(response, item['options'])
		print(colored(str(ans_index) + '. ' + response, 'cyan'), end=' / ')

		print(str(real_ans_index) + '. ' + item['options'][real_ans_index-1])
		if ans_index == real_ans_index:
			print(colored('Correct', 'green'), end=' ')
			correct_count += 1
		else:
			print(colored('Wrong', 'red'), end=' ')
	single_execution_time = calculateExecutionTime(single_start_time, single_end_time)
	print(f'{single_execution_time}ms')
	print('====================')

print(f'Correct: {correct_count}/{number}')
print(correct_count/number*100, '%')


end_time = time.time()
print("average time:", calculateExecutionTime(start_time, end_time) / number,'ms')
