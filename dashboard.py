from time import time
from termcolor import colored, cprint
from src.util import calculateExecutionTime

class Dashboard:
	def __init__(self):
		self.records = []

	def cleanRecords(self):
		self.records = []

	def addRecord(self, is_correct: bool, source):
		self.records.append(record(is_correct, source))

	def printScore(self):
		for record in self.records:
			if record.source == 'database':
				attr = 'underline'
			else:
				attr = 'bold'

			if record.is_correct:
				print(colored('*', 'green', attrs=[attr]), end=' ')
			else:
				print(colored('*', 'red', attrs=[attr]), end=' ')
		print('\n')

	def printRealAnswer(self, real_ans_index: int):
		if self.records[-1].is_correct:
			real_ans_color = 'green'
		else:
			real_ans_color = 'red'
		print('正確答案：', colored(real_ans_index, real_ans_color))


	def printTimes(self, time_stamps):
		time_elapses = []
		tags = ['截圖時間', 'OCR 時間', 'LLM 時間', '執行時間']

		for index, _ in enumerate(time_stamps[:-1]):
			time_elapses.append(calculateExecutionTime(time_stamps[index].value, time_stamps[index + 1].value))

		time_elapses.append(calculateExecutionTime(time_stamps[0].value, time_stamps[-1].value))

		for index, time_elapse in enumerate(time_elapses):
			print(tags[index], format(time_elapse, '4d'), '毫秒')


class record:
	def __init__(self, is_correct, source):
		self.is_correct = is_correct
		self.source = source

class TimeStamp:
	def __init__(self, name):
		self.value = time()
		self.name = name