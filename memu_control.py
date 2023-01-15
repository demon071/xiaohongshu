import subprocess
import config
import re
import time

CREATE_NO_WINDOW = 0x08000000


def create_memu(path):
    
    cer_path = config.sett_folder + '\\bin\\' + 'c8750f0d.0'
    result = subprocess.run([path, "create"],
                                    shell=True, stdout =subprocess.PIPE,
	                                stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    
    text = result.stdout.decode('utf-8')
    index = re.findall(r'([\d]+)', text)[0]
    
    st = subprocess.run([path, "setconfigex", "-i", index, "is_customed_resolution", "1"], stdout =subprocess.PIPE,
	                                stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    
    sw = subprocess.run([path, "setconfigex", "-i", index, "resolution_width", "720"], stdout =subprocess.PIPE,
	                                stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    
    sh = subprocess.run([path, "setconfigex", "-i", index, "resolution_height", "1280"], stdout =subprocess.PIPE,
	                                stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    
    time.sleep(2)
    subprocess.run([path, "start", "-i", index], stdout =subprocess.PIPE,
	                                stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    subprocess.run([path, "-i", index, "adb", "shell", "input", "keyevent", "3"], stdout =subprocess.PIPE,
	                                stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    time.sleep(10)
    subprocess.run([path, "-i", index, "adb", "shell", "input", "keyevent", "3"], stdout =subprocess.PIPE,
	                                stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    time.sleep(10)
    # input('set cấu hinh: ')
    subprocess.run([path, "-i", index, "adb", "root"], stdout =subprocess.PIPE,
	                                stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    subprocess.run([path, "-i", index, "adb", "remount"], stdout =subprocess.PIPE,
	                                stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    subprocess.run([path, "-i", index, "adb", "push", cer_path, "/sdcard/"], stdout =subprocess.PIPE,
	                                stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    subprocess.run([path, "-i", index, "adb", "shell", "mv", "/sdcard/c8750f0d.0", "/system/etc/security/cacerts/"], stdout =subprocess.PIPE,
	                                stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    subprocess.run([path, "-i", index, "adb", "shell", "chmod", "644", "/system/etc/security/cacerts/c8750f0d.0"], stdout =subprocess.PIPE,
	                                stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    config.memu_index = str(index)

def add_proxy(path, index, proxy):
    subprocess.run([path, "-i", index, "adb", "shell", "settings", "put", "global", "http_proxy", proxy], stdout =subprocess.PIPE,
	                                stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    # subprocess.call([path, "-i", index, "adb", "install", "-r", "tiktok.apk"],stdout=subprocess.PIPE,stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)

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