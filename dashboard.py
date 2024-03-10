from time import time
from termcolor import colored
import json

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
		return calculateExecutionTime(self.time_stamps[0].value, self.time_stamps[-1].value)

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

		with open(data_path, 'a') as jsonl_file:
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
		time_elapses = []
		tags = ['截圖時間', 'OCR 時間', 'LLM 時間', '執行時間']
		if self.records[-1].source == 'database':
			tags[2] = '比對時間'

		time_stamps = self.records[-1].time_stamps
		for index, _ in enumerate(time_stamps[:-1]):
			time_elapses.append(calculateExecutionTime(time_stamps[index].value, time_stamps[index + 1].value))

		time_elapses.append(calculateExecutionTime(time_stamps[0].value, time_stamps[-1].value))

		for index, time_elapse in enumerate(time_elapses):
			print(tags[index], format(time_elapse, '4d'), '毫秒')


class TimeStamp:
	def __init__(self, name):
		self.value = time()
		self.name = name