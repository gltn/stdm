"""
/***************************************************************************
Name                 : Scheme Lodgement Wizard
Description          : Dialog for lodging a new scheme.
Date                 : 01/July/2019
copyright            : (C) 2019
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
from time import strftime
from PyQt4.Qt import Qt
from PyQt4.QtGui import (
    QWizard,
    QFileDialog,
    QMessageBox,
    QAbstractItemView,
    QListView
)

from stdm.data.pg_utils import (
    export_data,
    fetch_with_filter,
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

        # Flag for checking if document type has been loaded
        self._suporting_docs_loaded = False

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
        self.relv_auth_obj = self.curr_p.entity('Relevant_authority')
        self.chk_relv_auth_type_obj = self.curr_p.entity('check_lht_relevant_authority')
        self.chk_region_obj = self.curr_p.entity('check_lht_region')

        if self.entity_obj is None:
            QMessageBox.critical(
                self,
                self.tr('Missing Scheme Entity'),
                self.tr("The scheme entity is missing in the profile.")
            )
            self.reject()

        # Entity models
        self.schm_model = entity_model(self.entity_obj)
        self.notif_model = entity_model(self.notif_obj)
        self.relv_auth_model = entity_model(self.relv_auth_obj)
        self.chk_relv_auth_typ_model = entity_model(self.chk_relv_auth_type_obj)
        self.chk_region_model = entity_model(self.chk_region_obj)

        self.relv_entity_object = self.relv_auth_model()

        if self.schm_model is None:
            QMessageBox.critical(
                self,
                self.tr('Scheme Entity Model'),
                self.tr("The scheme entity model could not be generated.")
            )
            self.reject()

        # Initializing mappermixin for saving attribute data
        MapperMixin.__init__(self, self.schm_model, self.entity_obj)

        # Configure notification bar
        self.notif_bar = NotificationBar(self.vlNotification)

        # Connect signals
        self.btn_brws_hld.clicked.connect(self.browse_holders_file)
        self.btn_upload_dir.clicked.connect(self.upload_multiple_files)
        self.currentIdChanged.connect(self.on_page_changed)
        self.cbx_region.currentIndexChanged.connect(
            self.update_relevant_authority)
        self.cbx_relv_auth.currentIndexChanged.connect(
            self.update_relevant_authority)

        self.cbx_relv_auth_name.currentIndexChanged.connect(
            self.on_ra_name_changed)

        # Populate lookup comboboxes
        self._populate_lookups()

        # Specify MapperMixin widgets
        self.register_col_widgets()

        # Notification details
        self._notif_status = 2
        self._notif_content = self.tr("Lodgement of scheme has been completed.")

    def _populate_combo(self, cbo, lookup_name):
        res = export_data(lookup_name)
        cbo.clear()
        cbo.addItem('')

        for r in res:
            cbo.addItem(r.value, r.id)

    def _populate_lookups(self):
        """
        Populate combobox dropdowns with values to be displayed when user
        clicks the dropdown
        """
        relv_auth_type_tbl = 'cb_check_lht_relevant_authority'
        lro_tbl = 'cb_check_lht_land_rights_office'
        region_tbl = 'cb_check_lht_region'
        reg_div_tbl = 'cb_check_lht_reg_division'

        # Check if the tables exists
        self._populate_combo(self.cbx_relv_auth,
                             relv_auth_type_tbl)
        self._populate_combo(self.cbx_lro,
                             lro_tbl)
        self._populate_combo(self.cbx_region,
                             region_tbl)
        self._populate_combo(self.cbx_reg_div,
                             reg_div_tbl)

    def update_relevant_authority(self):
        """
        Slot for updating the Relevant Authority combobox based on the
        selections made in the two previous comboboxes
        """
        # Clear dropdown elements
        clr_cbx_auth_name = self.cbx_relv_auth_name.clear()
        # Get the region ID
        region_id = self.cbx_region.itemData(self.cbx_region.currentIndex())
        # Get the relevant authority ID
        ra_id_type = self.cbx_relv_auth.itemData(
            self.cbx_relv_auth.currentIndex()
        )

        # Check if region combobox is selected
        if not region_id and not ra_id_type:
            return

        # Initial clear elements
        self.cbx_relv_auth_name.clear()

        # Add an empty itemData
        self.cbx_relv_auth_name.addItem('')

        # Query object for filtering items on name of relevant authority
        # combobox based on selected items in region and type
        res = self.relv_entity_object.queryObject().filter(
            self.relv_auth_model.region == region_id,
            self.relv_auth_model.type_of_relevant_authority ==
            ra_id_type
        ).all()

        # Looping through the results to get details
        for r in res:
            authority_name = r.name_of_relevant_authority
            authority_id = r.id
            l_value = r.last_value
            code = r.au_code

            # Add the items to combo
            # Date will contain tuple(ID, code and last value)
            self.cbx_relv_auth_name.addItem(
                authority_name,
                (authority_id, code, l_value)
            )

    def on_ra_name_changed(self):
        """
        Slot for updating the scheme number based on selection of name of
        relevant authority combobox selection
        """
        # Clear scheme number
        self.lnedit_schm_num.clear()

        if not self.cbx_relv_auth_name.currentText():
            return

        id, code, last_value = self.cbx_relv_auth_name.itemData(
            self.cbx_relv_auth_name.currentIndex()
        )

        scheme_code = self._gen_scheme_number(code, last_value)
        self.lnedit_schm_num.setText(scheme_code)

    def _gen_scheme_number(self, code, last_value):
        # Generates a new scheme number
        if not last_value:
            last_value = 0
        last_value += 1
        scheme_code = u'{0}.{1}'.format(code, str(last_value).zfill(3))
        
        return scheme_code

    def update_scheme_number(self):
        """
        Check for sequence number in the database and perform an incremenet
        """
        pass

    def page_title(self):
        """
        Set page title and subtitle instructions
        """
        # Set page titles
        self.wizardPage1.setTitle('New Land Hold Scheme')
        self.wizardPage2.setTitle('Import Holders')
        self.wizardPage.setTitle('Upload Documents')
        self.wizardPage_4.setTitle('Summary')

        # Set page subtitles
        self.wizardPage1.setSubTitle(self.tr('Please enter scheme information'
                                             ' below. '
                                             'Note that the scheme number'
                                             'will be automatically generated'
                                             )
                                     )
        self.wizardPage2.setSubTitle(self.tr('Please browse for list of holde'
                                             'rs file'))
        self.wizardPage_4.setSubTitle(self.tr(
            'Review the summary of the previous steps. Click Back to edit '
            'information or Finish to save'))

    def on_page_changed(self, idx):
        """
        Slot raised when the page with the given id is loaded.
        """
        page_num = idx + 1
        win_title = u'{0} - Step {1} of {2}'.format(self._base_win_title,
                                                    str(page_num),
                                                    str(self._num_pages))
        self.setWindowTitle(win_title)

        # Load scheme supporting documents
        if idx == 2:
            self._load_scheme_document_types()

    def browse_holders_file(self):
        """
        Browse for the holders file in the file directory
        """
        holders_file = QFileDialog.getOpenFileName(self,
                                                   "Browse Holder's File",
                                                   "~/",
                                                   "CSV Files (*.csv);;"
                                                   "Excel Files (*.xls *xlsx)"
                                                   )
        if holders_file:
            self.lnEdit_hld_path.setText(holders_file)
            self.tw_hld_prv.load_workbook(holders_file)

    def _load_scheme_document_types(self):
        """
        This is used in uploading and viewing of the scheme supporting
        documents
        """
        doc_type_table = 'cb_check_scheme_document_type'

        # Check if the document type lookup exists
        doc_type_entity = self.curr_p.entity_by_name(doc_type_table)
        if doc_type_entity is None:
            QMessageBox.critical(
                self,
                self.tr('Scheme Document Type Lookup'),
                self.tr(
                    'The lookup table containing the document types is '
                    'missing.'
                )
            )
            self.tbw_documents.setEnabled(False)

            return

        # No need of fetching the documents again if already done before
        if self._suporting_docs_loaded:
            return

        doc_res = export_data('cb_check_scheme_document_type')

        # Add the documents types to the view
        for d in doc_res:
            doc_type = d.value
            self.tbw_documents.add_document_type(doc_type)

        self._suporting_docs_loaded = True

    def upload_multiple_files(self):
        """
        Browse and select multiple documents
        """
        all_files_dlg = QFileDialog.getOpenFileNames(self,
                                                     "Open Holder's File",
                                                     '~/', " *.pdf")

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
            'region',
            self.cbx_region,
            pseudoname='Region'
        )
        self.addMapping(
            'relevant_authority',
            self.cbx_relv_auth,
            pseudoname='Relevant Authority Type'
        )
        self.addMapping(
            'relevant_authority_name',
            self.cbx_relv_auth_name,
            pseudoname='Relevant Authority Name'
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

    def create_notification(self):
        """
        Populate notification table
        """
        # Get the table columns and add mapping
        self.addMapping(
            'status',
            self._notif_status,
            pseudoname='status'
        )
        self.addMapping(
            'source_user_id',
            self.source_user_id,
            pseudoname='source user'
        )
        self.addMapping(
            'target_use_id',
            self.target_user_id,
            pseudoname='target user'
        )
        self.addMapping(
            'content',
            self._notif_content,
            pseudoname='content'
        )
        self.addMapping(
            'timestamp',
            str(strftime("%Y-%m-%d %H:%M:%S")),
            pseudoname='timestamp'
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
            self.populate_summary()
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

    def populate_summary(self):
        """
        Populating the scheme summary widget with values from the user input
        """
        # Scheme
        self.tr_summary.scm_num.setText(1, self.lnedit_schm_num.text()
                                        )
        self.tr_summary.scm_name.setText(1,
                                         self.lnedit_schm_nam.text()
                                         )
        self.tr_summary.scm_date_apprv.setText(1,
                                               self.date_apprv.text()
                                               )
        self.tr_summary.scm_date_est.setText(1,
                                             self.date_establish.text()
                                             )
        self.tr_summary.scm_region.setText(1, self.cbx_region.currentText()
                                           )
        self.tr_summary.scm_ra_type.setText(1,
                                            self.cbx_relv_auth.currentText()
                                            )
        self.tr_summary.scm_ra_name.setText(
            1,
            self.cbx_relv_auth_name.currentText()
        )
        self.tr_summary.scm_lro.setText(1, self.cbx_lro.currentText()
                                        )
        self.tr_summary.scm_township.setText(1, self.lnedit_twnshp.text()
                                             )
        self.tr_summary.scm_reg_div.setText(1, self.cbx_reg_div.currentText()
                                            )
        self.tr_summary.scm_blk_area.setText(1,
                                             self.dbl_spinbx_block_area.text()
                                             )

    def save_scheme(self):
        """
        Save scheme information to the database
        """
        self.submit()
