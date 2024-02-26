from src.ocr import *

def test_ocr():
	result = detect_text('images/test_1_cropped.jpg')
	text = '\n'.join([i[0] for i in result])
	assert text != ''
	assert len(text) > 0
	assert len(text) < 1000
