import os
from qgis.core import QgsNetworkAccessManager
from PyQt4.QtNetwork import (
    QNetworkAccessManager,
    QNetworkRequest
)
from PyQt4.QtCore import (
    QUrl,
    QByteArray,
    QEventLoop,
)

class KB_DocumentDownloader(object):
    """
    This class for downloading documents from KoBo 
    for use in the STDM document_downloader_win module
    """
    def __init__(self, username, password):
        self.manager = QNetworkAccessManager()
        self.manager.finished.connect(self.handle_download)
        self.header_data = QByteArray(
            '{}:{}'.format(username, password)
        ).toBase64()

    def kobo_download(self, src_url, dest_filename):
        self.download_result = None
        self.dest_filename = dest_filename
        request = QNetworkRequest(QUrl(src_url))
        request.setRawHeader(
            'Authorization',
            'Basic {}'.format(self.header_data)
        )
        try:
            self.manager.get(request)
            self.loop = QEventLoop()
            self.loop.exec_()
        except:
            pass
        
        self.loop = None

        if self.download_result is None:
            return False

        return self.download_result
            
    def handle_download(self, reply):
        if reply.errorString() != 'Unknown error':
            self.download_result = False
        else:
            dest_path = os.path.dirname(self.dest_filename)
            if not os.path.exists(dest_path):
                os.makedirs(dest_path)
            with open(self.dest_filename, 'wb') as f:
                f.write(reply.readAll())
            self.download_result = True
        reply = None
        self.loop.quit()