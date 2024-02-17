import subprocess

def ocr(image):
	#if image is str
	if not isinstance(image, str):
		image.save('tmp/tmp.jpg')
		command = ['./macocr_1', 'tmp/tmp.jpg']
	else:
		command = ['./macocr_1', image]
	process = subprocess.run(command, capture_output=True, text=True)
	return process.stdout
