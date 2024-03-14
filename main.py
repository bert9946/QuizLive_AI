import time
import datetime
from termcolor import colored, cprint
import argparse
import json
import cv2 as cv
import asyncio

from src.LLMs import Answer, vote

from src.gemini import Gemini_Model
from src.gpt import GPT_Model
from src.claude import Claude_Model

from src.windowcapture import WindowCapture
from src.ocr import image2text
from src.util import *
from src.adb import *
from src.dashboard import Dashboard, Record, TimeStamp


async def main():
	parser = argparse.ArgumentParser(description='Quiz Live AI')
	parser.add_argument('--test', action='store_true', help="won't save data to file")
	parser.add_argument('-c', '--continuous', action='store_true', help="continuous mode")
	parser.add_argument('--stage-master', action='store_true', help="match stage master")

	args = parser.parse_args()

	window_name = 'Android'
	wincap = WindowCapture(window_name)

	dashboard = Dashboard()
	MODELS = [Gemini_Model.GEMINI_PRO,
				Claude_Model.CLAUDE_3_SONNET,
				# Claude_Model.CLAUDE_3_OPUS,
				GPT_Model.GPT_3_5_TURBO,
				# GPT_Model.GPT_4_TURBO
	]
	timeout = 3.0

	isInMatch = False
	x = 0

	templates = []
	template_paths = ['assets/Find_new_opponent.jpg', 'assets/confirm_2.jpg', 'assets/level_up.jpg']
	for template_path in template_paths:
		templates.append(cv.imread(template_path, cv.IMREAD_GRAYSCALE))
	display_name_image = cv.imread('assets/display_name.jpg', cv.IMREAD_GRAYSCALE)

	if args.test:
		data_path = 'data/test.jsonl'
	else:
		data_path = 'data/data.jsonl'

	while True:
		time_stamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

		if args.test:
			image_path = 'tmp/test_0.jpg'
		else:
			image_path = 'data/images/' + time_stamp + '.jpg'

		# Capture image
		image = wincap.get_image_from_window()

		# Check if in match
		if matchImage(display_name_image, image, crop_coords=(75, 270, 105, 45)):
			isInMatch = True
			x = 0
		else:
			x += 1
			if x > 120:
				isInMatch = False
				dashboard.cleanRecords()

		if args.continuous:
			if not isInMatch:
				for template in templates:
					if button := matchImage(template, image):
						simulateTap(button)
						time.sleep(1)

				if args.stage_master:
					if button := matchImage('assets/match_again.jpg', image, crop_coords=(87, 1326, 130, 40)):
						simulateTap(button)
						time.sleep(1)
					if matchImage('assets/free_trial.jpg', image, crop_coords=(290, 507, 150, 40)):
						if button := matchImage('assets/dont_show_for_today.jpg', image, crop_coords=(60, 1440, 200, 40)):
							simulateTap(button)
							time.sleep(2)
					if button := matchImage('assets/confirm_4.jpg', image, crop_coords=(420, 850, 150, 50)):
						simulateTap(button)
						time.sleep(1)
					if button := matchImage('assets/confirm.jpg', image, crop_coords=(545, 943, 77, 44)):
						simulateTap(button)
						time.sleep(1)
					if button := matchImage('assets/master_beaten.jpg', image, crop_coords=(240, 1300, 250, 70)):
						simulateTap(button)
						time.sleep(1)
					if button := matchImage('assets/circle_2.jpg', image, mask_image_path='assets/circle_mask_2.jpg', crop_coords=(90, 370, 554, 907), threshold=0.65):
						simulateTap(button)
						time.sleep(1)
					if matchImage('assets/hint.jpg', image, crop_coords=(327, 505, 77, 45)):
						if button := matchImage('assets/close.jpg', image, crop_coords=(560, 506, 27, 24)):
							simulateTap(button)
							time.sleep(1)
					if matchImage('assets/trophy.jpg', image, crop_coords=(460, 640, 70, 60)):
						if button := matchImage('assets/confirm_3.jpg', image, crop_coords=(440, 945, 110, 40)):
							simulateTap(button)
							time.sleep(1)
					if button := matchImage('assets/stage_completed.jpg', image, crop_coords=(160, 680, 420, 120)):
						simulateTap(button)
						time.sleep(1)


		if not is_triggered(image):
			print(colored('waiting', 'dark_grey'), end='\r', flush=True)
		else:
			with open('data/data.jsonl', 'r', encoding='utf8') as file:
				data = [json.loads(line) for line in file]

			time_stamps = []
			print(colored('Triggered', 'dark_grey'), end='\r', flush=True)
			await asyncio.sleep(2)

			time_stamps.append(TimeStamp('start_time'))
			# Capture question
			image = wincap.get_image_from_window()
			image = preprocess_image(image)
			question_image = image[:300, :]
			question = await image2text(question_image)
			question = processQuestion(question)

			time_stamps.append(TimeStamp('question_capturing_time'))
			question_capturing_time = time_stamps[-1].value - time_stamps[-2].value
			await asyncio.sleep(1.25-question_capturing_time)


			# Capture options
			complete_image = wincap.get_image_from_window()
			print(colored('Captured', 'dark_grey'), end='\r', flush=True)
			image = preprocess_image(complete_image)
			option_images = [image[380+i*160:508+i*160, 30:450] for i in range(4)]

			tasks = [image2text(image) for image in option_images]
			options = await asyncio.gather(*tasks)
			time_stamps.append(TimeStamp('options_capturing_time'))

			text = combineQuestionAndOptions(question, options)

			record = Record()
			record.setQuestion(question)
			record.setOptions(options)

			cprint(text, 'light_grey')

			# Match question from database
			if ans_index := matchQuestionFromDatabase(text, data):
				ans_source = 'database'
			else: # LLM
				responses = await Answer(text, models=MODELS, timeout=timeout)
				record.setLLMResponses(responses)
				ans_index = vote(responses, options)
				ans_source = 'LLM'
			ans_text = options[ans_index - 1]
			ans = str(ans_index) + '. ' + ans_text
			record.setAnswer(ans)
			record.setAnswerSource(ans_source)

			time_stamps.append(TimeStamp('end_time'))

			# Tap
			try:
				tapOption(ans_index)
			except ValueError:
				tapOption(1)

			record.setTimeStamps(time_stamps)
			dashboard.addRecord(record)

			dashboard.printAnswer()
			if ans_source == 'LLM':
				dashboard.printLLMResponses()
			dashboard.printSource()
			dashboard.printTimes()

			print('正確答案：..', end='\r', flush=True)
			while True:
				image = wincap.get_image_from_window()
				if is_triggered(image):
					dashboard.records[-1].setRealAnswerIndex(-1)
					break
				real_ans_index = matchCorrentAnswer(image)
				if real_ans_index != 0:
					dashboard.records[-1].setRealAnswerIndex(real_ans_index)
					dashboard.printRealAnswer()
					break
			print('====================')
			dashboard.printScore()

			# Save image
			cv.imwrite(image_path, preprocess_image(complete_image))

			record.setImagePath(image_path)
			record.saveRecord(data_path)

if __name__ == '__main__':
	asyncio.run(main())