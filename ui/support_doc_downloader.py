import os

from PyQt4.QtGui import (
        QApplication,
        QDialog,
        QColor,
        QMessageBox
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

        self.setWindowTitle('Download Supporting Documents')

        self.sdoc_manager = support_doc_manager
        self.btnDownload.clicked.connect(self.start_download)
        self.btnCancel.clicked.connect(self.cancel_download)

        self.download_thread = QThread(self)
        self.sdoc_manager.moveToThread(self.download_thread)

        self.sdoc_manager.download_started.connect(self.doc_download_started)
        self.sdoc_manager.download_progress.connect(self.process_progress)
        self.sdoc_manager.download_counter.connect(self.update_download_counter)
        self.sdoc_manager.download_completed.connect(self.doc_download_completed)
        self.sdoc_manager.download_status.connect(self.update_download_status)

        self.sdoc_manager.upload_started.connect(self.doc_upload_started)
        self.sdoc_manager.upload_progress.connect(self.process_progress)
        self.sdoc_manager.upload_counter.connect(self.update_upload_counter)
        self.sdoc_manager.upload_completed.connect(self.doc_upload_completed)

        self.download_thread.started.connect(self.download_thread_started)
        self.download_thread.finished.connect(self.download_thread.deleteLater)

        self.lblDcount.setText('{} of {}'.format(0, self.sdoc_manager.size()))
        self.lblUcount.setText('{} of {}'.format(0, self.sdoc_manager.size()))

        self.finished_upload = False

    def closeEvent(self, event):
        if self.finished_upload:
            event.accept()
        else:
            result = QMessageBox.question(
                self,
                'Download Files',
                self.tr(
                    'Are you sure you want to close'\
                       ' without downloading files?'
                ),
                QMessageBox.Yes,
                QMessageBox.No
            )
            if result == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()

    def confirm_close(self, msg):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessage.Warning)
        msg_box.setText(msg)
        msg_box.setWindowTitle('Download Files')
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        ret_val = msg_box.exec_()
        return True if ret_val == QMessageBox.Yes else False

    def doc_download_started(self, msg):
        self.btnDownload.setEnabled(False)
        self.btnCancel.setText(self.tr('Cancel'))
        self.edt_progress_update(
            QColor(51, 182, 45),
            None,
            msg + ' Started...'
        )
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

    def update_download_status(self, DNLD_Status_id):
        if DNLD_Status_id == 0: # Success
            self.edt_progress_update(
                QColor(51, 182, 45),
                None,
                'Success',
                False
            )

        if DNLD_Status_id == 1: # Failed
            self.edt_progress_update(
                QColor('red'),
                None,
                'Failed',
                False
            )

        if DNLD_Status_id == 2: # File Already Exists
            self.edt_progress_update(
                QColor(255,170,0),
                None,
                'Already Exists',
                False
            )

    def doc_download_completed(self, msg):
        self.edt_progress_update(
            QColor(51, 182, 45),
            None,
            msg + ' completed.',
            True
        )
        self.edt_progress_update(
            QColor('black'),
            None,
            '----------------------------',
            True
        )
        #self.download_thread.quit()

    def doc_upload_started(self, msg):
        self.edt_progress_update(
            QColor(51, 182, 45),
            None,
            msg + ' started...',
            True
        )
        QApplication.processEvents()


    def update_upload_counter(self, count):
        self.lblUcount.setText('{} of {}'.format(count, self.sdoc_manager.size()))

    def doc_upload_completed(self, msg):
        self.edtProgress.setTextColor(QColor(51, 182, 45))
        self.edtProgress.append(msg+" completed.")
        self.download_thread.quit()
        self.finished_upload = True
        self.btnDownload.setEnabled(True)
        self.btnCancel.setText(self.tr('Close'))

    def download_thread_started(self):
        self.sdoc_manager.start_download()

    def start_download(self):
        self.download_thread.start()

    def cancel_download(self):
        self.close()

    def edt_progress_update(self, textcolor, textweight, msg, newline=False):
        if not textcolor is None:
            self.edtProgress.setTextColor(textcolor)
        if not textweight is None:
            self.edtProgress.setFontWeight(textweight)
        if not newline:
            self.edtProgress.textCursor().insertText(msg)
        else:
            self.edtProgress.append(msg)