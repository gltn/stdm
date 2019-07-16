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
from os.path import expanduser
from PyQt4.QtCore import *
from PyQt4.QtGui import (
    QWizard,
    QFileDialog,
    QMessageBox,
    QStringListModel,
    QTreeWidget,
    QTreeView,
    QPushButton,
    QTreeWidgetItem)

from stdm.data.pg_utils import (
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
        self.notif_obj = self.curr_p.entity('Notification')

        if self.entity_obj is None:
            QMessageBox.critical(
                self,
                self.tr('Missing Scheme Entity'),
                self.tr("The scheme entity is missing in the profile.")
            )
            self.reject()

        # Scheme entity model
        self.schm_model = entity_model(self.entity_obj)

        # Notification entity model
        self.notif_model = entity_model(self.notif_obj)

        if self.schm_model is None:
            QMessageBox.critical(
                self,
                self.tr('Scheme Entity Model'),
                self.tr("The scheme entity model could not be generated.")
            )
            self.reject()

        # Intializing mappermixin for saving attribute data
        MapperMixin.__init__(self, self.schm_model, self.entity_obj)

        # Configure notification bar
        self.notif_bar = NotificationBar(self.vlNotification)

        # Browse holders excel file
        self.btn_brws_hld.clicked.connect(self.browse_holders_file)

        # Browse multiple files
        self.btn_upload_dir.clicked.connect(self.upload_multiple_files)

        # Populate lookup comboboxes
        self._populate_lookups()

        self.register_col_widgets()

        # Scheme number
        self.scheme_num()

    def _populate_combo(self, cbo, lookup_name):
        res = export_data(lookup_name)
        cbo.clear()
        cbo.addItem('')

        for r in res:
            cbo.addItem(r.value, r.id)

    def _populate_lookups(self):
        # Load lookup columns
        self._populate_combo(self.cbx_relv_auth, 'cb_check_lht_relevant_authority')

        self._populate_combo(self.cbx_lro, 'cb_check_lht_land_rights_office')

        self._populate_combo(self.cbx_region, 'cb_check_lht_region')

        self._populate_combo(self.cbx_reg_div, 'cb_check_lht_reg_division')

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
            'information or Finish to save'))

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

    def supporting_documents(self):
        """
        This is used in uploading and viewing of the scheme supporting documents
        """
        notice_btn = QPushButton(self.tr("browse..."))
        expl_btn = QPushButton(self.tr("browse..."))
        councl_btn = QPushButton(self.tr("browse..."))
        tiltle_btn = QPushButton(self.tr("browse..."))
        covr_btn = QPushButton(self.tr("browse..."))
        lst_btn = QPushButton(self.tr("browse..."))
        condt_btn = QPushButton(self.tr("browse..."))
        digl_btn = QPushButton(self.tr("browse..."))

        # Defining list of items
        data = {
            'Document': [self.tr('Notice of Establishmment of Scheme'),
                         self.tr('Explanatory Report'),
                         self.tr('Council Resolution(Approval of Scheme'),
                         self.tr('Title Deed of Blockerf'),
                         self.tr('Cover Certificate'),
                         self.tr('List of Potential Holders'),
                         self.tr('Document(s) Imposing Conditions'),
                         self.tr('Digital Layout Plan')],
            'Browse': [notice_btn, expl_btn, councl_btn, tiltle_btn, covr_btn,
                       lst_btn, condt_btn, digl_btn],
            'Status': [],
            'View': [],
        }

    def upload_multiple_files(self):
        """
        Browse and select multiple documents
        """
        all_files_dlg = QFileDialog.getOpenFileNames(self,
                                                     "Open Holder's File",
                                                     '~/', " *.pdf")

    def scheme_num(self):
        """
        Generate random scheme number
        """
        self.lnedit_schm_num.setText('NMBWND.0001')
        # Use random and string library in generating scheme number

    def register_col_widgets(self):
        """
        Registers the column widgets
        """
        # Get the table columns and add mapping
        self.addMapping(
            'scheme_number',
            self.lnedit_schm_num,
            pseudoname='Scheme Number'
        )
        self.addMapping(
            'scheme_name',
            self.lnedit_schm_nam,
            pseudoname='Scheme Name'
        )
        self.addMapping(
            'date_of_approval',
            self.date_apprv,
            pseudoname='Approval Date'
        )
        self.addMapping(
            'date_of_establishment',
            self.date_establish,
            pseudoname='Establishment Date'
        )
        self.addMapping(
            'relevant_authority',
            self.cbx_relv_auth,
            pseudoname='Relevant Authority'
        )
        self.addMapping(
            'region',
            self.cbx_region,
            pseudoname='Region'
        )
        self.addMapping(
            'township',
            self.lnedit_twnshp,
            pseudoname='Township'
        )
        self.addMapping(
            'registration_division',
            self.cbx_reg_div,
            pseudoname='Registration Division'
        )
        self.addMapping(
            'area',
            self.dbl_spinbx_block_area,
            pseudoname='Area'
        )

    def validateCurrentPage(self):
        current_id = self.currentId()
        ret_status = False
        self.notif_bar.clear()

        if current_id == 0:
            # Check if values have been specified for the attribute widgets
            errors = self.validate_all()
            if len(errors) == 0:
                ret_status = True

        elif current_id == 1:
            # TODO --- Use RegExp validator
            if not self.lnEdit_hld_path.text():
                self.notif_bar.insertWarningNotification(
                    self.tr(
                        'Please choose the Excel file containing Holders '
                        'information'
                    )
                )
            else:
                ret_status = True
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

    def create_notification(self):
        """
        Populate notification table
        """
        # Get the table columns and add mapping
        self.addMapping('status', '2')
        self.addMapping('source_user_id', 'src_usr_id')
        self.addMapping('target_use_id', 'trgt_usr_id')
        self.addMapping('content', 'notification')
        self.addMapping('timestamp', QDateTime.currentDateTime(self).toString())


class SchemeSummary(QTreeView, LodgementWizard):
    """
    Widget that displays scheme information.
    """

    def __init__(self, parent=None):
        super(QTreeView, self).__init__(parent)

    def set_scheme(self):
        """
        Defines static and dynamic variables to be shown in the summary.
        """
        pointListBox = QTreeWidget()
        header = QTreeWidgetItem(['documents', 'data', 'files'])
        pointListBox.setHeaderItem(header)
        root = QTreeWidgetItem(pointListBox, ["root"])
        A = QTreeWidgetItem(root, ["A"])
        barA = QTreeWidgetItem(A, ["items", "items1"])
        barZ = QTreeWidgetItem(A, ["items", "items1"])
        pointListBox.show()

    def refresh(self):
        """
        Upating data in the summary when user changes or updates in the wizard
        """
        pass
