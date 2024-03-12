import json
import sys

def calculateAccuracyStats(data):
	total = 0
	accurate = 0
	for entry in data:
		if entry['real_ans'] == '':
			continue
		if entry['ans'][0] == str(entry['real_ans']):
			accurate += 1
		total += 1
	return accurate, total

def calculateAverageExecutionTime(data):

	sum = 0
	for entry in data:
		execution_time = entry['execution_time']
		if execution_time < 500 or execution_time > 5000:
			continue
		sum += entry['execution_time']
	return sum / len(data)

def countFromDatabase(data):
	count = 0
	for item in data:
		if item['ans_source'] == 'database':
			count += 1
	return count

def main():
	try:
		number = int(sys.argv[1])
	except:
		number = 1000

	data = []
	with open('data/data.jsonl', 'r', encoding='utf8') as file:
		data = [json.loads(line) for line in file][-number:]

	accurate, total = calculateAccuracyStats(data)
	print(f'Accuracy: {accurate}/{total} ({accurate/total*100:.2f}%)')
	print(f'Average Execution Time: {calculateAverageExecutionTime(data):.2f} ms')
	print(f'from database: {countFromDatabase(data)/len(data)*100:.2f} %' )

if __name__ == '__main__':
	main()