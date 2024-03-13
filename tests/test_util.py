from src.util import *

def test_calculateExecutionTime():
	start_time = 0
	end_time = 1
	result = calculateExecutionTime(start_time, end_time)
	assert result == 1000

def test_splitQuestionAndOptions():
	text1 = (
		'常見的人造纖維\n'
		'「Polyester」的中文是？\n'
		'酚醛樹脂\n'
		'聚異丁烯\n'
		'聚醯亞胺\n'
		'聚酯纖維\n'
	)

	question1, options1 = splitQuestionAndOptions(text1)
	assert question1 == '常見的人造纖維「Polyester」的中文是？'
	assert options1 == ['酚醛樹脂', '聚異丁烯', '聚醯亞胺', '聚酯纖維']

def test_matchOption():
	text = 'c'
	options = ['a', 'b', 'c', 'd']
	ans = matchOption(text, options)
	assert ans == 3

def test_processQuestion():
	text = '''請問網球選手 Novak
Djokovic 是哪一國人？'''
	result = processQuestion(text)
	assert result == '請問網球選手 Novak Djokovic 是哪一國人？'
