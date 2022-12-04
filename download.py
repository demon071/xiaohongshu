from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import requests, os, re
from base64 import *

class DownloadVideos(QObject):
    sig_download = pyqtSignal(str, str)
    sig_stop = pyqtSignal()
    sig_status = pyqtSignal(str)
    def __init__(self, q, output):
        super().__init__()
        self.q = q
        self.output = output
        self.flag = False
        self.fileString = '%(caption)s #%(short_id)s'

    def __rename(self, video_id, caption, number, user_id, user_name):
        if caption != '':
            caption = re.sub(r'[/\\:\*\?\'<>|\.\n\"\r\？\！]','', caption)[:150]
        dataFile = {
            'video_id': str(video_id),
            'caption': caption,
            'number': str(number),
            'short_id': video_id[-4:],
            'user_id': user_id,
            'user_name': user_name,
        }

        # print(dataFile)
        
        return self.fileString % dataFile
        
    def rename(self, caption, vid, folder):
        import unicodedata
        filename = ''
        if caption == '':
            filename = vid
        else:
            filename = re.sub(r'[/\\:\*\?\'<>|\.\n\"\r\？\！]','', caption)[:150]
            filename = unicodedata.normalize("NFKD",filename)
        # if os.path.exists(folder+"/{}.mp4".format(filename)):
        #     filename = filename + ' ' + str(vid)
        return vid


    def run(self):
        while True:
            
            try:
                vid, caption, url1, url2, row, user, name = self.q.get_nowait()
            except:
                break
            # QApplication.processEvents()
            try:
                if not os.path.exists(self.output+'/xiaohongshu_user'+str(user)):
                    os.makedirs(self.output+'/xiaohongshu_user'+str(user))
            except:
                pass
            folder = self.output+'/xiaohongshu_user'+str(user)
            fileName = self.__rename(vid, caption, row, user, name)
            headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "accept-encoding": "gzip, deflate, sdch, br",
                "accept-language": "en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4",
                "cache-control": "no-cache",
                'user-agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
            }
            try:
                # url1 = url1.replace('https', 'http')
                with requests.get(url1, headers=headers, stream=True) as r:
                    file_size = int(r.headers['Content-Length'])
                    total = 0
                    with open('{}/{}.mp4'.format(folder,fileName), 'wb') as f:
                        for chunk in r.iter_content(chunk_size=1024): 
                            total += len(chunk)
                            data_line = round((total/file_size)*100)
                            self.sig_download.emit(str(row), str(data_line)+'%')
                            f.write(chunk)
                self.sig_download.emit(str(row), 'Done')
                self.sig_status.emit('>> '+ str(fileName))
                
            except:
                try:
                    # url2 = url2.replace('https', 'http')
                    with requests.get(url2, headers=headers, stream=True) as r:
                        file_size = int(r.headers['Content-Length'])
                        total = 0
                        with open('{}/{}.mp4'.format(folder,fileName), 'wb') as f:
                            for chunk in r.iter_content(chunk_size=1024): 
                                total += len(chunk)
                                data_line = round((total/file_size)*100)
                                self.sig_download.emit(str(row), str(data_line)+'%')
                                f.write(chunk)
                    self.sig_download.emit(str(row), 'Done')
                    self.sig_status.emit('>> '+ str(fileName))
                except Exception as e:
                    self.sig_download.emit(str(row), str(e))
            # try:
            #     # photo = photo.replace('https', 'http')
            #     # with requests.get(photo, headers=headers, stream=True) as r:
            #     #     with open('{}/thumb/{}.jpg'.format(folder,fileName), 'wb') as f:
            #     #         for chunk in r.iter_content(chunk_size=1024): 
            #     #             f.write(chunk)
            # except:
            #     pass
            # self.q.task_done()
        self.sig_stop.emit()
        # self.sig_reset_status.emit()


