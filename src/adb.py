import subprocess

def adb(command):
	return subprocess.run(['/Users/bert9946/Library/Android/sdk/platform-tools/adb'] + command, capture_output=True, text=True).stdout

def simulateTap(coord):
	command = ['shell', 'input', 'tap', str(coord[0]), str(coord[1])]
	adb(command)

def tapOption(option_index):
	if option_index not in [1, 2, 3, 4]:
		raise ValueError('option must be 1, 2, 3, or 4')
	coord = (850, 1750)
	delta_y = 330

	simulateTap((coord[0], coord[1] + delta_y * (option_index - 1)))