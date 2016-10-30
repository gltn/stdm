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
from sqlalchemy import exc
from collections import OrderedDict
import logging
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *

from sqlalchemy import (
    func,
    String,
    Table
)
from sqlalchemy.orm import mapper

from stdm.ui.social_tenure.str_tree_view import STRTreeView, EditSTRTreeView

import stdm.data

from stdm.data.qtmodels import (
    BaseSTDMTableModel,
    STRTreeViewModel
)

from stdm.data.database import Content

from stdm.settings import current_profile
from stdm.data.configuration import entity_model

from stdm.navigation.socialtenure import (
    BaseSTRNode,
    EntityNode,
    EntityNodeFormatter,
    SpatialUnitNode,
    STRNode,
    SupportsDocumentsNode
)
from stdm.ui.spatial_unit_manager import SpatialUnitManagerDockWidget
from stdm.security.authorization import Authorizer
from stdm.utils.util import (
    entity_searchable_columns,
    entity_display_columns,
    format_name,
    get_db_attr,
    entity_attr_to_id,
    lookup_parent_entity
)
from .notification import (
    NotificationBar
)
from .sourcedocument import (
    SourceDocumentManager,
    DocumentWidget
)

from ui_view_str import Ui_frmManageSTR
from ui_str_view_entity import Ui_frmSTRViewEntity


LOGGER = logging.getLogger('stdm')

class ViewSTRWidget(QMainWindow, Ui_frmManageSTR):
    """
    Search and browse the social tenure relationship
    of all participating entities.
    """
    def __init__(self, plugin):
        QMainWindow.__init__(self, plugin.iface.mainWindow())
        self.setupUi(self)

        self._plugin = plugin
        QTimer.singleShot(
            300,
            lambda :self.tbPropertyPreview.set_iface(self._plugin.iface)
        )
        #self.tbPropertyPreview.set_iface(self._plugin.iface)
        self.curr_profile = current_profile()

        self.spatial_unit = self.curr_profile.social_tenure.spatial_unit
        #Center me
        self.move(QDesktopWidget().availableGeometry().center() -
                  self.frameGeometry().center())

        self.toolBox.setStyleSheet(
            '''
            QToolBox::tab {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #EDEDED, stop: 0.4 #EDEDED,
                    stop: 0.5 #EDEDED, stop: 1.0 #D3D3D3
                );
                border-radius: 2px;
                border-style: outset;
                border-width: 2px;
                height: 100px;
                border-color: #C3C3C3;
            }

            QToolBox::tab:selected {
                font: italic;
            }
            '''
        )
        self.tvSTRResults.setStyleSheet(
            '''
            QTreeView:!active {
                selection-background-color: #72a6d9;
            }
            '''
        )

        # Configure notification bar
        self._notif_search_config = NotificationBar(
            self.vl_notification
        )

        # set whether currently logged in user has
        # permissions to edit existing STR records
        self._can_edit = self._plugin.STRCntGroup.canUpdate()
        self._can_delete = self._plugin.STRCntGroup.canDelete()
        self._can_create = self._plugin.STRCntGroup.canCreate()
        # Variable used to store a reference to the
        # currently selected social tenure relationship
        # when displaying documents in the supporting documents tab window.
        # This ensures that there are no duplicates
        # when the same item is selected over and over again.

        self._strID = None
        self.removed_docs = None
        #Used to store the root hash of the currently selected node.
        self._curr_rootnode_hash = ""


        self.str_model, self.str_doc_model = entity_model(
            self.curr_profile.social_tenure, False, True
        )

        self._source_doc_manager = SourceDocumentManager(
            self.curr_profile.social_tenure.supporting_doc,
            self.str_doc_model,
            self
        )

        self._source_doc_manager.documentRemoved.connect(
            self.onSourceDocumentRemoved
        )

        self._source_doc_manager.setEditPermissions(False)


        self.initGui()
    
    def add_tool_buttons(self):
        """
        Add toolbar buttons of add, edit and delete buttons.
        :return: None
        :rtype: NoneType
        """
        tool_buttons = QToolBar()
        tool_buttons.setObjectName('form_toolbar')
        tool_buttons.setIconSize(QSize(16, 16))

        self.addSTR = QAction(QIcon(
            ':/plugins/stdm/images/icons/add.png'),
            QApplication.translate('ViewSTRWidget', 'Add'),
            self
        )

        self.editSTR = QAction(
            QIcon(':/plugins/stdm/images/icons/edit.png'),
            QApplication.translate('ViewSTRWidget', 'Edit'),
            self
        )

        self.deleteSTR = QAction(
            QIcon(':/plugins/stdm/images/icons/remove.png'),
            QApplication.translate('ViewSTRWidget', 'Remove'),
            self
        )

        tool_buttons.addAction(self.addSTR)
        tool_buttons.addAction(self.editSTR)
        tool_buttons.addAction(self.deleteSTR)

        self.toolbarVBox.addWidget(tool_buttons)

    def initGui(self):
        """
        Initialize widget
        """
        self.tb_actions.setVisible(False)
        QTimer.singleShot(30, self._load_entity_configurations)
        #self._load_entity_configurations()
        self.add_tool_buttons()

        #Connect signals
        self.tbSTREntity.currentChanged.connect(self.entityTabIndexChanged)
        self.btnSearch.clicked.connect(self.searchEntityRelations)
        self.btnClearSearch.clicked.connect(self.clearSearch)
        self.tvSTRResults.expanded.connect(self.onTreeViewItemExpanded)

        #Set the results treeview to accept requests for context menus
        self.tvSTRResults.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tvSTRResults.customContextMenuRequested.connect(
            self.onResultsContextMenuRequested
        )

        if not self._can_create:
            self.addSTR.hide()

        if not self._can_edit:
            self.editSTR.hide()
        else:
            self.editSTR.setDisabled(True)
        if not self._can_delete:
            self.deleteSTR.hide()
        else:
            self.deleteSTR.setDisabled(True)

        self.addSTR.triggered.connect(self.load_new_str_editor)

        self.deleteSTR.triggered.connect(self.delete_str)

        self.editSTR.triggered.connect(self.load_edit_str_editor)

        #Load async for the current widget
        self.entityTabIndexChanged(0)


    def add_spatial_unit_layer(self):
        """
        Adds spatial unit layers on the map canvas when
        View Social Tenure is launched.
        :return: None
        :rtype: NoneType
        """
        sp_unit_manager = SpatialUnitManagerDockWidget(
            self._plugin.iface, self._plugin
        )
        spatial_unit_lyr = sp_unit_manager.entity_layer_names(
            self.spatial_unit
        )

        for lyr in spatial_unit_lyr:
            sp_unit_manager.add_layer_by_name(lyr)

    def _check_permissions(self):
        """
        Enable/disable actions based on the
        permissions defined in the content
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
            tb_str_entities = [
                self.curr_profile.social_tenure.party,
                self.curr_profile.social_tenure.spatial_unit
            ]

            for t in tb_str_entities:

                entity_cfg = self._entity_config_from_profile(
                    str(t.name), t.short_name
                )

                if not entity_cfg is None:
                    entity_widget = self.add_entity_config(entity_cfg)

                    entity_widget.setNodeFormatter(
                        EntityNodeFormatter(
                            entity_cfg, self.tvSTRResults, self
                        )
                    )

        except Exception as pe:
            self._notif_search_config.clear()
            self._notif_search_config.insertErrorNotification(unicode(pe))

    def _entity_config_from_profile(self, table_name, short_name):
        """
        Creates an EntityConfig object from the table name.
        :param table_name: Name of the database table.
        :type table_name: str
        :return: Entity configuration object.
        :rtype: EntityConfig
        """
        table_display_name = format_name(short_name)

        entity = self.curr_profile.entity_by_name(table_name)
        model = entity_model(entity)

        if model is not None:
            #Entity configuration
            entity_cfg = EntityConfiguration()
            entity_cfg.Title = table_display_name
            entity_cfg.STRModel = model
            entity_cfg.data_source_name = table_name

            # Load filter and display columns
            # using only those which are of
            # numeric/varchar type
            searchable_columns = entity_searchable_columns(entity)
            display_columns = entity_display_columns(entity)
            for c in searchable_columns:
                if c != 'id':
                    entity_cfg.filterColumns[c] = format_name(c)
            for c in display_columns:
                if c != 'id':
                    entity_cfg.displayColumns[c] = format_name(c)
            return entity_cfg
        else:
            return None

    def add_entity_config(self, config):
        """
        Set an entity configuration option and
        add it to the 'Search Entity' tab.
        """
        entityWidg = STRViewEntityWidget(config)
        entityWidg.asyncStarted.connect(self._progressStart)
        entityWidg.asyncFinished.connect(self._progressFinish)

        tabIndex = self.tbSTREntity.addTab(entityWidg, config.Title)

        return entityWidg

    def entityTabIndexChanged(self, index):
        """
        Raised when the tab index of the entity search tab widget changes.
        """
        #Get the current widget in the tab container
        entityWidget = self.tbSTREntity.currentWidget()

        if isinstance(entityWidget,EntitySearchItem):
            entityWidget.loadAsync()

    def searchEntityRelations(self):
        """
        Slot that searches for matching items for
        the specified entity and corresponding STR entities.
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
                noResultsMsg = QApplication.translate(
                    'ViewSTR',
                    'No results found for "{}"'.format(searchWord)
                )
                self._notif_search_config.clear()
                self._notif_search_config.insertErrorNotification(
                    noResultsMsg
                )

                return

            if formattedNode is not None:
                self._load_root_node(formattedNode)

    def clearSearch(self):
        """
        Clear search input parameters (for current widget) and results.
        """
        entityWidget = self.tbSTREntity.currentWidget()
        if isinstance(entityWidget, EntitySearchItem):
            entityWidget.reset()

        self._reset_controls()

    def _reset_controls(self):
        #Clear tree view
        self._resetTreeView()

        #Clear document listings
        self._deleteSourceDocTabs()

        #Remove spatial unit memory layer
        self.tbPropertyPreview.remove_layer()

    def on_select_results(self):
        """
        Slot which is raised when the selection
        is changed in the tree view
        selection model.
        """
        index = self.tvSTRResults.currentIndex()

        #Check type of node and perform corresponding action
        #for mi in selIndexes:
        if index.isValid():
            node = index.internalPointer()
            self.editSTR.setDisabled(True)
            self.deleteSTR.setDisabled(True)
            if index.column() == 0:
                # Assert if node represents another
                # entity has been clicked
                self._on_node_reference_changed(node.rootHash())

                if isinstance(node, SupportsDocumentsNode):

                    src_docs = node.documents()

                    if isinstance(src_docs, dict):
                        self._load_source_documents(src_docs)
                        # if there is supporting document,
                        # expand supporting document tab
                        if len (src_docs) > 0:
                            self.toolBox.setCurrentIndex(1)
                        if self._can_edit:
                            self.deleteSTR.setDisabled(False)
                        if self._can_delete:
                            self.editSTR.setDisabled(False)

                if isinstance(node, SpatialUnitNode):
                    # Expand the Spatial Unit preview
                    self.toolBox.setCurrentIndex(0)
                    self.draw_spatial_unit(node.model())
                    self.editSTR.setDisabled(True)
                    self.deleteSTR.setDisabled(True)

    def load_edit_str_editor(self):

        index = self.tvSTRResults.currentIndex()
        node = None
        if index.isValid():
            node = index.internalPointer()
        if index.column() == 0:
            if isinstance(node, SupportsDocumentsNode):

                edit_str = EditSTRTreeView(self._plugin, node)
                status = edit_str.exec_()

                if status == 1:
                    if node._parent.typeInfo() == 'ENTITY_NODE':
                        if node._model.party_id == \
                                edit_str.updated_str_obj.party_id:
                            self.btnSearch.click()
                            index = node.treeView().model().index(0, 0)
                            node._on_expand(index)

                    if node._parent.typeInfo() == 'SPATIAL_UNIT_NODE':
                        if node._model.spatial_unit_id == \
                                edit_str.updated_str_obj.spatial_unit_id:
                            self.btnSearch.click()
                            index = node.treeView().model().index(0, 0)
                            node._on_expand(index)

    def load_new_str_editor(self):
        try:
            # Check type of node and perform corresponding action
            add_str = STRTreeView(self._plugin)
            add_str.exec_()

        except Exception as ex:
            QMessageBox.critical(
                self._plugin.iface.mainWindow(),
                QApplication.translate(
                    "STDMPlugin",
                    "Loading Error"
                ),
                unicode(ex)
            )

    def delete_str(self):
        index = self.tvSTRResults.currentIndex()
        node = None
        if index.isValid():
            node = index.internalPointer()
        if isinstance(node, SupportsDocumentsNode):
            node.onDelete(index)
            self.btnSearch.click()
            index = node.treeView().model().index(0, 0)
            node._on_expand(index)

    def onSourceDocumentRemoved(self, container_id, doc_uuid, removed_doc):
        """
        Slot raised when a source document is removed from the container.
        If there are no documents in the specified container then remove
        the tab.
        """
        curr_container = self.tbSupportingDocs.currentWidget()
        curr_doc_widget = curr_container.findChildren(DocumentWidget)

        for doc in curr_doc_widget:
            if doc.fileUUID == doc_uuid:
                doc.deleteLater()
        self.removed_docs = removed_doc

    def draw_spatial_unit(self, model):
        """
        Render the geometry of the given spatial unit in the spatial view.
        :param row_id: Sqlalchemy object representing a feature.
        """
        self.tbPropertyPreview.draw_spatial_unit(model)

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
        Slot raised when the user right-clicks
        on a node item to request the
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
        (Re)load map layers in the viewer and main canvas.
        :param event: Window event
        :type event: QShowEvent
        """
        self.setEnabled(True)
        QTimer.singleShot(200, self.init_mirror_map)
        #self.init_mirror_map()

        return QMainWindow.showEvent(self, event)

    def init_mirror_map(self):
        self._notify_no_base_layers()
        # Add spatial unit layer if it doesn't exist
        self.add_spatial_unit_layer()
        self.tbPropertyPreview.refresh_canvas_layers()
        self.tbPropertyPreview.load_web_map()

    def _notify_no_base_layers(self):
        """
        Checks if there are any base layers that will be used when
        visualizing the spatial units. If there are no base layers
        then insert warning message.
        """
        self._notif_search_config.clear()

        num_layers = len(self._plugin.iface.legendInterface().layers())
        if num_layers == 0:
            msg = QApplication.translate(
                "ViewSTR",
                "No basemap layers are loaded in the "
                "current project. Basemap layers "
                "enhance the visualization of spatial units."
            )
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
            self.disconnect(
                resultsSelModel,
                SIGNAL("selectionChanged(const QItemSelection&,const QItemSelection&)"),
                self.on_select_results
            )

    def _load_root_node(self, root):
        """
        Load the search results (formatted into
        an object of type 'stdm.navigaion.STR') into
        the tree view.
        """
        strTreeViewModel = STRTreeViewModel(
            root, view=self.tvSTRResults
        )
        self.tvSTRResults.setModel(strTreeViewModel)

        # Resize tree columns to fit contents
        self._resize_columns()

        #Capture selection changes signals when
        # results are returned in the tree view
        resultsSelModel = self.tvSTRResults.selectionModel()
        resultsSelModel.currentChanged.connect(
            self.on_select_results
        )

    def _resize_columns(self):
        """
        Adjusts the column sizes to fit its contents
        """
        qModel = self.tvSTRResults.model()
        columnCount = qModel.columnCount()

        for i in range(columnCount):
            self.tvSTRResults.resizeColumnToContents(i)

        #Once resized then slightly increase the width
        # of the first column so that text for 'No STR Defined' visible.
        currColWidth = self.tvSTRResults.columnWidth(0)
        newColWidth = currColWidth + 100
        self.tvSTRResults.setColumnWidth(0, newColWidth)

    def _load_source_documents(self, source_docs):
        """
        Load source documents into document listing widget.
        """
        # Configure progress dialog
        progress_msg = QApplication.translate(
            "ViewSTR", "Loading supporting documents..."
        )

        progress_dialog = QProgressDialog(self)
        if len(source_docs) > 0:
            progress_dialog.setWindowTitle(progress_msg)
            progress_dialog.setRange(0, len(source_docs))
            progress_dialog.setWindowModality(Qt.WindowModal)
            progress_dialog.setFixedWidth(380)
            progress_dialog.show()
            progress_dialog.setValue(0)
        self._notif_search_config.clear()

        self.tbSupportingDocs.clear()
        self._source_doc_manager.reset()

        if len(source_docs) < 1:
            empty_msg = QApplication.translate(
                'ViewSTR', 'No supporting document is uploaded '
                           'for this social tenure relationship.'
            )
            self._notif_search_config.clear()
            self._notif_search_config.insertWarningNotification(empty_msg)

        for i, (doc_type_id, doc_obj) in enumerate(source_docs.iteritems()):

            # add tabs, and container and widget for each tab
            tab_title = self._source_doc_manager.doc_type_mapping[doc_type_id]


            tab_widget = QWidget()
            tab_widget.setObjectName(tab_title)

            cont_layout = QVBoxLayout(tab_widget)
            cont_layout.setObjectName('widget_layout_' + tab_title)

            scrollArea = QScrollArea(tab_widget)
            scrollArea.setFrameShape(QFrame.NoFrame)

            scrollArea_contents = QWidget()
            scrollArea_contents.setObjectName('tab_scroll_area_' + tab_title)

            tab_layout = QVBoxLayout(scrollArea_contents)
            tab_layout.setObjectName('layout_' + tab_title)

            scrollArea.setWidgetResizable(True)

            scrollArea.setWidget(scrollArea_contents)
            cont_layout.addWidget(scrollArea)

            self._source_doc_manager.registerContainer(
                tab_layout, doc_type_id
            )

            for doc in doc_obj:

                try:
                    # add doc widgets
                    self._source_doc_manager.insertDocFromModel(
                        doc, doc_type_id
                    )
                except Exception as ex:
                    LOGGER.debug(str(ex))

            self.tbSupportingDocs.addTab(
                tab_widget, tab_title
            )
            progress_dialog.setValue(i + 1)

    def _on_node_reference_changed(self, rootHash):
        """
        Method for resetting document listing and map preview
        if another root node and its children
        are selected then the documents are reset as
        well as the map preview control.
        """
        if rootHash != self._curr_rootnode_hash:
            self._deleteSourceDocTabs()
            self._curr_rootnode_hash = rootHash

    def _progressStart(self):
        """
        Load progress dialog window.
        For items whose durations is unknown,
        'isindefinite' = True by default.
        If 'isindefinite' is False, then
        'rangeitems' has to be specified.
        """
        pass

    def _progressFinish(self):
        """
        Hide progress dialog window.
        """
        pass

    def _edit_permissions(self):
        """
        Returns True/False whether the current logged in user
        has permissions to create new social tenure relationships.
        If true, then the system assumes that
        they can also edit STR records.
        """
        canEdit = False
        userName = stdm.data.app_dbconn.User.UserName
        authorizer = Authorizer(userName)
        newSTRCode = "9576A88D-C434-40A6-A318-F830216CA15A"

        #Get the name of the content from the code
        cnt = Content()
        createSTRCnt = cnt.queryObject().filter(
            Content.code == newSTRCode
        ).first()
        if createSTRCnt:
            name = createSTRCnt.name
            canEdit = authorizer.CheckAccess(name)

        return canEdit

class EntitySearchItem(QObject):
    """
    Abstract class for implementation by widgets that
    enable users to search for entity records.
    """

    def __init__(self, formatter=None):
        # Specify the formatter that should be
        # applied on the result item. It should
        # inherit from 'stdm.navigation.STRNodeFormatter'
        self.formatter = formatter

    def setNodeFormatter(self, formatter):
        """
        Set the formatter that should be
        applied on the entity search results.
        """
        self.formatter = formatter

    def validate(self):
        """
        Method for validating the input arguments
        before a search is conducted.
        Should return bool indicating whether validation
        was successful and message (applicable if validation fails).
        """
        raise NotImplementedError()

    def executeSearch(self):
        """
        Implemented when the a search operation
        is executed. Should return tuple of formatted
        results for render in the tree view,raw
        object results and search word.
        """
        raise NotImplementedError(
            str(
                QApplication.translate(
                    "ViewSTR",
                    "Subclass must implement abstract method."
                )
            )
        )

    def loadAsync(self):
        """
        Any initialization that needs to be carried
        out when the parent container is activated.
        """
        pass

    def errorHandler(self,error):
        """
        Generic handler that logs error
        messages to the QGIS message log
        """
        #QgsMessageLog.logMessage(error,2)
        LOGGER.debug(error)

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
        self.curr_profile = current_profile()
        #Model for storing display and actual mapping values
        self._completer_model = None
        self._proxy_completer_model = None

        #Hook up signals
        self.cboFilterCol.currentIndexChanged.connect(
            self._on_column_index_changed
        )

    def setConfigOptions(self):
        """
        Apply configuration options.
        """
        #Set filter columns and remove id column
        for col_name, display_name in self.config.filterColumns.iteritems():
            if col_name != "id":
                self.cboFilterCol.addItem(
                    display_name, col_name
                )

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
            lambda: modelWorker.fetch(
                self.config.STRModel, self.currentFieldName()
            )
        )
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
            message = QApplication.translate(
                "ViewSTR", "Search word cannot be empty."
            )
            is_valid = False

        return is_valid, message

    def executeSearch(self):
        """
        Base class override.
        Search for matching items for the specified entity and column.
        """
        model_root_node = None

        prog_dialog = QProgressDialog(self)
        prog_dialog.setFixedWidth(380)
        prog_dialog.setWindowTitle(
            QApplication.translate(
                "STRViewEntityWidget",
                "Searching for STR..."
            )
        )
        prog_dialog.show()
        prog_dialog.setRange(
            0, 10
        )
        search_term = self._searchTerm()

        prog_dialog.setValue(2)
        #Try to get the corresponding search term value from the completer model
        if not self._completer_model is None:
            reg_exp = QRegExp("^%s$"%(search_term), Qt.CaseInsensitive,
                              QRegExp.RegExp2)
            self._proxy_completer_model.setFilterRegExp(reg_exp)

            if self._proxy_completer_model.rowCount() > 0:
                #Get corresponding actual value from the first matching item
                value_model_idx  = self._proxy_completer_model.index(0, 1)
                source_model_idx = self._proxy_completer_model.mapToSource(
                    value_model_idx
                )
                prog_dialog.setValue(4)
                search_term = self._completer_model.data(
                    source_model_idx, Qt.DisplayRole
                )

        modelInstance = self.config.STRModel()

        modelQueryObj = modelInstance.queryObject()
        queryObjProperty = getattr(
            self.config.STRModel, self.currentFieldName()
        )


        prog_dialog.setValue(6)
        # Get property type so that the filter can
        # be applied according to the appropriate type
        propType = queryObjProperty.property.columns[0].type
        results = []
        try:

            if not isinstance(propType, String):
                entity_name = modelQueryObj._primary_entity._label_name
                entity = self.curr_profile.entity_by_name(entity_name)
                col_name = self.currentFieldName()
                col = entity.columns[
                    self.currentFieldName()
                ]

                if col.TYPE_INFO == 'LOOKUP':
                    lookup_entity = lookup_parent_entity(
                        self.curr_profile, col_name
                    )
                    lkp_model = entity_model(lookup_entity)
                    lkp_obj = lkp_model()
                    value_obj = getattr(
                        lkp_model, 'value'
                    )

                    result  = lkp_obj.queryObject().filter(
                        func.lower(value_obj) == func.lower(search_term)
                    ).first()
                    if result is None:
                        result = lkp_obj.queryObject().filter(
                            func.lower(value_obj).like(search_term+'%')
                        ).first()
                    if not result is None:
                        results = modelQueryObj.filter(
                            queryObjProperty == result.id
                        ).all()
                    else:
                        results = []

            else:
                results = modelQueryObj.filter(
                    func.lower(queryObjProperty) == func.lower(search_term)
                ).all()

            prog_dialog.setValue(7)
        except exc.StatementError:
            return model_root_node, [], search_term

        if self.formatter is not None:
            self.formatter.setData(results)
            model_root_node = self.formatter.root()
            prog_dialog.setValue(10)
            prog_dialog.hide()
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
        Returns the name of the database field
        from the current item in the combo box.
        """
        curr_index = self.cboFilterCol.currentIndex()
        field_name = self.cboFilterCol.itemData(curr_index)

        if field_name is None:
            return
        else:
            return field_name

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
        field_formatter = self.config.LookupFormatters.get(
            self.currentFieldName(), None
        )

        # Store display and actual values in a
        # model for easier mapping and
        # retrieval when carrying out searches

        model_attr_mapping = []

        # Check if there are formaters specified
        # for the current field name
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
    Specifies the configuration to apply when creating
    a new tab widget for performing entity searches.
    """
    browseDescription = "Click on the browse button below to load entity " \
                        "records and their corresponding social tenure " \
                        "relationship definitions."
    defaultFieldName = ""
    # Format of each dictionary item:
    # property/db column name - display name
    filterColumns = OrderedDict()
    displayColumns = OrderedDict()
    groupBy = ""
    STRModel = None
    Title = ""
    data_source_name = ""
    # Functions for formatting values before
    # they are loaded into the completer
    LookupFormatters = {}

    def __init__(self):
        #Reset filter and display columns
        self.filterColumns = OrderedDict()
        self.displayColumns = OrderedDict()

class ModelWorker(QObject):
    """
    Worker for retrieving model attribute
    values stored in the database.
    """
    retrieved = pyqtSignal(object)
    error = pyqtSignal(unicode)

    pyqtSlot(object, unicode)
    def fetch(self, model, fieldname):
        """
        Fetch attribute values from the
        database for the specified model
        and corresponding column name.
        """
        try:
            if hasattr(model, fieldname):
                modelInstance = model()
                obj_property = getattr(model, fieldname)
                model_values = modelInstance.queryObject(
                    [obj_property]
                ).distinct()
                self.retrieved.emit(model_values)

        except Exception as ex:
            self.error.emit(unicode(ex))
