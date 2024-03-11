import cv2 as cv
import random
import json

from src.ocr import *
from src.util import splitQuestionAndOptions

async def test_ocr():
	with open('data/data.jsonl', 'r', encoding='utf8') as file:
		data = [json.loads(line) for line in file]

	item = random.choice(data)

	image_path = item['image_path']
	image = cv.imread(image_path, cv.IMREAD_GRAYSCALE)

	text = await image2text(image)

	question, options = splitQuestionAndOptions(text)

	assert question == item['question']
	assert options == item['options']