import subprocess
import json
import random
from thefuzz import fuzz
import cv2 as cv


def captureWindow(image_path='tmp/test.jpg', window_id=None):
    capture_command = ['screencapture', '-o', f'-l{window_id}', image_path]
    subprocess.run(capture_command)

def crop_image(image):
	h, w = image.shape[:2]
	return image[int(h*.3):int(h*.9), int(w*0.17):int(w*0.84)]

def calculateExecutionTime(start_time, end_time):
    return int((end_time - start_time) * 1000)

def splitQuestionAndOptions(text):
    lines = text.strip().split('\n')
    question = ''.join(lines[:-4])
    options = lines[-4:]
    return question, options

def combineQuestionAndOptionsFromItem(item):
	return combineQuestionAndOptions(item['question'], item['options'])

def combineQuestionAndOptions(question, options):
    return question + '\n' + '\n'.join(options)

def json_to_jsonl(input_path, output_path):
    with open(input_path, 'r') as json_file:
        data = json.load(json_file)

    with open(output_path, 'w') as jsonl_file:
        for item in data:
            jsonl_file.write(json.dumps(item, ensure_ascii=False) + '\n')

# determine if a pixel is a given color with a tolerance
def is_pixel_color_tolerance(pixel, color, tolerance=10):
    return all(abs(pixel[i] - color[i]) < tolerance for i in range(3))

def is_triggered(image):

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
    delat_y = 155

    if image.shape[0] < y + delat_y * 3:
        return -1
    if image.shape[1] < x:
        return -1

    target_color = (141, 168, 26)
    tolerance = 50

    for i in range(4):
        if is_pixel_color_tolerance(image[y + delat_y * i, x], target_color, tolerance):
            return i + 1
    return -1

def matchQuestionFromDatabase(text, data, question_score_threshold=95, options_score_threshold=80):
    question, options = splitQuestionAndOptions(text)
    options_str = ' '.join(options)

    candidates = []
    for item in data:
        if isItemValid(item):
            if (question_score := fuzz.ratio(question, item['question'])) > question_score_threshold:
                if (options_score := fuzz.token_sort_ratio(options_str, ' '.join(item['options']))) > options_score_threshold:
                    item['question_score'] = question_score
                    item['options_score'] = options_score
                    candidates.append(item)
                    if question_score == 100 and options_score == 100:
                        break

    if candidates == []:
        return None

    # find the candidate of quesiton with the highest score
    question_options_score = []
    for candidate in candidates:
        question_options_score.append(candidate['question_score'] + candidate['options_score'])

    max_score_index = question_options_score.index(max(question_options_score))
    target = candidates[max_score_index]

    # find the option with the highest score
    ans = target['options'][int(target['real_ans'])-1]
    return matchOption(ans, options)

def isItemValid(item):
    return item['real_ans'] in [1, 2, 3, 4] and len(item['options']) == 4 and item['question'] != ''

def randomPickItem(data):
    while True:
        if isItemValid(item := random.choice(data)):
            return item

def matchOption(text: str, options: list[str]) -> int:
    if text == '' or options == []:
        return -1
    ans_fuzz_score = []
    for option in options:
        ans_fuzz_score.append(fuzz.ratio(text, option))
    ans_index = ans_fuzz_score.index(max(ans_fuzz_score)) + 1
    return ans_index


def matchImage(needle_image, haystack_image, mask_image_path=None, crop_coords=None, threshold=0.9):
    if mask_image_path:
        mask_image = cv.imread(mask_image_path, cv.IMREAD_GRAYSCALE)
    else:
        mask_image = None
    if crop_coords:
        x, y, w, h = crop_coords
        haystack_image = haystack_image[y:y+h, x:x+w]
    else: x, y = 0, 0

    try:
        haystack_image = cv.cvtColor(haystack_image, cv.COLOR_BGR2GRAY)
        result = cv.matchTemplate(haystack_image, needle_image, cv.TM_CCOEFF_NORMED, mask=mask_image)
    except cv.error:
        return None

    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    button_w, button_h = needle_image.shape[:2][::-1]
    if max_val >= threshold:
        return max_loc[0] * 2 + button_w + x * 2, max_loc[1] * 2 + button_h + y * 2
    return None