from PyQt4.QtGui import (
    QMessageBox,
    QWidget
)

from stdm.network.cmis_manager import (
    PDFViewerException,
    PDFViewerProxy
)


class PDFViewerWidget(QWidget):
    """
    Visualization for Scheme supporting documents
    """
    def __init__(self, doc_uuid, doc_name, parent=None):
        # Create instance of viewer proxy
        # QWidget.__init__(parent)
        super(QWidget, self).__init__(parent)
        self._doc_uuid = doc_uuid
        self._doc_name = doc_name
        try:
            self._pdf_proxy = PDFViewerProxy(self)
        except PDFViewerException as pve:
            QMessageBox.warning(
                self,
                'View PDF Error',
                str(pve)
            )

        # Connect signal that shows error messages
        self._pdf_proxy.error.connect(
            self.on_pdf_view_error
        )

    def on_pdf_view_error(self, error_info):
        # error_info is a tuple containing the document UUID (0) and error message (1).
        err_msg = error_info[1]
        QMessageBox.critical(
            self,
            self.tr('View PDF Error'),
            err_msg
        )

    def view_document(self):
        # Function/slot raised to view a document.
        try:
            self._pdf_proxy.view_document(
                self._doc_uuid,
                self._doc_name
            )
        except PDFViewerException as pve:
            QMessageBox.warning(
                self,
                'View PDF Error',
                str(pve)
            )