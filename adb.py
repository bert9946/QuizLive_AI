import subprocess

def adb(command):
	return subprocess.run(['/Users/bert9946/Library/Android/sdk/platform-tools/adb'] + command, capture_output=True, text=True).stdout

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