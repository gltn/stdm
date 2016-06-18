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
from datetime import datetime
import logging
from collections import OrderedDict

from stdm.data.qtmodels import BaseSTDMTableModel
from PyQt4.QtCore import *
from PyQt4.QtGui import *


from sqlalchemy import (
    func
)

from notification import NotificationBar, ERROR, SUCCESS, WARNING, INFORMATION
from sourcedocument import *

from stdm.data.database import (
    STDMDb,
    Base
)
from stdm.settings import (
    current_profile
)
from stdm.utils.util import (
    format_name,
    entity_display_columns,
    model_display_data
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
        QWizard.__init__(self, plugin.iface.mainWindow())
        self.setupUi(self)
        self.plugin = plugin
        #STR Variables
        self.sel_party = []
        self.sel_spatial_unit = []

        self.sel_str_type = []
        self.row = 0 # number of party rows
        # Current profile instance and properties
        self.curr_profile = current_profile()
        self.social_tenure = self.curr_profile.social_tenure
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
        self.party_notice = NotificationBar(self.vlPartyNotif)

        self.spatial_unit_notice = NotificationBar(
            self.vlSpatialUnitNotif
        )
        # Connect signal when the finish
        # button is clicked
        btnFinish = self.button(
            QWizard.FinishButton
        )
        self.init_preview_map()
        if str_edit_model is not None:
            title = QApplication.translate(
                'newSTRWiz',
                'Edit Social Tenure Relationship'
            )
            self.setWindowTitle(title)
            self.removePage(0)
            self.str_edit_obj = str_edit_model.model()
            self.str_doc_edit_obj = str_edit_model.documents()
            self.load_edit_data()
            self.removed_docs = None
            self.init_document_type()
            self.init_document_edit()
            self.init_document_add()
            self.cboDocType.currentIndexChanged.connect(
                self.init_document_add
            )

        else:
            self.init_party_add()
            self.init_spatial_unit_add()
            self.init_document_type()
            self.init_document_add()
            self.cboDocType.currentIndexChanged.connect(
                self.init_document_add
            )


    def load_edit_data(self):
        """
        Loads data for editing from an str model.
        :return: None
        :rtype: NoneType
        """
        party_model = entity_model(self.party)
        party_obj = party_model()
        
        party_result = party_obj.queryObject().filter(
            party_model.id == self.str_edit_obj.party_id
        ).first()

        self.init_party_str_type_edit(
            party_result,
            self.str_edit_obj.tenure_type
        )

        spatial_unit_model = entity_model(self.spatial_unit)
        spatial_unit_obj = spatial_unit_model()

        spatial_unit_result = spatial_unit_obj.queryObject().filter(
            spatial_unit_model.id == self.str_edit_obj.spatial_unit_id
        ).first()

        self.init_spatial_unit_edit(
            spatial_unit_result
        )

    def init_party_str_type_edit(self,  result, str_type_id):
        table_data = []
        vertical_layout = QVBoxLayout(
            self.partyRecBox
        )
        table_view = self.create_table(
            self.partyRecBox, vertical_layout
        )
        # Make the party table one row
        table_view.setMinimumSize(QSize(55, 30))
        table_view.setMaximumSize(QSize(5550, 75))
        spacer = QSpacerItem(
            20, 338, QSizePolicy.Minimum, QSizePolicy.Expanding
        )
        self.verticalLayout_2.addItem(spacer)

        self.add_table_headers(
            self.party, table_data, table_view
        )
        data = OrderedDict()
        self.party_signals(table_view, table_data)

        for col in entity_display_columns(self.party):
            attr = getattr(result, col)

            # change id to value if lookup,
            # else return the same value
            attr = lookup_id_to_value(
                self.curr_profile, col, attr
            )
            data[col] = attr

        table_data.append(data.values())
        table_view.model().layoutChanged.emit()
        table_view.resizeColumnsToContents()


        
        self.init_str_type(str_type_id)


    def init_spatial_unit_edit(self, result):
        table_data = []
        vertical_layout = QVBoxLayout(
            self.spatialUnitRecBox
        )
        table_view = self.create_table(
            self.spatialUnitRecBox, vertical_layout
        )
        self.add_table_headers(
            self.spatial_unit, table_data, table_view
        )
        data = OrderedDict()

        for col in entity_display_columns(self.spatial_unit):
            attr = getattr(result, col)

            # change id to value if lookup, else return the same value
            attr = lookup_id_to_value(
                self.curr_profile, col, attr
            )
            data[col] = attr

        table_data.append(data.values())
        table_view.model().layoutChanged.emit()

        self.update_table_view(table_view, False)

        spatial_unit_id = self.get_spatial_unit_data()
        self.set_record_to_model(
            self.spatial_unit, spatial_unit_id
        )
        self.spatial_unit_signals(table_view, table_data)

    def party_signals(self, party_table, party_data):

        self.AddPartybtn.clicked.connect(
            lambda: self.add_record(
                party_table, self.party, party_data
            )
        )

        self.AddPartybtn.clicked.connect(
            self.init_str_type
        )

        self.RemovePartybtn.clicked.connect(
            lambda: self.remove_row(
                party_table, self.party_notice
            )
        )

    def spatial_unit_signals(self, table_view, data):
        self.AddSpatialUnitbtn.clicked.connect(
            lambda: self.add_record(
                table_view,
                self.spatial_unit,
                data
            )
        )

        self.RemoveSpatialUnitbtn.clicked.connect(
            lambda: self.remove_row(
                table_view, self.spatial_unit_notice
            )
        )
    def init_party_add(self):
        """
        Initialize the party page
        :returns:None
        :rtype: NoneType
        """

        party_data = []
        vertical_layout = QVBoxLayout(
            self.partyRecBox
        )
        party_table = self.create_table(
            self.partyRecBox, vertical_layout
        )

        self.add_table_headers(
            self.party, party_data, party_table
        )
        self.party_signals(party_table, party_data)



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

    def init_spatial_unit_add(self):
        """
        Initialize the spatial unit page.
        :returns: None
        :rtype: NoneType
        """


        spatial_unit_data = []
        vertical_layout = QVBoxLayout(
            self.spatialUnitRecBox
        )
        spatial_unit_table = self.create_table(
            self.spatialUnitRecBox,
            vertical_layout
        )
        self.add_table_headers(
            self.spatial_unit,
            spatial_unit_data,
            spatial_unit_table
        )

        self.spatial_unit_signals(
            spatial_unit_table, spatial_unit_data
        )


    def remove_row(self, table_view, notification):
        """
        A slot that removes a selected party or
        spatial unit record/row.
        :param table_view: The table view in which
            the row is removed.
        :type table_view: QTableView
        :param notification: The notification
        :type notification: NotificationBar object
        :returns: None
        :rtype: NoneType
        """
        if len(table_view.selectedIndexes()) > 0:
            notification.clear()
            row_index = table_view.selectedIndexes()[0]
            table_view.model().removeRow(
                row_index.row(), row_index
            )
            table_view.model().layoutChanged.emit()
            if notification == self.party_notice:
                self.remove_str_type(row_index.row())

        else:
            msg = QApplication.translate(
                        "newSTRWiz",
                        "Please select a row you"
                        " would like to remove. "
            )
            notification.clear()
            notification.insertNotification(msg, ERROR)


    def remove_str_type(self, row_position):
        """
        Removes corresponding social tenure type
        row when a party row is removed.
        :param row_position: Party row position that is removed.
        :type row_position: integer
        :returns: None
        :rtype: NoneType
        """
        # As there are two tableviews in str type page
        # due to an additional tableview for social
        # tenure type combo (FreezeTableWidget),
        # we have to multiply by 2 to get the correct
        # position of str_type row to be removed
        matching_table = row_position * 2
        for position, item in enumerate(
                self.frmWizSTRType.findChildren(QTableView)
        ):
            if item.__class__.__name__ == 'FreezeTableWidget':
                if position == matching_table:
                    self.STRTypePartyBox.removeWidget(item)
                    item.deleteLater()


    def initializePage(self, id):
        """
        Initialize summary page based on user
        selections.
        :param id: the page id of the wizard
        :type id: QWizard id
        :returns: None
        :rtype: NoneType
        """
        if id == 5:
            self.buildSummary()

    def create_table(self, parent, container):
        """
        Creates an empty QTableView in party and
        spatial unit pages.
        :param parent: The parent of the tableview
        :type parent: QWidget
        :param container: The layout that holds the parent
        :type parent: QVBoxLayout
        :returns: QTableView
        :rtype: QTableView
        """
        table_view = QTableView()

        table_view.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )
        table_view.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )
        table_view.setAlternatingRowColors(True)

        container.setSpacing(4)
        container.setMargin(5)

        grid_layout = QGridLayout(parent)
        grid_layout.setHorizontalSpacing(5)
        grid_layout.setColumnStretch(4, 5)

        container.addLayout(grid_layout)
        container.addWidget(table_view)
        # Reduce the height for spatial unit
        if parent == self.spatialUnitRecBox:
            table_view.setMinimumSize(QSize(55, 30))
            table_view.setMaximumSize(QSize(5550, 75))
        # Reduce the height of party table if multi party is false
        if parent == self.partyRecBox and not self.social_tenure.multi_party:
            table_view.setMinimumSize(QSize(55, 30))
            table_view.setMaximumSize(QSize(5550, 75))
            spacer = QSpacerItem(
                20, 338, QSizePolicy.Minimum, QSizePolicy.Expanding
            )
            self.verticalLayout_2.addItem(spacer)
        return table_view

    def create_str_type_table(
            self, parent, container, table_data, headers, str_type_id
    ):
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
        table_view = FreezeTableWidget(
            table_data, headers, str_type_id, parent
        )
        table_view.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        # Select the first column

        container.setSpacing(4)
        container.setMargin(5)
        grid_layout = QGridLayout(parent)
        grid_layout.setHorizontalSpacing(5)
        grid_layout.setColumnStretch(4, 5)
        container.addLayout(grid_layout)
        container.addWidget(table_view)

        return table_view

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

    def add_table_headers(
            self, entity, table_data, tableview, str_type=False
    ):
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
        db_model = entity_model(entity, True)
        headers = []
        #Load headers
        if db_model is not None:
            entity_display_columns(self.party)
            # Append str type if the method is used for str_type
            if str_type:
                #First (ID) column will always be hidden
                headers.append('Social Tenure Type')

            for col in entity_display_columns(entity):
                headers.append(format_name(col))
            if not str_type:
                self.prepare_table_model(
                    tableview, table_data, headers, self
                )
        if entity == self.party:
            self.party_header = headers

        if str_type:
            return headers
        else:
            self.update_table_view(tableview, str_type)


    def add_record(
            self, table_view, entity, table_data, str_type=False
    ):
        """
        :param table_view:
        :type table_view:
        :param entity:
        :type entity:
        :param table_data:
        :type table_data:
        :param str_type:
        :type str_type:
        :return:
        :rtype:
        """
        data = OrderedDict()
        db_model = entity_model(entity, True)
        db_obj = db_model()

        if str_type:
            data['social_tenure_type'] = None

        for col in entity_display_columns(entity):
            attr = getattr(db_model, col)

            value = db_obj.queryObject([attr]).all()
            if len(value) > 0:
                value = value[0][0]
            else:
                return
            # change id to value if lookup, else return the same value
            value = lookup_id_to_value(
                self.curr_profile, col, value
            )
            data[col] = value
        if entity == self.spatial_unit:
            # Clear existing data before adding
            # new one to only allow one spatial_unit
            if table_view.model().rowCount() > 0:
                table_view.model().rowCount(0)
                table_view.model().removeRow(0)
        if entity == self.party and (
                    not self.social_tenure.multi_party or
                        self.str_edit_obj is not None
        ):

            # Clear existing data before adding
            # new one to only allow one party
            if table_view.model().rowCount() > 0:
                table_view.model().rowCount(0)
                table_view.model().removeRow(0)
                # Remove str type table
                for item in self.frmWizSTRType.findChildren(QTableView):
                    self.STRTypePartyBox.removeWidget(item)
                    item.deleteLater()

        table_data.append(data.values())
        # Get the id and set it to self.sel_spatial_unit
        # so that it can be previewed on the map under
        # the preview tab.
        if entity == self.spatial_unit:
            spatial_unit_id = self.get_spatial_unit_data()
            if self.social_tenure.multi_party:
                self.validate_occupants(spatial_unit_id[0])
            self.set_record_to_model(
                self.spatial_unit, spatial_unit_id
            )

        table_view.model().layoutChanged.emit()
        self.update_table_view(table_view, str_type)


    def get_table_data(self, table_view, str_type=True):
        """
        Gets the data from a table_view.
        :param table_view: The table view from when
        the data is pulled.
        :type table_view: QTableView
        :param str_type: A boolean whether the header is for
        str_type or not.
        :type str_type: Boolean
        :return: A list containing a list of ids of
        the selected str related table or str_type value.
        :rtype: List
        """
        model = table_view.model()
        table_data = []


        if str_type:
            str_type_idx = model.index(0, 0)
            party_id_idx = model.index(0, 1)

            if model.data(
                party_id_idx, Qt.DisplayRole
            ) is not None:
                table_data.append(model.data(
                    party_id_idx, Qt.DisplayRole
                ))
                table_data.append(model.data(
                    str_type_idx, Qt.DisplayRole
                ))
        else:
            spatial_unit_idx = model.index(0, 0)
            table_data.append(model.data(
                spatial_unit_idx, Qt.DisplayRole
            ))

        return table_data

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
        party_ids = []

        for item in self.frmWizSTRType.findChildren(QTableView):
            if len(item.findChildren(QComboBox)) > 0:
                str_type = item.findChildren(QComboBox)[0].currentText()
                str_types.append(str_type)
            if item.__class__.__name__ == 'FreezeTableWidget':

                if len(self.get_table_data(item)) > 0:
                    party_id, str_type = self.get_table_data(item)
                    party_ids.append(party_id)

        return party_ids, str_types

    def enable_str_type_combo(self):

        for item in self.frmWizSTRType.findChildren(QTableView):
            item.openPersistentEditor(item.model().index(0, 0))

    def get_spatial_unit_data(self):
        """
        Gets spatial unit data from spatial unit
        page (page 2 of the wizard). It uses
        get_table_data() method.
        :return: A list containing a list of ids of
        spatial units select.
        :rtype: List
        """
        spatial_unit_id = None
        for item in self.spatialUnitRecBox.findChildren(QTableView):
            if item is not None:
                spatial_unit_id = self.get_table_data(item, False)
                break

        return spatial_unit_id

    def validate_occupants(self, spatial_unit_id):

        str_obj = self.str_model()

        # returns the number of entries for a specific parcel.
        usage_count = str_obj.queryObject(
            [func.count().label('spatial_unit_count')]
        ).filter(
            self.str_model.spatial_unit_id == spatial_unit_id
        ).first()

        # If entry is found, show error and return
        if usage_count.spatial_unit_count > 0:

            self.spatial_unit_notice.clear()
            if self.social_tenure.multi_party:
                if usage_count.spatial_unit_count == 1:
                    ocup = ' occupant.'
                else:
                    ocup = ' occupants.'
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
                    ' has already been assigned to an occupant.'
                )
                self.spatial_unit_notice.insertNotification(
                    msg, ERROR
                )
                return False
        else:
            return True

    def set_record_to_model(self, entity, sel_attr):
        """
        Sets selected record data to model and stores it as
        a list model.
        :param entity: The entity from which the model is created.
        :type entity: Entity object
        :param sel_attr: List of selected records that is the
        return from get_spatial_unit_data() or
        get_party_str_type_data()
        :type sel_attr: List
        :return: None
        :rtype: NoneType
        """
        db_model = entity_model(entity, True)
        db_obj = db_model()
        if entity == self.party:
            self.sel_party = []
            for sel_id in sel_attr:
                party_query = db_obj.queryObject(
                    entity_display_columns(entity)
                ).filter(
                db_model.id == sel_id
                ).first()
                self.sel_party.append(party_query)

        if entity == self.spatial_unit:
            self.sel_spatial_unit = []
            spatial_unit_query = db_obj.queryObject().filter(
            db_model.id == sel_attr[0]
            ).first()
            self.sel_spatial_unit.append(spatial_unit_query)

        if entity == self.str_type:
            self.sel_str_type = []

            for sel_value in sel_attr:
                str_query = db_obj.queryObject().filter(
                    db_model.value == sel_value
                ).all()

                sel_str_type_id = getattr(
                    str_query[0],
                    'id',
                    None
                )
                self.sel_str_type.append(sel_str_type_id)

    def init_str_type(self, str_type_id=0):
        """
        Initialize 'Social Tenure Type page.
        :return: None
        :rtype: NoteType
        """
        party_data = []
        headers = self.add_table_headers(
            self.party,
            party_data,
            None,
            True
        )
        str_type_table = self.create_str_type_table(
            self.STRTypeWidget,
            self.STRTypePartyBox,
            party_data,
            headers,
            str_type_id
        )

        self.add_record(
            str_type_table,
            self.party,
            party_data,
            True
        )

        self.notifSTR = NotificationBar(
            self.vlSTRTypeNotif
        )

        self.enable_str_type_combo()

    def init_document_edit(self):
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


    def init_document_type(self):
        """
        Initializes the document type combobox by
        populating data.
        :return: None
        :rtype: NoneType
        """
        self.sourceDocManager = SourceDocumentManager(
            self.str_doc_model, self
        )
        doc_entity = self.social_tenure.\
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
            scrollArea_contents.setObjectName('tab_scroll_area_'+doc)

            tab_layout = QVBoxLayout(scrollArea_contents)
            tab_layout.setObjectName('layout_'+doc)

            scrollArea.setWidgetResizable(True)

            scrollArea.setWidget(scrollArea_contents)
            cont_layout.addWidget(scrollArea)

            self.docs_tab.addTab(tab_widget, doc)
            self.cboDocType.addItem(doc, id)


        self.suppDocumentBox.addWidget(self.docs_tab, 1)

        self.doc_notice = NotificationBar(
            self.vlSourceDocNotif
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

        combo_text = self.cboDocType.currentText()
        if combo_text is not None and len(combo_text) > 0:
            index = self.docs_tab_index[combo_text]
            self.docs_tab.setCurrentIndex(index)

    def match_doc_tab_to_combo(self):
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
            QVBoxLayout, 'layout_'+doc_text
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

    def selectSourceDocumentDialog(self, title):
        '''
        Displays a file dialog for a user
        to specify a source document
        '''
        files = QFileDialog.getOpenFileNames(
            self, title, "/home", "Source "
                                  "Documents (*.jpg *.jpeg *.png *.bmp *.tiff *.svg)"
        )
        return files

    def uploadDocument(self, path, containerid):
        '''
        Upload source document
        '''
        self.sourceDocManager.insertDocumentFromFile(
            path, containerid, self.social_tenure
        )

    def buildSummary(self):
        """
        Display summary information in the tree view.
        :return: None
        :rtype: NoneType
        """
        summaryTreeLoader = TreeSummaryLoader(self.twSTRSummary)

        sel_party, sel_str_types = self.get_party_str_type_data()
        # Add each str type next to each party.
        for q_obj, item in zip(self.sel_party, sel_str_types):
            party_mapping = model_display_data(
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
            spatial_unit_mapping = model_display_data(
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

            if self.get_party_str_type_data() is not None:
                party_ids, str_type = self.get_party_str_type_data()
                if len(party_ids) > 0:
                    self.set_record_to_model(self.party, party_ids)

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
                unoccupied = self.validate_occupants(
                    self.sel_spatial_unit[0].id
                )
                if not unoccupied:
                    isValid = False


        #Validate STR Type
        if currPageIndex == 3:
            #Get current selected index
            str_types = []
            if self.get_party_str_type_data() is not None:
                party_ids, str_types = self.get_party_str_type_data()


            if None in str_types or ' ' in str_types or len(str_types) < 1:
                msg = QApplication.translate(
                    'newSTRWiz',
                    'Please select an item from the drop down '
                    'menu under each Social Tenure Type column.'
                )
                self.notifSTR.clear()
                self.notifSTR.insertErrorNotification(msg)
                isValid = False

            if isValid != False:
                self.set_record_to_model(
                    self.str_type, str_types
                )
            if len(self.sel_party) > 1:
                self.doc_notice.clear()
                msg = QApplication.translate(
                    'newSTRWiz',
                    'For each document uploaded, a copy '
                    'will be made based on the number of party.'
                )
                self.doc_notice.insertNotification(msg, INFORMATION)

        if currPageIndex == 5:
            isValid = self.on_create_str()
        return isValid


    def on_add_str(self, progress):
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
        for j, (sel_party, str_type_id) in enumerate(zip(self.sel_party, self.sel_str_type)):
            # get all model objects
            doc_objs = self.sourceDocManager.model_objects()
            # get the number of unique documents.
            number_of_docs = len(doc_objs) / len(self.sel_party)

            str_obj = self.str_model(
                party_id=sel_party.id,
                spatial_unit_id=self.sel_spatial_unit[0].id,
                tenure_type=str_type_id
            )
            progress.setValue(index)
            index = index + 1
            # Insert Supporting Document if a
            # supporting document is uploaded.
            if len(doc_objs) > 0:
                # The number of jumps (to avoid duplication) when
                # looping though document objects
                loop_increment = j * number_of_docs
                # loop through each document objects
                for doc_type_obj in doc_objs:
                    # loop per each number of documents
                    for k in range(number_of_docs):
                        # append into the str obj
                        str_obj.documents.append(
                            doc_objs[k + loop_increment]
                        )
                    # Avoids duplicate entry into the database
                    # in case of batch multi party
                    break

            str_objs.append(str_obj)

        _str_obj.saveMany(str_objs)

    def on_edit_str(self, progress):

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


            strMsg = unicode(QApplication.translate(
                "newSTRWiz",
                "The social tenure relationship has "
                "been successfully created!"
            ))
            QMessageBox.information(
                self, QApplication.translate(
                    "newSTRWiz", "STR Creation"
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
            errMsg = str(e)
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
                    str(self.gpOLTitle),
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
        else:
            self.spatial_unit_notice.clear()
            msg = QApplication.translate(
                "newSTRWiz",
                "Error - The property map cannot be loaded."
            )
            self.spatial_unit_notice.insertErrorNotification(msg)
        
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
        list_item_index = index.model().data(
            index, Qt.DisplayRole
        )
        if list_item_index is not None and \
                not isinstance(list_item_index, (unicode, int)):
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
            self, table_data, headers, str_type_id, parent = None, *args
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
            0, 0, QModelIndex()
        )
        self.frozen_table_view.model().setData(
            index, '', Qt.EditRole
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
        self.setMaximumSize(QSize(5550, 75))
        self.setGeometry(QRect(0, 0, 619, 75))
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
            LOGGER.debug('FrozenTableWidget-resizeEvent: '+str(log))


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
