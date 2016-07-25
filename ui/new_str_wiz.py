"""
/***************************************************************************
Name                 : New STR Wizard
Description          : Wizard that enables users to define a new social tenure
                       relationship.
Date                 : 3/July/2013
copyright            : (C) 2013 by John Gitau
email                : gkahiu@gmail.com
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
import logging
from collections import OrderedDict

from stdm.data.qtmodels import BaseSTDMTableModel
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from sqlalchemy import (
    func
)

from notification import NotificationBar, ERROR, INFORMATION
from sourcedocument import *

from stdm.data.database import (
    STDMDb,
    Base
)

from stdm.settings import (
    current_profile
)
from stdm.settings.registryconfig import (
    last_document_path,
    set_last_document_path
)
from stdm.utils.util import (
    format_name,
    entity_display_columns,
    model_obj_display_data
)

from stdm.data.configuration import entity_model

from stdm.navigation import (
    TreeSummaryLoader,
    WebSpatialLoader,
    GMAP_SATELLITE,
    OSM
)

from stdm.utils import *
from stdm.utils.util import (
    lookup_id_to_value,
    entity_id_to_attr,
    format_name
)

from ui_new_str import Ui_frmNewSTR

LOGGER = logging.getLogger('stdm')

class newSTRWiz(QWizard, Ui_frmNewSTR):
    """
    This class enable users choose party,
    spatial unit, social tenure, and supporting
    document to create a social tenure relationship.
    """

    def __init__(self, plugin, str_edit_model=None):
        """
        Initializes the ui file, party, spatial unit, social
        tenure type, and supporting document pages.
        It also defines class properties.
        :param plugin: STDM plugin
        :type plugin: STDMQGISLoader
        :returns: None
        :rtype: NoneType
        """
        QWizard.__init__(
            self, plugin.iface.mainWindow()
        )

        self.setupUi(self)
        self.plugin = plugin
        self.setOption(QWizard.IndependentPages, True)
        #STR Variables
        self.sel_party = []
        self.sel_spatial_unit = []
        self.str_type_data = []
        self.sel_str_type = []
        self.row = 0 # number of party rows
        # Current profile instance and properties
        self.curr_profile = current_profile()

        self.social_tenure = self.curr_profile.social_tenure
        self.str_type_table = None
        self.party = self.social_tenure.party

        self.spatial_unit = self.social_tenure.spatial_unit

        self.str_type = self.curr_profile.\
            social_tenure.tenure_type_collection

        self.str_model, self.str_doc_model = entity_model(
            self.social_tenure, False, True
        )

        self.party_header = []
        self.docs_tab_index = None
        self.docs_tab = None
        self.doc_types = None
        self.str_edit_obj = None
        self.str_doc_edit_obj = None
        self.updated_doc_obj = None
        self.updated_str_obj = None
        self.party_notice = NotificationBar(
            self.vlPartyNotif
        )
        self.spatial_unit_notice = NotificationBar(
            self.vlSpatialUnitNotif
        )
        # Connect signal when the finish
        # button is clicked
        btnFinish = self.button(
            QWizard.FinishButton
        )

        # For editing STR
        if str_edit_model is not None:
            title = QApplication.translate(
                'newSTRWiz',
                'Edit Social Tenure Relationship'
            )
            self.setWindowTitle(title)
            self.removePage(0)
            self.str_edit_obj = str_edit_model.model()
            self.str_doc_edit_obj = str_edit_model.documents()

    def initializePage(self, page_id):
        """
        Initialize summary page based on user
        selections.
        :param id: the page id of the wizard
        :type id: QWizard id
        :returns: None
        :rtype: NoneType
        """
        if page_id == 0:
            if self.str_edit_obj is None:
                self.create_str_type_table()
                self.init_party_add()

        if page_id == 1:
            if self.str_edit_obj is None:
                self.init_spatial_unit_add()
            else:
                self.create_str_type_table()

                self.init_party_str_type_edit()
                self.init_spatial_unit_edit()
        if page_id == 2:
            self.init_preview_map()

        if page_id == 3:
            self.doc_notice = NotificationBar(
                self.vlSourceDocNotif
            )
        if page_id == 4:

            self.init_documents()
            self.init_document_add()
            if not self.str_edit_obj is None:
                self.init_document_edit()

        if page_id == 5:
            self.buildSummary()

    def init_party_str_type_edit(self):
        """
        Initializes party table with STR type edit.
        :param result: The object of the selected STR
        :type result: Object
        :param str_type_id: The id of the social tenure type lookup
        :type str_type_id: Integer
        :return:
        :rtype:
        """
        party_model_obj = getattr(
            self.str_edit_obj, self.party.name
        )

        self.sel_party.append(party_model_obj)
        str_type_id = self.str_edit_obj.tenure_type
        entity_config = self._load_entity_config(self.party)
        party_fk_mapper = self._create_fk_mapper(
            entity_config, self.partyRecBox, self.party_notice
        )

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(party_fk_mapper)

        self.partyRecBox.setLayout(vertical_layout)

        party_fk_mapper.setEntities(party_model_obj)

        self.init_str_type(
            party_model_obj,
            party_fk_mapper,
            str_type_id,
            0
        )
        self.party_signals(party_fk_mapper)
        self.resize_to_single_row(
            party_fk_mapper, self.verticalLayout_2
        )

    def resize_to_single_row(self, fk_mapper, layout, height=265):
        """
        Reduce the table to one row.
        :param fk_mapper: Foreign Key mapper class
        :type fk_mapper: Object
        :param layout: layout container of the spacer
        :type layout: QVBoxLayout
        :return: None
        :rtype: NoneType
        """
        fk_mapper._tbFKEntity.setMinimumSize(QSize(55, 30))
        fk_mapper._tbFKEntity.setMaximumSize(QSize(5550, 100))
        spacer = QSpacerItem(
            20,
            height,
            QSizePolicy.Minimum,
            QSizePolicy.Expanding
        )
        layout.addItem(spacer)

    def init_spatial_unit_edit(self):

        spatial_unit_model_obj = getattr(
            self.str_edit_obj, self.spatial_unit.name
        )
        self.sel_spatial_unit.append(spatial_unit_model_obj)

        entity_config = self._load_entity_config(
            self.spatial_unit
        )
        sp_unit_fk_mapper = self._create_fk_mapper(
            entity_config,
            self.spatialUnitRecBox,
            self.spatial_unit_notice
        )

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(
            sp_unit_fk_mapper
        )

        self.spatialUnitRecBox.setLayout(
            vertical_layout
        )

        sp_unit_fk_mapper.setEntities(
            spatial_unit_model_obj
        )
        self.spatial_unit_signals(
            sp_unit_fk_mapper
        )
        self.resize_to_single_row(
            sp_unit_fk_mapper,
            self.verticalLayout_10,
            220
        )

    def set_model_obj(self, model_obj, sel_models_cont):
        if sel_models_cont == self.sel_party:
            self.party_notice.clear()
        if sel_models_cont == self.sel_spatial_unit:
            self.sel_spatial_unit[:] = []
        elif not self.social_tenure.multi_party:
            self.sel_party[:] = []
        sel_models_cont.append(model_obj)

    def erase_table_data(self, table_view):

        if table_view.model().rowCount() > 0:
            table_view.model().rowCount(0)
            table_view.model().removeRow(0)

    def clear_str_type_data(self, party_table):
        # Clear existing if multi-party is not
        #  allowed or on editing mode
        if not self.social_tenure.multi_party or \
                        self.str_edit_obj is not None:
                if party_table.model().rowCount() > 0:
                    self.remove_str_type_row([0])

    def party_signals(self, party_table):

        party_table.beforeEntityAdded.connect(
            lambda model_obj: self.set_model_obj(
                model_obj, self.sel_party
            )
        )

        party_table.afterEntityAdded.connect(
            lambda model_obj, row: self.init_str_type(
                model_obj, party_table, 0, row
            )
        )

        # Clear str type table data if multi-party is
        #  not allowed or on editing mode
        if not self.social_tenure.multi_party or \
            self.str_edit_obj is not None:
            party_table.beforeEntityAdded.connect(
                lambda : self.erase_table_data(
                    party_table._tbFKEntity
                )
            )

        if self.str_edit_obj is not None:
            party_table.beforeEntityAdded.connect(
                lambda: self.erase_table_data(
                    self.str_type_table
                )
            )

        party_table.deletedRows.connect(
            self.remove_str_type_row
        )

        party_table.deletedRows.connect(
            lambda rows: self.remove_model(rows, self.sel_party)
        )

    def spatial_unit_signals(self, spatial_unit_table):

        spatial_unit_table.beforeEntityAdded.connect(
            lambda model_obj: self.set_model_obj(
                model_obj, self.sel_spatial_unit
            )
        )
        spatial_unit_table.beforeEntityAdded.connect(
            lambda: self.erase_table_data(
                spatial_unit_table._tbFKEntity
            )
        )
        spatial_unit_table.beforeEntityAdded.connect(
            self.validate_party_count
        )

        spatial_unit_table.deletedRows.connect(
            lambda rows: self.remove_model(
                rows, self.sel_spatial_unit
            )
        )


    def init_party_add(self):
        """
        Initialize the party page
        :returns:None
        :rtype: NoneType
        """

        entity_config = self._load_entity_config(self.party)
        party_fk_mapper = self._create_fk_mapper(
            entity_config, self.partyRecBox, self.party_notice
        )

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(party_fk_mapper)

        self.partyRecBox.setLayout(vertical_layout)

        self.party_signals(party_fk_mapper)

        if not self.social_tenure.multi_party:
            self.resize_to_single_row(
                party_fk_mapper, self.verticalLayout_2
            )

    def init_spatial_unit_add(self):
        """
        Initialize the spatial unit page.
        :returns: None
        :rtype: NoneType
        """
        entity_config = self._load_entity_config(
            self.spatial_unit
        )
        sp_fk_mapper = self._create_fk_mapper(
            entity_config,
            self.spatialUnitRecBox,
            self.spatial_unit_notice
        )
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(sp_fk_mapper)

        self.spatialUnitRecBox.setLayout(vertical_layout)

        self.spatial_unit_signals(sp_fk_mapper)
        self.resize_to_single_row(
            sp_fk_mapper, self.verticalLayout_10, 250
        )

    def remove_model(self, rows, sel_record):
        """
        A slot that removes a selected party or
        spatial unit model list.
        :param rows: The list of rows removed.
        :type rows: List
        :param sel_record: List of selected records
         from which a model will be removed.
        :type sel_record: List
        :returns: None
        :rtype: NoneType
        """
        for row in rows:
            sel_record.pop(row)

    def remove_str_type_row(self, rows=[0]):
        """
        Removes corresponding social tenure type
        row when a party row is removed.
        :param rows: Party row position that is removed.
        :type rows: integer
        :returns: None
        :rtype: NoneType
        """
        # As there are two tableviews in str type page
        # due to an additional tableview for social
        # tenure type combo (FreezeTableWidget),
        # we have to multiply by 2 to get the correct
        # position of str_type row to be removed

        for row in rows:
            self.str_type_table.model().removeRow(row)

    def copy_party_table(self, row, table_view):
        party_row_data = []
        model = table_view.model()
        for col in range(model.columnCount()):
            party_id_idx = model.index(row, col)

            party_row_data.append(model.data(
                party_id_idx, Qt.DisplayRole
            ))
        return party_row_data

    def add_str_type_data(
            self,
            table_view,
            table_data,
            row_data,
            str_type_id,
            insert_row
    ):
        """
        :param table_view:
        :type table_view:
        :param db_model:
        :type db_model:
        :param table_data:
        :type table_data:
        :return:
        :rtype:
        """
        data = [None] + row_data
        self.str_type_data.append(data)
        self.str_type_table.add_combobox(str_type_id, insert_row)

        self.str_type_table.model().layoutChanged.emit()
        self.update_table_view(
            self.str_type_table, True
        )
        self.enable_str_type_combo(insert_row)

    def init_str_type(
            self, party_model, party_table, str_type_id=0, row=0
    ):
        """
        Initialize 'Social Tenure Type page.
        :param str_type_id: The currently being edited STR type id.
        :type str_type_id: Integer
        :return: None
        :rtype: NoteType
        """
        self.str_type_notice = NotificationBar(
            self.vlSTRTypeNotif
        )
        if self.str_edit_obj is None:
            insert_row = len(self.sel_party) - 1
        else:
            insert_row = 0

        row_data = self.copy_party_table(
            row, party_table._tbFKEntity
        )

        self.add_str_type_data(
            self.str_type_table,
            self.str_type_data,
            row_data,
            str_type_id,
            insert_row
        )

    def init_document_edit(self):
        """
        Initializes the supporting document page.
        :return: None
        :rtype: NoneType
        """
        if self.str_doc_edit_obj is not None:
            if len(self.str_doc_edit_obj) > 0:

                for doc_id, doc_objs in self.str_doc_edit_obj.iteritems():
                    index = self.cboDocType.findData(
                        doc_id
                    )
                    doc_text = self.cboDocType.itemText(index)

                    layout = self.docs_tab.findChild(
                        QVBoxLayout, 'layout_' + doc_text
                    )

                    self.sourceDocManager.registerContainer(
                        layout, doc_id
                    )
                    for doc_obj in doc_objs:
                        self.sourceDocManager.insertDocFromModel(
                            doc_obj, doc_id
                        )

    def init_documents(self):
        """
        Initializes the document type combobox by
        populating data.
        :return: None
        :rtype: NoneType
        """
        self.sourceDocManager = SourceDocumentManager(
            self.social_tenure.supporting_doc, self.str_doc_model, self
        )
        doc_entity = self.social_tenure. \
            supporting_doc.document_type_entity

        doc_type_model = entity_model(doc_entity)

        docs = doc_type_model()
        doc_type_list = docs.queryObject().all()
        self.doc_types = [(doc.id, doc.value) for doc in doc_type_list]
        self.doc_types = OrderedDict(self.doc_types)
        self.docs_tab = QTabWidget()
        self.docs_tab_index = OrderedDict()

        for i, (id, doc) in enumerate(self.doc_types.iteritems()):
            self.docs_tab_index[doc] = i
            tab_widget = QWidget()
            tab_widget.setObjectName(doc)

            cont_layout = QVBoxLayout(tab_widget)
            cont_layout.setObjectName('widget_layout_' + doc)
            scrollArea = QScrollArea(tab_widget)
            scrollArea.setFrameShape(QFrame.NoFrame)
            scrollArea_contents = QWidget()
            scrollArea_contents.setObjectName(
                'tab_scroll_area_' + doc
            )

            tab_layout = QVBoxLayout(scrollArea_contents)
            tab_layout.setObjectName('layout_' + doc)

            scrollArea.setWidgetResizable(True)

            scrollArea.setWidget(scrollArea_contents)
            cont_layout.addWidget(scrollArea)

            self.docs_tab.addTab(tab_widget, doc)
            self.cboDocType.addItem(doc, id)

        self.suppDocumentBox.addWidget(self.docs_tab, 1)

        self.cboDocType.currentIndexChanged.connect(
            self.init_document_add
        )
        self.cboDocType.currentIndexChanged.connect(
            self.match_doc_combo_to_tab
        )
        self.docs_tab.currentChanged.connect(
            self.match_doc_tab_to_combo
        )

        self.btnAddDocument.clicked.connect(
            self.on_upload_document
        )

    def match_doc_combo_to_tab(self):
        """
        Changes the active tab based on the
        selected value of document type combobox.
        :return: None
        :rtype: NoneType
        """
        combo_text = self.cboDocType.currentText()
        if combo_text is not None and len(combo_text) > 0:
            index = self.docs_tab_index[combo_text]
            self.docs_tab.setCurrentIndex(index)

    def match_doc_tab_to_combo(self):
        """
        Changes the document type combobox value based on the
        selected tab.
        :return: None
        :rtype: NoneType
        """
        doc_tab_index = self.docs_tab.currentIndex()
        self.cboDocType.setCurrentIndex(doc_tab_index)

    def init_document_add(self):
        """
        Initialize the supporting document page.
        :return: None
        :rtype: NoneType
        """
        doc_text = self.cboDocType.currentText()
        cbo_index = self.cboDocType.currentIndex()
        doc_id = self.cboDocType.itemData(cbo_index)
        layout = self.docs_tab.findChild(
            QVBoxLayout, 'layout_' + doc_text
        )

        self.sourceDocManager.registerContainer(
            layout, doc_id
        )

    def on_upload_document(self):
        '''
        Slot raised when the user clicks
        to upload a title deed
        '''
        document_str = QApplication.translate(
            "newSTRWiz",
            "Specify the Document File Location"
        )

        documents = self.selectSourceDocumentDialog(document_str)

        cbo_index = self.cboDocType.currentIndex()
        doc_id = self.cboDocType.itemData(cbo_index)
        party_count = len(self.sel_party)

        for doc in documents:
            self.sourceDocManager.insertDocumentFromFile(
                doc,
                doc_id,
                self.social_tenure,
                party_count
            )
        # Set last path
        if len(documents) > 0:
            doc = documents[0]
            fi = QFileInfo(doc)
            dir_path = fi.absolutePath()
            set_last_document_path(dir_path)

    def selectSourceDocumentDialog(self, title):
        '''
        Displays a file dialog for a user
        to specify a source document
        '''

        #Get last path for supporting documents
        last_path = last_document_path()
        if last_path is None:
            last_path = '/home'

        files = QFileDialog.getOpenFileNames(
            self, title, last_path, "Source "
                                  "Documents (*.jpg *.jpeg *.png *.bmp *.tiff *.svg)"
        )
        return files



    def _load_entity_config(self, entity):
        """
        Creates an EntityConfig object from entity.
        :param entity: The entity object
        :type entity: Object
        """
        table_display_name = format_name(entity.short_name)
        table_name = entity.name
        model = entity_model(entity)

        if model is not None:
            return EntityConfig(
                title=table_display_name,
                data_source=table_name,
                model=model,
                expression_builder=False,
                entity_selector=None
            )
        else:
            return None

    def _create_fk_mapper(self, config, parent, notif_bar):
        from .foreign_key_mapper import ForeignKeyMapper
        fk_mapper = ForeignKeyMapper(config.ds_entity, parent, notif_bar)
        fk_mapper.setDatabaseModel(config.model())
        fk_mapper.setSupportsList(True)
        fk_mapper.setDeleteonRemove(False)
        fk_mapper.setNotificationBar(notif_bar)

        return fk_mapper

    def create_str_type_table(self):
        """
        Creates social tenure type table that is composed
        of each selected party rows with a combobox for
        social tenure type.
        :param parent:  The parent of the tableview
        :type parent: QWidget
        :param container: The layout that holds the parent
        :type container: QVBoxLayout
        :param table_data: The table data that is composed
            of the added party record. It is empty when
            the method is called. But gets populated inside
            the model.
        :type table_data: List
        :param headers: Header of the tableview
        :type headers: List
        :return: QTableView
        :rtype: QTableView
        """
        headers = self.add_str_type_headers()

        self.str_type_table = FreezeTableWidget(
            self.str_type_data, headers, self.STRTypeWidget
        )
        self.str_type_table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.STRTypePartyBox.setSpacing(4)
        self.STRTypePartyBox.setMargin(5)
        grid_layout = QGridLayout(self.STRTypeWidget)
        grid_layout.setHorizontalSpacing(5)
        grid_layout.setColumnStretch(4, 5)
        if len(self.sel_party) < 1:
            self.STRTypePartyBox.addLayout(grid_layout)
            self.STRTypePartyBox.addWidget(self.str_type_table)

        #return table_view

    def update_table_view(self, table_view, str_type):
        """
        Updates a tableview by resizing row and headers
        to content size and by hiding id columns
        :param table_view: The table view to be updated.
        :type table_view: QTableView
        :param str_type: A boolean that sets if it is
        for str type table or not.
        :type str_type: Boolean
        :return: None
        :rtype: NoneType
        """
        # show grid
        table_view.setShowGrid(True)
        # set column width to fit contents
        table_view.resizeColumnsToContents()
        # set row height
        table_view.resizeRowsToContents()
        # enable sorting
        table_view.setSortingEnabled(False)
        if str_type:
            table_view.hideColumn(1)
        else:
            table_view.hideColumn(0)

    def prepare_table_model(
            self, tableview, table_data, headers, parent
    ):
        table_model = BaseSTDMTableModel(
            table_data, headers, parent
        )
        tableview.setModel(table_model)

        tableview.horizontalHeader().setResizeMode(
            QHeaderView.Interactive
        )
        tableview.verticalHeader().setVisible(True)

    def add_str_type_headers(self):
        """
        Adds headers data for tableview columns. The
        headers comes from the selected entity.
        :param entity: The entity for which the table
        header is created for.
        :type entity: Entity Object
        :param table_data: The table data of the table view.
        :type table_data: List
        :param tableview: The tableview in which the header
        is added in.
        :type tableview: QTableView
        :param str_type: A boolean whether the header is for
        str_type or not.
        :type str_type: Boolean
        :return: List of Table headers
        :rtype: List
        """
        db_model = entity_model(self.party, True)
        headers = []
        #Load headers
        if db_model is not None:
            entity_display_columns(self.party)
            # Append str type if the method is used for str_type

            #First (ID) column will always be hidden
            headers.append('Social Tenure Type')

            for col in entity_display_columns(self.party):
                headers.append(format_name(col))

            return headers


    def get_party_str_type_data(self):
        """
        Gets party and str_type data from str_type
        page (page 3 of the wizard). It uses
        get_table_data() method.
        :return: A list containing a list of ids of
        the selected str related table or str_type value.
        :rtype: List
        """
        str_types = []
        frozen_table = self.str_type_table.frozen_table_view
        combo_boxes = frozen_table.findChildren(QComboBox)

        for combo in combo_boxes:
            str_type = combo.currentText()
            str_types.append(str_type)

        db_model = entity_model(self.str_type, True)
        db_obj = db_model()
        for sel_value in str_types:
            str_query = db_obj.queryObject().filter(
                db_model.value == sel_value
            ).all()
            if len(str_query) > 0:
                sel_str_type_id = getattr(
                    str_query[0],
                    'id',
                    None
                )
                self.sel_str_type.append(sel_str_type_id)

        return str_types

    def enable_str_type_combo(self, row):
        model = self.str_type_table.frozen_table_view.model()
        self.str_type_table.frozen_table_view.\
            openPersistentEditor(
            model.index(row, 0)
        )

    def validate_party_count(self, spatial_unit_obj):
        from .foreign_key_mapper import ForeignKeyMapper
        # Get entity browser notification bar
        fk_mapper = self.sender()
        browser_notif = None
        if isinstance(fk_mapper, ForeignKeyMapper):
            # Insert error in entity browser too
            browser_notif = NotificationBar(
                fk_mapper._entitySelector.vlNotification
            )

            layout = fk_mapper._entitySelector.vlNotification

            for i in reversed(range(layout.count())):
                notif = layout.itemAt(i).widget()
                for lbl in notif.findChildren(QWidget):
                    layout.removeWidget(lbl)
                    lbl.setVisible(False)
                    lbl.deleteLater()

                notif.setParent(None)


        str_obj = self.str_model()
        self.spatial_unit_notice.clear()
        # returns the number of entries for a specific parcel.
        usage_count = str_obj.queryObject(
            [func.count().label('spatial_unit_count')]
        ).filter(
            self.str_model.spatial_unit_id == spatial_unit_obj.id
        ).first()

        # If entry is found, show error and return
        if usage_count.spatial_unit_count > 0:
            if self.social_tenure.multi_party:
                if usage_count.spatial_unit_count == 1:
                    ocup = ' party.'
                else:
                    ocup = ' parties.'
                msg = QApplication.translate(
                    "newSTRWiz",
                    'This ' + format_name(self.spatial_unit.short_name) +
                    ' has already been assigned to '+
                    str(usage_count.spatial_unit_count)+ocup
                )
                self.spatial_unit_notice.insertNotification(
                    msg, INFORMATION
                )
                return True
            else:
                msg = QApplication.translate(
                    "newSTRWiz",
                    'Unfortunately, this ' +
                    format_name(self.spatial_unit.short_name) +
                    ' has already been assigned to a party.'
                )
                self.spatial_unit_notice.insertNotification(
                    msg, ERROR
                )

                if isinstance(fk_mapper, ForeignKeyMapper):
                    if browser_notif is not None:
                        browser_notif.insertErrorNotification(msg)
                return False
        else:
            return True


    def buildSummary(self):
        """
        Display summary information in the tree view.
        :return: None
        :rtype: NoneType
        """
        summaryTreeLoader = TreeSummaryLoader(self.twSTRSummary)

        sel_str_types = self.get_party_str_type_data()
        # Add each str type next to each party.
        for q_obj, item in zip(self.sel_party, sel_str_types):
            party_mapping = model_obj_display_data(
                q_obj, self.party, self.curr_profile
            )

            summaryTreeLoader.addCollection(
                party_mapping,
                QApplication.translate(
                    "newSTRWiz","Party Information"),
                ":/plugins/stdm/images/icons/user.png"
            )

            str_mapping = self.map_str_type(item)
            summaryTreeLoader.addCollection(
                str_mapping,
                QApplication.translate(
                    "newSTRWiz",
                    "Social Tenure Relationship Information"),
                ":/plugins/stdm/images/icons/social_tenure.png"
            )

        for q_obj in self.sel_spatial_unit:
            spatial_unit_mapping = model_obj_display_data(
                q_obj, self.spatial_unit, self.curr_profile
            )

            summaryTreeLoader.addCollection(
                spatial_unit_mapping,
                QApplication.translate(
                    "newSTRWiz", "Spatial Unit Information"),
                ":/plugins/stdm/images/icons/property.png"
            )

        if self.str_edit_obj is None:
            #Check the source documents based on the type of property
            src_doc_mapping = self.sourceDocManager.attributeMapping()
        else:
            src_doc_mapping = self.sourceDocManager.attributeMapping(True)
        summaryTreeLoader.addCollection(
            src_doc_mapping,
            QApplication.translate(
                "newSTRWiz","Source Documents"),
            ":/plugins/stdm/images/icons/attachment.png"
        )
      
        summaryTreeLoader.display()  


    def validateCurrentPage(self):
        """
        Validate the current page before
        proceeding to the next one and gets and 
        sets data from each page so that it can be used
        in on_create_str.
        :return: None
        :rtype: NoneType
        """
        isValid = True
        currPageIndex = self.currentId()       
        
        #Validate person information
        if currPageIndex == 1:

            if len(self.sel_party) == 0:
                msg = QApplication.translate(
                    "newSTRWiz",
                    "Please choose a party for whom you are "
                    "defining the social tenure relationship for."
                )

                self.party_notice.clear()
                self.party_notice.insertNotification(msg, ERROR)
                isValid = False

        #Validate property information
        if currPageIndex == 2:

            if len(self.sel_spatial_unit) == 0:
                msg = QApplication.translate(
                    "newSTRWiz",
                    "Please add a spatial unit using the Add button."
                )
                self.spatial_unit_notice.clear()
                self.spatial_unit_notice.insertNotification(
                    msg, ERROR
                )
                isValid = False
            if len(self.sel_spatial_unit) > 0:
                # Validate on editing
                if self.str_edit_obj is not None:
                    if self.str_edit_obj.spatial_unit_id != \
                            self.sel_spatial_unit[0].id:
                        unoccupied = self.validate_party_count(
                            self.sel_spatial_unit[0]
                        )
                        if not unoccupied:
                            isValid = False
                # Validate on adding
                else:
                    unoccupied = self.validate_party_count(
                        self.sel_spatial_unit[0]
                    )
                    if not unoccupied:
                        isValid = False


        #Validate STR Type
        if currPageIndex == 3:
            #Get current selected index
            str_types = []
            if self.get_party_str_type_data() is not None:
                str_types = self.get_party_str_type_data()


            if None in str_types or ' ' in str_types or len(str_types) < 1:
                msg = QApplication.translate(
                    'newSTRWiz',
                    'Please select an item from the drop down '
                    'menu under each cells in Social Tenure Type column.'
                )
                self.str_type_notice.clear()
                self.str_type_notice.insertErrorNotification(msg)
                isValid = False


            if len(self.sel_party) > 1:
                self.doc_notice.clear()
                msg = QApplication.translate(
                    'newSTRWiz',
                    'For each document uploaded, a copy '
                    'will be made based on the number of parties.'
                )
                self.doc_notice.insertNotification(msg, INFORMATION)

        if currPageIndex == 5:
            isValid = self.on_create_str()
        return isValid


    def on_add_str(self, progress):
        """
        Adds new STR record into the database
        with a supporting document record, if uploaded.
        :param progress: The progressbar
        :type progress: QProgressDialog
        :return: None
        :rtype: NoneType
        """
        _str_obj = self.str_model()
        str_objs = []
        index = 4
        progress.setValue(3)
        # Social tenure and supporting document insertion
        # The code below is have a workaround to enable
        # batch supporting documents without affecting single
        # party upload. The reason a hack was needed is,
        # whenever a document is inserted in a normal way,
        # duplicate entry is added to the database.
        no_of_party = len(self.sel_party)
        for j, (sel_party, str_type_id) in enumerate(
                zip(self.sel_party, self.sel_str_type)
        ):
            # get all model objects
            doc_objs = self.sourceDocManager.model_objects()
            # get the number of unique documents.
            number_of_docs = len(doc_objs) / no_of_party

            str_obj = self.str_model(
                party_id=sel_party.id,
                spatial_unit_id=self.sel_spatial_unit[0].id,
                tenure_type=str_type_id
            )
            # Insert Supporting Document if a
            # supporting document is uploaded.
            if len(doc_objs) > 0:
                # # loop through each document objects
                # loop per each number of documents
                for k in range(number_of_docs):
                    # The number of jumps (to avoid duplication) when
                    # looping though document objects
                    loop_increment = (k * no_of_party) + j
                    # append into the str obj
                    str_obj.documents.append(
                        doc_objs[loop_increment]
                    )
                    
            str_objs.append(str_obj)
            index = index + 1
            progress.setValue(index)
        _str_obj.saveMany(str_objs)

    def on_edit_str(self, progress):
        """
         Adds edits a selected STR record
         with a supporting document record, if uploaded.
         :param progress: The progressbar
         :type progress: QProgressDialog
         :return: None
         :rtype: NoneType
         """
        _str_obj = self.str_model()

        progress.setValue(3)

        str_edit_obj = _str_obj.queryObject().filter(
            self.str_model.id == self.str_edit_obj.id
        ).first()

        str_edit_obj.party_id=self.sel_party[0].id,
        str_edit_obj.spatial_unit_id=self.sel_spatial_unit[0].id,
        str_edit_obj.tenure_type=self.sel_str_type[0]

        progress.setValue(5)
        added_doc_objs = self.sourceDocManager.model_objects()

        self.str_doc_edit_obj = [obj for obj in sum(self.str_doc_edit_obj.values(), [])]

        new_doc_objs = list(set(added_doc_objs) - set(self.str_doc_edit_obj))

        self.updated_str_obj = str_edit_obj
        # Insert Supporting Document if a new
        # supporting document is uploaded.
        if len(new_doc_objs) > 0:

            # looping though newly added objects list
            for doc_obj in new_doc_objs:
                # append into the str edit obj
                str_edit_obj.documents.append(
                    doc_obj
                )
        progress.setValue(7)

        str_edit_obj.update()

        self.updated_str_obj = str_edit_obj

        progress.setValue(10)

        progress.hide()

    def on_create_str(self):
        """
        Slot raised when the user clicks on Finish
        button in order to create a new STR entry.
        :return: None
        :rtype: NoneType
        """
        isValid = True
        #Create a progress dialog
        prog_dialog = QProgressDialog(self)
        prog_dialog.setWindowTitle(
            QApplication.translate(
                "newSTRWiz",
                "Creating New STR"
            )
        )


        try:

            if self.str_edit_obj is None:
                prog_dialog.setRange(0, 4 + len(self.sel_party))
                prog_dialog.show()
                self.on_add_str(prog_dialog)
            else:
                prog_dialog.setRange(0, 10)
                prog_dialog.show()
                self.on_edit_str(prog_dialog)

            mode = 'created'
            if self.str_edit_obj is not None:
                mode = 'updated'
            strMsg = unicode(QApplication.translate(
                "newSTRWiz",
                "The social tenure relationship has "
                "been successfully {}!".format(mode)
            ))
            QMessageBox.information(
                self, QApplication.translate(
                    "newSTRWiz", "Social Tenure Relationship"
                ),
                strMsg
            )

        except sqlalchemy.exc.OperationalError as oe:
            errMsg = oe.message
            QMessageBox.critical(
                self,
                QApplication.translate(
                    "newSTRWiz", "Unexpected Error"
                ),
                errMsg
            )
            prog_dialog.hide()
            isValid = False

        except sqlalchemy.exc.IntegrityError as ie:
            errMsg = ie.message
            QMessageBox.critical(
                self,
                QApplication.translate(
                    "newSTRWiz",
                    "Duplicate Relationship Error"
                ),
                errMsg
            )
            prog_dialog.hide()
            isValid = False

        except Exception as e:
            errMsg = unicode(e)
            QMessageBox.critical(
                self,
                QApplication.translate(
                    'newSTRWiz','Unexpected Error'
                ),
                errMsg
            )

            isValid = False
        finally:
            STDMDb.instance().session.rollback()
            prog_dialog.hide()

        return isValid

    def on_property_browser_error(self, err):
        """
        Slot raised when an error occurs when
        loading items in the property browser
        :param err: The error message to be displayed
        :type err: QString
        :return: None
        :rtype: NoneType
        """
        self.spatial_unit_notice.clear()
        self.spatial_unit_notice.insertNotification(
            err, ERROR
        )
        
    def on_property_browser_loading(self, progress):
        """
        Slot raised when the property browser is
        loading. Displays the progress of the
        page loading as a percentage.
        :param progress: load progress
        :type progress: Integer
        :return: None
        :rtype: NoneType
        """
        if progress <= 0 or progress >= 100:
            self.gpOpenLayers.setTitle(self.gpOLTitle)
        else:
            self.gpOpenLayers.setTitle(
                "%s (Loading...%s%%)"%(
                    unicode(self.gpOLTitle),
                    str(progress)
                )
            )
            
    def on_property_browser_finished(self, status):
        """
        Slot raised when the property browser
        finishes loading the content
        :param status: Boolean of the load status.
        :type status: Boolean
        :return: None
        :rtype: NoneType
        """
        if status:
            self.olLoaded = True
            self.overlayProperty()
            self.spatial_unit_notice.clear()
            msg = QApplication.translate(
                'newSTRWiz',
                'Web overlay may vary from actual '
                'representation in the local map.'
            )
            self.spatial_unit_notice.insertWarningNotification(msg)
        else:
            self.spatial_unit_notice.clear()
            msg = QApplication.translate(
                "newSTRWiz",
                "Error - The property map cannot be loaded."
            )
            self.spatial_unit_notice.insertErrorNotification(msg)

    def init_preview_map(self):

        self.gpOLTitle = self.gpOpenLayers.title()

        # Flag for checking whether
        # OpenLayers base maps have been loaded
        self.olLoaded = False
        # Connect signals
        QObject.connect(
            self.gpOpenLayers,
            SIGNAL("toggled(bool)"),
            self.on_enable_ol_groupbox
        )
        QObject.connect(
            self.zoomSlider,
            SIGNAL("sliderReleased()"),
            self.on_zoom_changed
        )
        QObject.connect(
            self.btnResetMap,
            SIGNAL("clicked()"),
            self._onResetMap
        )

        # Start background thread
        self.propBrowser = WebSpatialLoader(
            self.propWebView, self
        )
        self.connect(
            self.propBrowser,
            SIGNAL("loadError(QString)"),
            self.on_property_browser_error
        )
        self.connect(
            self.propBrowser,
            SIGNAL("loadProgress(int)"),
            self.on_property_browser_loading
        )
        self.connect(
            self.propBrowser,
            SIGNAL("loadFinished(bool)"),
            self.on_property_browser_finished
        )
        self.connect(
            self.propBrowser,
            SIGNAL("zoomChanged(int)"),
            self.onMapZoomLevelChanged
        )

        # Connect signals
        QObject.connect(
            self.rbGMaps,
            SIGNAL("toggled(bool)"),
            self.onLoadGMaps
        )
        QObject.connect(
            self.rbOSM,
            SIGNAL("toggled(bool)"),
            self.onLoadOSM
        )

    def on_enable_ol_groupbox(self, state):
        """
        Slot raised when a user chooses to select
        the group box for enabling/disabling to view
        the property in OpenLayers.
        :param state: Boolean of the load status.
        :type state: Boolean
        :return: None
        :rtype: NoneType
        """
        if state:

            if len(self.sel_spatial_unit) < 1:
                self.spatial_unit_notice.clear()
                msg = QApplication.translate(
                    "newSTRWiz",
                    "You have to add a spatial unit record "
                    "in order to be able to preview it."
                )
                self.spatial_unit_notice.insertWarningNotification(msg)                
                self.gpOpenLayers.setChecked(False)
                return  
            
            #Load property overlay
            if not self.olLoaded:                
                self.propBrowser.load()            
                   
        else:
            #Remove overlay
            self.propBrowser.removeOverlay()     
            
    def on_zoom_changed(self):
        """
        Slot raised when the zoom value in the slider changes.
        This is only raised once the user
        releases the slider with the mouse.
        :return: None
        :rtype: NoneType
        """
        zoom = self.zoomSlider.value()        
        self.propBrowser.zoom_to_level(zoom)


    def map_str_type(self, item):
        """
        Loads the selected social tenure type into an
        ordered dictionary for the summary page treeview
        :param item: The social tenure type
        :type item: OrderedDict
        :return: 
        :rtype: 
        """
        str_mapping = OrderedDict()
        str_mapping[
            QApplication.translate(
                "newSTRWiz","Tenure Type"
            )
        ] = item
        return str_mapping

    def onLoadGMaps(self,state):
        '''
        Slot raised when a user clicks to set
        Google Maps Satellite as the base layer
        '''
        if state:                     
            self.propBrowser.setBaseLayer(
                GMAP_SATELLITE
            )
        
    def onLoadOSM(self,state):
        '''
        Slot raised when a user clicks to set
        OSM as the base layer
        '''
        if state:                     
            self.propBrowser.setBaseLayer(OSM)
            
    def onMapZoomLevelChanged(self,level):
        '''
        Slot which is raised when the zoom
        level of the map changes.
        '''
        self.zoomSlider.setValue(level)
       
    def _onResetMap(self):
        '''
        Slot raised when the user clicks
        to reset the property
        location in the map.
        '''
        self.propBrowser.zoom_to_extents()
       
    def overlayProperty(self):
        '''
        Overlay property boundaries on
        the basemap imagery
        '''
        geometry_col_name = [c.name for c in
            self.spatial_unit.columns.values()
            if c.TYPE_INFO == 'GEOMETRY'
        ]
        for geom in geometry_col_name:
            self.propBrowser.add_overlay(
                self.sel_spatial_unit[0], geom
            )


class ComboBoxDelegate(QItemDelegate):
    def __init__(self, str_type_id=0, parent=None):

        QItemDelegate.__init__(self, parent)
        self.row = 0
        self.str_type_id = str_type_id
        self.curr_profile = current_profile()
        self.social_tenure = self.curr_profile.social_tenure

    def str_type_combo (self):
        """
        A slot raised to add new str type
        matched with the party.
        :return: None
        """
        str_type_cbo = QComboBox()
        str_type_cbo.setObjectName(
            'STRTypeCbo'+str(self.row+1)
        )
        self.row = self.row + 1
        return str_type_cbo

    def str_type_set_data(self):
        str_lookup_obj = self.social_tenure.tenure_type_collection
        str_types = entity_model(str_lookup_obj, True)
        str_type_obj = str_types()
        self.str_type_data = str_type_obj.queryObject().all()
        strType = [(lookup.id, lookup.value) for lookup in self.str_type_data]

        return OrderedDict(strType)

    def createEditor(self, parent, option, index):
        str_combo = QComboBox(parent)
        str_combo.insertItem(0, " ")
        for id, type in self.str_type_set_data().iteritems():
            str_combo.addItem(type, id)

        str_combo.setCurrentIndex(self.str_type_id)

        return str_combo

    def setEditorData( self, comboBox, index ):
        list_item_index = None
        if not index.model() is None:
            list_item_index = index.model().data(
                index, Qt.DisplayRole
            )
        if list_item_index is not None and \
                not isinstance(list_item_index, (unicode, str)):
            value = list_item_index.toInt()
            comboBox.blockSignals(True)
            comboBox.setCurrentIndex(value[0])
            comboBox.blockSignals(False)

    def setModelData(self, editor, model, index):
        value = editor.currentIndex()
        model.setData(
            index,
            editor.itemData(
            value, Qt.DisplayRole)
        )

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

class FreezeTableWidget(QTableView):

    def __init__(
            self, table_data, headers, parent = None, *args
    ):
        QTableView.__init__(self, parent, *args)
        # set the table model
        table_model = BaseSTDMTableModel(
            table_data, headers, parent
        )

        # set the proxy model
        proxy_model = QSortFilterProxyModel(self)
        proxy_model.setSourceModel(table_model)

        # Assign a data model for TableView
        self.setModel(table_model)

        # frozen_table_view - first column
        self.frozen_table_view = QTableView(self)
        # Set the model for the widget, fixed column
        self.frozen_table_view.setModel(table_model)
        # Hide row headers
        self.frozen_table_view.verticalHeader().hide()
        # Widget does not accept focus
        self.frozen_table_view.setFocusPolicy(
            Qt.StrongFocus|Qt.TabFocus|Qt.ClickFocus
        )
        # The user can not resize columns
        self.frozen_table_view.horizontalHeader().\
            setResizeMode(QHeaderView.Fixed)
        self.frozen_table_view.setObjectName('frozen_table')
        # Style frozentable view
        self.frozen_table_view.setStyleSheet(
            '''
            #frozen_table{
                border-top:none;
            }
            '''
        )
        self.setSelectionMode(QAbstractItemView.NoSelection)

        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(5)
        self.shadow.setOffset(2)
        self.shadow.setYOffset(0)
        self.frozen_table_view.setGraphicsEffect(self.shadow)

        # Remove the scroll bar
        self.frozen_table_view.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )
        self.frozen_table_view.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        # Puts more widgets to the foreground
        self.viewport().stackUnder(self.frozen_table_view)
        # # Log in to edit mode - even with one click
        # Set the properties of the column headings
        hh = self.horizontalHeader()
        # Text alignment centered
        hh.setDefaultAlignment(Qt.AlignCenter)

        # Set the width of columns
        columns_count = table_model.columnCount(self)
        for col in xrange(columns_count):
            if col == 0:
                # Set the size
                self.horizontalHeader().resizeSection(
                    col, 60
                )
                # Fix width
                self.horizontalHeader().setResizeMode(
                    col, QHeaderView.Fixed
                )
                # Width of a fixed column - as in the main widget
                self.frozen_table_view.setColumnWidth(
                    col, self.columnWidth(col)
                )
            elif col == 1:
                self.horizontalHeader().resizeSection(
                    col, 150
                )
                self.horizontalHeader().setResizeMode(
                    col, QHeaderView.Fixed
                )
                self.frozen_table_view.setColumnWidth(
                    col, self.columnWidth(col)
                )
            else:
                self.horizontalHeader().resizeSection(
                    col, 100
                )
                # Hide unnecessary columns in the widget fixed columns
                self.frozen_table_view.setColumnHidden(
                    col, True
                )

        # Set properties header lines
        vh = self.verticalHeader()
        vh.setDefaultSectionSize(25) # height lines
        # text alignment centered
        vh.setDefaultAlignment(Qt.AlignCenter) 
        vh.setVisible(True)
        # Height of rows - as in the main widget
        self.frozen_table_view.verticalHeader().\
            setDefaultSectionSize(
            vh.defaultSectionSize()
        )

        # Show frozen table view
        self.frozen_table_view.show()
        # Set the size of him like the main
        self.update_frozen_table_geometry()

        self.setHorizontalScrollMode(
            QAbstractItemView.ScrollPerPixel
        )
        self.setVerticalScrollMode(
            QAbstractItemView.ScrollPerPixel
        )
        self.frozen_table_view.setVerticalScrollMode(
            QAbstractItemView.ScrollPerPixel
        )


        self.frozen_table_view.selectColumn(0)

        self.frozen_table_view.setEditTriggers(
            QAbstractItemView.AllEditTriggers
        )
        size_policy = QSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Fixed
        )
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(
            self.sizePolicy().hasHeightForWidth()
        )
        self.setSizePolicy(size_policy)
        self.setMinimumSize(QSize(55, 75))
        self.setMaximumSize(QSize(5550, 5555))
        #self.setGeometry(QRect(0, 0, 619, 75))
        self.SelectionMode(
            QAbstractItemView.SelectColumns
        )

        # set column width to fit contents
        self.frozen_table_view.resizeColumnsToContents()
        # set row height
        self.frozen_table_view.resizeRowsToContents()

        # Connect the headers and scrollbars of
        # both tableviews together
        self.horizontalHeader().sectionResized.connect(
            self.update_section_width
        )
        self.verticalHeader().sectionResized.connect(
            self.update_section_height
        )
        self.frozen_table_view.verticalScrollBar().\
            valueChanged.connect(
            self.verticalScrollBar().setValue
        )
        self.verticalScrollBar().valueChanged.connect(
            self.frozen_table_view.verticalScrollBar().setValue
        )
    def add_combobox(self, str_type_id, insert_row):
        delegate = ComboBoxDelegate(str_type_id)
        # Set delegate to add combobox under
        # social tenure type column
        self.frozen_table_view.setItemDelegate(
            delegate
        )
        self.frozen_table_view.setItemDelegateForColumn(
            0, delegate
        )
        index = self.frozen_table_view.model().index(
            insert_row, 0, QModelIndex()
        )
        self.frozen_table_view.model().setData(
            index, '', Qt.EditRole
        )

    def update_section_width(
            self, logicalIndex, oldSize, newSize
    ):
        if logicalIndex==0 or logicalIndex==1:
            self.frozen_table_view.setColumnWidth(
                logicalIndex, newSize
            )
            self.update_frozen_table_geometry()

    def update_section_height(
            self, logicalIndex, oldSize, newSize
    ):
        self.frozen_table_view.setRowHeight(
            logicalIndex, newSize
        )

    def resizeEvent(self, event):
        QTableView.resizeEvent(self, event)
        try:
            self.update_frozen_table_geometry()
        except Exception as log:
            LOGGER.debug(str(log))


    def scrollTo(self, index, hint):
        if index.column() > 1:
            QTableView.scrollTo(self, index, hint)

    def update_frozen_table_geometry(self):
        if self.verticalHeader().isVisible():
            self.frozen_table_view.setGeometry(
                self.verticalHeader().width() +
                self.frameWidth(),
                self.frameWidth(),
                self.columnWidth(0) +
                self.columnWidth(1),
                self.viewport().height() +
                self.horizontalHeader().height()
            )
        else:
            self.frozen_table_view.setGeometry(
                self.frameWidth(),
                self.frameWidth(),
                self.columnWidth(0) + self.columnWidth(1),
                self.viewport().height() +
                self.horizontalHeader().height()
            )

    # move_cursor override function for correct
    # left to scroll the keyboard.
    def move_cursor(self, cursor_action, modifiers):
        current = QTableView.move_cursor(
            self, cursor_action, modifiers
        )
        if cursor_action == self.MoveLeft and current.column() > 1 and \
                        self.visualRect(current).topLeft().x() < \
                        (self.frozen_table_view.columnWidth(0) +
                             self.frozen_table_view.columnWidth(1)):
            new_value = self.horizontalScrollBar().value() + \
                       self.visualRect(current).topLeft().x() - \
                       (self.frozen_table_view.columnWidth(0) +
                        self.frozen_table_view.columnWidth(1))
            self.horizontalScrollBar().setValue(new_value)
        return current

class EntityConfig(object):
    """
    Configuration class for specifying the foreign key mapper and document
    generator settings.
    """
    def __init__(self, **kwargs):
        self._title = kwargs.pop("title", "")
        self._link_field = kwargs.pop("link_field", "")
        self._display_formatters = kwargs.pop("formatters", OrderedDict())

        self._data_source = kwargs.pop("data_source", "")
        self._ds_columns = []
        self.curr_profile = current_profile()
        self.ds_entity = self.curr_profile.entity_by_name(self._data_source)

        self._set_ds_columns()

        self._base_model = kwargs.pop("model", None)
        self._entity_selector = kwargs.pop("entity_selector", None)
        self._expression_builder = kwargs.pop("expression_builder", False)

    def _set_ds_columns(self):
        if not self._data_source:
            self._ds_columns = []

        else:
            self._ds_columns = entity_display_columns(
                self.ds_entity
            )

    def model(self):
        return self._base_model

