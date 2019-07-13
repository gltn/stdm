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
    QAbstractButton,
    QMessageBox
)

from stdm.data.pg_utils import(
    export_data
)
from stdm.settings import current_profile
from stdm.data.configuration import entity_model
from stdm.data.mapping import MapperMixin
from ui_scheme_lodgement import Ui_ldg_wzd
from ..notification import NotificationBar, ERROR


class LodgementWizard(QWizard, Ui_ldg_wzd, MapperMixin):
    """
    Wizard that incorporates lodgement of all information required for a Land
    Hold Title Scheme
    """

    wizardFinished = pyqtSignal(object, bool)

    def __init__(self, parent=None):
        QWizard.__init__(self, parent)

        self.setupUi(self)
        self.page_title()
        self._num_pages = len(self.pageIds())
        self._base_win_title = self.windowTitle()

        # Current profile
        self.curr_p = current_profile()

        if self.curr_p is None:
            QMessageBox.critical(
                self,
                self.tr('Missing Profile'),
                self.tr("No profile has been specified")
            )
            self.reject()

        # Entities
        self.entity_obj = self.curr_p.entity('Scheme')

        if self.entity_obj is None:
            QMessageBox.critical(
                self,
                self.tr('Missing Scheme Entity'),
                self.tr("The scheme entity is missing in the profile.")
            )
            self.reject()

        # Entity model
        self.schm_model = entity_model(self.entity_obj)

        if self.schm_model is None:
            QMessageBox.critical(
                self,
                self.tr('Scheme Entity Model'),
                self.tr("The scheme entity model could not be generated.")
            )
            self.reject()

        # Intializing mappermixin
        MapperMixin.__init__(self, self.schm_model, self.entity_obj)

        # Populate lookup comboboxes
        self._populate_lookups()

        self.register_col_widgets()

    def _populate_combo(self, cbo, lookup_name):
        res = export_data(lookup_name)
        cbo.clear()
        cbo.addItem('')

        for r in res:
            cbo.addItem(r.value, r.id)

    def _populate_lookups(self):
        # Load lookup columns
        self._populate_combo(self.cbx_relv_auth, 'cb_check_lht_relevant_authority')

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
        self.wizardPage1.setSubTitle(self.tr('Please enter scheme information below. '
                                             'Note that the scheme number'
                                             'will be automatically generated'))
        self.wizardPage2.setSubTitle(self.tr('Please browse for list of holde'
                                             'rs file'))
        self.wizardPage.setSubTitle(self.tr
                                    ('Review the summary of the previous '
                                     'steps. Click Back to edit information of '
                                     'Finish to save'))
        self.wizardPage_4.setSubTitle(self.tr(
            'Review the summary of the previous steps. Click Back to edit '
            'information of Finish to save'))

    def on_page_changed(self, idx):
        """
         Show the page id that is loaded
        """
        page_num = idx + 1
        win_title = u'{0} - Step {1} of {2}'.format(self._base_win_title,
                                                    str(page_num),
                                                    str(self._num_pages))
        self.setWindowTitle(win_title)
        self.save_data()

    def browse_holders_file(self):
        """
        Browse for the holders file in the file directory
        """
        holders_file = QFileDialog.getOpenFileName(self, "Open Holder's File",
                                                   '~/',
                                                   " Excel Files *.xls *xlsx")
        if holders_file:
            self.lnEdit_hld_path.setText(holders_file)
            self.tw_hld_prv.load_workbook(holders_file)

    def upload_multiple_files(self):
        """
        Browse and select multiple documents
        """
        all_files_dlg = QFileDialog.getOpenFileNames(self,
                                                     "Open Holder's File",
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

    def register_col_widgets(self):
        """
        Registers the column widgets
        """
        # Get the table columns and add mapping
        self.addMapping('scheme_name', self.lnedit_schm_nam)
        self.addMapping('date_of_approval', self.date_apprv)
        self.addMapping('date_of_establishment', self.date_establish)
        self.addMapping('relevant_authority', self.cbx_relv_auth)
        self.addMapping('region', self.cbx_region)
        self.addMapping('township', self.lnedit_twnshp)
        self.addMapping('registration_division', self.cbx_reg_div)
        self.addMapping('area', self.dbl_spinbx_block_area)

    def validateCurrentPage(self):
        current_id = self.currentId()
        ret_status = False

        if current_id == 0:
            # Check if all fields have been specified
            return True
        elif current_id == 1:
            # Check if the holders file has been uploaded
            return True
        elif current_id == 2:
            # Check if all documents have been uploaded
            return True
        elif current_id == 3:
            # This is the last page
            try:
                self.save_scheme()
                # Add other functionality

                ret_status = True
            except Exception as err:
                QMessageBox.critical(
                    self,
                    self.tr('Error in Saving Scheme'),
                    unicode(err)
                )
        return ret_status

    def save_scheme(self):
        """
        Save scheme information to the database
        """
        self.submit()


if __name__ == '__main__':
    import sys

    app = QWizard.QApplication(sys.argv)
    wizard = LodgementWizard()
    wizard.show()
    sys.exit(app.exec_())
