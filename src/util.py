import subprocess
import json
from thefuzz import fuzz

def getWindowId():
	command = ['osascript', '-e', 'tell app "QuickTime Player" to id of window 1']
	process = subprocess.run(command, capture_output=True, text=True)
	return int(process.stdout)

def captureWindow(image_path='tmp/test.jpg', window_id=None):
	capture_command = ['screencapture', '-o', f'-l{window_id}', image_path]
	subprocess.run(capture_command)

def calculateExecutionTime(start_time, end_time):
    return int((end_time - start_time) * 1000)

def splitQuestionAndOptions(text):
    lines = text.strip().split('\n')
    question = ''.join(lines[:-4])
    options = lines[-4:]

    return question, options

    # question = ''
    # lines = text.split('\n')
    # for line in lines:
    #     question += line.strip()
    #     if line.strip().endswith('？'):
    #         options = lines[lines.index(line) + 1:][:4]
    #         return question, options

def json_to_jsonl(input_path, output_path):
    with open(input_path, 'r') as json_file:
        data = json.load(json_file)

    with open(output_path, 'w') as jsonl_file:
        for item in data:
            jsonl_file.write(json.dumps(item, ensure_ascii=False) + '\n')

# from log data to fine_tuning data
def modifyData(data):
	modified_data = {
		'messages':
			[
				{
					'role': 'system',
					'content': '根據問題，回答最可能的答案。（只要回答選項的數字順序以及文字，如：「1. 選項一」。）'
				},
				{
					'role': 'user',
					'content': data['question'] + '\n' + '\n'.join(data['options'])
				},
				{
					'role': 'assistant',
					'content': data['real_ans']+'. '+data['options'][int(data['real_ans'])-1]
				}
			]
	}
	return modified_data

def speak(text, rate=225):
    command = ['say', text, '--rate', str(rate)]
    try:
        process = subprocess.Popen(command)
        process.communicate(timeout=1.5)
    except subprocess.TimeoutExpired:
        process.kill()

# determine if a pixel is a given color with a tolerance
def is_pixel_color_tolerance(pixel, color, tolerance=10):
    return all(abs(pixel[i] - color[i]) < tolerance for i in range(3))

def is_triggered(image):

    # quicktime player
    # trigger_pixel_1 = 466, 140
    # trigger_pixel_2 = 520, 580

    # android emulator Pixel 7 pro
    trigger_pixel_1 = 390, 124
    trigger_pixel_2 = 430, 480

    # guard: index out of range
    if trigger_pixel_1[1] >= image.shape[0] or trigger_pixel_1[0] >= image.shape[1] or trigger_pixel_2[1] >= image.shape[0] or trigger_pixel_2[0] >= image.shape[1]:
        return False

    trigger_pixel_color_1 = image[trigger_pixel_1[1], trigger_pixel_1[0]]
    trigger_pixel_color_2 = image[trigger_pixel_2[1], trigger_pixel_2[0]]


    # BGR
    color1 = (255, 255, 255)
    color2 = (34, 72, 185)

    return is_pixel_color_tolerance(trigger_pixel_color_1, color1, 90) and is_pixel_color_tolerance(trigger_pixel_color_2, color2, 30)

def matchCorrentAnswer(image):
    x = 170
    y = 920
    # x = 80
    # y = 500

    delat_y = 155

    target_color = (141, 168, 26)
    
    if is_pixel_color_tolerance(image[y, x], target_color, 30):
        return 1
    if is_pixel_color_tolerance(image[y + delat_y, x], target_color, 30):
        return 2
    if is_pixel_color_tolerance(image[y + delat_y * 2, x], target_color, 30):
        return 3
    if is_pixel_color_tolerance(image[y + delat_y * 3, x], target_color, 30):
        return 4
    return -1

def matchQuestionFromDatabase(text):
    with open('data/data.json', 'r', encoding='utf8') as file:
        data = json.load(file)

    for item in data:
        if item['question'] == text:
            return item['real_ans']

# TODO: use candidate to find the answer
def matchQuestionFromDatabase(text, data_path='data/data.json', question_score_threshold=90, options_score_threshold=80):
    with open(data_path, 'r', encoding='utf8') as file:
        data = json.load(file)

    question, options = splitQuestionAndOptions(text)
    options_str = ' '.join(options)

    for item in data:
        if (question_score := fuzz.ratio(question, item['question'])) > question_score_threshold:
            if (options_score := fuzz.token_sort_ratio(options_str, ' '.join(item['options']))) > options_score_threshold:
                ans = item['options'][int(item['real_ans'])-1]
                ans_fuzz_score = []
                for option in options:
                    ans_fuzz_score.append(fuzz.ratio(option, ans))
                ans_index = ans_fuzz_score.index(max(ans_fuzz_score)) + 1
                return str(ans_index) + '. ' + ans
            
                
                    

                        
    return None