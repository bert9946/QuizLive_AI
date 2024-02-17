from src.ocr import *

def test_ocr():
	text = ocr('images/test_1_cropped.jpg')
	assert text != ''
	assert len(text) > 0
	assert len(text) < 1000
