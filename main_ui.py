__version__ = 0.1
__author__ = 'AceeStudio TD_ACE'
__whatisthis__ = \
"""
CG Web is a crawler collector
writed by python and openSource hosted in
the GitHub this software can improve the speed of information transmission
improve the efficiency of study and work
"""

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
import os
from PyQt4.QtNetwork import *
import time
import urllib
import webdata
import StringIO
SELF_PATH = os.path.dirname(sys.argv[0])
timeout = 50


import paramiko
import os
#transport = paramiko.Transport(('211.149.223.67', 18759))
#privatekeyfile = os.path.expanduser('d:\\test\\test.rsa')
#mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
#username = 'acee'
#transport.connect(username = username, pkey = mykey)
#sftp = paramiko.SFTPClient.from_transport(transport)
#print dir(sftp)
#remotepath='d:\\test\\1.jpg'
#localpath='file2.jpg'
#sftp.put(remotepath, localpath)



class App(QApplication):
    """
    QApplication subclass that emits a "startup" signal after
    the event loop has started. This may trigger deferred
    file loading, among other things.
    """
    signal_starting_up = pyqtSignal()
    messageAvailable = pyqtSignal(int)

    def __init__(self, args):
        super(App, self).__init__(args)
        # trigger the callback after the main event loop starts
        self._uniqueKey = "Acee Studio CG hub"
        self.sharedMemory = QSharedMemory(self._uniqueKey)

        if self.sharedMemory.attach():
            self._isRunning = True
        else:
            self._isRunning = False

            QTimer.singleShot(1, self.starting)
            if not self.sharedMemory.create(1):
                #print "Unable to create single instance"
                return
            self.localServer = QLocalServer(self)
            self.connect(self.localServer, SIGNAL("newConnection()"), self.receiveMessage)
            self.localServer.listen(self._uniqueKey)

    def receiveMessage(self):
        localSocket = self.localServer.nextPendingConnection()
        if not localSocket.waitForReadyRead(timeout):
            #print [localSocket.errorString().toLatin1()]
            return
        byteArray = localSocket.readAll()
        self.messageAvailable.emit(byteArray.toInt()[0])
        localSocket.disconnectFromServer()

    def isRunning(self):
        return self._isRunning

    def sendMessage(self, message):

        if not self._isRunning:
            return False

        localSocket = QLocalSocket(self)
        localSocket.connectToServer(self._uniqueKey, QIODevice.WriteOnly)

        if not localSocket.waitForConnected(timeout):
            #print localSocket.errorString().toLatin1()
            return False

        localSocket.write(message)

        if not localSocket.waitForBytesWritten(timeout):

            #print localSocket.errorString().toLatin1()
            #print self._uniqueKey
            return False

        localSocket.disconnectFromServer()

        return True

    def starting(self):
        """
        Callback function for Timer timeout.
        """
        self.signal_starting_up.emit()


class MainUi(QWidget):

    def __init__(self, parent=None):
        super(MainUi, self).__init__(parent)

        self.resize(2560, 1600)
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)

        self.image_list_widget = ListImageWidget(self)

        self.main_layout.addWidget(self.image_list_widget)


def download_file(downloadfilename, savefilename, reporthook):
    urllib.urlretrieve(downloadfilename, savefilename, stringio=reporthook)


class ImageListItem(QStandardItem):

    Update_Image = pyqtSignal()

    def __init__(self, index, title="", parent=None):
        super(ImageListItem, self).__init__()

        self.title = title
        self.image = None
        self.set_ui()

        self.setIcon(QIcon("test.gif"))
        self.movie = QMovie("test.gif")
        self.movie.setSpeed(150)
        self.movie.updated.connect(self.update_gif_image)
        #self.movie.start()

    def set_ui(self):
        self.setSizeHint(QSize(60, 60))
        self.setText(self.title)

    def update_gif_image(self):
        self.setIcon(QIcon(self.movie.currentPixmap()))

    def update_download_image(self, test):
        #self.movie.stop()
        while 1:
            test[0].seek(0)
            data = test[0].read()
            p = QPixmap()
            p.loadFromData(data, "jpeg")

            self.setIcon(QIcon(p))
            if p.isNull():
                print data
                break

            break


class WebData(QThread):
    Links_Data = pyqtSignal(list)

    def __init__(self, page, parent=None):
        super(WebData, self).__init__(parent)
        self.page = page

    def run(self):
        while True:
            try:
                data = webdata.get_image_from_cgtalk(self.page)
                break
            except:
                time.sleep(0.5)
        self.Links_Data.emit(data)


class DownloadFile(QThread):
    Downloading = pyqtSignal(list)
    Test = pyqtSignal(int)
    def __init__(self, url, parent=None):
        super(DownloadFile, self).__init__(parent)
        self.url = url
        self.save = StringIO.StringIO()
        #self.save = 'cache/'+os.path.basename(url)+'.jpg'



    def run(self):
        while True:
            try:
                download_file(self.url, self.save, None)
                self.save.seek(0)
                data = self.save.read()
                if "<!DOCTYPE HTML PUBLIC" in data:
                    self.url = data.split(' <a href="')[1].split('">here<')[0]
                    print self.url, 5
                    raise IOError
                if "<HTML>\n<HEAD>\n<TITLE>404 Not Found" in data:
                    print self.url
                if "Web Server at cgnetworks.com" in data:
                    raise IOError

                break
            except BaseException, info:
                self.save = StringIO.StringIO()
                time.sleep(0.5)
                print info

        time.sleep(0.5)
        self.Downloading.emit([self.save])


class CGtalk(QObject):
    Get_Data = pyqtSignal(list)
    Item_Setup = pyqtSignal(QStandardItem)

    def __init__(self, page, parent=None):
        super(CGtalk, self).__init__(parent)
        self.items = []

        self.get_data = WebData(page)
        self.get_data.Links_Data.connect(self.set_icon)

    def create_items(self):
        self.get_data.start()

    def set_icon(self, data):
        self.items = [ImageListItem(a) for a in xrange(len(data))]
        for a in self.items:
            self.Item_Setup.emit(a)

        list_item = zip(data, self.items)
        for a in list_item:
            url, width, height, title = a[0]
            item = a[1]
            #save = 'Cache/'+os.path.basename(url)

            item.setText(title)
            download_img = DownloadFile(url, self)
            download_img.Downloading.connect(item.update_download_image)
            download_img.start()


class ListImageWidget(QListView):

    GET_IMAGE = pyqtSignal(list)

    def __init__(self, parent=None):
        super(ListImageWidget, self).__init__(parent)

        self.setIconSize(QSize(60, 60))
        self.setGridSize(QSize(60, 60))

        self.cokMusicListModel = QStandardItemModel(0,1)

        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setViewMode(QListView.IconMode)
        self.setModel(self.cokMusicListModel)
        #self.setSpacing(5)

        self.page = 0

        for a in xrange(45):
            self.add_page()

    def mouseDoubleClickEvent(self, event):
        self.add_page()

    def add_page(self):
        self.page += 1
        test = CGtalk(self.page, self)
        test.Item_Setup.connect(self.set_item)
        test.create_items()

    def set_item(self, item):
        self.cokMusicListModel.appendRow(item)

import style


class AboutTableWidget(QLabel):

    def __init__(self, text='', color=None, range_blur=(0, 10), size=30,  image=None, parent=None):
        super(AboutTableWidget, self).__init__(parent)
        self.range_blur = range_blur
        self.font_size = size
        if image:
            self.setPixmap(QPixmap('Icons/github.png'))

        if text:
            self.setText(text)
        if color:
            palette = self.palette()
            palette.setColor(self.foregroundRole(), color)
            palette.setColor(self.backgroundRole(),color)
            self.setPalette(palette)

        self.setFont(QFont("Open Sans Light", size))

        self.effect = QGraphicsBlurEffect()
        self.effect.setBlurHints(QGraphicsBlurEffect.QualityHint)
        self.effect.setBlurRadius(range_blur[1])
        self.setGraphicsEffect(self.effect)

    def enterEvent(self, event):
        self.effect.setBlurRadius(self.range_blur[0])

    def leaveEvent(self, event):
        self.effect.setBlurRadius(self.range_blur[1])

creator_list = [u"AceeStudio-TD_Ace", u"Acee-Studio@qq.com"]


class textwidget(QWidget):

    def __init__(self, parent=None):
        super(textwidget, self).__init__(parent)
        self.title_label = AboutTableWidget(text=u"CG Web", color=Qt.white, parent=self)
        self.version_label = AboutTableWidget(text=u"version:{ver}".format(ver=__version__),size=15, color=Qt.white, parent=self)

        self.creator_title = AboutTableWidget(text=u"Creator : ", color=Qt.white, parent=self)

        self.user_acee = AboutTableWidget(text=u'\n'.join(creator_list), color=Qt.white, size=13, parent=self)

        self.follower = AboutTableWidget(text=u"Follower :", color=Qt.white, parent=self)
        self.follower_user = AboutTableWidget(text='\n'.join(['Null']), color=Qt.white, size=13, parent=self)

        self.github = AboutTableWidget(text=u"GitHub : www.github.", color=Qt.white, parent=self)

        self.info = AboutTableWidget(text=u"What is this : ", color=Qt.white, parent=self)
        self.wat = AboutTableWidget(text=__whatisthis__, color=Qt.white, size=13, parent=self)

        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)

        software_layout = QVBoxLayout()
        software_layout.addWidget(self.title_label)
        software_layout.addWidget(self.version_label)
        software_layout.addStretch(1)

        user_layout = QVBoxLayout()
        user_layout.addWidget(self.creator_title)
        user_layout.addWidget(self.user_acee)
        user_layout.addWidget(self.follower)
        user_layout.addWidget(self.follower_user)
        user_layout.addStretch(1)


        self.main_layout.addLayout(software_layout)
        self.main_layout.addLayout(user_layout)

        info_layout = QVBoxLayout()
        info_layout.addWidget(self.info)
        info_layout.addWidget(self.wat)

        info_layout.addWidget(self.github)

        info_layout.addStretch(1)


        user_layout.addLayout(info_layout)


class AboutWidget(QWidget):

    def __init__(self, parent=None):
        super(AboutWidget, self).__init__(parent)
        #self.setMouseTracking(True)
        self.back_ground = AboutTableWidget(image='Icons/github.png',range_blur=(35, 50), parent=self)

        self.widget_count = 0
        self.text_widget = textwidget(self)


        #self.sort_widget(self.title_label)
        #self.sort_widget(self.version_label)
        #self.sort_widget(self.back_ground)
        #self.sort_widget(self.acee_label)
        #self.sort_widget(self.follower)
        #self.sort_widget(self.github)

        #self.setStyleSheet(style.about_css)
    def resizeEvent(self, event):
        self.text_widget.resize(self.width(), self.height())


    def sort_widget(self, widget, space=5):

        widget.move(0, widget.font_size*self.widget_count+space)
        self.widget_count += 1

    def mouseMoveEvent(self, event):
        print event

        super(AboutWidget, self).mouseMoveEvent(event)

    def sizeHint(self):
        return QSize(800, 500)

    def paintEvent(self, p):
        qp = QPainter()
        qp.begin(self)
        qp.setBrush(QBrush(QColor(128, 128, 128)))
        qp.drawRect(0, 0, self.width() ,self.height())
        #qp.drawPixmap(self.width()/2-(self.image.size().width()/2), self.height()/2-(self.image.size().height()/2), self.image)
        qp.end()

app = App(sys.argv)

if __name__ == '__main__':
    if app.isRunning():
        app.sendMessage(sys.argv[1])
        app.quit()
        os._exit(0)
        try:
            sys.exit()
        except:
            sys.exit(1)
    else:
        #loding_widget = MainUi()
        loding_widget = AboutWidget()
        loding_widget.show()
    app.exec_()