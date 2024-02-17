from src.util import *
import json
from collections import defaultdict


def checkFormatVadility(dataset):
	# Format error checks
	format_errors = defaultdict(int)

	for ex in dataset:
		if not isinstance(ex, dict):
			format_errors["data_type"] += 1
			continue

		messages = ex.get("messages", None)
		if not messages:
			format_errors["missing_messages_list"] += 1
			continue

		for message in messages:
			if "role" not in message or "content" not in message:
				format_errors["message_missing_key"] += 1

			if any(k not in ("role", "content", "name", "function_call") for k in message):
				format_errors["message_unrecognized_key"] += 1

			if message.get("role", None) not in ("system", "user", "assistant", "function"):
				format_errors["unrecognized_role"] += 1

			content = message.get("content", None)
			function_call = message.get("function_call", None)

			if (not content and not function_call) or not isinstance(content, str):
				format_errors["missing_content"] += 1

		if not any(message.get("role", None) == "assistant" for message in messages):
			format_errors["example_missing_assistant_message"] += 1

	if format_errors:
		print("Found errors:")
		for k, v in format_errors.items():
			print(f"{k}: {v}")
	else:
		print("No errors found")


def generateFineTuningData(raw_data_path, fine_tuning_data_path):
	with open(raw_data_path, 'r', encoding='utf8') as file:
		dataset = [json.loads(line) for line in file]

	with open(fine_tuning_data_path, 'w', encoding='utf8') as file:
		for data in dataset[50:60]:
			if data['real_ans'] == '':
				continue
			data = modifyData(data)
			file.write(json.dumps(data, ensure_ascii=False) + '\n')

def main():
	generateFineTuningData('data/data.jsonl', 'data/fine_tuning_validate.jsonl')


	# with open('data/fine_tuning.jsonl', 'r', encoding='utf8') as file:
	# 	dataset = [json.loads(line) for line in file]
	# checkFormatVadility(dataset)


if __name__ == '__main__':
	main()