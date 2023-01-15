import numpy as np
from PIL import Image
import subprocess
import re
from time import sleep
from datetime import datetime
import os
# import pyotp

try:
	ld_path = open('bin\\ld_path.txt', 'r').read()
except:
	ld_path = 'D:\\XuanZhi\\LDPlayer'

# button = {}
# button['like'] = Image.open('bin/images/like.png')
# button['heart'] = Image.open('bin/images/heart.png')
# button['share'] = Image.open('bin/images/share.png')
# button['comment'] = Image.open('bin/images/comment.png')
# button['send_comment'] = Image.open('bin/images/send_comment.png')

CREATE_NO_WINDOW = 0x08000000

def get_list_ld():
	proc = subprocess.Popen(ld_path + '/dnconsole.exe list2', shell=True, stdout =subprocess.PIPE, creationflags=CREATE_NO_WINDOW)
	serviceList = proc.communicate()[0].decode('ascii').split('\n')

	list_ld = []
	for i in range(len(serviceList)):
		serviceList[i] = serviceList[i].split(',')
		if len(serviceList[i][0]) > 0:
			list_ld.append(serviceList[i][1])
	return list_ld

def open_ld(ld_name):
	subprocess.call(ld_path + '/dnconsole.exe launch --name '+ld_name, shell=True, creationflags=CREATE_NO_WINDOW)

def quit_ld(ld_name):
	subprocess.call(ld_path + '/dnconsole.exe quit --name '+ld_name, shell=True, creationflags=CREATE_NO_WINDOW)

def quit_all_ld():
	subprocess.call(ld_path + '/dnconsole.exe quitall', shell=True, creationflags=CREATE_NO_WINDOW)

def create_ld(ld_name):
	subprocess.call(ld_path + '/dnconsole.exe add --name '+ld_name, shell=True, creationflags=CREATE_NO_WINDOW)

def clone_ld(ld_name, ld_name0):
	subprocess.call(ld_path + '/dnconsole.exe copy --name '+ld_name+' --from '+ld_name0, shell=True, creationflags=CREATE_NO_WINDOW)

def remove_ld(ld_name):
	subprocess.call(ld_path + '/dnconsole.exe remove --name '+ld_name, shell=True, creationflags=CREATE_NO_WINDOW)

def setup_ld(ld_name):
	subprocess.call(ld_path + '/dnconsole.exe modify --name '+ld_name+' --resolution 540,960,240 --cpu 1 --memory 1024 --imei auto', shell=True, creationflags=CREATE_NO_WINDOW)

def get_list_devices():
	proc = subprocess.Popen('ADB\\adb.exe devices', shell=True, stdout =subprocess.PIPE, creationflags=CREATE_NO_WINDOW)
	serviceList = proc.communicate()[0].decode('ascii').split('\n')

	list_device = []
	for i in range(1, len(serviceList)-2):
		try:
			device = serviceList[i].split('\t')[0]
			list_device.append(device)
		except:
			pass
	return list_device

def open_facebook(device):
	subprocess.call('ADB\\adb.exe -s '+device+' shell monkey -p com.facebook.katana -c android.intent.category.LAUNCHER 1', shell=True, creationflags=CREATE_NO_WINDOW)

def close_facebook(device):
	subprocess.call('ADB\\adb.exe -s '+device+' shell am force-stop com.facebook.katana', shell=True, creationflags=CREATE_NO_WINDOW)

def open_facebook_link(device, link):
	subprocess.call('ADB\\adb.exe -s '+device+' shell am start -W -a android.intent.action.VIEW -d fb://faceweb/f?href='+link, shell=True, creationflags=CREATE_NO_WINDOW)

def open_facebook_home(device):
	subprocess.call('ADB\\adb.exe -s '+device+' shell am start -d fb://feed', shell=True, creationflags=CREATE_NO_WINDOW)

def swipe(device, x1 = 400, y1 = 900, x2 = 400, y2 = 120, duration = 1000):
	subprocess.call('ADB\\adb.exe -s '+device+' shell input swipe '+str(x1)+' '+str(y1)+' '+str(x2)+' '+str(y2)+' '+str(duration), shell=True, creationflags=CREATE_NO_WINDOW)

def find_image(im, tpl):
	im = np.atleast_3d(im)
	tpl = np.atleast_3d(tpl)
	H, W, D = im.shape[:3]
	h, w = tpl.shape[:2]

	sat = im.cumsum(1).cumsum(0)
	tplsum = np.array([tpl[:, :, i].sum() for i in range(D)])

	iA, iB, iC, iD = sat[:-h, :-w], sat[:-h, w:], sat[h:, :-w], sat[h:, w:] 
	lookup = iD - iB - iC + iA

	possible_match = np.where(np.logical_and.reduce([lookup[..., i] == tplsum[i] for i in range(D)]))

	for y, x in zip(*possible_match):
		if np.all(im[y+1:y+h+1, x+1:x+w+1] == tpl):
			return (x+1, y+1)
	return (-1, -1)

def search_position(device, action):
	timestamp = str(datetime.timestamp(datetime.now())).replace('.','')
	subprocess.call('ADB\\adb.exe -s '+device+' shell screencap -p /sdcard/screen'+timestamp+'.png', shell=True, creationflags=CREATE_NO_WINDOW) 
	subprocess.call('ADB\\adb.exe -s '+device+' pull /sdcard/screen'+timestamp+'.png bin/images/screen'+timestamp+'.png', shell=True, creationflags=CREATE_NO_WINDOW) 
	subprocess.call('ADB\\adb.exe -s '+device+' shell rm /sdcard/screen'+timestamp+'.png', shell=True, creationflags=CREATE_NO_WINDOW) 

	img = button[action]
	template = Image.open('bin/images/screen'+timestamp+'.png')

	position = find_image(template, img)
	os.remove('bin/images/screen'+timestamp+'.png')
	return position

def like(device):
	position = search_position(device, 'like')
	if position != (-1, -1):
		tap(device, position[0], position[1])

def heart(device):
	position = search_position(device, 'like')
	if position != (-1, -1):
		longpress(device, position[0], position[1])
	position = search_position(device, 'heart')
	if position != (-1, -1):
		tap(device, position[0]+20, position[1])

def comment(device, message):
	position = search_position(device, 'comment')
	
	if position != (-1, -1):
		tap(device, position[0], position[1])
		sleep(3)

		# position = search_position(device, 'write_a_comment')
		# tap(device, position[0], position[1])
		# sleep(1)
		
		# input_text(device, message.replace(' ', '%s'))
		# change_keyboard(device)
		# sleep(1)
		input_unicode_text(device, message)

		position = search_position(device, 'send_comment')
		tap(device, position[0], position[1])
		sleep(5)

		back(device)
		back(device)

def input_text(device,txt):
	subprocess.call('ADB\\adb.exe -s '+device+' shell input text "'+txt+'"', shell=True, creationflags=CREATE_NO_WINDOW)
	
def tap(device, x, y):
	subprocess.call('ADB\\adb.exe -s '+device+' shell input tap '+str(x)+' '+str(y), shell=True, creationflags=CREATE_NO_WINDOW) 

def longpress(device, x, y):
	subprocess.call('ADB\\adb.exe -s '+device+' shell input swipe '+str(x)+' '+str(y)+' '+str(x)+' '+str(y)+' 500', shell=True, creationflags=CREATE_NO_WINDOW) 

def back(device):
	subprocess.call('ADB\\adb.exe -s '+device+' shell input keyevent KEYCODE_BACK', shell=True, creationflags=CREATE_NO_WINDOW)

def change_keyboard(device):
	subprocess.call('ADB\\adb.exe -s '+device+' shell ime set com.android.adbkeyboard/.AdbIME', shell=True, creationflags=CREATE_NO_WINDOW)

def input_unicode_text(device, txt):
	subprocess.call("ADB\\adb.exe -s "+device+" shell am broadcast -a ADB_INPUT_TEXT --es msg '" + txt + "'", shell=True, creationflags=CREATE_NO_WINDOW)

def create_memu():
	import re, time
	path = 'C:\\Program Files\\Microvirt\\MEmu\\memuc.exe'
	result = subprocess.run([path, "create"],
	                                shell=True, stdout =subprocess.PIPE, creationflags=CREATE_NO_WINDOW)
	text = result.stdout.decode('utf-8')
	print(text)
	index = re.findall(r'([\d]+)', text)[0]
	print(index)
	# return
	st = subprocess.run([path, "setconfigex", "-i", index, "is_customed_resolution", "1"],stdout=subprocess.PIPE,stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
	print(st.stdout.decode('utf-8'))
	sw = subprocess.run([path, "setconfigex", "-i", index, "resolution_width", "720"],stdout=subprocess.PIPE,stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
	print(sw.stdout.decode('utf-8'))
	sh = subprocess.run([path, "setconfigex", "-i", index, "resolution_height", "1280"],stdout=subprocess.PIPE,stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
	print(sh.stdout.decode('utf-8'))
	time.sleep(2)
	subprocess.run([path, "start", "-i", index],stdout=subprocess.PIPE,stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
	subprocess.run([path, "-i", index, "adb", "shell", "input", "keyevent", "3"],stdout=subprocess.PIPE,stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
	time.sleep(10)
	subprocess.run([path, "-i", index, "adb", "shell", "input", "keyevent", "3"],stdout=subprocess.PIPE,stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
	time.sleep(10)
	# input('set cấu hinh: ')
	subprocess.run([path, "-i", index, "adb", "root"],stdout=subprocess.PIPE,stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
	subprocess.run([path, "-i", index, "adb", "remount"],stdout=subprocess.PIPE,stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
	subprocess.run([path, "-i", index, "adb", "push", "9a5ba575.0", "/sdcard/"],stdout=subprocess.PIPE,stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
	subprocess.run([path, "-i", index, "adb", "shell", "mv", "/sdcard/9a5ba575.0", "/system/etc/security/cacerts/"],stdout=subprocess.PIPE,stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
	subprocess.run([path, "-i", index, "adb", "shell", "chmod", "644", "/system/etc/security/cacerts/9a5ba575.0"],stdout=subprocess.PIPE,stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
	subprocess.run([path, "-i", index, "adb", "shell", "settings", "put", "global", "http_proxy", "192.168.1.4:8082"],stdout=subprocess.PIPE,stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
	subprocess.run([path, "-i", index, "adb", "install", "-r", "tiktok.apk"],stdout=subprocess.PIPE,stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)

create_memu()
# memuc setconfigex -i 20 resolution_width 720
# memuc setconfigex -i 20 resolution_height 1280
# memuc start -i 20
# memuc -i 20 adb root
# adb remount
# adb push 9a5ba575.0 /sdcard/
# adb shell mv /sdcard/9a5ba575.0 /system/etc/security/cacerts/
# adb shell chmod 644 /system/etc/security/cacerts/9a5ba575.0
# adb shell settings put global http_proxy 192.168.1.19:8082

# adb install -r tiktok.apk
# adb shell input keyevent 82