from time import time
from termcolor import colored
import json
from enum import Enum

from src.util import calculateExecutionTime

class Record:
	def __init__(self):
		pass

	def setAnswerSource(self, source):
		self.source = source

	def isAnswerCorrect(self):
		return int(self.ans[0]) == self.real_ans_index

	def setImagePath(self, image_path):
		self.image_path = image_path

	def setAnswer(self, ans):
		self.ans = ans

	def setLLMResponses(self, responses):
		self.LLM_responses = responses

	def setRealAnswerIndex(self, index):
		self.real_ans_index = index

	def setQuestion(self, question):
		self.question = question

	def setOptions(self, options):
		self.options = options

	def getExecutionTime(self):
		return calculateExecutionTime(self.time_stamps[0].value, self.time_stamps[-1].value) -1250

	def setTimeStamps(self, time_stamps):
		self.time_stamps = time_stamps

	def saveRecord(self, data_path='data.jsonl'):
		item = {
			'image_path': self.image_path,
			'question': self.question,
			'options': self.options,
			'ans': self.ans,
			'ans_source': self.source,
			'real_ans': self.real_ans_index,
			'execution_time': self.getExecutionTime()
		}
		if self.source == 'LLM':
			item['LLM_responses'] = self.LLM_responses

		with open(data_path, 'a', encoding='utf8') as jsonl_file:
			jsonl_file.write(json.dumps(item, ensure_ascii=False) + '\n')

class Dashboard:
	def __init__(self):
		self.records = []

	def cleanRecords(self):
		self.records = []

	def addRecord(self, record: Record):
		self.records.append(record)

	def printScore(self):
		for record in self.records:
			if record.source == 'database':
				attr = 'underline'
			else:
				attr = 'bold'

			if record.isAnswerCorrect():
				print(colored('*', 'green', attrs=[attr]), end=' ')
			else:
				print(colored('*', 'red', attrs=[attr]), end=' ')
		print('\n')

	def printLLMResponses(self):
		record = self.records[-1]
		for response in record.LLM_responses:
			print(format(response['model'], '16s'), format(response['text'], '8s'), format(response['time_elapsed'], '4d'), 'ms')

	def printAnswer(self):
		if self.records[-1].source == 'database':
			ans_color = 'blue'
		else:
			ans_color = 'yellow'

		print(colored('\n' + self.records[-1].ans + ' \n', ans_color, attrs=['reverse']))

	def printSource(self):
		print(colored(f'from {self.records[-1].source}', 'dark_grey'))


	def printRealAnswer(self):
		if self.records[-1].isAnswerCorrect():
			real_ans_color = 'green'
		else:
			real_ans_color = 'red'
		print('正確答案：', colored(self.records[-1].real_ans_index, real_ans_color))


	def printTimes(self):
		record = self.records[-1]
		time_stamps = record.time_stamps

		tags = [TimeTag(index) for index in range(5)]

		if record.source == 'database':
			tags.remove(TimeTag.LLM_QUERYING)
		else:
			tags.remove(TimeTag.DATABASE_MATCHING)

		time_elapses = []
		for index, _ in enumerate(time_stamps[:-1]):
			time_elapses.append(calculateExecutionTime(time_stamps[index].value, time_stamps[index + 1].value))

		time_elapses.append(calculateExecutionTime(time_stamps[0].value, time_stamps[-1].value))

		time_elapses[1] -= 1250
		time_elapses[1] += time_elapses[0]
		time_elapses[3] -= 1250

		for index, time_elapse in enumerate(time_elapses):
			print(format(str(tags[index]), '<24s'), format(time_elapse, '4d'), 'ms')


class TimeTag(Enum):
	QUESTION_CAPTURING = 0
	OPTIONS_CAPTURING = 1
	LLM_QUERYING = 2
	DATABASE_MATCHING = 3
	EXECUTION = 4

	def __str__(self):
		name = ' '.join(x.lower() for x in self.name.split('_')) + ' time'
		return name

class TimeStamp:
	def __init__(self, name):
		self.value = time()
		self.name = name