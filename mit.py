#!/bin/env python
import asyncio
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from mitmproxy import options
from mitmproxy.tools import dump
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from ui_main import Ui_MainWindow
import qasync, queue, threading
from qasync import asyncSlot, asyncClose, QApplication
import functools, key
from pathlib import Path
from qt_material import apply_stylesheet
from download import DownloadVideos

__version__ = '2202.11.05'

class RequestLogger(QtCore.QObject):
    url = QtCore.pyqtSignal(dict)
    def response(self, flow):
        # url = flow.request.url
        # print(url)
        if '/user/posted' in flow.request.url:
            url = flow.request.url
            # print(url)
            data = flow.response.text
            self.url.emit({
                'url': url,
                'data': data
            })

class MyForm(QtWidgets.QMainWindow):
    sende = QtCore.pyqtSignal()
    """docstring for MyForm"""
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # self.ui.tableWidget.verticalHeader().hide()
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.ui.pushButton_3.clicked.connect(self.resetData)
        self.ui.pushButton_2.clicked.connect(self.download)
        self.ui.pushButton.clicked.connect(self.saveFolder)
        # self.master = None
        self.start_proxy('0.0.0.0', 8080)
        self.flag_download = False
        self.q = queue.Queue()
        self.data = []
        self.checkSaveFolder()
        self.checkLicense()

    def resetData(self):
        self.data = []
        self.q.queue.clear()
        self.ui.tableWidget.clearContents()
        self.ui.tableWidget.setRowCount(0)
        self.ui.statusbar.showMessage('')

    @asyncClose
    async def closeEvent(self, event):
        await self.master.shutdown()


    @asyncSlot()
    async def start_proxy(self, host, port):
        opts = options.Options(listen_host=host, listen_port=port)

        self.master = dump.DumpMaster(
            opts,
            with_termlog=False,
            with_dumper=False,
        )
        addon = RequestLogger()
        addon.url.connect(self.shows)
        self.master.addons.add(addon)
        await self.master.run()
        return self.master

    def shows(self, _dict):
        # self.ui.textEdit.append(_dict['url'])
        import json
        json_data = json.loads(_dict['data'])
        for x in json_data['data']['notes']:
            # data.notes[0].type
            if x['type'] == 'video':
                rows = self.ui.tableWidget.rowCount()
                self.ui.tableWidget.insertRow(rows)
                self.ui.tableWidget.setItem(rows, 0, QtWidgets.QTableWidgetItem(str(x['id'])))
                self.ui.tableWidget.setItem(rows, 1, QtWidgets.QTableWidgetItem(str(x['title'])))
                self.ui.tableWidget.setItem(rows, 2, QtWidgets.QTableWidgetItem(str(x['user']['userid'])))
                self.ui.tableWidget.setItem(rows, 3, QtWidgets.QTableWidgetItem(str(x['likes'])))
                vid = str(x['id'])
                caption = x['title']
                url1 = x['video_info_v2']['media']['stream']['h264'][0]['backup_urls'][0]
                url2 = x['video_info_v2']['media']['stream']['h264'][0]['backup_urls'][1]
                user = x['user']['userid']
                name = x['user']['nickname']
                data = [vid, caption, url1, url2, rows, user, name]
                self.q.put(data)
                self.ui.statusbar.showMessage('Total video: '+ str(rows))
                # data.notes[0].user.nickname
            # data.notes[1].video_info_v2.media.stream.h264[0].backup_urls[0]
            # self.ui.tableWidget.setItem(rows, 4, QTableWidgetItem(url1))
            # self.ui.tableWidget.setItem(rows, 5, QTableWidgetItem(url2))
        # with open('text.txt', 'w', encoding='utf-8-sig') as f:
        #     f.write(str(_dict['data']))
            # data.notes[0].id
            # data.notes[0].title
            # data.notes[0].likes
            # data.notes[0].user.userid
            # data.notes[0].video_info_v2.media.stream.h264[0].master_url

    def download_status(self, row, string):
        self.ui.tableWidget.setItem(int(row), 4, QtWidgets.QTableWidgetItem(string))

    def download(self):
        if self.flag_download == False:
            output = self.ui.lineEdit_3.text()
            self.__threads = []
            # self.NUM_THREADS = int(setting['appSetting']['thread'])
            for _ in range(3):
                thread = QtCore.QThread()
                thread.setObjectName('thread_' + str(_))
                worker = DownloadVideos(self.q, output)
                self.__threads.append((thread, worker))
                worker.moveToThread(thread)
                worker.sig_download.connect(self.download_status)
                worker.sig_stop.connect(thread.quit)
                worker.sig_status.connect(self.status_download)
                thread.started.connect(worker.run)
                thread.finished.connect(self.reset_download)
                thread.start()
            self.flag_download = True
        
    def status_download(self, _str):
        self.ui.statusbar.showMessage(_str)

    def reset_download(self):
        check = 0
        # worker.deleteLater()
        for thread, worker in self.__threads:
            if thread.isRunning() == True:
                check += 1
        if check == 0:
            self.flag_download = False

    def checkSaveFolder(self):
        try:
            path = str(Path().absolute())
            dirr = open(path+'folder.dat', 'r').read()
            self.ui.lineEdit_3.setText(str(dirr))
            dirr.close()
        except:
            path = str(Path().absolute())
            self.ui.lineEdit_3.setText(path)

    def saveFolder(self):
        path = str(Path().absolute())
        dir_ = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select folder", '', QtWidgets.QFileDialog.ShowDirsOnly)
        if dir_:
            self.ui.lineEdit_3.setText(str(dir_))
            dirr = open(path+'folder.dat', 'w')
            dirr.write(str(dir_))
            dirr.close()

    def checkLicense(self):
        self.ui.centralwidget.setEnabled(False)
        keytool = key.create_key("Xiaohongshu")
        http = key.HttpReq(self, key_reg=keytool, tool_name="Xiaohongshu", ver=__version__)
        http.request()
        dirr = open('key.txt', 'w')
        dirr.write(str(keytool))
        dirr.close()

async def main():
    def close_future(future, loop):
        loop.call_later(10, future.cancel)
        future.cancel()

    loop = asyncio.get_event_loop()
    future = asyncio.Future()

    app = QApplication.instance()
    if hasattr(app, "aboutToQuit"):
        getattr(app, "aboutToQuit").connect(
            functools.partial(close_future, future, loop)
        )

    mainWindow = MyForm()
    apply_stylesheet(mainWindow, theme='dark_yellow.xml')
    mainWindow.show()

    await future
    return True



if __name__ == "__main__":
    try:
        qasync.run(main())
    except asyncio.exceptions.CancelledError:
        sys.exit(0)
    

# if __name__=="__main__":
#     app = QtWidgets.QApplication(sys.argv)
#     w = MyForm()
#     w.show()
#     sys.exit(app.exec_())





# class RequestLogger:
#     def request(self, flow):
#         print(flow.request)

# async def start_proxy(host, port):
#     opts = options.Options(listen_host=host, listen_port=port)

#     master = dump.DumpMaster(
#         opts,
#         with_termlog=False,
#         with_dumper=False,
#     )
#     master.addons.add(RequestLogger())
    
#     await master.run()
#     return master

# if __name__ == '__main__':
#     host=sys.argv[1]
#     port=int(sys.argv[2])
#     asyncio.run(start_proxy(host, port))
# 2096913697