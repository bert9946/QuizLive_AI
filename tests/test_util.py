from src.util import *

def test_getWindowId():
	result = getWindowId()
	assert isinstance(result, int)
	assert result > 0

def test_calculateExecutionTime():
	start_time = 0
	end_time = 1
	result = calculateExecutionTime(start_time, end_time)
	assert result == 1000

def test_splitQuestionAndOptions():
	text1 = '''常見的人造纖維
「Polyester」的中文是？
酚醛樹脂
聚異丁烯
聚醯亞胺
聚酯纖維
'''

	text2 = '''這個問題
沒有問號
選項一
選項二
選項三
選項四'''

	question1, options1 = splitQuestionAndOptions(text1)
	assert question1 == '常見的人造纖維「Polyester」的中文是？'
	assert options1 == ['酚醛樹脂', '聚異丁烯', '聚醯亞胺', '聚酯纖維']

	# question2, options2 = splitQuestionAndOptions(text2)
	# assert question2 == '這個問題沒有問號'
	# assert options2 == ['選項一', '選項二', '選項三', '選項四']

def test_modifyData():
	data = {
		"image_path": "data/images/2024-02-17-16-22-52.jpg",
		"question": "下列何者不是「元代四大畫家」之一？",
		"options": [
			"倪匡",
			"吳鎮",
			"黃公望",
			"王蒙"
		],
		"ans": "1. 倪匡",
		"real_ans": "1",
		"execution_time": 1250
	}
	expected_result = {
		'messages':
			[
				{
					'role': 'system',
					'content': '根據問題，回答最可能的答案。（只要回答選項的數字順序以及文字，如：「1. 選項一」。）'
				},
				{
					'role': 'user',
					'content': "下列何者不是「元代四大畫家」之一？倪匡\n吳鎮\n黃公望\n王蒙"
				},
				{
					'role': 'assistant',
					'content': '1. 倪匡'
				}
			]
	}
	assert modifyData(data) == expected_result
