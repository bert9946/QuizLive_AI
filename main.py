import time
import datetime
from termcolor import colored
import argparse
import json
import cv2 as cv


from windowcapture import WindowCapture
import gpt
from gemini import Gemini
from src.ocr import image2text
from src.util import *
from adb import *
from dashboard import Dashboard


def main():
	parser = argparse.ArgumentParser(description='Quiz Live AI')
	parser.add_argument('--test', action='store_true', help="won't save data to file")
	parser.add_argument('--speech', action='store_true', help="speak the answer out load")
	parser.add_argument('-c', '--continuous', action='store_true', help="continuous mode")
	parser.add_argument('--stage-master', action='store_true', help="match stage master")
	parser.add_argument("--llm", help="language model to use", dest="llm", default="gpt")


	args = parser.parse_args()

	window_name = 'Android'
	wincap = WindowCapture(window_name)

	dashboard = Dashboard()
	gemini = Gemini()

	isInMatch = False
	x = 0

	while True:
		if args.test:
			image_path = 'tmp/test_0.jpg'
		else:
			time_stamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
			image_path = 'data/images/' + time_stamp + '.jpg'

		# Capture image
		image = wincap.get_image_from_window()

		# Check if in match
		if matchImage('assets/display_name.jpg', image, crop_coords=(75, 270, 105, 45)):
			isInMatch = True
			x = 0
		else:
			x += 1
			if x > 120:
				isInMatch = False
				dashboard.cleanRecords()

		if args.continuous:
			if not isInMatch:
				if button := matchImage('assets/Find_new_opponent.jpg', image, crop_coords=(87, 1326, 130, 40)):
					simulateTap(button[0], button[1])
					time.sleep(1)
				if matchImage('assets/acquire.jpg', image, crop_coords=(40, 310, 270, 70)):
					if button := matchImage('assets/confirm_2.jpg', image):
						simulateTap(button[0], button[1])
						time.sleep(1)
				if button := matchImage('assets/level_up.jpg', image, crop_coords=(190, 660, 360, 140)):
					simulateTap(button[0], button[1])
					time.sleep(1)

				if args.stage_master:
					if button := matchImage('assets/match_again.jpg', image, crop_coords=(87, 1326, 130, 40)):
						simulateTap(button[0], button[1])
						time.sleep(1)
					if matchImage('assets/free_trial.jpg', image, crop_coords=(290, 507, 150, 40)):
						if button := matchImage('assets/dont_show_for_today.jpg', image, crop_coords=(60, 1440, 200, 40)):
							simulateTap(button[0], button[1])
							time.sleep(2)
					if button := matchImage('assets/confirm_4.jpg', image, crop_coords=(420, 850, 150, 50)):
						simulateTap(button[0], button[1])
						time.sleep(1)
					if button := matchImage('assets/confirm.jpg', image, crop_coords=(545, 943, 77, 44)):
						simulateTap(button[0], button[1])
						time.sleep(1)
					if button := matchImage('assets/master_beaten.jpg', image, crop_coords=(240, 1300, 250, 70)):
						simulateTap(button[0], button[1])
						time.sleep(1)
					if button := matchImage('assets/circle_2.jpg', image, mask_image_path='assets/circle_mask_2.jpg', crop_coords=(90, 370, 554, 907), threshold=0.65):
						simulateTap(button[0], button[1])
						time.sleep(1)
					if matchImage('assets/hint.jpg', image, crop_coords=(327, 505, 77, 45)):
						if button := matchImage('assets/close.jpg', image, crop_coords=(560, 506, 27, 24)):
							simulateTap(button[0], button[1])
							time.sleep(1)
					if matchImage('assets/trophy.jpg', image, crop_coords=(460, 640, 70, 60)):
						if button := matchImage('assets/confirm_3.jpg', image, crop_coords=(440, 945, 110, 40)):
							simulateTap(button[0], button[1])
							time.sleep(1)
					if button := matchImage('assets/stage_completed.jpg', image, crop_coords=(160, 680, 420, 120)):
						simulateTap(button[0], button[1])
						time.sleep(1)


		if not is_triggered(image):
			print(colored('waiting', 'dark_grey'), end='\r', flush=True)
		else:
			print(colored('Triggered', 'dark_grey'), end='\r', flush=True)
			with open('data/data.jsonl', 'r', encoding='utf8') as file:
				data = [json.loads(line) for line in file]
			time.sleep(3.25)

			start_time = time.time()

			image = wincap.get_image_from_window()
			print(colored('Captured', 'dark_grey'), end='\r', flush=True)

			# Crop
			cropped_image = crop_image(image)
			cropped_image = cv.cvtColor(cropped_image, cv.COLOR_BGR2GRAY)
			print(colored('Cropped', 'dark_grey'), end='\r', flush=True)
			capturing_time = time.time()

			# OCR
			text = image2text(cropped_image)
			ocr_time = time.time()

			question, options = splitQuestionAndOptions(text)
			print(colored(question, 'light_grey'))
			for option in options:
				print(colored(option, 'light_grey'))

			# Match question from database
			if ans_index := matchQuestionFromDatabase(text, data):
				ans_color = 'blue'
				ans_source = 'database'
				ans_text = options[int(ans_index) - 1]
			else: # LLM
				if args.llm == 'gpt':
					ans_text = gpt.Answer(text)
					ans_color = 'yellow'
					ans_source = 'GPT'
				elif args.llm == 'gemini':
					try:
						ans_text = gemini.Answer(text)
					except Exception:
						ans_text = 'None'
					ans_color = 'yellow'
					ans_source = 'Gemini'
				ans_index = matchOption(ans_text, options)
			ans = str(ans_index) + '. ' + ans_text

			# Tap
			try:
				tapOption(ans_index)
			except ValueError:
				tapOption(1)

			# IMPORTANT: Print result
			print(colored('\n' + ans + ' \n', ans_color, attrs=['reverse']))
			print(colored(f'from {ans_source}', 'dark_grey'))
			end_time = time.time()

			print(colored(f'截圖時間：{calculateExecutionTime(start_time, capturing_time)} 毫秒', 'dark_grey'))
			print(colored(f'OCR 時間：{calculateExecutionTime(capturing_time, ocr_time)} 毫秒', 'dark_grey'))
			if ans_source in ['GPT', 'Gemini']:
				print(colored(f'LLM 時間：{calculateExecutionTime(ocr_time, end_time)} 毫秒', 'dark_grey'))
			elif ans_source == 'database':
				print(colored(f'比對時間：{calculateExecutionTime(ocr_time, end_time)} 毫秒', 'dark_grey'))

			execution_time = end_time - start_time

			print(colored(f'執行時間：{calculateExecutionTime(start_time, end_time)} 毫秒', 'dark_grey'))

			if args.speech: speak(ans_text)

			print('正確答案：..', end='\r', flush=True)
			while True:
				image = wincap.get_image_from_window()
				real_ans = matchCorrentAnswer(image)
				if real_ans != -1:
					if int(ans_index) == real_ans:
						real_ans_color = 'green'
						dashboard.addRecord(True, ans_source)
					else:
						real_ans_color = 'red'
						dashboard.addRecord(False, ans_source)
					print('正確答案：', colored(real_ans, real_ans_color))
					break
			print('====================')
			dashboard.printRecords()

			# save data
			if args.test:
				data_path = 'data/test.jsonl'
			else:
				data_path = 'data/data.jsonl'

			# save image
			cv.imwrite(image_path, cropped_image)

			item = {
				'image_path': image_path,
				'question': question,
				'options': options,
				'ans': ans,
				'ans_source': ans_source,
				'real_ans': real_ans,
				'execution_time': int(execution_time * 1000)
			}

			with open(data_path, 'a') as jsonl_file:
				jsonl_file.write(json.dumps(item, ensure_ascii=False) + '\n')


if __name__ == '__main__':
	main()