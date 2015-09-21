"""
/***************************************************************************
Name                 : View STR Relationships
Description          : Main Window for searching and browsing the social tenure
                       relationship of the participating entities.
Date                 : 24/May/2014
copyright            : (C) 2014 by UN-Habitat and implementing partners.
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
from collections import OrderedDict

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from sqlalchemy import (
    func,
    String,
    Table
)
from sqlalchemy.orm import mapper

import stdm.data
from stdm.data import (
    BaseSTDMTableModel,
    ConfigTableReader,
    Content,
    display_name,
    numeric_varchar_columns,
    pg_table_exists,
    ProfileException,
    STRTreeViewModel
)
from stdm.navigation.socialtenure import (
    BaseSTRNode,
    EntityNode,
    EntityNodeFormatter,
    SpatialUnitNode,
    STRNode,
    SupportsDocumentsNode
)
from stdm.security import Authorizer

from notification import (
    NotificationBar
)
from .sourcedocument import (
    SourceDocumentManager,
    DOC_TYPE_MAPPING,
    STR_DOC_TYPE_MAPPING
)
from .str_editor import SocialTenureEditor
from ui_view_str import Ui_frmManageSTR
from ui_str_view_entity import Ui_frmSTRViewEntity
from .stdmdialog import DeclareMapping

class ViewSTRWidget(QMainWindow, Ui_frmManageSTR):
    """
    Search and browse the social tenure relationship of all participating entities.
    """
    def __init__(self, plugin):
        QMainWindow.__init__(self, plugin.iface.mainWindow())
        self.setupUi(self)

        self._plugin = plugin
        self.tbPropertyPreview.set_iface(self._plugin.iface)

        #Center me
        self.move(QDesktopWidget().availableGeometry().center() - self.frameGeometry().center())

        #set whether currently logged in user has permissions to edit existing STR records
        self._can_edit = self._plugin.STRCntGroup.canUpdate()

        '''
        Variable used to store a reference to the currently selected social tenure relationship
        when displaying documents in the supporting documents tab window.
        This ensures that there are no duplicates when the same item is selected over and over again.
        '''
        self._strID = None

        #Used to store the root hash of the currently selected node.
        self._curr_rootnode_hash = ""
        self._source_doc_manager = SourceDocumentManager()
        self._source_doc_manager.documentRemoved.connect(self.onSourceDocumentRemoved)
        self._source_doc_manager.setEditPermissions(self._can_edit)

        self._config_table_reader = ConfigTableReader()

        self.initGui()

    def initGui(self):
        """
        Initialize widget
        """
        self.tb_actions.setVisible(False)
        self._load_entity_configurations()

        #self.gb_supporting_docs.setCollapsed(True)

        #Connect signals
        self.tbSTREntity.currentChanged.connect(self.entityTabIndexChanged)
        self.btnSearch.clicked.connect(self.searchEntityRelations)
        self.btnClearSearch.clicked.connect(self.clearSearch)
        self.tvSTRResults.expanded.connect(self.onTreeViewItemExpanded)

        #Configure notification bar
        self._notif_search_config = NotificationBar(self.vl_notification)

        #Set the results treeview to accept requests for context menus
        self.tvSTRResults.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tvSTRResults.customContextMenuRequested.connect(self.onResultsContextMenuRequested)

        #Load async for the current widget
        self.entityTabIndexChanged(0)

    def _check_permissions(self):
        """
        Enable/disable actions based on the permissions defined in the content
        group.
        """
        if self._can_edit:
            self.tb_actions.addAction(self._new_str_action)
        else:
            self.tb_actions.removeAction(self._new_str_action)

        if len(self.tb_actions.actions()) == 0:
            self.tb_actions.setVisible(False)

        else:
            self.tb_actions.setVisible(True)

    def _load_entity_configurations(self):
        """
        Specify the entity configurations.
        """
        try:
            tables = self._config_table_reader.social_tenure_tables()

            for t in tables:
                #Ensure 'supporting_document' table is not in the list
                if t.find("supporting_document") == -1:
                    entity_cfg = self._entity_config_from_table(t)

                    if not entity_cfg is None:
                        entity_widget = self.add_entity_config(entity_cfg)
                        entity_widget.setNodeFormatter(
                            EntityNodeFormatter(entity_cfg, self.tvSTRResults,
                                                self)
                        )

        except ProfileException as pe:
            self._notif_bar.clear()
            self._notif_bar.insertErrorNotification(pe.message)

    def _entity_config_from_table(self, table_name):
        """
        Creates an EntityConfig object from the table name.
        :param table_name: Name of the database table.
        :type table_name: str
        :return: Entity configuration object.
        :rtype: EntityConfig
        """
        table_display_name = display_name(table_name)
        model = DeclareMapping.instance().tableMapping(table_name)

        if model is not None:
            #Entity configuration
            entity_cfg = EntityConfiguration()
            entity_cfg.Title = table_display_name
            entity_cfg.STRModel = model
            entity_cfg.data_source_name = table_name

            '''
            Load filter and display columns using only those which are of
            numeric/varchar type
            '''
            cols = numeric_varchar_columns(table_name)
            search_cols = self._config_table_reader.table_searchable_columns(table_name)
            disp_cols = self._config_table_reader.table_columns(table_name)

            for c in search_cols:
                #Ensure it is a numeric or text type column
                if c in cols:
                    entity_cfg.filterColumns[c] = display_name(c)

            if len(disp_cols) == 0:
                entity_cfg.displayColumns = entity_cfg.displayColumns

            else:
                for dc in disp_cols:
                    if dc in cols:
                        entity_cfg.displayColumns[dc] = display_name(dc)

            return entity_cfg

        else:
            return None

    def add_entity_config(self, config):
        """
        Set an entity configuration option and add it to the 'Search Entity' tab.
        """
        entityWidg = STRViewEntityWidget(config)
        entityWidg.asyncStarted.connect(self._progressStart)
        entityWidg.asyncFinished.connect(self._progressFinish)
        tabIndex = self.tbSTREntity.addTab(entityWidg, config.Title)

        return entityWidg

    def entityTabIndexChanged(self,index):
        """
        Raised when the tab index of the entity search tab widget changes.
        """
        #Get the current widget in the tab container
        entityWidget = self.tbSTREntity.currentWidget()

        if isinstance(entityWidget,EntitySearchItem):
            entityWidget.loadAsync()

    def searchEntityRelations(self):
        """
        Slot that searches for matching items for the specified entity and corresponding STR entities.
        """
        self._reset_controls()

        entityWidget = self.tbSTREntity.currentWidget()
        if isinstance(entityWidget,EntitySearchItem):
            valid, msg = entityWidget.validate()

            if not valid:
                self._notif_search_config.clear()
                self._notif_search_config.insertErrorNotification(msg)

                return

            formattedNode, results, searchWord = entityWidget.executeSearch()

            #Show error message
            if len(results) == 0:
                noResultsMsg = QApplication.translate("ViewSTR", "No results found for '" + searchWord + "'")
                self._notif_search_config.clear()
                self._notif_search_config.insertErrorNotification(noResultsMsg)

                return

            if formattedNode is not None:
                self._load_root_node(formattedNode)

    def clearSearch(self):
        """
        Clear search input parameters (for current widget) and results.
        """
        entityWidget = self.tbSTREntity.currentWidget()
        if isinstance(entityWidget,EntitySearchItem):
            entityWidget.reset()

        self._reset_controls()

    def _reset_controls(self):
        #Clear tree view
        self._resetTreeView()

        #Clear document listings
        self._deleteSourceDocTabs()

        #Remove spatial unit memory layer
        self.tbPropertyPreview.remove_layer()

    def on_select_results(self, selected, deselected):
        """
        Slot which is raised when the selection is changed in the tree view
        selection model.
        """
        selIndexes = selected.indexes()

        #Check type of node and perform corresponding action
        for mi in selIndexes:
            if mi.isValid():
                node = mi.internalPointer()

                if mi.column() == 0:
                    #Assert if node represents another entity has been clicked
                    self._on_node_reference_changed(node.rootHash())

                    if isinstance(node, SupportsDocumentsNode):
                        src_docs = node.documents()
                        str_id = node.id()

                        if str_id != self._strID:
                            self._strID = str_id
                            self._load_source_documents(src_docs)

                    if isinstance(node, SpatialUnitNode):
                        self.draw_spatial_unit(node.model())

    def onSourceDocumentRemoved(self, container_id):
        """
        Slot raised when a source document is removed from the container.
        If there are no documents in the specified container then remove
        the tab.
        """
        for i in range(self.tbSupportingDocs.count()):
            docwidget = self.tbSupportingDocs.widget(i)
            if docwidget.containerId() == container_id:
                docCount = docwidget.container().count()
                if docCount == 0:
                    self.tbSupportingDocs.removeTab(i)
                    del docwidget
                    break

    def draw_spatial_unit(self, model):
        """
        Render the geometry of the given spatial unit in the spatial view.
        :param row_id: Sqlalchemy oject representing a feature.
        """
        self.tbPropertyPreview.draw_spatial_unit(model)

    def removeSourceDocumentWidget(self,container_id):
        """
        Convenience method that removes the tab widget that lists the source documents
        with the given container id.
        """
        for i in range(self.tbSupportingDocs.count()):
            docwidget = self.tbSupportingDocs.widget(i)
            if docwidget.containerId() == container_id:
                self.tbSupportingDocs.removeTab(i)
                self._source_doc_manager.removeContainer(container_id)
                del docwidget
                break

    def onTreeViewItemExpanded(self,modelindex):
        """
        Raised when a tree view item is expanded.
        Reset the document listing and map view if the hash
        of the parent node is different.
        """
        if modelindex.isValid():
            node = modelindex.internalPointer()
            #Assert if node representing another entity has been clicked
            self._on_node_reference_changed(node.rootHash())

    def onResultsContextMenuRequested(self,pnt):
        """
        Slot raised when the user right-clicks on a node item to request the
        corresponding context menu.
        """
        #Get the model index at the specified point
        mi = self.tvSTRResults.indexAt(pnt)
        if mi.isValid():
            node = mi.internalPointer()
            rMenu = QMenu(self)
            #Load node actions items into the context menu
            node.manageActions(mi,rMenu)
            rMenu.exec_(QCursor.pos())

    def showEvent(self, event):
        """
        (Re)load map layers in the viewer canvas.
        :param event: Window event
        :type event: QShowEvent
        """
        #Check if there are entity configurations defined
        if self.tbSTREntity.count() == 0:
            msg = QApplication.translate("ViewSTR", "There are no configured "
                                        "entities to search against. Please "
                                        "check the social tenure relationship "
                                        "tables in the Form Designer.")
            QMessageBox.critical(self, QApplication.translate("ViewSTR",
                                            "Social Tenure Relationship"),
                                    msg)
            self.setEnabled(False)
            event.ignore()

            return QMainWindow.showEvent(self, event)

        if not self._check_str_table():
            msg = QApplication.translate("ViewSTR", "'social_tenure_relationship' "
                                        "table could not be found. Please "
                                        "recreate the table in the Form "
                                        "Designer and configure the related "
                                        "entities.")
            QMessageBox.critical(self, QApplication.translate("ViewSTR",
                                            "Social Tenure Relationship"),
                                    msg)
            self.setEnabled(False)
            event.ignore()

            return QMainWindow.showEvent(self, event)

        self.setEnabled(True)

        self._notify_no_base_layers()

        self.tbPropertyPreview.refresh_canvas_layers()
        self.tbPropertyPreview.load_web_map()

        return QMainWindow.showEvent(self, event)

    def _check_str_table(self):
        """
        Checks whether a table explicitly named 'social_tenure_relationship'
        exists in th database.
        :return: True if the table exists.Otherwise False.
        :rtype: bool
        """
        return pg_table_exists("social_tenure_relationship", False)

    def _notify_no_base_layers(self):
        """
        Checks if there are any base layers that will be used when
        visualizing the spatial units. If there are no base layers
        then insert warning message.
        """
        self._notif_search_config.clear()

        num_layers = len(self._plugin.iface.legendInterface().layers())
        if num_layers == 0:
            msg = QApplication.translate("ViewSTR", "No basemap layers are loaded in the current project. "
                                                    "Basemap layers enhance the visualization of"
                                                    " spatial units.")
            self._notif_search_config.insertWarningNotification(msg)

    def _deleteSourceDocTabs(self):
        """
        Removes all source document tabs and deletes their references.
        """
        tabCount = self.tbSupportingDocs.count()

        while tabCount != 0:
            srcDocWidget = self.tbSupportingDocs.widget(tabCount-1)
            self.tbSupportingDocs.removeTab(tabCount-1)
            del srcDocWidget
            tabCount -= 1

        self._strID = None
        self._source_doc_manager.reset()

    def _resetTreeView(self):
        """
        Clears the results tree view.
        """
        #Reset tree view
        strModel = self.tvSTRResults.model()
        resultsSelModel = self.tvSTRResults.selectionModel()

        if strModel:
            strModel.clear()

        if resultsSelModel:
            self.disconnect(resultsSelModel, SIGNAL("selectionChanged(const QItemSelection&,const QItemSelection&)"),
                                     self.on_select_results)

    def _load_root_node(self, root):
        """
        Load the search results (formatted into an object of type 'stdm.navigaion.STR') into
        the tree view.
        """
        strTreeViewModel = STRTreeViewModel(root, view=self.tvSTRResults)
        self.tvSTRResults.setModel(strTreeViewModel)

        # Resize tree columns to fit contents
        self._resize_columns()

        #Capture selection changes signals when results are returned in the tree view
        resultsSelModel = self.tvSTRResults.selectionModel()
        resultsSelModel.selectionChanged.connect(self.on_select_results)

    def _resize_columns(self):
        """
        Adjusts the column sizes to fit its contents
        """
        qModel = self.tvSTRResults.model()
        columnCount = qModel.columnCount()

        for i in range(columnCount):
            self.tvSTRResults.resizeColumnToContents(i)

        #Once resized then slightly increase the width of the first column so that text for 'No STR Defined' visible.
        currColWidth = self.tvSTRResults.columnWidth(0)
        newColWidth = currColWidth + 100
        self.tvSTRResults.setColumnWidth(0, newColWidth)

    def _load_source_documents(self, source_docs):
        """
        Load source documents into document listing widget.
        """
        #Configure progress dialog
        progressMsg = QApplication.translate("ViewSTR", "Loading supporting documents...")
        progressDialog = QProgressDialog(progressMsg, "", 0, len(source_docs), self)
        progressDialog.setWindowModality(Qt.WindowModal)

        for i,doc in enumerate(source_docs):
            progressDialog.setValue(i)
            type_id = doc.document_type
            container = self._source_doc_manager.container(type_id)

            #Check if a container has been defined and create if None is found
            if container is None:
                src_doc_widget = SourceDocumentContainerWidget(type_id)
                container = src_doc_widget.container()
                self._source_doc_manager.registerContainer(container, type_id)

                #Add widget to tab container for source documents
                tab_title = QApplication.translate("ViewSTR", "General")
                if type_id in DOC_TYPE_MAPPING:
                    tab_title = DOC_TYPE_MAPPING[type_id]

                else:
                    if type_id in STR_DOC_TYPE_MAPPING:
                        tab_title = STR_DOC_TYPE_MAPPING[type_id]

                self.tbSupportingDocs.addTab(src_doc_widget, tab_title)

            self._source_doc_manager.insertDocFromModel(doc, type_id)

        progressDialog.setValue(len(source_docs))

    def _on_node_reference_changed(self, rootHash):
        """
        Method for resetting document listing and map preview if another root node and its children
        are selected then the documents are reset as well as the map preview control.
        """
        if rootHash != self._curr_rootnode_hash:
            self._deleteSourceDocTabs()
            self._curr_rootnode_hash = rootHash

    def _progressStart(self):
        """
        Load progress dialog window.
        For items whose durations is unknown, 'isindefinite' = True by default.
        If 'isindefinite' is False, then 'rangeitems' has to be specified.
        """
        pass

    def _progressFinish(self):
        """
        Hide progress dialog window.
        """
        pass

    def _edit_permissions(self):
        """
        Returns True/False whether the current logged in user has permissions to create new social tenure relationships.
        If true, then the system assumes that they can also edit STR records.
        """
        canEdit = False
        userName = stdm.data.app_dbconn.User.UserName
        authorizer = Authorizer(userName)
        newSTRCode = "9576A88D-C434-40A6-A318-F830216CA15A"

        #Get the name of the content from the code
        cnt = Content()
        createSTRCnt = cnt.queryObject().filter(Content.code == newSTRCode).first()
        if createSTRCnt:
            name = createSTRCnt.name
            canEdit = authorizer.CheckAccess(name)

        return canEdit

class EntitySearchItem(QObject):
    """
    Abstract class for implementation by widgets that enable users to search for entity records.
    """

    def __init__(self, formatter=None):
        #Specify the formatter that should be applied on the result item. It should inherit from 'stdm.navigation.STRNodeFormatter'
        self.formatter = formatter

    def setNodeFormatter(self, formatter):
        """
        Set the formatter that should be applied on the entity search results.
        """
        self.formatter = formatter

    def validate(self):
        """
        Method for validating the input arguments before a search is conducted.
        Should return bool indicating whether validation was successful and message (applicable if validation fails).
        """
        raise NotImplementedError()

    def executeSearch(self):
        """
        Implemented when the a search operation is executed.
        Should return tuple of formatted results for render in the tree view,raw object results and search word.
        """
        raise NotImplementedError(str(QApplication.translate("ViewSTR",
                                                             "Subclass must implement abstract method.")))

    def loadAsync(self):
        """
        Any initialization that needs to be carried out when the parent container is activated.
        """
        pass

    def errorHandler(self,error):
        """
        Generic handler that logs error messages to the QGIS message log
        """
        QgsMessageLog.logMessage(error,2)

    def reset(self):
        """
        Clear search results.
        """
        pass

class STRViewEntityWidget(QWidget,Ui_frmSTRViewEntity,EntitySearchItem):
    """
    A widget that represents options for searching through an entity.
    """
    asyncStarted = pyqtSignal()
    asyncFinished = pyqtSignal()

    def __init__(self, config, formatter=None, parent=None):
        QWidget.__init__(self, parent)
        EntitySearchItem.__init__(self, formatter)
        self.setupUi(self)
        self.config = config
        self.setConfigOptions()

        #Model for storing display and actual mapping values
        self._completer_model = None
        self._proxy_completer_model = None

        #Hook up signals
        self.cboFilterCol.currentIndexChanged.connect(self._on_column_index_changed)

    def setConfigOptions(self):
        """
        Apply configuration options.
        """
        #self.lblBrowseDescription.setText(self.config.browseDescription)

        #Set filter columns and remove id column
        for col_name, display_name in self.config.filterColumns.iteritems():
            if col_name != "id":
                self.cboFilterCol.addItem(display_name, col_name)

    def loadAsync(self):
        """
        Asynchronously loads an entity's attribute values.
        """
        self.asyncStarted.emit()

        #Create model worker
        workerThread = QThread(self)
        modelWorker = ModelWorker()
        modelWorker.moveToThread(workerThread)

        #Connect signals
        modelWorker.error.connect(self.errorHandler)
        workerThread.started.connect(
                     lambda: modelWorker.fetch(self.config.STRModel, self.currentFieldName()))
        modelWorker.retrieved.connect(self._asyncFinished)
        modelWorker.retrieved.connect(workerThread.quit)
        workerThread.finished.connect(modelWorker.deleteLater)
        workerThread.finished.connect(workerThread.deleteLater)

        #Start thread
        workerThread.start()

    def validate(self):
        """
        Validate entity search widget
        """
        is_valid = True
        message = ""

        if self.txtFilterPattern.text() == "":
            message = QApplication.translate("ViewSTR", "Search word cannot be empty.")
            is_valid = False

        return is_valid, message

    def executeSearch(self):
        """
        Base class override.
        Search for matching items for the specified entity and column.
        """
        model_root_node = None

        search_term = self._searchTerm()

        #Try to get the corresponding search term value from the completer model
        if not self._completer_model is None:
            reg_exp = QRegExp("^%s$"%(search_term), Qt.CaseInsensitive,
                              QRegExp.RegExp2)
            self._proxy_completer_model.setFilterRegExp(reg_exp)

            if self._proxy_completer_model.rowCount() > 0:
                #Get corresponding actual value from the first matching item
                value_model_idx  = self._proxy_completer_model.index(0, 1)
                source_model_idx = self._proxy_completer_model.mapToSource(value_model_idx)

                search_term = self._completer_model.data(source_model_idx, Qt.DisplayRole)

        modelInstance = self.config.STRModel()

        modelQueryObj = modelInstance.queryObject()
        queryObjProperty = getattr(self.config.STRModel, self.currentFieldName())

        #Get property type so that the filter can be applied according to the appropriate type
        propType = queryObjProperty.property.columns[0].type

        try:
            if not isinstance(propType, String):
                results = modelQueryObj.filter(queryObjProperty == search_term).all()

            else:
                results = modelQueryObj.filter(func.lower(queryObjProperty) == func.lower(search_term)).all()

        except StatementError:
            return model_root_node, [], search_term

        if self.formatter is not None:
            self.formatter.setData(results)
            model_root_node = self.formatter.root()

        return model_root_node, results, search_term

    def reset(self):
        """
        Clear search input parameters.
        """
        self.txtFilterPattern.clear()
        if self.cboFilterCol.count() > 0:
            self.cboFilterCol.setCurrentIndex(0)

    def currentFieldName(self):
        """
        Returns the name of the database field from the current item in the combo box.
        """
        currIndex = self.cboFilterCol.currentIndex()
        fieldName = self.cboFilterCol.itemData(currIndex)

        return fieldName

    def _searchTerm(self):
        """
        Returns the search term specified by the user.
        """
        return self.txtFilterPattern.text()

    def _asyncFinished(self, model_values):
        """
        Slot raised when worker has finished retrieving items.
        """
        #Create QCompleter and add values to it.
        self._update_completer(model_values)
        self.asyncFinished.emit()

    def _update_completer(self, values):
        #Get the items in a tuple and put them in a list
        field_formatter = self.config.LookupFormatters.get(self.currentFieldName(),
                                                         None)
        '''
        Store display and actual values in a model for easier mapping and
        retrieval when carrying out searches
        '''
        model_attr_mapping = []

        #Check if there are formatters specified for the current field name
        for mv in values:
            f_model_values = []

            m_val = mv[0]

            #2-column model - display (0) and actual(1)
            if field_formatter is None:
                f_model_values.append(m_val)
                f_model_values.append(m_val)

            else:
                f_model_values.append(field_formatter(m_val))
                f_model_values.append(m_val)

            model_attr_mapping.append(f_model_values)

        self._completer_model = BaseSTDMTableModel(model_attr_mapping, ["",""], self)

        #We will use the QSortFilterProxyModel for filtering purposes
        self._proxy_completer_model = QSortFilterProxyModel()
        self._proxy_completer_model.setDynamicSortFilter(True)
        self._proxy_completer_model.setSourceModel(self._completer_model)
        self._proxy_completer_model.setSortCaseSensitivity(Qt.CaseInsensitive)
        self._proxy_completer_model.setFilterKeyColumn(0)

        #Configure completer
        mod_completer = QCompleter(self._completer_model, self)
        mod_completer.setCaseSensitivity(Qt.CaseInsensitive)
        mod_completer.setCompletionMode(QCompleter.PopupCompletion)
        mod_completer.setCompletionColumn(0)
        mod_completer.setCompletionRole(Qt.DisplayRole)

        self.txtFilterPattern.setCompleter(mod_completer)

    def _on_column_index_changed(self,int):
        """
        Slot raised when the user selects a different filter column.
        """
        self.txtFilterPattern.clear()
        self.loadAsync()

class EntityConfiguration(object):
    """
    Specifies the configuration to apply when creating a new tab widget for performing entity searches.
    """
    browseDescription = "Click on the browse button below to load entity " \
                        "records and their corresponding social tenure " \
                        "relationship definitions."
    defaultFieldName = ""
    #Format of each dictionary item: property/db column name - display name
    filterColumns = OrderedDict()
    displayColumns = OrderedDict()
    groupBy = ""
    STRModel = None
    Title = ""
    data_source_name = ""
    #Functions for formatting values before they are loaded into the completer
    LookupFormatters = {}

    def __init__(self):
        #Reset filter and display columns
        self.filterColumns = OrderedDict()
        self.displayColumns = OrderedDict()

class ModelWorker(QObject):
    """
    Worker for retrieving model attribute values stored in the database.
    """
    retrieved = pyqtSignal(object)
    error = pyqtSignal(unicode)

    pyqtSlot(object, unicode)
    def fetch(self, model, fieldname):
        """
        Fetch attribute values from the database for the specified model
        and corresponding column name.
        """
        if hasattr(model, fieldname):
            try:
                modelInstance = model()
                obj_property = getattr(model, fieldname)
                model_values = modelInstance.queryObject([obj_property]).distinct()
                self.retrieved.emit(model_values)

            except Exception as ex:
                self.error.emit(unicode(ex))

class SourceDocumentContainerWidget(QWidget):
    """
    Widget that enables source documents of one type to be displayed.
    """
    def __init__(self, container_id = -1,parent = None):
        QWidget.__init__(self,parent)

        #Set overall layout for the widget
        vtLayout = QVBoxLayout()
        self.setLayout(vtLayout)

        self.docVtLayout = QVBoxLayout()
        vtLayout.addLayout(self.docVtLayout)

        #Id of the container
        self._containerId = container_id

    def container(self):
        """
        Returns the container in which source documents will rendered in.
        """
        return self.docVtLayout

    def setContainerId(self, id):
        """
        Sets the ID of the container.
        """
        self._containerId = id

    def containerId(self):
        """
        Returns the ID of the container.
        """
        return self._containerId
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        
        