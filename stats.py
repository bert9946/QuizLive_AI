import json

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



def main():
	data = []
	with open('data/data.jsonl', 'r', encoding='utf8') as file:
		for line in file:
			data.append(json.loads(line))
	accurate, total = calculateAccuracyStats(data)
	print(f'Accuracy: {accurate}/{total} ({accurate/total*100:.2f}%)')
	print(f'Average Execution Time: {calculateAverageExecutionTime(data):.2f} ms')

if __name__ == '__main__':
	main()