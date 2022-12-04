from json import tool
from requests import Session
import time
import hashlib		
import wmi, jwt , json			#pip install wmi pywin32
from PyQt5 import QtCore
from PyQt5.QtCore import QObject, QUrl, QByteArray
from PyQt5.QtNetwork import QNetworkAccessManager,QNetworkRequest
from urllib.parse import urlencode


class HttpReq(QObject):
    result = QtCore.pyqtSignal(bool, str)
    def __init__(self, parent, key_reg, tool_name, ver):
        super(HttpReq, self).__init__(parent)
        self.m_netAccessManager = QNetworkAccessManager(self)
        self.m_netReply = None
        self.key_reg = key_reg
        self.tool_name = tool_name
        self.ver = ver


    def request(self):

        if self.m_netReply is not None:
            self.m_netReply.disconnect()

        req = QNetworkRequest(QUrl("https://snaptikz.com/key/checks/"))
        req.setHeader(QNetworkRequest.ContentTypeHeader,"application/x-www-form-urlencoded")

        data = {
                'key': self.key_reg,
                'tool': self.tool_name
            }
        keys = 'django-insecure-acx@56-c0)my9z2f16t@)yp6d*9^wpy+9a$+r8m@^m3@!f^2!8'
        data_encode = jwt.encode(data, keys, algorithm='HS256')
        data_ = {
            'data': data_encode
        }

        senda = QByteArray()
        senda.append(urlencode(data_))

        self.m_netReply = self.m_netAccessManager.post(req,senda)
        self.m_netReply.finished.connect(self.readData)
        self.m_netReply.error.connect(self.requesterr)
    
    def date_to_int(self, ddate):
        idate = ddate.replace('-', '').replace('/', '')
        return int(idate)

    def readData(self):
        try:
            recvData = self.m_netReply.readAll()
            data_ = str(bytes(recvData.data()), encoding="utf-8")
        
            data_raw = json.loads(data_)
            keys = 'django-insecure-acx@56-c0)my9z2f16t@)yp6d*9^wpy+9a$+r8m@^m3@!f^2!8'
            data = jwt.decode(data_raw['data'], keys, algorithms=['HS256'], verify_signature=True)
            # print(data)
            text = 'Actived'
            if data['result'] == '0':
                text = 'Key not found'
                self.show_result(False, text)
                return 
            idate_now = int(time.strftime("%Y%m%d"))
            idate_key = self.date_to_int(data['expiry_date'])
            if idate_now > idate_key:
                text = 'Key has expired'
                self.show_result(False, text)
                return 
            key_result = data['key_result']
            if key_result != self.key_reg:
                text = 'Key is error'
                self.show_result(False, text)
                return 
            self.show_result(True, data['expiry_date'])
            return 
        except:
            self.show_result(False, 'Server error')


    def show_result(self, check, text):
        self.parent().ui.statusbar.showMessage(str(self.key_reg+'-'+text+'-ver:'+self.ver))
        if(check == True):
            self.parent().ui.centralwidget.setEnabled(True)
        else:
            self.parent().ui.centralwidget.setEnabled(False)

    def requesterr(self,err):
        print(err)



def create_key(tool_name):
    try:
        c = wmi.WMI()
        dic = {}
        for item in c.Win32_PhysicalMedia():
            dic[str(item.wmi_property('Tag').value).replace('\\','')] = str(item.wmi_property('SerialNumber').value).replace(' ','')
        diskserial = dic['.PHYSICALDRIVE0']
    except:
        diskserial = ''

    try:
        c = wmi.WMI()
        hwid =  (c.Win32_ComputerSystemProduct()[0].wmi_property('UUID').value).replace(' ','')
    except:
        hwid = ''
        

    key_reg = diskserial + ' ' + hwid + ' ' + tool_name
    # print(key_reg)
    key_reg = hashlib.md5(key_reg.encode('utf-8')).hexdigest()
    # print(key_reg)
    return key_reg

# create_key('reg_clone')

def encode_key(key_reg):
    key_value = '0123456789'
    key_result = ''
    for i in range(len(key_reg)):
        key_result += key_value[ord(key_reg[i]) % len(key_value)]
    return key_result

def date_to_int(ddate):
    idate = ddate.replace('-', '').replace('/', '')
    return int(idate)

def check_key(key_reg, tool_name):
    ses = Session()
    data = {
        'key': key_reg,
        'tool': tool_name
    }
    key = 'django-insecure-acx@56-c0)my9z2f16t@)yp6d*9^wpy+9a$+r8m@^m3@!f^2!8'
    data_encode = jwt.encode(data, key, algorithm='HS256')
    # print(data_encode)
    # res = ses.post('http://127.0.0.1:8000/key/checks/', data={'data': data_encode}, timeout=10)
    res = ses.post('https://snaptikz.com/key/checks/', data={'data': data_encode}, timeout=10)
    # print(res.text)
    data_raw = res.json()
    data = jwt.decode(data_raw['data'], key, algorithms=['HS256'], verify_signature=True)
    # print(data)
    text = 'Actived'
    if data['result'] == '0':
        text = 'Key not found'
        return False, text
    if data['key_result'] != key_reg:
        text = 'Key not found'
        return False, text
    idate_now = int(time.strftime("%Y%m%d"))
    idate_key = date_to_int(data['expiry_date'])
    if idate_now > idate_key:
        text = 'Key has expired'
        return False, text
    key_result = data['key_result']
    if key_result != key_reg:
        text = 'Key is error'
        return False, text
    return True, data['expiry_date']

