"""
/***************************************************************************
Name                 : Entity Browser Dialog
Description          : Dialog for browsing entity data based on the specified
                       database model.
Date                 : 18/February/2014 
copyright            : (C) 2015 by UN-Habitat and implementing partners.
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
from datetime import date
from collections import OrderedDict

import cProfile
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.utils import (
    iface
)
from qgis.core import (
    QgsMapLayerRegistry,
    QgsCoordinateReferenceSystem
)

from stdm.data.configuration import entity_model
from stdm.data.configuration.columns import (
    GeometryColumn,
    MultipleSelectColumn,
    VirtualColumn
)
from stdm.data.configuration.entity import Entity
from stdm.data.pg_utils import(
    table_column_names,
    qgsgeometry_from_wkbelement,
    export_data,
    fetch_from_table,
    pg_table_count
)

from stdm.data.qtmodels import (
    BaseSTDMTableModel,
    VerticalHeaderSortFilterProxyModel
)

from stdm.ui.forms.widgets import ColumnWidgetRegistry
from stdm.navigation import TableContentGroup
from stdm.network.filemanager import NetworkFileManager
from stdm.ui.forms.editor_dialog import EntityEditorDialog
# from stdm.ui.forms.advanced_search import AdvancedSearch
from stdm.ui.sourcedocument import (
    DocumentWidget,
    network_document_path,
    DOWNLOAD_MODE
)
from stdm.ui.spatial_unit_manager import (
    SpatialUnitManagerDockWidget
)

from stdm.ui.document_viewer import DocumentViewManager

from stdm.ui.gps_tool import GPSToolDialog
from .admin_unit_manager import VIEW,MANAGE,SELECT
from .ui_entity_browser import Ui_EntityBrowser
from .helpers import SupportsManageMixin
from .notification import NotificationBar
from stdm.utils.util import (
    format_name,
    entity_id_to_attr
)

from stdm.settings import (
        get_entity_browser_record_limit,
        get_entity_sort_order
        )

__all__ = ["EntityBrowser", "EntityBrowserWithEditor", "ContentGroupEntityBrowser"]

class _EntityDocumentViewerHandler(object):
    """
    Class that loads the document viewer to display all documents
    pertaining to a given entity record.
    """
    def __init__(self, title='', parent=None):
        self._title = title
        self._parent = parent

        # Set default manager for document viewing
        self._doc_view_manager = DocumentViewManager(self._parent)
        self._doc_view_manager.setWindowTitle(self._title)
        self._network_doc_path = network_document_path()
        self._network_manager = NetworkFileManager(self._network_doc_path)

    def _create_document_viewer(self, d):
        doc_widget_proxy = DocumentWidget(
            fileManager=self._network_manager,
            mode=DOWNLOAD_MODE,
            view_manager=self._doc_view_manager
        )
        doc_widget_proxy.setModel(d)
        # Load proxies to the document view manager
        return self._doc_view_manager.load_viewer(doc_widget_proxy, False)

    def load(self, documents):
        # Reset viewer
        self._doc_view_manager.reset()

        # Assert if the root document directory exists
        if not self.root_directory_exists():
            base_msg = QApplication.translate(
                'EntityBrowser',
                'The root document directory does not exist'
            )
            msg = u'{0}:\n{1}'.format(base_msg, self._network_doc_path)
            QMessageBox.critical(self._parent, self._title, msg)

            return

        # Configure progress bar
        num_docs = len(documents)
        prog_dlg = QProgressDialog('', None, 0, num_docs, self._parent)
        prog_dlg.setWindowModality(Qt.WindowModal)
        prog_msg = QApplication.translate(
            'EntityBrowser',
            'Loading {0:d} of {1:d}'
        )

        QApplication.setOverrideCursor(Qt.WaitCursor)

        # Create document widgets proxies
        # for loading into the doc viewer
        for i, d in enumerate(documents):
            #Update progress dialog
            p_msg = prog_msg.format((i+1), num_docs)
            prog_dlg.setLabelText(p_msg)
            prog_dlg.setValue(i)

            status = self._create_document_viewer(d)

            if not status:
                QApplication.restoreOverrideCursor()
                prog_dlg.hide()

            QApplication.processEvents()

        prog_dlg.setValue(num_docs)

        #cRestore pointer cursor
        QApplication.restoreOverrideCursor()

        self._doc_view_manager.setVisible(True)

    def root_directory_exists(self):
        # Returns True if the root document
        # directory exists, otherwise False.
        dir = QDir(self._network_doc_path)

        return dir.exists()


class EntityBrowser(SupportsManageMixin, QDialog, Ui_EntityBrowser):
    """
    Dialog for browsing entity records in a table view.
    """

    # Custom signal that is raised when the dialog
    # is in SELECT state. It contains
    # the record id of the selected row.

    recordSelected = pyqtSignal(int)
    
    def __init__(self, entity, ent_rec_id=0, parent=None, state=MANAGE, load_records=True, plugin=None):
        QDialog.__init__(self,parent)
        self.setupUi(self)

        # Add maximize buttons
        self.setWindowFlags(
            self.windowFlags() |
            Qt.WindowSystemMenuHint |
            Qt.WindowMaximizeButtonHint
        )

        SupportsManageMixin.__init__(self, state)
        # Init document viewer setup
        self._view_docs_act = None
        viewer_title = QApplication.translate(
            'EntityBrowser',
            'Document Viewer'
        )

        self.doc_viewer_title = u'{0} {1}'.format(
            entity.ui_display(),
            viewer_title
        )

        self._doc_viewer = _EntityDocumentViewerHandler(
            self.doc_viewer_title,
            self
        )
        
        self.load_records = load_records
        #Initialize toolbar
        self.plugin = plugin
        self.tbActions = QToolBar()
        self.tbActions.setObjectName('eb_actions_toolbar')
        self.tbActions.setIconSize(QSize(16, 16))
        self.tbActions.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.vlActions.addWidget(self.tbActions)

        self._entity = entity
        self._dbmodel = entity_model(entity)
        self._state = state
        self._tableModel = None
        self._parent = parent
        self._data_initialized = False
        self._notifBar = NotificationBar(self.vlNotification)
        self._headers = []
        self._entity_attrs = []
        self._cell_formatters = {}
        self.filtered_records = []
        self._searchable_columns = OrderedDict()
        self._show_docs_col = False
        self.child_model = OrderedDict()
        #ID of a record to select once records have been added to the table
        self._select_item = None
        self.current_records = 0

        self.parent_record_id = ent_rec_id
        self.record_limit = self.get_records_limit() #get_entity_browser_record_limit()
        self.sort_order = get_entity_sort_order()

        #Enable viewing of supporting documents
        if self.can_view_supporting_documents:
            self._add_view_supporting_docs_btn()

        # self._add_advanced_search_btn()
        #Connect signals
        self.buttonBox.accepted.connect(self.onAccept)
        self.tbEntity.doubleClicked[QModelIndex].connect(self.onDoubleClickView)

    def get_records_limit(self):
        records = get_entity_browser_record_limit()
        if records == 0:
            records = pg_table_count(self.entity.name)
        return records

    def children_entities(self):
        """
        :return: Returns a list of children entities
        that refer to the main entity as the parent.
        :rtype: list
        """
        return [ch for ch in self._entity.children()
                if ch.TYPE_INFO == Entity.TYPE_INFO]

    @property
    def entity(self):
        """
        :return: Returns the Entity object used in this browser.
        :rtype: Entity
        """
        return self._entity

    @property
    def can_view_supporting_documents(self):
        """
        :return: True if the browser supports the viewing of supporting
        documents.
        :rtype: bool
        """
        test_ent_obj = self._dbmodel()

        if self._entity.supports_documents \
                and hasattr(test_ent_obj, 'documents'):
            return True

        return False

    def _add_view_supporting_docs_btn(self):
        #Add button for viewing supporting documents if supported
        view_docs_str = QApplication.translate(
            'EntityBrowser',
            'View Documents'
        )
        self._view_docs_act = QAction(
            QIcon(':/plugins/stdm/images/icons/document.png'),
            view_docs_str,
            self
        )

        #Connect signal for showing document viewer
        self._view_docs_act.triggered.connect(self.on_load_document_viewer)

        self.tbActions.addAction(self._view_docs_act)


    # def _add_advanced_search_btn(self):
    #     #Add button for viewing supporting documents if supported
    #     search_str = QApplication.translate(
    #         'EntityBrowser',
    #         'Advanced Search'
    #     )
    #     self._search_act = QAction(
    #         QIcon(':/plugins/stdm/images/icons/advanced_search.png'),
    #         search_str,
    #         self
    #     )

    #     #Connect signal for showing document viewer
    #     self._search_act.triggered.connect(self.on_advanced_search)

    #     self.tbActions.addAction(self._search_act)

    def dateFormatter(self):
        """
        Function for formatting date values
        """
        return self._dateFormatter

    def setDateFormatter(self,formatter):
        """
        Sets the function for formatting date values. Overrides the default function.
        """
        self._dateFormatter = formatter

    def state(self):
        '''
        Returns the current state that the dialog has been configured in.
        '''
        return self._state

    def setState(self,state):
        '''
        Set the state of the dialog.
        '''
        self._state = state

    def set_selection_record_id(self, id):
        """
        Set the ID of a record to be selected only once all records have been
        added to the table view.
        :param id: Record id to be selected.
        :type id: int
        """
        self._select_item = id

    def title(self):
        '''
        Set the title of the entity browser dialog.
        Protected method to be overridden by subclasses.
        '''
        records = QApplication.translate('EntityBrowser', 'Records')
        if self._entity.label != '':
            title = self._entity.label
        else:
            title = self._entity.ui_display()

        return u'{} {}'.format(title, records)

    def setCellFormatters(self,formattermapping):
        '''
        Dictionary of attribute mappings and corresponding functions for
        formatting the attribute value to the display value.
        '''
        self._cell_formatters = formattermapping

    def addCellFormatter(self,attributeName,formatterFunc):
        '''
        Add a new cell formatter configuration to the collection
        '''
        self._cell_formatters[attributeName] = formatterFunc

    def showEvent(self,showEvent):
        '''
        Override event for loading the database records once the dialog is visible.
        This is for improved user experience i.e. to prevent the dialog from taking
        long to load.
        '''
        self.setWindowTitle(unicode(self.title()))

        if self._data_initialized:
            return
        try:
            if not self._dbmodel is None:
                self._initializeData()
        except Exception as ex:
            QMessageBox.critical(
                self,
                QApplication.translate(
                    'EntityBrowser', 'showEvent method'
                ),
                unicode(ex.message))
            return

        self._data_initialized = True

    def hideEvent(self,hideEvent):
        '''
        Override event which just sets a flag to indicate that the data records have already been
        initialized.
        '''
        pass

    def clear_selection(self):
        """
        Deselects all selected items in the table view.
        """
        self.tbEntity.clearSelection()

    def clear_notifications(self):
        """
        Clears all notifications messages in the dialog.
        """
        self._notifBar.clear()

    def recomputeRecordCount(self, init_data=False):
        '''
        Get the number of records in the specified table and updates the window title.
        '''
        entity = self._dbmodel()

        # Get number of records
        numRecords = entity.queryObject().count()

        if init_data:
            if self.current_records < 1:
                if numRecords > self.record_limit:
                    self.current_records = self.record_limit
                    numRecords = self.record_limit
                else:
                    self.current_records = numRecords

        rowStr = QApplication.translate('EntityBrowser', 'row') \
            if numRecords == 1 \
            else QApplication.translate('EntityBrowser', 'rows')
        showing = QApplication.translate('EntityBrowser', 'Showing')
        windowTitle = u"{0} - {1} {2} of {3} {4}".format(
            self.title(), showing, self.current_records, numRecords, rowStr
        )

        self.setWindowTitle(windowTitle)

        return numRecords

    def _init_entity_columns(self):
        """
        Asserts if the entity columns actually do exist in the database. The
        method also initializes the table headers, entity column and cell
        formatters.
        """
        self._headers[:] = []
        table_name = self._entity.name
        columns = table_column_names(table_name)
        missing_columns = []

        header_idx = 0

        #Iterate entity column and assert if they exist

        for c in self._entity.columns.values():


            # Exclude geometry columns
            if isinstance(c, GeometryColumn):
                continue

            # Do not include virtual columns in list of missing columns
            if not c.name in columns and not isinstance(c, VirtualColumn):
                missing_columns.append(c.name)

            else:
                header = c.ui_display()
                self._headers.append(header)
                col_name = c.name

                '''
                If it is a virtual column then use column name as the header
                but fully qualified column name (created by SQLAlchemy
                relationship) as the entity attribute name.
                '''

                if isinstance(c, MultipleSelectColumn):
                    col_name = c.model_attribute_name

                self._entity_attrs.append(col_name)

                # Get widget factory so that we can use the value formatter
                w_factory = ColumnWidgetRegistry.factory(c.TYPE_INFO)
                if not w_factory is None:
                    formatter = w_factory(c)
                    self._cell_formatters[col_name] = formatter

                # Set searchable columns
                if c.searchable:
                    self._searchable_columns[c.ui_display()] = {
                        'name': c.name,
                        'header_index': header_idx
                    }

                header_idx += 1

        if len(missing_columns) > 0:
            msg = QApplication.translate(
                'EntityBrowser',
                u'The following columns have been defined in the '
                u'configuration but are missing in corresponding '
                u'database table, please re-run the configuration wizard '
                u'to create them.\n{0}'.format(
                    '\n'.join(missing_columns)
                )
            )

            QMessageBox.warning(
                self,
                QApplication.translate('EntityBrowser','Entity Browser'),
                msg
            )

    def _select_record(self, id):
        #Selects record with the given ID.
        if id is None:
            return

        m = self.tbEntity.model()
        s = self.tbEntity.selectionModel()

        start_idx = m.index(0, 0)
        idxs = m.match(
            start_idx,
            Qt.DisplayRole,
            id,
            1,
            Qt.MatchExactly
        )

        if len(idxs) > 0:
            sel_idx = idxs[0]
             #Select item
            s.select(
                sel_idx,
                QItemSelectionModel.ClearAndSelect|QItemSelectionModel.Rows
            )

    # def on_advanced_search(self):
    #     search = AdvancedSearch(self._entity, parent=self)
    #     search.show()

    def on_load_document_viewer(self):
        #Slot raised to show the document viewer for the selected entity
        sel_rec_ids = self._selected_record_ids()

        if len(sel_rec_ids) == 0:
            return

        #Get document objects
        ent_obj = self._dbmodel()

        for sel_id in sel_rec_ids:
            er = ent_obj.queryObject().filter(self._dbmodel.id == sel_id).first()
            if not er is None:
                docs = er.documents

                #Notify there are no documents for the selected doc
                if len(docs) == 0:
                    msg = QApplication.translate(
                        'EntityBrowser',
                        'There are no supporting documents for the selected record.'
                    )

                    QMessageBox.warning(
                        self,
                        self.doc_viewer_title,
                        msg
                    )

                    continue

                self._doc_viewer.load(docs)

    def _initializeData(self, filtered_records=None):
        '''
        Set table model and load data into it.
        '''
        if self._dbmodel is None:
            msg = QApplication.translate(
                'EntityBrowser',
                'The data model for the entity could not be loaded, \n'
                'please contact your database administrator.'
            )
            QMessageBox.critical(
                self,
                QApplication.translate('EntityBrowser', 'Entity Browser'),
                msg
            )

        else:
            self._init_entity_columns()

            # Load entity data. There might be a better way in future in order
            # to ensure that there is a balance between user data discovery
            # experience and performance.
            if filtered_records is not None:
                self.current_records = filtered_records.rowcount

            numRecords = self.recomputeRecordCount(init_data=True)

            # Load progress dialog
            progressLabel = QApplication.translate(
                "EntityBrowser", "Fetching Records..."
            )
            progressDialog = QProgressDialog(
                progressLabel, None, 0, numRecords, self
            )

            QApplication.processEvents()
            progressDialog.show()
            progressDialog.setValue(0)

            entity_records = []
            # Add records to nested list for enumeration in table model
            load_data = True
            if self.plugin is not None:
                if self._entity.name in self.plugin.entity_table_model.keys():
                    if filtered_records is None:
                        self._tableModel = self.plugin.entity_table_model[
                            self._entity.name
                        ]

            if isinstance(self._parent, EntityEditorDialog):
                load_data = True

            if load_data:
                # Only one filter is possible.
                if len(self.filtered_records) > 0:
                    entity_records = self.filtered_records
                else:
                    entity_cls = self._dbmodel()

                    ordering = self.get_sorting_order(self._entity)

                    if type(self.parent_record_id) == int and self.parent_record_id > 0:
                        col = self.filter_col(self._entity)
                        if col is None:
                            entity_records = entity_cls.queryObject().filter().order_by(
                                    ordering).limit(self.record_limit).all()
                        else:
                            child_model = entity_model(self._entity)
                            col_name = getattr(child_model, col.name)
                            child_model_obj = child_model()
                            entity_records = child_model_obj.queryObject().filter(
                                    col_name==self.parent_record_id
                                    ).order_by(ordering).all()
                    else: 
                        #if isinstance(self._parent, QMainWindow):
                        if not isinstance(self._parent, EntityEditorDialog):
                            entity_records = entity_cls.queryObject().filter().order_by(
                                    ordering).limit(self.record_limit).all()

                    numRecords = len(entity_records)

            # if self._tableModel is None:
                entity_records_collection = []
                for i, er in enumerate(entity_records):
                    if i == self.record_limit:
                        break
                    QApplication.processEvents()
                    entity_row_info = []
                    progressDialog.setValue(i)
                    try:
                        for attr in self._entity_attrs:
                            attr_val = getattr(er, attr)

                            # Check if there are display formatters and apply if
                            # one exists for the given attribute.
                            if attr_val is not None: # No need of formatter for None value
                                if attr in self._cell_formatters:
                                    formatter = self._cell_formatters[attr]
                                    attr_val = formatter.format_column_value(attr_val)
                            entity_row_info.append(attr_val)
                    except Exception as ex:
                        QMessageBox.critical(
                            self,
                            QApplication.translate(
                                'EntityBrowser', 'Loading Records'
                            ),
                            unicode(ex.message))
                        return

                    entity_records_collection.append(entity_row_info)


                self._tableModel = BaseSTDMTableModel(
                    entity_records_collection, self._headers, self
                )

                if self.plugin is not None:
                    self.plugin.entity_table_model[self._entity.name] = \
                            self._tableModel

            # Add filter columns
            for header, info in self._searchable_columns.iteritems():
                column_name, index = info['name'], info['header_index']
                if column_name != 'id':
                    self.cboFilterColumn.addItem(header, info)

            #Use sortfilter proxy model for the view
            self._proxyModel = VerticalHeaderSortFilterProxyModel()
            self._proxyModel.setDynamicSortFilter(True)
            self._proxyModel.setSourceModel(self._tableModel)
            self._proxyModel.setSortCaseSensitivity(Qt.CaseInsensitive)

            #USe first column in the combo for filtering
            if self.cboFilterColumn.count() > 0:
                self.set_proxy_model_filter_column(0)

            self.tbEntity.setModel(self._proxyModel)
            #if numRecords < self.record_limit:

            self.tbEntity.setSortingEnabled(True)
            self.tbEntity.sortByColumn(1, Qt.AscendingOrder)

            #First (ID) column will always be hidden
            #self.tbEntity.hideColumn(0)

            #self.tbEntity.horizontalHeader().setResizeMode(QHeaderView.Interactive)
            #self.tbEntity.horizontalHeader().resizeSections(QHeaderView.Stretch)

            #self.tbEntity.resizeColumnsToContents()

            #Connect signals
            self.connect(self.cboFilterColumn, SIGNAL('currentIndexChanged (int)'), self.onFilterColumnChanged)
            self.connect(self.txtFilterPattern, SIGNAL('textChanged(const QString&)'), self.onFilterRegExpChanged)

            #Select record with the given ID if specified
            if not self._select_item is None:
                self._select_record(self._select_item)

            if numRecords > 0:
                # Set maximum value of the progress dialog
                progressDialog.setValue(numRecords)
            else:
                progressDialog.close()

    def filter_col(self, child_entity):
        for col in child_entity.columns.values():
            if col.TYPE_INFO == 'FOREIGN_KEY':
                return col
                #parent_entity = col.parent
                #if parent_entity == self._entity:
                    #return col

    def get_sorting_order(self, entity):
        '''
        Return a string containing a column and sort order (asc-Ascending, desc-Descending)
        :rtype: str
        '''
        ordering = ''

        if self.sort_order is None:
            return ordering

        if self.sort_order=='':
            return ordering

        if self.sort_order == 'idasc':
            ordering ='id asc'

        if self.sort_order == 'iddesc':
            ordering = 'id desc'

        if self.sort_order not in ['idasc', 'iddesc']:
            sort_field = self.get_sorting_field(entity)
            if sort_field == "":
                ordering = 'id desc'
            else:
                ordering = sort_field+' '+self.sort_order

        return ordering

    def get_sorting_field(self, entity):
        '''
        Return sorting column based on the rowindex of the column
        in the entity. Rowindex is set when you re-order the columns (drag-n-drop)
        in the configration wizard (Rowindex is saved in the configuration file).
        Column with the smallest(positive integer) rowindex is the first
        column on an entity, and thats the column we use for sorting.

        :rtype: str
        '''
        try:
            cols = {}
            for k in entity.updated_columns.keys():
                cols[int(entity.updated_columns[k].row_index)] = k
            cols_ordered = OrderedDict(sorted(cols.items()))
            min_id = min(i for i in cols_ordered.keys() if i > -1)
            column = cols_ordered[min_id]
        except:
            column = ""
        return column

            
    def _header_index_from_filter_combo_index(self, idx):
        col_info = self.cboFilterColumn.itemData(idx)
        return col_info['name'], col_info['header_index']

    def set_proxy_model_filter_column(self, index):
        #Set the filter column for the proxy model using the combo index
        name, header_idx = self._header_index_from_filter_combo_index(index)
        self._proxyModel.setFilterKeyColumn(header_idx)

    def onFilterColumnChanged(self, index):
        '''
        Set the filter column for the proxy model.
        '''
        self.set_proxy_model_filter_column(index)

    def _onFilterRegExpChanged(self,text):
        cProfile.runctx('self._onFilterRegExpChanged(text)', globals(), locals())

    def onFilterRegExpChanged(self,text):
        '''
        Slot raised whenever the filter text changes.
        '''
        regExp = QRegExp(text,Qt.CaseInsensitive,QRegExp.FixedString)
        self._proxyModel.setFilterRegExp(regExp)

    def onDoubleClickView(self,modelindex):
        '''
        Slot raised upon double clicking the table view.
        To be implemented by subclasses.
        '''
        pass

    def _selected_record_ids(self):
        '''
        Get the IDs of the selected row in the table view.
        '''
        self._notifBar.clear()

        selected_ids = []
        sel_row_indices = self.tbEntity.selectionModel().selectedRows(0)

        if len(sel_row_indices) == 0:
            msg = QApplication.translate("EntityBrowser",
                                         "Please select a record from the table.")

            self._notifBar.insertWarningNotification(msg)

            return selected_ids

        for proxyRowIndex in sel_row_indices:
            #Get the index of the source or else the row items will have unpredictable behavior
            row_index = self._proxyModel.mapToSource(proxyRowIndex)
            entity_id = row_index.data(Qt.DisplayRole)
            selected_ids.append(entity_id)

        return selected_ids

    def onAccept(self):
        '''
        Slot raised when user clicks to accept the dialog. The resulting action will be dependent
        on the state that the browser is currently configured in.
        '''
        selIDs = self._selected_record_ids()
        if len(selIDs) == 0:
            return

        if self._mode == SELECT:
            #Get all selected records
            for sel_id in selIDs:
                self.recordSelected.emit(sel_id)

            rec_selected = QApplication.translate(
                'EntityBrowser',
                'record(s) selected'
            )

            msg = u'{0:d} {1}.'.format(len(selIDs), rec_selected)
            self._notifBar.insertInformationNotification(msg)

    def addModelToView(self, model_obj):
        '''
        Convenience method for adding model info into the view.
        '''
        insertPosition = self._tableModel.rowCount()
        self._tableModel.insertRows(insertPosition, 1)

        for i, attr in enumerate(self._entity_attrs):

            prop_idx = self._tableModel.index(insertPosition, i)
            attr_val = getattr(model_obj, attr)

            '''
            Check if there are display formatters and apply if one exists
            for the given attribute.
            '''
            if attr in self._cell_formatters:
                formatter = self._cell_formatters[attr]
                attr_val = formatter.format_column_value(attr_val)

            self._tableModel.setData(prop_idx, attr_val)
        return insertPosition

    def _model_from_id(self, record_id, row_number):
        '''
        Convenience method that returns the model object based on its ID.
        '''
        dbHandler = self._dbmodel()
        modelObj = dbHandler.queryObject().filter(
            self._dbmodel.id == record_id
        ).first()

        if modelObj is None:
            modelObj = self.child_model[row_number+1]

        return modelObj


class EntityBrowserWithEditor(EntityBrowser):
    """
    Entity browser with added functionality for carrying out CRUD operations
    directly.
    """
    def __init__(self, entity, r_id=0, parent=None, state=MANAGE, load_records=True, plugin=None):
        EntityBrowser.__init__(self, entity, ent_rec_id=r_id, parent=parent, state=MANAGE, load_records=load_records, plugin=plugin)

        self.record_id = 0

        self.highlight = None
        self.load_records = load_records
        self.selection_layer = None
        self.plugin = plugin
        self.entity_browser = self

        #Add action toolbar if the state contains Manage flag
        if (state & MANAGE) != 0:
            add = QApplication.translate("EntityBrowserWithEditor", "Add")
            edit = QApplication.translate("EntityBrowserWithEditor","Edit")
            remove = QApplication.translate("EntityBrowserWithEditor", "Remove")

            self._newEntityAction = QAction(QIcon(":/plugins/stdm/images/icons/add.png"),
                                            add, self)

            self.connect(self._newEntityAction,SIGNAL("triggered()"),self.onNewEntity)

            self._editEntityAction = QAction(QIcon(":/plugins/stdm/images/icons/edit.png"),
                                             edit,self)
            self._editEntityAction.setObjectName(
                QApplication.translate("EntityBrowserWithEditor", "edit_tool")
            )


            self.connect(self._editEntityAction,SIGNAL("triggered()"),self.onEditEntity)

            self._removeEntityAction = QAction(QIcon(":/plugins/stdm/images/icons/remove.png"),
                                  remove, self)
            self._removeEntityAction.setObjectName(
                QApplication.translate("EntityBrowserWithEditor", "remove_tool")
            )
            self.connect(self._removeEntityAction,SIGNAL("triggered()"),self.onRemoveEntity)

            #Manage position of the actions based on whether the entity
            # supports documents.
            if self.can_view_supporting_documents:
                manage_acts = [self._newEntityAction, self._editEntityAction,
                               self._removeEntityAction]
                self.tbActions.insertActions(self._view_docs_act, manage_acts)

                #Add action separator
                self._act_sep = QAction(self)
                self._act_sep.setSeparator(True)
                self.tbActions.insertAction(self._view_docs_act, self._act_sep)

            else:
                self.tbActions.addAction(self._newEntityAction)
                self.tbActions.addAction(self._editEntityAction)
                self.tbActions.addAction(self._removeEntityAction)

            if isinstance(parent, EntityEditorDialog):
                if self.can_view_supporting_documents:
                    self._view_docs_act.setVisible(False)
                self.parent_entity = parent._entity

            else:
                self.parent_entity = None

            # hide the add button and add layer preview for spatial entity
            if entity.has_geometry_column(): #and self.parent_entity is None:
                self.sp_unit_manager = SpatialUnitManagerDockWidget(
                        iface, self.plugin)
                #self.sp_unit_manager = self.plugin.spatialLayerManagerDockWidget

                self.geom_cols = self.sp_unit_manager.geom_columns(
                    self._entity
                )

                self.add_spatial_unit_layer()

                self.tbEntity.clicked.connect(
                    self.on_select_attribute
                )

                self.tbEntity.entered.connect(
                    self.on_select_attribute
                )

                self.shift_spatial_entity_browser()

                # Hide the add button from spatial tables
                # self._newEntityAction.setVisible(False)

            self._editor_dlg = EntityEditorDialog

    def onNewEntity(self):
        '''
        Load editor dialog for adding a new record.
        '''
        self._notifBar.clear()

        if not self._can_add_edit():
            msg = QApplication.translate(
                'EntityBrowserWithEditor',
                'There are no user-defined columns for this entity.'
            )
            self._notifBar.insertErrorNotification(msg)

            return
        if self._entity.has_geometry_column():
            self.sp_unit_manager.active_layer_source()

            gps_tool = GPSToolDialog(
                iface,
                self._entity,
                self._entity.name,
                self.sp_unit_manager.active_sp_col,
                reload=False,
                entity_browser=self
            )

            result = gps_tool.exec_()
            result = False # a workaround to avoid duplicate model insert
            self.addEntityDlg = gps_tool.entity_editor
        else:
            self.addEntityDlg = self._editor_dlg(
                self._entity, parent=self, parent_entity=self.parent_entity, plugin=self.plugin
            )

            self.addEntityDlg.addedModel.connect(self.on_save_and_new)

            result = self.addEntityDlg.exec_()

        if result == QDialog.Accepted:
            model_obj = self.addEntityDlg.model()
            if self.addEntityDlg.is_valid:
                if self.parent_entity is None:
                    self.addModelToView(model_obj)
                    self.recomputeRecordCount()

    def on_save_and_new(self, model):
        """
        A slot raised when save and new button is clicked. It updates
        the entity browser with the new model added.
        :param model: The model saved.
        :type model: SQL Alchemy Model
        """
        if model is not None:
            insert_position = self.addModelToView(model)
            self.set_child_model(model, insert_position + 1)
            self.recomputeRecordCount()

    def _can_add_edit(self):
        """
        Check if there are columns specified (apart from id) for the given
        entity.
        :return: Returns True if there are other columns apart from id,
        otherwise False.
        """
        columns = self._entity.columns.values()

        if len(columns) < 2:
            return False

        return True

    def onEditEntity(self):
        '''
        Slot raised to load the editor for the selected row.
        '''
        self._notifBar.clear()

        if not self._can_add_edit():
            msg = QApplication.translate(
                'EntityBrowserWithEditor',
                'There are no user-defined columns for this entity.'
            )
            self._notifBar.insertErrorNotification(msg)

            return
        if self.tbEntity.selectionModel() is None:
            return

        selRowIndices = self.tbEntity.selectionModel().selectedRows(0)

        if len(selRowIndices) == 0:
            msg = QApplication.translate("EntityBrowserWithEditor",
                                         "Please select a record in the table"
                                         " below for editing.")
            self._notifBar.insertWarningNotification(msg)

            return

        #Exit if more than one record has been selected
        if len(selRowIndices) > 1:
            msg = QApplication.translate(
                "EntityBrowserWithEditor",
                "Multiple selection detected, please choose one record "
                "only for editing."
            )
            self._notifBar.insertWarningNotification(msg)

            return

        rowIndex = self._proxyModel.mapToSource(selRowIndices[0])
        recordid = rowIndex.data()

        self._load_editor_dialog(recordid, rowIndex.row())

    def set_child_model(self, model, row_position):
        """
        Sets the child model so that it can be used for editing and deleting if
        needed.
        :param model: The child model saved
        :type model: Object
        """
        self.child_model[row_position] = model


    def onRemoveEntity(self):
        '''
        Load editor dialog for editing an existing record.
        '''
        self._notifBar.clear()

        sel_row_indices = self.tbEntity.selectionModel().selectedRows(0)


        if len(sel_row_indices) == 0:
            msg = QApplication.translate(
                "EntityBrowserWithEditor",
                "Please select one or more records in the "
                "table below to be deleted."
            )
            self._notifBar.insertWarningNotification(msg)

            return

        msg = QApplication.translate(
            "EntityBrowserWithEditor",
            "Are you sure you want to delete the selected record(s)?\n"
            "This action cannot be undone."
        )

        response = QMessageBox.warning(
            self,
            QApplication.translate(
                "EntityBrowserWithEditor",
                "Delete Record(s)"),
            msg,
            QMessageBox.Yes|QMessageBox.No, QMessageBox.No
        )

        if response == QMessageBox.No:
            return

        while len(sel_row_indices) > 0:

            ri = sel_row_indices[0]
            source_row_index = self._proxyModel.mapToSource(ri)
            record_id = source_row_index.data()

            row_number = source_row_index.row()

            #Delete record
            result = self._delete_record(record_id, row_number)

            if not result:
                title = QApplication.translate(
                'EntityBrowserWithEditor',
                'Delete Record(s)'
                )

                msg =  QApplication.translate(
                'EntityBrowserWithEditor',
                'An error occurred while attempting to delete a record, this '
                'is most likely caused by a dependency issue.\nPlease check '
                'if the record has dependencies such as social tenure '
                'relationship or related entities. If it has then delete '
                'these dependencies first.'
                )
                QMessageBox.critical(self, title, msg)

                break

            #Refresh list of selected records
            sel_row_indices = self.tbEntity.selectionModel().selectedRows(0)


    def remove_rows(self):
        """
        Removes rows from the entity browser.
        """
        if self.tbEntity.model() is not None:
            row_count = self.tbEntity.model().rowCount()
            self.tbEntity.model().removeRows(0, row_count)

    def _load_editor_dialog(self, recid, rownumber):
        '''
        Load editor dialog based on the selected model instance with the given ID.
        '''
        model_obj = self._model_from_id(recid, rownumber)
        # show GPS editor if geometry
        if self._entity.has_geometry_column():
            self.sp_unit_manager.active_layer_source()

            gps_tool = GPSToolDialog(
                iface,
                self._entity,
                self._entity.name,
                self.sp_unit_manager.active_sp_col,
                model=model_obj,
                reload=False,
                row_number=rownumber,
                entity_browser=self
            )

            result = gps_tool.exec_()
        else:
            #Load editor dialog
            print('XXX -->> XXX')
            edit_entity_dlg = self._editor_dlg(self._entity, model=model_obj,
                                             parent=self, parent_entity=self.parent_entity, plugin=self.plugin)

            result = edit_entity_dlg.exec_()

        if result == QDialog.Accepted:

            if self._entity.has_geometry_column():
                edit_entity_dlg = gps_tool.entity_editor

            updated_model_obj = edit_entity_dlg.model()
            if not edit_entity_dlg.is_valid:
                return
            for i, attr in enumerate(self._entity_attrs):
                prop_idx = self._tableModel.index(rownumber, i)
                attr_val = getattr(updated_model_obj, attr)

                '''
                Check if there are display formatters and apply if
                one exists for the given attribute.
                '''
                if attr in self._cell_formatters:
                    formatter = self._cell_formatters[attr]
                    attr_val = formatter.format_column_value(attr_val)

                self._tableModel.setData(prop_idx, attr_val)

    def _delete_record(self, rec_id, row_number):
        """
        Delete the record with the given id and remove it from the table view.
        """
        del_result = True

        if self.parent_entity is not None:
            idx = row_number+1
            if idx in self.child_model:
                del self.child_model[idx]
                del self._parent.child_models[idx, self.entity]

            self._tableModel.removeRows(row_number, 1)
            # Update number of records
            self.recomputeRecordCount()

            #Clear previous notifications
            self._notifBar.clear()

        #Remove record from the database
        dbHandler = self._dbmodel()
        entity = dbHandler.queryObject().filter(
            self._dbmodel.id == rec_id
        ).first()

        if entity:
            result = entity.delete()

            if not result:
                return False

            self._tableModel.removeRows(row_number, 1)

            #Clear previous notifications
            self._notifBar.clear()

            #Notify user
            delMsg = QApplication.translate(
                "EntityBrowserWithEditor",
                "Record successfully deleted!"
            )

            self._notifBar.insertInformationNotification(delMsg)

            #Update number of records
            self.recomputeRecordCount()

        return del_result

    def onDoubleClickView(self, modelindex):
        '''
        Override for loading editor dialog.
        '''
        rowIndex = self._proxyModel.mapToSource(modelindex)
        rowNumber = rowIndex.row()
        recordIdIndex = self._tableModel.index(rowNumber, 0)
    
        recordId = recordIdIndex.data()
        self._load_editor_dialog(recordId,recordIdIndex.row())


    def shift_spatial_entity_browser(self):
        """
        Shift records manager to the bottom left corner
        :rtype:
        :return:
        """
        parent_height = self.parent().geometry().height()
        parent_width = self.parent().geometry().width()
        parent_x = self.parent().geometry().x()
        parent_y = self.parent().geometry().y()
        dialog_width = self.width()
        dialog_height = self.height()
        self.setGeometry(
            parent_x,
            parent_y+parent_height-dialog_height-40,
            dialog_width,
            dialog_height
        )

    def on_select_attribute(self):
        """
        Slot raised when selecting a spatial entity row.
        """
        sel_row_indices = self.tbEntity.\
            selectionModel().selectedRows(0)
        record_ids = []

        for sel_row_index in sel_row_indices:
            rowIndex = self._proxyModel.mapToSource(
                sel_row_index
            )
            record_id = rowIndex.data()
            record_ids.append(record_id)

        self.record_feature_highlighter(record_ids)

    def record_feature_highlighter(self, record_ids):
        """
        Highlights a feature of a record.
        :param record_id: The id of a row
        :type record_id: Integer
        :return: None
        :rtype: NoneType
        """
        if len(record_ids) < 1:
            return

        for geom in self.geom_cols:

            geom_wkb = entity_id_to_attr(
                self._entity,
                geom.name,
                record_ids[0]
            )

            if geom_wkb is not None:

                sel_lyr_name = self.sp_unit_manager. \
                    geom_col_layer_name(
                    self._entity.name, geom
                )

                self.add_spatial_unit_layer(sel_lyr_name)
                layers = QgsMapLayerRegistry.instance().mapLayersByName(
                    sel_lyr_name
                )

                if len(layers) > 0:
                    layers[0].removeSelection()

                    canvas = iface.mapCanvas()

                    layers[0].blockSignals(True)
                    # Get selection and extent while disabling signals of selection
                    # especially for geometry tools.
                    layers[0].select(record_ids)
                    bounding_box = layers[0].boundingBoxOfSelected()

                    layers[0].blockSignals(False)
                    canvas.setCrsTransformEnabled(True)

                    canvas.zoomToSelected(layers[0])

                    #iface.mapCanvas().setExtent(bounding_box)
                    #layers[0].select(record_ids)
                    #canvas.refresh()
                    #self.selection_layer = layers[0]

    def add_spatial_unit_layer(self, layer_name=None):
        """
        Add the spatial unit layer into the map canvas for later use.
        :param layer_name: The name of the layer to be added to the map canvas.
        :type layer_name: String
        """
        if layer_name is not None:
            self.sp_unit_manager.add_layer_by_name(layer_name)
        else:
            # As this is used for startup of
            # entity browser, just add the first geom layer.
            if len(self.geom_cols) > 0:
                layer_name_item = \
                    self.sp_unit_manager.geom_col_layer_name(
                        self._entity.name,
                        self.geom_cols[0]
                )
                self.sp_unit_manager.\
                    add_layer_by_name(layer_name_item)

    def closeEvent(self, event):
        """
        The event handler that is triggered
        when the dialog is closed.
        :param event: the event
        :type QCloseEvent
        :return: None
        """
        if self._entity.has_geometry_column():
            try:
                if self.selection_layer is not None:
                    self.selection_layer.removeSelection()

            except RuntimeError:
                pass

    def hideEvent(self, hideEvent):
        """
        The event handler that is triggered
        when the dialog is hidden.
        :param hideEvent: the event
        :type QCloseEvent
        :return: None
        """
        if self._entity.has_geometry_column():
            if self.selection_layer is not None:
                self.selection_layer.removeSelection()


class ContentGroupEntityBrowser(EntityBrowserWithEditor):
    """
    Entity browser that loads editing tools based on the content permission
    settings defined by the administrator.
    This is an abstract class that needs to be implemented for subclasses
    representing specific entities.
    :param dataModel: Entity
    :param tableContentGroup: Instance of TableContentGroup
    :param parent: Owner of this entity browser
    :param state: Constants to indicate the funtions of a entity browser,
        VIEW=2301, MANAGE=2302,
        SELECT=2303 #When widget is used to select one or more records from the table list
    """
    def __init__(self, dataModel, tableContentGroup, rec_id=0, parent=None, plugin=None, current_user=None, load_recs=False, state=VIEW|MANAGE):
        EntityBrowserWithEditor.__init__(self, dataModel, r_id=rec_id, parent=parent, state=VIEW|MANAGE, load_records=load_recs, plugin=plugin)

        self.current_user = current_user

        self.resize(700,500)
        
        if not isinstance(tableContentGroup, TableContentGroup):
            raise TypeError("Content group is not of type 'TableContentGroup'")

        self._tableContentGroup = tableContentGroup
        
        #Enable/disable tools based on permissions
        if (state & MANAGE) != 0:
            if not self._tableContentGroup.canCreate():
                self._newEntityAction.setVisible(False)
                    
            if not self._tableContentGroup.canUpdate():
                self._editEntityAction.setVisible(False)
                    
            if not self._tableContentGroup.canDelete():
                self._removeEntityAction.setVisible(False)
                
        self._setFormatters() 
        
    def _setFormatters(self):
        """
        Specify formatting mappings.
        Subclasses to implement.
        """   
        pass
    
    def onDoubleClickView(self, modelindex):
        """
        Checks if user has permission to edit.
        """
        if self._tableContentGroup.canUpdate():
            super(ContentGroupEntityBrowser,self).onDoubleClickView(modelindex)
    
    def tableContentGroup(self):
        """
        Returns the content group instance used in the browser.
        """
        return self._tableContentGroup

class ForeignKeyBrowser(EntityBrowser):
    """
    Browser for  foreign key records.
    """
    def __init__(self, parent=None, table=None, state=MANAGE):
        model = table

        if isinstance(table, str) or isinstance(table, unicode):
            #mapping = DeclareMapping.instance()
            #model = mapping.tableMapping(table)
            self._data_source_name = table

        else:
            self._data_source_name = table.__name__

        EntityBrowser.__init__(self, parent, model, state)

    def title(self):
        return QApplication.translate("EnumeratorEntityBrowser",
                    "%s Entity Records")%(self._data_source_name).replace("_"," ").capitalize()
