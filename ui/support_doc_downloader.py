import os

from PyQt4.QtGui import (
        QApplication,
        QDialog,
        QColor
        )

from PyQt4.QtCore import (
    Qt,
    QObject,
    QThread
)
from stdm.ui.support_doc_manager import SupportDocManager

from ui_downup_support_doc import Ui_SupportDocDownloader

class SupportDocDownloader(QDialog, Ui_SupportDocDownloader):
    def __init__(self, support_doc_manager):
        QDialog.__init__(self)
        self.setupUi(self)

        self.setWindowTitle('Download supporting documents')

        self.sdoc_manager = support_doc_manager
        self.btnClose.clicked.connect(self.close)
        self.btnDownload.clicked.connect(self.start_download)

        self.download_thread = QThread(self)
        self.sdoc_manager.moveToThread(self.download_thread)

        self.sdoc_manager.download_started.connect(self.doc_download_started)
        self.sdoc_manager.download_progress.connect(self.process_progress)
        self.sdoc_manager.download_counter.connect(self.update_download_counter)
        self.sdoc_manager.download_completed.connect(self.doc_download_completed)

        self.sdoc_manager.upload_started.connect(self.doc_upload_started)
        self.sdoc_manager.upload_progress.connect(self.process_progress)
        self.sdoc_manager.upload_counter.connect(self.update_upload_counter)
        self.sdoc_manager.upload_completed.connect(self.doc_upload_completed)

        self.download_thread.started.connect(self.download_thread_started)
        self.download_thread.finished.connect(self.download_thread.deleteLater)

        self.lblDcount.setText('{} of {}'.format(0, self.sdoc_manager.size()))
        self.lblUcount.setText('{} of {}'.format(0, self.sdoc_manager.size()))

    def close(self):
        self.done(1)

    def doc_download_started(self, msg):
        self.edtProgress.append(msg+" started...")
        QApplication.processEvents()

    def process_progress(self, info_id, msg):
        if info_id == 0: # information
            self.edtProgress.setTextColor(QColor('black'))

        if info_id == 1: # Warning
            self.edtProgress.setTextColor(QColor(255, 170, 0))

        if info_id == 2: # Error
            self.edtProgress.setTextColor(QColor('red'))

        self.edtProgress.append(msg)
        QApplication.processEvents()

    def update_download_counter(self, count):
        self.lblDcount.setText('{} of {}'.format(count, self.sdoc_manager.size()))

    def doc_download_completed(self, msg):
        self.edtProgress.setTextColor(QColor(51, 182, 45))
        self.edtProgress.setFontWeight(75)
        self.edtProgress.append(msg+" completed.")
        #self.download_thread.quit()

    def doc_upload_started(self, msg):
        self.edtProgress.append(msg+" started...")
        QApplication.processEvents()

    def update_upload_counter(self, count):
        self.lblUcount.setText('{} of {}'.format(count, self.sdoc_manager.size()))

    def doc_upload_completed(self, msg):
        self.edtProgress.setTextColor(QColor(51, 182, 45))
        self.edtProgress.setFontWeight(75)
        self.edtProgress.append(msg+" completed.")
        self.download_thread.quit()

    def download_thread_started(self):
        self.sdoc_manager.start_download()

    def start_download(self):
        self.download_thread.start()

