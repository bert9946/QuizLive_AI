from termcolor import colored

class Dashboard:
	def __init__(self):
		self.records = []

	def cleanRecords(self):
		self.records = []

	def addRecord(self, is_correct: bool, source):
		self.records.append(record(is_correct, source))

	def printRecords(self):
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

class record:
	def __init__(self, is_correct, source):
		self.is_correct = is_correct
		self.source = source