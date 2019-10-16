"""
/***************************************************************************
Name                 : SchemeSummaryWidget
Description          : A table widget that provides a quick access menus for
                       uploading and viewing supporting documents.
Date                 : 16/July/2019
copyright            : (C) 2019 by UN-Habitat and implementing partners.
                       See the accompanying file CONTRIBUTORS.txt in the root
email                : stdm@unhabitat.org
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
from cmislib.exceptions import (
    CmisException
)
from PyQt4.QtCore import (
    QDate,
    QDir,
    Qt,
    SIGNAL
)
from PyQt4.QtGui import (
    QDialog,
    QFileDialog,
    QMessageBox,
    QProgressDialog,
    QWizard
)
from qgis.core import QgsApplication

from stdm.ui.customcontrols.documents_table_widget import (
    DirDocumentTypeSelector
)
from stdm.data.pg_utils import (
    export_data,
    fetch_with_filter,
)
from stdm.network.cmis_manager import (
    CmisDocumentMapperException,
    CmisManager,
    CmisEntityDocumentMapper
)
from stdm.settings.registryconfig import (
    last_document_path,
    set_last_document_path
)
from stdm.data.flts.validators import(
    EntityVectorLayerValidator,
    ValidatorException
)
from stdm.data.flts.db_importer import (
    EntityVectorLayerDbImporter
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
        # Equate number of pages in wizard to page IDs
        self._num_pages = len(self.pageIds())
        self._base_win_title = self.windowTitle()

        # Current profile
        self.curr_p = current_profile()

        # Flag for checking if document type has been loaded
        self._supporting_docs_loaded = False

        # Entity names
        self._sch_entity_name = 'Scheme'
        self._rel_auth_entity_name = 'Relevant_authority'
        self._rel_auth_chk_entity_name = 'check_lht_relevant_authority'
        self._rgn_chk_entity_name = 'check_lht_region'
        self._reg_div_chk_entity_name = 'check_lht_reg_division'
        self._scheme_doc_type_lookup = 'cb_check_scheme_document_type'
        self._holders_entity_name = 'Holder'

        # Check if the current profile exists
        if self.curr_p is None:
            QMessageBox.critical(
                self,
                self.tr('Missing Profile'),
                self.tr("No profile has been specified")
            )
            self.reject()

        # Scheme entity
        self.sch_entity = self.curr_p.entity(self._sch_entity_name)

        # Entity models
        self.schm_model, self._scheme_doc_model = entity_model(
            self.sch_entity,
            with_supporting_document=True
        )

        # Check if scheme entity models exist
        if self.schm_model is None:
            QMessageBox.critical(
                self,
                self.tr('Scheme Entity Model'),
                self.tr("The scheme entity model could not be generated.")
            )
            self.reject()

        # Entity objects
        self._relv_auth_entity = None
        self._relevant_auth_lookup = None
        self._region_lookup = None
        self._reg_div_lookup = None
        self._holder_entity = None

        # Entity models
        self._relevant_auth_type_model = None
        self._region_lookup_model = None
        self._relevant_auth_model = None
        self._regdiv_lookup_model = None

        # Initialize Mappermixin for saving attribute data
        MapperMixin.__init__(self, self.schm_model, self.sch_entity)

        # Configure notification bars
        self.notif_bar = NotificationBar(self.vlNotification)
        self.docs_notif_bar = NotificationBar(self.vlNotification_docs)
        self.holders_notif_bar = NotificationBar(self.vlNotification_holders)

        # CMIS stuff for document management
        self._cmis_mgr = CmisManager()

        # Mapper will be set in 1st page initialization
        self._cmis_doc_mapper = None

        # Last int value used for generating the scheme number
        self._abs_last_scheme_value = None

        # Validator for holders data
        self._holders_validator = None

        # Progress dialog for showing validation status
        self._h_validation_prog_dlg = QProgressDialog(self)

        # Database importer
        self._holder_importer = None

        # Connect signals
        self.btn_brws_hld.clicked.connect(self.browse_holders_file)
        self.btn_upload_dir.clicked.connect(self.on_upload_multiple_files)
        self.currentIdChanged.connect(self.on_page_changed)
        self.cbx_region.currentIndexChanged.connect(
            self.update_relevant_authority)
        self.cbx_relv_auth.currentIndexChanged.connect(
            self.update_relevant_authority)
        self.cbx_relv_auth_name.currentIndexChanged.connect(
            self.on_ra_name_changed)
        self.btn_reload_holders.clicked.connect(
            self.load_holders_file
        )
        self.chk_holders_validate.toggled.connect(
            self.on_validate_holders
        )

        # Populate lookup comboboxes
        self._populate_lookups()

        # Set date limits
        self._configure_date_controls()

        # Specify MapperMixin widgets
        self.register_col_widgets()

    def _populate_combo(self, cbo, lookup_name):
        """
        Populates comboboxes with items from the database
        :param cbo: Combobox object
        :param lookup_name: name of the lookup table
        """
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
        # Check if the tables exists
        self._populate_combo(self.cbx_region,
                             'cb_check_lht_region')
        self._populate_combo(self.cbx_relv_auth,
                             'cb_check_lht_relevant_authority')
        self._populate_combo(self.cbx_lro,
                             'cb_check_lht_land_rights_office')
        self._populate_combo(self.cbx_reg_div,
                             'cb_check_lht_reg_division')

        # Sort region combobox items
        self.cbx_region.model().sort(0)

    def _configure_date_controls(self):
        # Set maximum dates for date widgets
        self.date_apprv.setMaximumDate(QDate.currentDate())
        self.date_establish.setMaximumDate(QDate.currentDate())

        # Set the current dates
        self.date_establish.setDate(QDate.currentDate())
        self.date_apprv.setDate((QDate.currentDate()))

    def _update_entities_and_models(self):
        # Update the entity objects and db models related to selecting
        # relevant authority.
        if not self._relv_auth_entity:
            self._relv_auth_entity = self.curr_p.entity(
                self._rel_auth_entity_name
            )
        if not self._relevant_auth_lookup:
            self._relevant_auth_lookup = self.curr_p.entity(
                self._rel_auth_chk_entity_name
            )
        if not self._region_lookup:
            self._region_lookup = self.curr_p.entity(
                self._rgn_chk_entity_name
            )
        if not self._reg_div_lookup:
            self._reg_div_lookup = self.curr_p.entity(
                self._reg_div_chk_entity_name
            )

        # Check if entities exist
        if self._relv_auth_entity is None:
            QMessageBox.critical(
                self,
                self.tr('Missing Relevant Authority Entity'),
                self.tr("The relevant authority entity is missing in the "
                        "profile.")
            )
            self.reject()
        elif self._relevant_auth_lookup is None:
            QMessageBox.critical(
                self,
                self.tr('Missing Relevant Authority Entity Lookup'),
                self.tr("The relevant authority entity lookup is missing in the "
                        "profile.")
            )
            self.reject()
        elif self._region_lookup is None:
            QMessageBox.critical(
                self,
                self.tr('Missing Relevant Authority Entity Lookup'),
                self.tr("The relevant authority entity lookup is missing in the "
                        "profile.")
            )
            self.reject()
        elif self._reg_div_lookup is None:
            QMessageBox.critical(
                self,
                self.tr('Missing Relevant Authority Entity Lookup'),
                self.tr("The relevant authority entity lookup is missing in the "
                        "profile.")
            )
            self.reject()

        # Entity models
        if not self._relevant_auth_type_model:
            self._relevant_auth_type_model = entity_model(
                self._relevant_auth_lookup
            )
        if not self._region_lookup_model:
            self._region_lookup_model = entity_model(self._region_lookup)
        if not self._relevant_auth_model:
            self._relevant_auth_model = entity_model(self._relv_auth_entity)
        if not self._regdiv_lookup_model:
            self._regdiv_lookup_model = entity_model(self._reg_div_lookup)

    def update_relevant_authority(self):
        """
        Slot for updating the Relevant Authority combobox based on the
        selections made in the two previous comboboxes
        """
        # Update the entity object and model references
        self._update_entities_and_models()

        # Entity object
        relv_entity_obj = self._relevant_auth_model()

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
        self.cbx_reg_div.clear()

        # Add an empty itemData
        self.cbx_relv_auth_name.addItem('')
        self.cbx_reg_div.addItem('')

        # Query object for filtering items on name of relevant authority
        # combobox based on selected items in region and type
        res = relv_entity_obj.queryObject().filter(
            self._relevant_auth_model.region == region_id,
            self._relevant_auth_model.type_of_relevant_authority ==
            ra_id_type
        ).all()

        # Looping through the results to get details
        for r in res:
            authority_name = r.name_of_relevant_authority
            authority_id = r.id
            code = r.au_code
            last_val = r.last_val
            reg_divs = []
            for i in r.cb_check_lht_reg_division_collection:
                reg_divs.append(
                    (i.id, i.value)
                )
            # Add items to combobox
            # Data will contain tuple(IDm code and registration division)
            self.cbx_relv_auth_name.addItem(
                authority_name, (
                    authority_id, code, last_val, reg_divs
                )
            )

    def on_ra_name_changed(self):
        """
        Slot for updating the scheme number based on selection of name of
        relevant authority combobox selection
        """
        # Clear scheme number
        self.lnedit_schm_num.clear()
        self.cbx_reg_div.clear()

        if not self.cbx_relv_auth_name.currentText():
            return

        authority_id, code, last_value, reg_divs = self.cbx_relv_auth_name.itemData(
            self.cbx_relv_auth_name.currentIndex()
        )

        # Registration division
        self.cbx_reg_div.addItem('')

        for regdiv in reg_divs:
            self.cbx_reg_div.addItem(regdiv[1], regdiv[0])

        # Select the first item automatically if there is only one division
        if self.cbx_reg_div.count() ==  2:
            self.cbx_reg_div.setCurrentIndex(1)

        scheme_code = self._gen_scheme_number(code, last_value)
        self.lnedit_schm_num.setText(scheme_code)

    def _gen_scheme_number(self, code, last_value):
        # Generates a new scheme number
        if not last_value:
            last_value = 0
        last_value += 1
        self._abs_last_scheme_value = last_value
        scheme_code = u'{0}.{1}'.format(code, str(last_value).zfill(3))

        return scheme_code

    def page_title(self):
        """
        Insert page subtitles which contain instructions to the user.
        """
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
        win_title = u'{0} - Step {1} of {2}'.format(
            self._base_win_title,
            str(page_num),
            str(self._num_pages)
        )
        self.setWindowTitle(win_title)

        # First page
        # Set entity document mapper if connection to CMIS is successful
        if idx == 0:
            self._init_cmis_doc_mapper()

        # Load scheme supporting documents
        elif idx == 1:
            self._load_scheme_document_types()

            # Disable widget if doc mapper could not be initialized
            if not self._cmis_doc_mapper:
                self.tbw_documents.setEnabled(False)

        # Initialize holders stuff
        elif idx == 2:
            self._init_holder_helpers()

        # Last page
        elif idx == 3:
            # Populate summary widget
            self.populate_summary()

    def _init_holder_helpers(self):
        # Init helper classes for holders data
        if not self._holder_entity:
            self._holder_entity = self.curr_p.entity(
                self._holders_entity_name
            )
            if not self._holder_entity:
                msg = self.tr(
                    'Could not find the Holders entity.\nPlease check to '
                    'confirm that it has been created in the configuration'
                )
                QMessageBox.critical(
                    self,
                    self.tr('Missing Holders Entity'),
                    msg
                )

                return

    def _init_cmis_doc_mapper(self):
        # Initializes CMIS stuff
        conn_status = self._cmis_mgr.connect()
        if not conn_status:
            msg = self.tr(
                'Failed to connect to the CMIS Service.\nPlease check the '
                'URL and login credentials for the CMIS service.'
            )
            QMessageBox.critical(
                self,
                self.tr(
                    'CMIS Server Error'
                ),
                msg
            )
        if conn_status:
            if not self._cmis_doc_mapper:
                try:
                    self._cmis_doc_mapper = CmisEntityDocumentMapper(
                        cmis_manager=self._cmis_mgr,
                        doc_model_cls=self._scheme_doc_model,
                        entity_name=self._sch_entity_name
                    )

                    # Set the CMIS document mapper in document widget
                    self.tbw_documents.cmis_entity_doc_mapper = \
                        self._cmis_doc_mapper
                except CmisDocumentMapperException as cm_ex:
                    QMessageBox.critical(
                        self,
                        self.tr('CMIS Server Error'),
                        str(cm_ex)
                    )
                except CmisException as c_ex:
                    QMessageBox.critical(
                        self,
                        self.tr('CMIS Server Error'),
                        c_ex.status
                    )

    def browse_holders_file(self):
        """
        Browse for the holders file in the file directory
        """
        last_doc_path = last_document_path()
        if not last_doc_path:
            last_doc_path = '~/'

        holders_file = QFileDialog.getOpenFileName(
            self,
            'Browse Holders File',
            last_doc_path,
            'Excel File (*.xls *xlsx);;CSV (Comma Delimited) (*.csv)'
        )

        if holders_file:
            set_last_document_path(holders_file)
            self.lnEdit_hld_path.setText(holders_file)
            self.load_holders_file()

    def load_holders_file(self):
        """
        Load the holders data into the table view based on the file specified
        in the path textbox.
        """
        h_path = self.lnEdit_hld_path.text()
        if not h_path:
            QMessageBox.warning(
                self,
                self.tr('Empty File Path'),
                self.tr(
                    'Please specify the path to the Holders file.'
                )
            )

            return

        self.tw_hld_prv.load_holders_file(h_path)

        curr_sheet = self.tw_hld_prv.current_sheet_view()

        # Clear validation result label
        self.lbl_validation_description.clear()

        # Check if a signal has been defined in the sheet view and disconnect
        # Use old-style signal to check if signal is connected
        receivers = curr_sheet.receivers(SIGNAL('itemSelectionChanged()'))
        # Disconnect all slots for the itemSelectionChanged signal
        if receivers > 0:
            curr_sheet.itemSelectionChanged.disconnect()

        # Reconnect signal
        curr_sheet.itemSelectionChanged.connect(
            self._on_holders_table_selection_changed
        )

        # Create validator object
        ds = self.tw_hld_prv.current_sheet_view().vector_layer
        self._holders_validator = EntityVectorLayerValidator(
            self._holder_entity,
            ds,
            parent=self
        )

        # Connect signals
        self._holders_validator.featureValidated.connect(
            self._on_holder_feat_validated
        )
        self._holders_validator.validationFinished.connect(
            self._on_holder_validation_complete
        )

        # Create holder importer
        self._holder_importer = EntityVectorLayerDbImporter(
            self._holder_entity,
            ds,
            unique_cols=['holder_identifier'],
            parent=self
        )

        # Perform validation immediately after loading the data
        if self.chk_holders_validate.isChecked():
            self._validate_holders()

    def on_validate_holders(self, toggled):
        """
        Slot raised when the checkbox for validating holders data is
        checked/unchecked.
        :param toggled: Toggle status
        :type toggled: bool
        """
        # Notify user that validation will be done prior to moving to
        # the next page.
        if not toggled:
            msg = 'Validation of the holders data will be performed prior to ' \
                  'loading the summary page upon clicking Next.'
            self.holders_notif_bar.insertInformationNotification(msg)

    def _validate_holders(self):
        # Validates holders data
        # Reset the validator
        self._holders_validator.reset()

        try:
            # Performs some pre-validation checks.
            # Check if mandatory columns have been mapped
            passed_mandatory, cols = self._holders_validator.validate_mandatory()
            if not passed_mandatory:
                cols_str = '\n'.join(cols)
                msg = self.tr(
                    'The following mandatory columns have not been '
                    'mapped: {0}'.format(cols_str)
                )
                QMessageBox.critical(
                    self,
                    self.tr('Missing Mandatory Columns'),
                    msg
                )

                return

            # Check if at least one data source column has been mapped
            ds_mapped = self._holders_validator.validate_mapped_ds_columns()
            if not ds_mapped:
                msg = 'At least one column in the data source has to be ' \
                      'mapped.'
                QMessageBox.critical(
                    self,
                    self.tr('Mapped Data Source Columns'),
                    msg
                )

                return

            # Check if at least one entity column has been mapped
            entity_mapped = self._holders_validator.validate_entity_columns()
            if not entity_mapped:
                msg = 'At least one entity column has to be mapped.'
                QMessageBox.critical(
                    self,
                    self.tr('Mapped Entity Columns'),
                    msg
                )

                return

            # Set progress dialog properties
            self._h_validation_prog_dlg.setMinimum(0)
            self._h_validation_prog_dlg.setMaximum(
                self._holders_validator.count
            )
            self._h_validation_prog_dlg.setWindowModality(
                Qt.WindowModal
            )
            self._h_validation_prog_dlg.setLabelText(
                self.tr('Validating holders records in the data source...')
            )
            self._h_validation_prog_dlg.setWindowTitle(
                self.tr('Validation Progress')
            )
            # Connect canceled signal
            self._h_validation_prog_dlg.canceled.connect(
                self._on_validation_canceled
            )
            self._h_validation_prog_dlg.setValue(0)

            # Start the validation process
            self._holders_validator.start()

        except ValidatorException as ve:
            QMessageBox.critical(
                self,
                self.tr('Holders Validation Error'),
                unicode(ve)
            )

    def _on_holder_feat_validated(self, results):
        # Slot raised when a feature in the data source has been validated.
        # Highlight warning or error cells
        for r in results:
            if len(r.warnings) > 0 or len(r.errors) > 0:
                self.tw_hld_prv.current_sheet_view().\
                    highlight_validation_cell(r)

        # Update progress bar
        curr_val = self._h_validation_prog_dlg.value()
        curr_val += 1
        self._h_validation_prog_dlg.setValue(curr_val)

    def _on_holder_validation_complete(self):
        # Slot raised when holder validation is complete.
        num_features = self._holders_validator.count
        num_err_features = len(
            self._holders_validator.row_warnings_errors.keys()
        )

        # Get features that have warnings or errors
        msg = self.tr(
            u'Validation process complete.\nOut of the {0} features in the '
            u'data source, {1} have warnings and/or errors.\nPlease click '
            u'on a cell with an error icon in the preview table to get more '
            u'details.'.format(
                str(num_features),
                str(num_err_features)
            )
        )
        QMessageBox.information(
            self,
            self.tr('Validation Summary'),
            msg
        )

    def _on_validation_canceled(self):
        """"
        Slot raised when the validation process has been cancelled by the
        user.
        """
        if self._holders_validator:
            self._holders_validator.cancel()

    def _on_holders_table_selection_changed(self):
        # Slot raised when selection changes in the holders table widget.
        self.lbl_validation_description.setText('')

        # Check if validator has been initialized
        if not self._holders_validator:
            return

        curr_sheet = self.tw_hld_prv.current_sheet_view()
        sel_items = curr_sheet.selectedItems()
        if len(sel_items) == 0:
            return

        sel_item = sel_items[0]
        if self._holders_validator.status == \
                EntityVectorLayerValidator.NOT_STARTED:
            self.lbl_validation_description.setText(
                self.tr('Not validated')
            )
        elif self._holders_validator.status == \
                EntityVectorLayerValidator.NOT_COMPLETED:
            self.lbl_validation_description.setText(
                self.tr('UNKNOWN: Validation process not complete')
            )
        elif self._holders_validator.status == \
                EntityVectorLayerValidator.FINISHED:
            # Get data stored in the user role
            val_results = sel_item.data(Qt.UserRole)
            if not val_results:
                self.lbl_validation_description.setText(
                    self.tr('SUCCESSFUL')
                )
            else:
                combined_msgs = val_results.errors + val_results.warnings
                str_msgs = [str(vr) for vr in combined_msgs]
                self.lbl_validation_description.setText(
                    '\n- '.join(str_msgs)
                )

    def _load_scheme_document_types(self):
        """
        This is used in uploading and viewing of the scheme supporting
        documents
        """
        # Check if the document type lookup exists
        doc_type_entity = self.curr_p.entity_by_name(self._scheme_doc_type_lookup)
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
        if self._supporting_docs_loaded:
            return

        # Check Doc mapper
        if not self._cmis_doc_mapper:
            QMessageBox.critical(
                self,
                self.tr('CMIS Server Error'),
                self.tr(
                    'Document mapper could not be initialized, please check '
                    'the connection to the CMIS server.'
                )
            )
            self.tbw_documents.setEnabled(False)
            self.btn_upload_dir.setEnabled(False)

            return

        doc_res = export_data(self._scheme_doc_type_lookup)
        # Add the documents types to the view
        for d in doc_res:
            doc_type = d.value
            code = d.code
            type_id = d.id
            self.tbw_documents.add_document_type(doc_type)
            # Also add the types to the CMIS doc mapper
            self._cmis_doc_mapper.add_document_type(doc_type, code, type_id)

        self._supporting_docs_loaded = True

    def on_upload_multiple_files(self):
        """
        Browse and select multiple supporting documents.
        """
        last_doc_path = last_document_path()
        if not last_doc_path:
            last_doc_path = '~/'

        docs_dir = QFileDialog.getExistingDirectory(
            self,
            'Browse Supporting Documents Source Directory',
            last_doc_path
        )
        if not docs_dir:
            return

        # Check if there are files in the selected directory
        dir = QDir(docs_dir)
        els = dir.entryList(QDir.NoDot | QDir.NoDotDot | QDir.Files)
        if len(els) == 0:
            QMessageBox.warning(
                self,
                'Supporting Documents',
                self.tr('There are no files in the selected directory.')
            )
            return

        doc_types = self.tbw_documents.document_types()
        dir_doc_dlg = DirDocumentTypeSelector(
            docs_dir,
            doc_types,
            self
        )
        res = dir_doc_dlg.exec_()
        if res == QDialog.Accepted:
            # Get document types selected by the user
            selected_doc_types = dir_doc_dlg.selected_document_types

            # Upload the files
            for d_type, d_path in selected_doc_types.iteritems():
                self.tbw_documents.upload_document(
                    d_path,
                    d_type
                )

    def register_col_widgets(self):
        """
        Registers the column widgets to the table columns
        """
        # Get the table columns and add mapping
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
            'registration_division',
            self.cbx_reg_div,
            pseudoname='Registration Division'
        )
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
            'land_rights_office',
            self.cbx_lro,
            pseudoname='Land Rights Office'
        )
        self.addMapping(
            'township',
            self.lnedit_twnshp,
            pseudoname='Township'
        )
        self.addMapping(
            'area',
            self.dbl_spinbx_block_area,
            pseudoname='Area'
        )

    def create_notification(self):
        """
        Create a notification once the Scheme lodgement is completed.
        """
        # Notification entity
        notif_entity = self.curr_p.entity('Notification')

        # Check if entity exists
        if notif_entity is None:
            QMessageBox.critical(
                self,
                self.tr('Missing Notification Entity'),
                self.tr("The notification entity is missing in the "
                        "profile.")
            )
            self.reject()

        notification_model = entity_model(notif_entity)

        # Check if model exists
        if notification_model is None:
            QMessageBox.critical(
                self,
                self.tr('Notification Entity Model'),
                self.tr("The notification entity model could not be generated.")
            )
            self.reject()

        notif_entity_obj = notification_model()

        # Get the table columns and add mapping
        notif_entity_obj.status = 1
        notif_entity_obj.source_user_id = 1
        notif_entity_obj.target_user_id = 2
        notif_entity_obj.content = 'Lodgement'
        notif_entity_obj.timestamp = strftime("%m-%d-%Y %H:%M:%S")
        notif_entity_obj.save()

    def validate_block_area(self):
        """
        Check whether the block area value is zero
        """
        # Preset minimum value equals to zero
        min_value = self.dbl_spinbx_block_area.minimum()

        if self.dbl_spinbx_block_area.value() == min_value:
            self.notif_bar.insertWarningNotification(
                self.tr(
                    "Block Area value cannot be zero."
                )
            )
        else:
            return True

    def validateCurrentPage(self):
        # Validate each page
        current_id = self.currentId()
        ret_status = False
        self.notif_bar.clear()

        if current_id == 0:
            # Check if values have been specified for the attribute widgets
            errors = self.validate_all()
            if self.validate_block_area() and len(errors) == 0:
                ret_status = True

        # Holders page
        elif current_id == 2:
            if not self.lnEdit_hld_path.text():
                self.holders_notif_bar.clear()
                self.holders_notif_bar.insertWarningNotification(
                    self.tr(
                        'Please upload the file containing the Holders '
                        'information.'
                    )
                )
            else:
                status = self._holders_validator.status
                if status == EntityVectorLayerValidator.NOT_STARTED:
                    msg = self.tr(
                        'The holders data has not yet been validated.'
                    )
                elif status == EntityVectorLayerValidator.NOT_COMPLETED:
                    msg = self.tr(
                        'The validation process was interrupted.'
                    )
                elif status == EntityVectorLayerValidator.FINISHED:
                    # Check if there were errors (exclude warnings)
                    num_err_features = len(
                        self._holders_validator.row_errors.keys()
                    )
                    if num_err_features > 0:
                        msg = self.tr(
                            'There were errors in the last validation '
                            'process.'
                        )
                    else:
                        ret_status = True

                if not ret_status and msg:
                    # Give user the option to (re)run the validation process.
                    action_msg = self.tr(
                        'Do you want to (re)run the validation process?'
                    )
                    res= QMessageBox.warning(
                        self,
                        self.tr('Validation Status'),
                        u'{0}\n{1}'.format(
                            msg,
                            action_msg
                        ),
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )

                    # Run the validation if the user selects Yes
                    if res == QMessageBox.Yes:
                        self._validate_holders()

        # Documents page
        elif current_id == 1:
            ret_status = self._is_documents_page_valid()
            if not ret_status:
                self.docs_notif_bar.clear()
                msg = self.tr(
                    '(FOR NOW) Please upload at least one supporting '
                    'document.'
                )
                self.docs_notif_bar.insertWarningNotification(msg)

            # Check if there is an active document upload/removal operation
            active_operation = self.tbw_documents.has_active_operation
            if active_operation:
                ret_status = False
                msg = self.tr(
                    'There is an ongoing operation with the CMIS server. '
                    'Please wait a few moments.'
                )
                self.docs_notif_bar.insertWarningNotification(msg)

        elif current_id == 3:
            # This is the last page
            try:
                self.save_scheme()
                self.populate_workflow()
                ret_status = True

            except Exception as err:
                QMessageBox.critical(
                    self,
                    self.tr('Error in Saving Scheme'),
                    unicode(err)
                )

        return ret_status

    def _is_documents_page_valid(self):
        # Checks if the documents have been uploaded
        # TODO: Update to incorporate a check for all documents
        is_valid = False
        uploaded_docs = self.tbw_documents.uploaded_documents.values()
        for d in uploaded_docs:
            # Check if not None. To be refactored.
            if d:
                is_valid = True
                break

        return is_valid

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

    def _save_ra_last_value(self, scheme_number):
        # Save the last value for the given relevant authority
        if not self._abs_last_scheme_value:
            return

        num_parts = scheme_number.split('.')
        if len(num_parts) > 0:
            code = num_parts[0]
            rel_auth_obj = self._relevant_auth_model()
            res = rel_auth_obj.queryObject().filter(
                self._relevant_auth_model.au_code == code
            ).first()
            if res:
                # Update last value
                res.last_val = self._abs_last_scheme_value
                res.update()

    def save_scheme(self):
        """
        Save scheme information, move supporting documents, save holders
        table and create appropriate notifications.
        """
        pg_dlg = QProgressDialog(
            parent=self
        )
        pg_dlg.setWindowModality(Qt.WindowModal)
        pg_dlg.setMinimum(0)
        pg_dlg.setMaximum(4)
        pg_dlg.setCancelButton(None)
        pg_dlg.setWindowTitle(self.tr(
            'Saving Scheme Information...'
        ))

        pg_dlg.setLabelText(self.tr(
            'Retrieving scheme attribute data...'
        ))
        pg_dlg.setValue(1)
        # Get scheme db object for manual saving to database.
        self.submit(True)
        scheme_obj = self.model()
        QgsApplication.processEvents()

        pg_dlg.setLabelText(self.tr(
            'Saving supporting documents, please wait...'
        ))
        pg_dlg.setValue(2)
        # Attach documents
        doc_objs = self._cmis_doc_mapper.persist_documents(
            scheme_obj.scheme_number
        )
        scheme_obj.documents = doc_objs
        QgsApplication.processEvents()

        pg_dlg.setLabelText(self.tr(
            'Saving scheme data...'
        ))
        pg_dlg.setValue(3)
        scheme_obj.save()

        # Update last value for generating scheme number
        self._save_ra_last_value(scheme_obj.scheme_number)
        QgsApplication.processEvents()

        pg_dlg.setLabelText(self.tr(
            'Saving holders data...'
        ))
        pg_dlg.setValue(4)
        QgsApplication.processEvents()
        # Attach the scheme object to the holders
        self._holder_importer.set_extra_attribute_value(
            'cb_scheme_collection',
            [scheme_obj]
        )
        # Save holders data
        self._holder_importer.start()
        QgsApplication.processEvents()

        msg = self.tr(
            u'A new scheme (No. {0}) has been successfully lodged.'.format(
                scheme_obj.scheme_number
            )
        )
        QMessageBox.information(
            self,
            self.tr('New Scheme'),
            msg
        )

    def populate_workflow(self):
        """
        Update the workflow link table once lodgement has been done
        :return:
        """
        # Entities
        chk_workflow_lookup = self.curr_p.entity('check_lht_workflow')
        chk_approval_lookup = self.curr_p.entity('check_lht_approval_status')
        scheme_workflow = self.curr_p.entity('Scheme_workflow')

        # Check if entity exists
        if chk_workflow_lookup is None:
            QMessageBox.critical(
                self,
                self.tr('Missing workflow Entity'),
                self.tr("The workflow entity is missing in the "
                        "profile.")
            )

        if chk_approval_lookup is None:
            QMessageBox.critical(
                self,
                self.tr('Missing approval Entity'),
                self.tr("The approval entity is missing in the "
                        "profile.")
            )

        if scheme_workflow is None:
            QMessageBox.critical(
                self,
                self.tr('Missing scheme workflow Entity'),
                self.tr("The scheme workflow entity is missing in the "
                        "profile.")
            )

        # Models
        workflow_model = entity_model(chk_workflow_lookup)
        approval_model = entity_model(chk_approval_lookup)
        scheme_workflow_model = entity_model(scheme_workflow)

        # Check if model exists
        if workflow_model is None:
            QMessageBox.critical(
                self,
                self.tr('Workflow Entity Model'),
                self.tr("The workflow entity model could not be generated.")
            )

        if approval_model is None:
            QMessageBox.critical(
                self,
                self.tr('Workflow Entity Model'),
                self.tr("The approval entity model could not be generated.")
            )

        if scheme_workflow_model is None:
            QMessageBox.critical(
                self,
                self.tr('Scheme Workflow Entity Model'),
                self.tr("The scheme workflow entity model could not be "
                        "generated.")
            )

        # Entity objects
        scheme_obj = self.schm_model()
        chk_workflow_obj = workflow_model()
        chk_approval_obj = approval_model()
        scheme_workflow_obj = scheme_workflow_model()

        # Get last lodged scheme ID
        scheme_res = scheme_obj.queryObject().order_by(
            self.schm_model.id.desc()
        ).first()

        # Filter the lookup IDs based on values
        workflow_res = chk_workflow_obj.queryObject().filter(
            workflow_model.value == 'Lodgement'
        ).one()

        # approval_res = chk_approval_obj.queryObject().filter(
        #     approval_model.value == 'Pending'
        # ).one()

        approval_lodge_res = chk_approval_obj.queryObject().filter(
            approval_model.value == 'Approved'
        ).one()

        # Save details
        if approval_lodge_res:
            scheme_workflow_obj.scheme_id = scheme_res.id
            scheme_workflow_obj.workflow_id = workflow_res.id
            scheme_workflow_obj.approval_id = approval_lodge_res.id
            scheme_workflow_obj.timestamp = strftime("%m-%d-%Y %H:%M:%S")
            scheme_workflow_obj.save()

            self.populate_establishment_workflow()

    def populate_establishment_workflow(self):
        """
        Update the workflow link table with establishment as unapproved.
        :return:
        """
        # Entities
        chk_workflow_lookup = self.curr_p.entity('check_lht_workflow')
        chk_approval_lookup = self.curr_p.entity('check_lht_approval_status')
        scheme_workflow = self.curr_p.entity('Scheme_workflow')

        # Check if entity exists
        if chk_workflow_lookup is None:
            QMessageBox.critical(
                self,
                self.tr('Missing workflow Entity'),
                self.tr("The workflow entity is missing in the "
                        "profile.")
            )

        if chk_approval_lookup is None:
            QMessageBox.critical(
                self,
                self.tr('Missing approval Entity'),
                self.tr("The approval entity is missing in the "
                        "profile.")
            )

        if scheme_workflow is None:
            QMessageBox.critical(
                self,
                self.tr('Missing scheme workflow Entity'),
                self.tr("The scheme workflow entity is missing in the "
                        "profile.")
            )

        # Models
        workflow_model = entity_model(chk_workflow_lookup)
        approval_model = entity_model(chk_approval_lookup)
        scheme_workflow_model = entity_model(scheme_workflow)

        # Check if model exists
        if workflow_model is None:
            QMessageBox.critical(
                self,
                self.tr('Workflow Entity Model'),
                self.tr("The workflow entity model could not be generated.")
            )

        if approval_model is None:
            QMessageBox.critical(
                self,
                self.tr('Workflow Entity Model'),
                self.tr("The approval entity model could not be generated.")
            )

        if scheme_workflow_model is None:
            QMessageBox.critical(
                self,
                self.tr('Scheme Workflow Entity Model'),
                self.tr("The scheme workflow entity model could not be "
                        "generated.")
            )

        # Entity objects
        scheme_obj = self.schm_model()
        chk_workflow_obj = workflow_model()
        chk_approval_obj = approval_model()
        scheme_workflow_obj = scheme_workflow_model()

        # Get last lodged scheme ID
        scheme_res = scheme_obj.queryObject().order_by(
            self.schm_model.id.desc()
        ).first()

        # Filter the lookup IDs based on values
        # workflow_res = chk_workflow_obj.queryObject().filter(
        #     workflow_model.value == 'Lodgement'
        # ).one()

        # Filter the lookup IDs based on values
        workflow_res = chk_workflow_obj.queryObject().filter(
            workflow_model.value == 'Establishment'
        ).one()

        approval_res = chk_approval_obj.queryObject().filter(
            approval_model.value == 'Pending'
        ).one()

        approval_lodge_res = chk_approval_obj.queryObject().filter(
            approval_model.value == 'Approved'
        ).one()

        # Save details
        if approval_lodge_res:
            scheme_workflow_obj.scheme_id = scheme_res.id
            scheme_workflow_obj.workflow_id = workflow_res.id
            scheme_workflow_obj.approval_id = approval_res.id
            scheme_workflow_obj.timestamp = strftime("%m-%d-%Y %H:%M:%S")
            scheme_workflow_obj.save()



