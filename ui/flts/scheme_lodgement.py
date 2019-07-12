"""
/***************************************************************************
Name                 : Scheme Lodgement Wizard
Description          : Dialog for lodging a new scheme.
Date                 : 01/July/2019
copyright            : (C) 2019 by Joseph Kariuki
email                : joehene@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from collections import OrderedDict
from PyQt4.QtCore import *
from PyQt4.QtGui import (
    QWizard,
    QFileDialog,
    QVBoxLayout,
    QMessageBox
)

from stdm.data.configuration import entity_model
from stdm.data.configuration.entity import Entity
from stdm.data.configuration.columns import (
    MultipleSelectColumn,
    VirtualColumn
)
from stdm.data.mapping import MapperMixin
from stdm.data.pg_utils import table_column_names
from stdm.utils.util import format_name

from ui_scheme_lodgement import Ui_Ldg_Wzd
from ..notification import NotificationBar, ERROR


class LodgementWizard(QWizard, Ui_Ldg_Wzd, MapperMixin):
    """
    Wizard that incorporates lodgement of all information required for a Land Hold Title Scheme
    """

    addedModel = pyqtSignal(object)

    def __init__(self, parent=None):
        QWizard.__init__(self, parent)

        self.entity_table_model = {}

        self.setupUi(self)
        self.page_title()
        self._num_pages = len(self.pageIds())
        self._base_win_title = self.windowTitle()

        # connecting signals with our slot
        self.btn_brws_hld.clicked.connect(self.browse_holders_file)
        self.btn_upld_multi.clicked.connect(self.upload_multiple_files)
        self.currentIdChanged.connect(self.on_page_changed)

    def page_title(self):
        """
        set page title and subtitle instructions
        """
        # Set page titles
        self.wizardPage1.setTitle('New Land Hold Scheme')
        self.wizardPage2.setTitle('Import Holders')
        self.wizardPage.setTitle('Upload Documents')
        self.wizardPage_4.setTitle('Summary')

        # Set page subtitles
        self.wizardPage1.setSubTitle('Please enter scheme information below. '
                                     'Note that the scheme number'
                                     'will be automatically generated')
        self.wizardPage2.setSubTitle('Please browse for list of holders file')
        self.wizardPage.setSubTitle(
            'Review the summary of the previous steps. Click Back to edit information of Finish to save')
        self.wizardPage_4.setSubTitle(
            'Review the summary of the previous steps. Click Back to edit information of Finish to save')

    def on_page_changed(self, idx):
        """
         Show the page id that is loaded
        """
        page_num = idx + 1
        win_title = u'{0} - Step {1} of {2}'.format(self._base_win_title, str(page_num), str(self._num_pages))
        self.setWindowTitle(win_title)

    def browse_holders_file(self):
        """
        Browse for the holders file in the file directory
        """
        holders_file = QFileDialog.getOpenFileName(self, "Open Holder's File",
                                                   '~/', " Excel Files *.xls *xlsx")
        if holders_file:
            self.lnEdit_hld_path.setText(holders_file)
            self.tw_hld_prv.load_workbook(holders_file)

    def upload_multiple_files(self):
        """
        Browse and select multiple documents
        """
        all_files_dlg = QFileDialog.getOpenFileNames(self, "Open Holder's File",
                                                     '~/', " *.pdf")

    def accept_dlg(self):
        # Check if the user has selected an action from the list widget
        self.notif_bar.clear()

        selected_items = self.lsw_category_action.selectedItems()

        if len(selected_items) == 0:
            self.notif_bar.insertWarningNotification(
                self.tr("Please select an operation to perform"))
            return

        self._action_code = selected_items[0].data(Qt.UserRole)
        self.accept()
        pass


if __name__ == '__main__':
    import sys

    app = QWizard.QApplication(sys.argv)
    wizard = LodgementWizard()
    wizard.show()
    sys.exit(app.exec_())
