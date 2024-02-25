import subprocess

def adb(command):
	return subprocess.run(['/Users/bert9946/Library/Android/sdk/platform-tools/adb'] + command, capture_output=True, text=True).stdout

# command = ['shell', 'input', 'tap', '1000', '2700']

def simulateTap(x, y):
	command = ['shell', 'input', 'tap', str(x), str(y)]
	adb(command)

def tapOption(option_index):
	if option_index not in [1, 2, 3, 4]:
		raise ValueError('option must be 1, 2, 3, or 4')
	x = 850
	y = 1750
	delta_y = 330

	simulateTap(x, y + delta_y * (option_index - 1))

# tap('1') # tap the first option
# simulateTap(1000, 2700) # tap the middle of the screen

# while True:
# 	option = input('Press Enter to tap: ')
# 	tap(option) # tap the first option
