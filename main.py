import time
import datetime
from termcolor import colored
import argparse
import json
import asyncio

import crop
import gpt
import src.ocr as ocr
from src.util import *


def main():
	parser = argparse.ArgumentParser(description='Quiz Live AI')
	parser.add_argument('--test', action='store_true', help="won't save data to file")
	parser.add_argument('--speech', action='store_true', help="speak the answer out load")

	args = parser.parse_args()

	windowId = getWindowId()

	input("請按下 Enter 鍵繼續...")
	while True:
		print('====================')

		start_time = time.time()

		if args.test:
			image_path = 'tmp/test_0.jpg'
		else:
			image_path = 'data/images/' + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + '.jpg'

		#Capture image
		captureWindow(image_path, windowId)

		capturing_time = time.time()

		#Crop
		cropped_image = crop.crop_image(image_path)

		#save image
		cropped_image.save(image_path)

		cropping_time = time.time()

		#OCR
		text = ocr.ocr(image_path)
		print(text)

		ocr_time = time.time()


		#GPT
		ans = gpt.Anwser(text)

		# IMPORTANT!!
		#Print result
		print(colored(ans + ' \n', 'red', attrs=['reverse']))


		end_time = time.time()
		print(colored(f'截圖時間: {calculateExecutionTime(start_time, capturing_time)} 毫秒', 'dark_grey'))
		print(colored(f'裁剪時間: {calculateExecutionTime(capturing_time, cropping_time)} 毫秒', 'dark_grey'))
		print(colored(f'OCR 時間: {calculateExecutionTime(cropping_time, ocr_time)} 毫秒', 'dark_grey'))
		print(colored(f'GPT 時間: {calculateExecutionTime(ocr_time, end_time)} 毫秒', 'dark_grey'))

		execution_time = end_time - start_time

		print(colored(f'執行時間: {calculateExecutionTime(start_time, end_time)} 毫秒', 'dark_grey'))

		question, options = splitQuestionAndOptions(text)

		if args.speech: speak(ans[2:])


		real_ans = input("正確答案： ")

		#save data

		if not args.test:
			data_path = 'data/data.json'
		else:
			data_path = 'data/test.json'

		with open(data_path, 'r', encoding='utf8') as file:
			obj = json.load(file)

		data = {
			'image_path': image_path,
			'question': question,
			'options': options,
			'ans': ans,
			'real_ans': real_ans,
			'execution_time': int(execution_time * 1000)
		}
		obj.append(data)

		with open(data_path, 'w', encoding='utf8') as file:
			json.dump(obj, file, indent=4, ensure_ascii=False)
			file.write('\n')

if __name__ == '__main__':
	main()