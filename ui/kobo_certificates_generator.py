from distutils.log import ERROR
from email import header
from email.mime import application
import os
import hashlib
import shutil
from time import sleep
import requests
import json
from datetime import datetime

from PyQt4 import QtGui
from PyQt4.QtGui import (
    QApplication,
    QDialog,
    QFileDialog,
    QProgressBar,
    QMessageBox,
)
    
from stdm.settings import (
    current_profile
)

from stdm.utils.util import (
    getIndex, 
    mapfile_section,
    get_working_mapfile
)

from PyQt4.QtCore import (
    Qt,
    QUrl,
    QObject,
    pyqtSignal,
    QByteArray,
    QEventLoop,
    QFile,
    QFileInfo,
    SIGNAL,
    QSignalMapper,
    QThread
)

from qgis.core import QgsNetworkAccessManager
from PyQt4.QtNetwork import (
    QNetworkAccessManager,
    QNetworkRequest
)
from stdm.data.importexport.document_downloader import (
    DocumentDownloader
)

from stdm.data.pg_utils import (
    pg_create_supporting_document,
    pg_create_parent_supporting_document,
    get_lookup_data
)

from stdm.settings.registryconfig import (
        RegistryConfig,
        NETWORK_DOC_RESOURCE
)
from stdm.data.importexport import (
    kobo_outpath,
    set_kobo_outpath
)
from stdm.data.stdm_reqs_sy_ir import fix_auto_sequences
from stdm.data.kobo_certificates import(
    enum_enumerators,
    find_enumerator,
    find_respondent,
    find_respondent_sdocs,
    find_respondent_id_doc,
    find_respondent_id_doc_file,
    find_claim,
    find_claim_sdocs,
    find_evidence,
    find_evidence_file,
    find_household_member,
    find_household_member_id_doc,
    find_household_member_id_doc_file,
    find_lostdoc,
    kobo_certificate_read_from_template
)
from ui_kobo_certificates_generator import Ui_KoboCertificatesGenerator

try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(
            context,
            text,
            disambig,
            _encoding
        )
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(
            context,
            text,
            disambig
        )

class KoboCertificatesGenerator(QDialog, Ui_KoboCertificatesGenerator):
    update_progress = pyqtSignal(int, unicode)

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.setupUi(self)

        self.current_profile = current_profile()
        self.btnCancel.clicked.connect(self.kobocertificates_cancel)
        self.btnGenerate.clicked.connect(self.kobocertificates_generate)
        self.update_progress.connect(self.update_progress_event)

        self.bt_outpath.clicked.connect(self.get_outpath)

        path = kobo_outpath()
        self.ed_outpath.setReadOnly(True)
        if os.path.exists(path):
            self.ed_outpath.setText(path)
        else:
            self.ed_outpath.setText('c:\\k_cert')

    def get_outpath(self):
        dialog = QFileDialog()
        doc_folder = dialog.getExistingDirectory(
            self,
            self.tr('Select document directory'),
            self.ed_outpath.text()
        )
        if doc_folder != '':
            self.ed_outpath.setText(doc_folder)
            self.edtProgress.clear()

    def kobocertificates_generate(self):
        self.printed = 0
        self.uploaded = 0
        self.output = self.ed_outpath.text()
        self.btnGenerate.setEnabled(False)
        self.cbIgnorePrinted.setEnabled(False)
        self.cbUploadCertificates.setEnabled(False)
        self.cbCertLang.setEnabled(False)
        self.bt_outpath.setEnabled(False)
        self.ed_outpath.setEnabled(False)
                    
        self.ForceRegenerate = self.cbIgnorePrinted.checkState()
        self.UploadCertificate = self.cbUploadCertificates.checkState()
        self.Certificate_Language = self.cbCertLang.checkState()

        self.cancelled = False
        #if 0 == enum_enumerators(' ', self):
        #if 0 == enum_enumerators(' Where hl_enumeration.kobo_id in (select kobo_id from enumeration_filter)', self):
        if 0 == enum_enumerators(' Where hl_enumeration.kobo_id = 553649557', self):
            set_kobo_outpath(self.output)

        self.btnGenerate.setEnabled(True)
        self.cbIgnorePrinted.setEnabled(True)
        self.cbUploadCertificates.setEnabled(True)
        self.cbCertLang.setEnabled(True)
        self.bt_outpath.setEnabled(True)
        self.ed_outpath.setEnabled(True)
        return 0
    
        ErrMessage(unicode(
            find_respondent_id_doc_file(' where hl_respondent_document_supporting_document.id = 10 ')[0]['sdoc_fileext']
        ))
        return
        enums = enum_enumerators('')
        if enums is None:
            ErrMessage('Failed')
            return
        for enum in enums:
            resps = find_respondent(' WHERE hl_respondent.kobo_id = {}'.format(enum['kobo_id']))
            for resp in resps:
                hhms = find_household_member(' WHERE hl_household_member.kobo_submission_id = {}'.format(resp['kobo_id']))
                for hhm in hhms:
                    pass#ErrMessage(u'{}'.format(hhm['household_member_first_name']))
                claims = find_claim(' WHERE hl_property.respondent = {}'.format(resp['respondent_id']))
                for clm in claims:
                    pass#ErrMessage(u'{}'.format(clm['claim_ref_number']))
                evds = find_evidence(' WHERE hl_evidence.respondent = {}'.format(resp['respondent_id']))
                for evd in evds:
                    ErrMessage(u'{}'.format(evd['evidence_number']))
        return

    def kobocertificates_cancel(self):
        self.cancelled = True
        self.close()

    def update_progress_event(self, info_id, msg):
        if info_id == 0:
            self.edtProgress.append(msg)
            QApplication.processEvents()
        
        if info_id == 1:
            self.printed += 1
            self.edtProgress.textCursor().insertText(msg)
            self.lblPcount.setText(u'{}'.format(self.printed))
            QApplication.processEvents()

        if info_id == 2:
            self.uploaded += 1
            self.edtProgress.textCursor().insertText(msg)
            self.lblUcount.setText(u'{}'.format(self.uploaded))
            QApplication.processEvents()


def ErrMessage(message):
    # Error Message Box
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText(message)
    msg.exec_()