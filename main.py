import time
import datetime
from termcolor import colored
import argparse
import json
import cv2 as cv


from windowcapture import WindowCapture
import crop
import gpt
import src.ocr as ocr
from src.util import *
from adb import tap


def main():
	parser = argparse.ArgumentParser(description='Quiz Live AI')
	parser.add_argument('--test', action='store_true', help="won't save data to file")
	parser.add_argument('--speech', action='store_true', help="speak the answer out load")

	args = parser.parse_args()

	# window_name = '未命名.mov'
	window_name = 'Android'

	wincap = WindowCapture(window_name)

	input("請按下 Enter 鍵繼續...")
	while True:
		if args.test:
			image_path = 'tmp/test_0.jpg'
		else:
			image_path = 'data/images/' + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + '.jpg'

		# Capture image
		image = wincap.get_image_from_window()

		if not is_triggered(image):
			print(colored('waiting', 'dark_grey'), end='\r', flush=True)
		else:
			print(colored('Triggered', 'dark_grey'), end='\r', flush=True)
			time.sleep(3.25)

			start_time = time.time()

			image = wincap.get_image_from_window()
			print(colored('Captured', 'dark_grey'), end='\r', flush=True)

			# Crop
			cropped_image = crop.crop_image(image)
			print(colored('Cropped', 'dark_grey'), end='\r', flush=True)
			capturing_time = time.time()

			# save image
			cv.imwrite(image_path, cropped_image)

			# OCR
			text = ocr.ocr(image_path)
			ocr_time = time.time()

			question, options = splitQuestionAndOptions(text)
			print(colored(question, 'light_grey'))
			for option in options:
				print(colored(option, 'light_grey'))

			# Match question from database
			if ans_index := matchQuestionFromDatabase(text):
				ans_color = 'blue'
				ans_source = 'database'
				ans_text = options[int(ans_index) - 1]
			else: # GPT
				ans_text = gpt.Anwser(text)
				ans_index = matchOption(ans_text, options)
				ans_color = 'yellow'
				ans_source = 'GPT'
			ans = str(ans_index) + '. ' + ans_text

			# Tap
			try:
				tap(ans_index)
			except ValueError:
				tap(1)

			# IMPORTANT: Print result
			print(colored('\n' + ans + ' \n', ans_color, attrs=['reverse']))
			print(colored(f'from {ans_source}', 'dark_grey'))
			end_time = time.time()

			print(colored(f'截圖時間：{calculateExecutionTime(start_time, capturing_time)} 毫秒', 'dark_grey'))
			print(colored(f'OCR 時間：{calculateExecutionTime(capturing_time, ocr_time)} 毫秒', 'dark_grey'))
			if ans_source == 'GPT':
				print(colored(f'GPT 時間：{calculateExecutionTime(ocr_time, end_time)} 毫秒', 'dark_grey'))
			elif ans_source == 'database':
				print(colored(f'比對時間：{calculateExecutionTime(ocr_time, end_time)} 毫秒', 'dark_grey'))

			execution_time = end_time - start_time

			print(colored(f'執行時間：{calculateExecutionTime(start_time, end_time)} 毫秒', 'dark_grey'))

			if args.speech: speak(ans_text)

			# save data
			if not args.test:
				data_path = 'data/data.json'
			else:
				data_path = 'data/test.json'

			# while time.time() - end_time < 1:
			while True:
				image = wincap.get_image_from_window()
				real_ans = matchCorrentAnswer(image)
				if real_ans != -1:
					if int(ans_index) == real_ans:
						print('正確答案：', colored(real_ans, 'green'))
					else:
						print('正確答案：', colored(real_ans, 'red'))
					break
			print('====================')

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