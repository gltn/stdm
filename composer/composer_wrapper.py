"""
/***************************************************************************
Name                 : STDM Composer Wrapper
Description          : Embeds custom STDM tools in a QgsComposer instance.
Date                 : 10/May/2014 
copyright            : (C) 2014 by John Gitau
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
import copy

from PyQt4.QtGui import (
    QToolBar,
    QAction,
    QMenu,
    QMenuBar,
    QDockWidget,
    QApplication,
    QMessageBox,
    QInputDialog
)
from PyQt4.QtCore import (
    Qt,
    QObject,
    pyqtSignal,
    QFile,
    QFileInfo,
    QIODevice
)
from PyQt4.QtXml import QDomDocument

from qgis.core import (
    QgsComposerArrow,
    QgsComposerAttributeTableV2,
    QgsComposerLabel,
    QgsComposerItem,
    QgsComposerMap,
    QgsComposerPicture,
    QgsMapLayerRegistry,
    QgsPaperItem
)

from stdm.data.pg_utils import (
    vector_layer
)
from stdm.settings.registryconfig import RegistryConfig
from stdm.ui.composer import (
    ComposerChartConfigEditor,
    ComposerDataSourceSelector,
    ComposerFieldSelector,
    ComposerPhotoDataSourceEditor,
    ComposerSymbolEditor,
    ComposerTableDataSourceEditor
)
from stdm.utils.util import documentTemplates
from stdm.utils.case_insensitive_dict import CaseInsensitiveDict

from .chart_configuration import ChartConfigurationCollection
from .composer_item_config import ComposerItemConfig
from .composer_data_source import ComposerDataSource
from .photo_configuration import PhotoConfigurationCollection
from .spatial_fields_config import SpatialFieldsConfiguration
from .table_configuration import TableConfigurationCollection
from .item_formatter import (
    ChartFormatter,
    DataLabelFormatter,
    LineFormatter,
    MapFormatter,
    PhotoFormatter,
    TableFormatter
)

def load_table_layers(config_collection):
    """
    In order to be able to use attribute tables in the composition, the
    corresponding vector layers need to be added to the layer
    registry. This method creates vector layers from the linked tables
    in the configuration items. This is required prior to creating the
    composition from file.
    :param config_collection: Table configuration collection built from
    the template file.
    :type config_collection: TableConfigurationCollection
    :returns: Valid layers that have been successfully added to the
    registry.
    :rtype: list
    """
    table_configs = config_collection.items().values()

    v_layers = []

    for conf in table_configs:
        layer_name = conf.linked_table()
        v_layer = vector_layer(layer_name)

        if v_layer is None:
            return

        if not v_layer.isValid():
            return

        v_layers.append(v_layer)

    QgsMapLayerRegistry.instance().addMapLayers(v_layers, False)

    return v_layers

class ComposerWrapper(QObject):
    """
    Embeds custom STDM tools in a QgsComposer instance for managing map-based
    STDM document templates.
    """
    dataSourceSelected = pyqtSignal(str)

    def __init__(self, composerView, iface):
        QObject.__init__(self, composerView)

        self._compView = composerView
        self._stdmTB = self.mainWindow().addToolBar("STDM Document Designer")
        self._selectMoveAction = None
        self._iface = iface

        #Container for custom editor widgets
        self._widgetMappings = {}

        #Hide default dock widgets
        if self.itemDock() is not None:
            self.itemDock().hide()

        if self.atlasDock() is not None:
            self.atlasDock().hide()

        if self.generalDock() is not None:
            self.generalDock().hide()

        # Remove default toolbars
        self._remove_composer_toolbar('mAtlasToolbar')

        self._remove_composer_toolbar('mComposerToolbar')

        #Create dock widget for configuring STDM data source
        self._stdmDataSourceDock = QDockWidget(
            QApplication.translate("ComposerWrapper","STDM Data Source"),
            self.mainWindow())
        self._stdmDataSourceDock.setObjectName("STDMDataSourceDock")
        self._stdmDataSourceDock.setMinimumWidth(300)
        self._stdmDataSourceDock.setFeatures(QDockWidget.DockWidgetMovable|QDockWidget.DockWidgetClosable)
        self.mainWindow().addDockWidget(Qt.RightDockWidgetArea,
                                        self._stdmDataSourceDock)

        self._dataSourceWidget = ComposerDataSourceSelector()
        self._stdmDataSourceDock.setWidget(self._dataSourceWidget)
        self._stdmDataSourceDock.show()

        #Re-insert dock widgets
        if self.generalDock() is not None:
            self.generalDock().show()

        if self.itemDock() is not None:
            self.itemDock().show()

        #Create dock widget for configuring STDM item properties
        self._stdmItemPropDock = QDockWidget(
            QApplication.translate("ComposerWrapper","STDM item properties"),
            self.mainWindow())

        self._stdmItemPropDock.setObjectName("STDMItemDock")
        self._stdmItemPropDock.setMinimumWidth(300)
        self._stdmItemPropDock.setFeatures(QDockWidget.DockWidgetMovable|QDockWidget.DockWidgetClosable)
        self.mainWindow().addDockWidget(Qt.RightDockWidgetArea,self._stdmItemPropDock)
        self._stdmItemPropDock.show()

        #Re-arrange dock widgets and push up STDM data source dock widget
        if self.generalDock() is not None:
            self.mainWindow().splitDockWidget(self._stdmDataSourceDock,
                                              self.generalDock(),Qt.Vertical)

        if self.itemDock() is not None:
            self.mainWindow().splitDockWidget(self._stdmDataSourceDock,
                                             self.itemDock(),Qt.Vertical)
            if self.generalDock() is not None:
                self.mainWindow().tabifyDockWidget(self.generalDock(),
                                              self.itemDock())

        if self.itemDock() is not None:
            self.mainWindow().splitDockWidget(self.itemDock(),
                                              self._stdmItemPropDock,
                                              Qt.Vertical)

        #Set focus on composition properties window
        if self.generalDock() is not None:
            self.generalDock().activateWindow()
            self.generalDock().raise_()

        #Connect signals
        self.composition().itemRemoved.connect(self._onItemRemoved)
        self._dataSourceWidget.cboDataSource.currentIndexChanged.connect(
            self.propagateDataSourceSelection
        )
        self.composerView().selectedItemChanged.connect(self._onItemSelected)

        #Current template document file
        self._currDocFile = None

        #Copy of template document file
        self._copy_template_file = None

        self._selected_item_uuid = unicode()

        self._current_ref_table_index = -1

    @property
    def copy_template_file(self):
        return self._copy_template_file

    @copy_template_file.setter
    def copy_template_file(self, value):
        self._copy_template_file = value

    @property
    def selected_item_uuid(self):
        return self._selected_item_uuid

    @selected_item_uuid.setter
    def selected_item_uuid(self, uuid):
        self._selected_item_uuid = uuid

    @property
    def current_ref_table_index(self):
        return self._current_ref_table_index

    @current_ref_table_index.setter
    def current_ref_table_index(self, value):
        self._current_ref_table_index = value

    def _remove_composer_toolbar(self, object_name):
        """
        Removes toolbars from composer window.
        :param object_name: The object name of the toolbar
        :type object_name: String
        :return: None
        :rtype: NoneType
        """
        composers = self._iface.activeComposers()
        for i in range(len(composers)):
            comp = composers[i].composerWindow()
            widgets = comp.findChildren(QToolBar, object_name)
            for widget in widgets:
                comp.removeToolBar(widget)

    def _removeActions(self):
        """
        Remove inapplicable actions and their corresponding toolbars and menus.
        """
        removeActions = ["mActionSaveProject","mActionNewComposer","mActionDuplicateComposer"]

        composerToolbar = self.composerMainToolBar()
        if composerToolbar != None:
            saveProjectAction = None

            for itemAction in composerToolbar.actions():
                if itemAction.objectName() == "mActionSaveProject":
                    saveProjectAction = itemAction
                    break

            if saveProjectAction != None:
                composerMenu = saveProjectAction.menu()

    def configure(self):
        #Create instances of custom STDM composer item configurations
        for ciConfig in ComposerItemConfig.itemConfigurations:
            ciConfig(self)

    def addWidgetMapping(self,uniqueIdentifier,widget):
        """
        Add custom STDM editor widget based on the unique identifier of the composer item
        """
        self._widgetMappings[uniqueIdentifier] = widget

    def widgetMappings(self):
        """
        Returns a dictionary containing uuid values of composer items linked to STDM widgets.
        """
        return self._widgetMappings

    def clearWidgetMappings(self):
        """
        Resets the widget mappings collection.
        """
        self._widgetMappings = {}

    def mainWindow(self):
        """
        Returns the QMainWindow used by the composer view.
        """
        return self._compView.composerWindow()

    def stdmToolBar(self):
        """
        Returns the instance of the STDM toolbar added to the QgsComposer.
        """
        return self._stdmTB

    def composerView(self):
        """
        Returns the composer view.
        """
        return self._compView

    def composition(self):
        """
        Returns the QgsComposition instance used in the composer view.
        """
        return self._compView.composition()

    def composerItemToolBar(self):
        """
        Returns the toolbar containing actions for adding composer items.
        """
        return self.mainWindow().findChild(QToolBar,"mItemToolbar")

    def composerMainToolBar(self):
        """
        Returns the toolbar containing actions for managing templates.
        """
        return self.mainWindow().findChild(QToolBar,"mComposerToolbar")

    def selectMoveAction(self):
        """
        Returns the QAction for selecting or moving composer items.
        """
        if self.composerItemToolBar() != None:
            if self._selectMoveAction == None:
                for itemAction in self.composerItemToolBar().actions():
                    if itemAction.objectName() == "mActionSelectMoveItem":
                        self._selectMoveAction = itemAction
                        break

        return self._selectMoveAction

    def checkedItemAction(self):
        """
        Returns the currently selected composer item action.
        """
        if self.selectMoveAction() != None:
            return self.selectMoveAction().actionGroup().checkedAction()

        return None

    def itemDock(self):
        """
        Get the 'Item Properties' dock widget.
        """
        return self.mainWindow().findChild(QDockWidget,"ItemDock")

    def atlasDock(self):
        """
        Get the 'Atlas generation' dock widget.
        """
        return self.mainWindow().findChild(QDockWidget,"AtlasDock")

    def generalDock(self):
        """
        Get the 'Composition' dock widget.
        """
        return self.mainWindow().findChild(QDockWidget,"CompositionDock")

    def stdmDataSourceDock(self):
        """
        Returns the STDM data source dock widget.
        """
        return self._stdmDataSourceDock

    def stdmItemDock(self):
        """
        Returns the STDM item dock widget.
        """
        return self._stdmItemPropDock

    def documentFile(self):
        """
        Returns the QFile instance associated with the current document. 'None' will be returned for
        new, unsaved documents.
        """
        return self._currDocFile

    def setDocumentFile(self, docFile):
        """
        Sets the document file.
        """
        if not isinstance(docFile, QFile):
            return

        self._currDocFile = docFile

    def selectedDataSource(self):
        """
        Returns the name of the data source specified by the user.
        """
        row = self._stdmDataSourceDock.widget().cboDataSource.currentIndex()
        table_name = self._stdmDataSourceDock.widget().cboDataSource.itemData(row)

        return table_name

    def selected_referenced_table(self):
        """
        :return: Returns the name of currently specified referenced table name.
        :rtype: str
        """
        return self._stdmDataSourceDock.widget().referenced_table_name()

    def selectedDataSourceCategory(self):
        """
        Returns the category (view or table) that the data source belongs to.
        """
        if not self.stdmDataSourceDock().widget() is None:
            return self.stdmDataSourceDock().widget().category()

        return ""

    def propagateDataSourceSelection(self, index):
        """
        Propagates the signal when a user select a data source. Listening objects can hook on to it.
        """
        data_source_name = self._stdmDataSourceDock.widget().cboDataSource.itemData(index)
        self.dataSourceSelected.emit(data_source_name)

    def composer_items(self):
        """
        :return: Returns a list of custom composer items.
        :rtype: list
        """
        return [self.composition().getComposerItemById(uuid) for uuid in self._widgetMappings.keys()
                if not self.composition().getComposerItemById(uuid) is None]

    def _clear_composition(self):
        """
        Removes composer items which, otherwise, are causing QGIS to crash
        when loading a subsequent document template.
        """
        items = self.composition().items()

        for c_item in items:
            if isinstance(c_item, QgsComposerItem) and not isinstance(c_item, QgsPaperItem):
                if c_item.uuid() in self._widgetMappings:
                    #Remove corresponding widget as well as reference in the collection
                    del self._widgetMappings[c_item.uuid()]

                self.composition().removeItem(c_item)
                self.composition().itemRemoved.emit(c_item)

                del c_item

        self.composition().undoStack().clear()
        self.composition().itemsModel().clear()

    def create_new_document_designer(self, file_path):
        """
        Creates a new document designer and loads the document template
        defined in file path.
        :param file_path: Path to document template
        :type file_path: str
        """
        if len(self.composerView().items()) == 3:
            self.composerView().composerWindow().close()
        
        document_designer = self._iface.createNewComposer("STDM Document Designer")

        #Embed STDM customizations
        cw = ComposerWrapper(document_designer, self._iface)
        cw.configure()

        #Load template
        cw.loadTemplate(file_path)

    def loadTemplate(self, filePath):
        """
        Loads a document template into the view and updates the necessary STDM-related composer items.
        """
        if not QFile.exists(filePath):
                QMessageBox.critical(self.composerView(),
                                     QApplication.translate("OpenTemplateConfig",
                                                            "Open Template Error"),
                                    QApplication.translate("OpenTemplateConfig",
                                                           "The specified template does not exist."))
                return

        copy_file = filePath.replace('sdt', 'cpy')

        # remove existing copy file
        if QFile.exists(copy_file):
            copy_template = QFile(copy_file)
            copy_template.remove()

        orig_template_file = QFile(filePath)

        self.setDocumentFile(orig_template_file)

        # make a copy of the original
        orig_template_file.copy(copy_file)

        #templateFile = QFile(filePath)

        # work with copy
        templateFile = QFile(copy_file)

        self.copy_template_file = templateFile

        if not templateFile.open(QIODevice.ReadOnly):
            QMessageBox.critical(self.composerView(),
                                 QApplication.translate("ComposerWrapper",
                                                        "Open Operation Error"),
                                            "{0}\n{1}".format(QApplication.translate(
                                                "ComposerWrapper",
                                                "Cannot read template file."),
                                                      templateFile.errorString()
                                                      ))
            return

        templateDoc = QDomDocument()

        if templateDoc.setContent(templateFile):
            table_config_collection = TableConfigurationCollection.create(templateDoc)
            '''
            First load vector layers for the table definitions in the config
            collection before loading the composition from file.
            '''
            load_table_layers(table_config_collection)

            self.clearWidgetMappings()

            #Load items into the composition and configure STDM data controls
            self.composition().loadFromTemplate(templateDoc)

            #Load data controls
            composerDS = ComposerDataSource.create(templateDoc)

            #Set title by appending template name
            title = QApplication.translate("STDMPlugin", "STDM Document Designer")

            composer_el = templateDoc.documentElement()
            if not composer_el is None:
                template_name = ""
                if composer_el.hasAttribute("title"):
                    template_name = composer_el.attribute("title", "")
                elif composer_el.hasAttribute("_title"):
                    template_name = composer_el.attribute("_title", "")

                if template_name:
                    win_title = u"{0} - {1}".format(title, template_name)
                    self.mainWindow().setWindowTitle(template_name)

            self._configure_data_controls(composerDS)

            #Load symbol editors
            spatialFieldsConfig = SpatialFieldsConfiguration.create(templateDoc)
            self._configureSpatialSymbolEditor(spatialFieldsConfig)

            #Load photo editors
            photo_config_collection = PhotoConfigurationCollection.create(templateDoc)
            self._configure_photo_editors(photo_config_collection)

            # Load table editors
            self._configure_table_editors(table_config_collection)

            items = self.composerView().items()
            items = []
            
            #Load chart property editors
            chart_config_collection = ChartConfigurationCollection.create(templateDoc)
            self._configure_chart_editors(chart_config_collection)

            self._sync_ids_with_uuids()

    def saveTemplate(self):
        """
        Creates and saves a new document template.
        """
        #Validate if the user has specified the data source
        #if not self.selectedDataSource():
            #QMessageBox.critical(self.composerView(),
                                 #QApplication.translate("ComposerWrapper","Error"),
                                #QApplication.translate("ComposerWrapper","Please specify the "
                                            #"data source name for the document composition."))
            #return

        #Assert if the referenced table name has been set
        #if not self.selected_referenced_table():
            #QMessageBox.critical(self.composerView(),
                                 #QApplication.translate("ComposerWrapper","Error"),
                                #QApplication.translate("ComposerWrapper","Please specify the "
                                            #"referenced table name for the selected data source."))
            #return

        #If it is a new unsaved document template then prompt for the document name.
        docFile = self.documentFile()

        if docFile is None:
            docName,ok = QInputDialog.getText(self.composerView(),
                            QApplication.translate("ComposerWrapper","Template Name"),
                            QApplication.translate("ComposerWrapper","Please enter the template name below"),
                            )

            if not ok:
                return

            if ok and not docName:
                QMessageBox.critical(self.composerView(),
                        QApplication.translate("ComposerWrapper", "Error"),
                        QApplication.translate("ComposerWrapper",
                            "Please enter a template name!") )
                self.saveTemplate()

            if ok and docName:
                templateDir = self._composerTemplatesPath()

                if templateDir is None:
                    QMessageBox.critical(self.composerView(),
                        QApplication.translate("ComposerWrapper","Error"),
                        QApplication.translate("ComposerWrapper",
                        "Directory for document templates cannot not be found."))

                    return

                absPath = templateDir + "/" + docName + ".sdt"

                #Check if there is an existing document with the same name
                caseInsenDic = CaseInsensitiveDict(documentTemplates())
                if docName in caseInsenDic:
                    result = QMessageBox.warning(self.composerView(),
                            QApplication.translate("ComposerWrapper",
                                                   "Existing Template"),
                                            u"'{0}' {1}.\nDo you want to replace the "
                                            "existing template?".format(docName,
                                            QApplication.translate("ComposerWrapper",
                                                                   "already exists")),
                                            QMessageBox.Yes|QMessageBox.No)

                    if result == QMessageBox.Yes:
                        #Delete the existing template
                        delFile = QFile(absPath)
                        remStatus = delFile.remove()
                        if not remStatus:
                            QMessageBox.critical(self.composerView(),
                            QApplication.translate("ComposerWrapper",
                                                   "Delete Error"),
                                            "'{0}' {1}.".format(docName,
                            QApplication.translate("ComposerWrapper",
                            "template could not be removed by the system,"
                            " please remove it manually from the document templates directory.")))
                            return

                    else:
                        return

                docFile= QFile(absPath)

            else:
                return

        docFileInfo = QFileInfo(docFile)

        if not docFile.open(QIODevice.WriteOnly):
            QMessageBox.critical(self.composerView(),
                                 QApplication.translate("ComposerWrapper",
                                "Save Operation Error"),
                                "{0}\n{1}".format(QApplication.translate("ComposerWrapper",
                                "Could not save template file."),
                                                      docFile.errorString()
                                ))

            return

        templateDoc = QDomDocument()
        template_name = docFileInfo.completeBaseName()
        self._writeXML(templateDoc, template_name)

        if docFile.write(templateDoc.toByteArray()) == -1:
            QMessageBox.critical(self.composerView(),
            QApplication.translate("ComposerWrapper","Save Error"),
            QApplication.translate("ComposerWrapper","Could not save template file."))

            return

        else:
            self.mainWindow().setWindowTitle(template_name)

        self.setDocumentFile(docFile)
        docFile.close()

    def _writeXML(self, xml_doc, doc_name):
        """
        Write the template configuration into the XML document.
        """
        #Write default composer configuration
        composer_element = xml_doc.createElement("Composer")
        composer_element.setAttribute("title", doc_name)
        composer_element.setAttribute("visible", 1)

        xml_doc.appendChild(composer_element)

        self.composition().writeXML(composer_element, xml_doc)

        #Write STDM data field configurations
        dataSourceElement = ComposerDataSource.domElement(self, xml_doc)
        composer_element.appendChild(dataSourceElement)

        #Write spatial field configurations
        spatialColumnsElement = SpatialFieldsConfiguration.domElement(self, xml_doc)
        dataSourceElement.appendChild(spatialColumnsElement)

        #Write photo configuration
        tables_element = PhotoConfigurationCollection.dom_element(self, xml_doc)
        dataSourceElement.appendChild(tables_element)

        #Write table configuration
        tables_element = TableConfigurationCollection.dom_element(self, xml_doc)
        dataSourceElement.appendChild(tables_element)

        #Write chart configuration
        charts_element = ChartConfigurationCollection.dom_element(self, xml_doc)
        dataSourceElement.appendChild(charts_element)

    def _configure_data_controls(self, composer_data_source):
        """
        Configure the data source and data field controls based on the composer data
        source configuration.
        """
        if not self.stdmDataSourceDock().widget() is None:
            #Set data source
            dataSourceWidget = self.stdmDataSourceDock().widget()
            dataSourceWidget.setCategory(composer_data_source.category())
            dataSourceWidget.setSelectedSource(composer_data_source.name())
            dataSourceWidget.set_referenced_table(
                composer_data_source.referenced_table_name
            )

            #Set data field controls
            for composerId in composer_data_source.dataFieldMappings().reverse:
                #Use composer item id since the uuid is stripped off
                composerItem = self.composition().getComposerItemById(composerId)

                if not composerItem is None:
                    compFieldSelector = ComposerFieldSelector(self, composerItem, self.composerView())
                    compFieldSelector.selectFieldName(composer_data_source.dataFieldName(composerId))

                    #Add widget to the collection but now use the current uuid of the composition item
                    self.addWidgetMapping(composerItem.uuid(), compFieldSelector)

    def _configureSpatialSymbolEditor(self,spatial_field_config):
        """
        Configure symbol editor controls.
        """
        if not self.stdmDataSourceDock().widget() is None:
            for item_id, spFieldsMappings in spatial_field_config.spatialFieldsMapping().iteritems():
                mapItem = self.composition().getComposerItemById(item_id)

                if not mapItem is None:
                    composerSymbolEditor = ComposerSymbolEditor(self, self.composerView())
                    composerSymbolEditor.add_spatial_field_mappings(spFieldsMappings)

                    #Add widget to the collection but now use the current uuid of the composer map
                    self.addWidgetMapping(mapItem.uuid(), composerSymbolEditor)

    def _configure_photo_editors(self, photo_config_collection):
        """
        Creates widgets for editing photo data sources.
        :param photo_config_collection: PhotoConfigurationCollection instance.
        :type photo_config_collection: PhotoConfigurationCollection
        """
        if self.stdmDataSourceDock().widget() is None:
            return

        for item_id, photo_config in photo_config_collection.mapping().iteritems():
            pic_item = self.composition().getComposerItemById(item_id)

            if not pic_item is None:
                photo_editor = ComposerPhotoDataSourceEditor(self, self.composerView())
                photo_editor.set_configuration(photo_config)

                self.addWidgetMapping(pic_item.uuid(), photo_editor)


    def _configure_chart_editors(self, chart_config_collection):
        """
        Creates widgets for editing chart properties.
        :param chart_config_collection: ChartConfigurationCollection instance.
        :type chart_config_collection: ChartConfigurationCollection
        """
        if self.stdmDataSourceDock().widget() is None:
            return

        for item_id, chart_config in chart_config_collection.mapping().iteritems():
            chart_item = self.composition().getComposerItemById(item_id)

            if not chart_item is None:
                chart_editor = ComposerChartConfigEditor(self, self.composerView())
                chart_editor.set_configuration(chart_config)

                self.addWidgetMapping(chart_item.uuid(), chart_editor)

    def _configure_table_editors(self, table_config_collection):
        """
        Creates widgets for editing table data sources.
        :param table_config_collection: TableConfigurationCollection instance.
        :type table_config_collection: TableConfigurationCollection
        """
        if self.stdmDataSourceDock().widget() is None:
            return

        for item_id, table_config in table_config_collection.mapping().iteritems():
            table_item = self.composition().getComposerItemById(item_id)
            if table_item is not None:
                table_editor = ComposerTableDataSourceEditor(self, table_item, self.composerView())
                table_editor.set_configuration(table_config)

                table_editor.ref_table.cbo_ref_table.currentIndexChanged[str].connect(
                        table_editor.set_table_vector_layer)

                self.addWidgetMapping(table_item.uuid(), table_editor)

    def _sync_ids_with_uuids(self):
        """
        Matches IDs of custom STDM items with the corresponding UUIDs. This
        is applied when loading existing templates so that the saved
        document contains a matching pair of ID and UUID for each composer
        item.
        """
        items = self._widgetMappings.keys()
        for item_uuid in self._widgetMappings.keys():
            item = self.composition().getComposerItemByUuid(item_uuid)
            if not item is None:
                item.setId(item_uuid)

    def _composerTemplatesPath(self):
        """
        Reads the path of composer templates in the registry.
        """
        regConfig = RegistryConfig()
        keyName = "ComposerTemplates"

        valueCollection = regConfig.read([keyName])

        if len(valueCollection) == 0:
            return None

        else:
            return valueCollection[keyName]

    def _onItemRemoved(self,item):
        """
        Slot raised when a composer item is removed from the scene.
        """
        """
        Code will not work since a QObject instance is returned instead of a QgsComposerItem
        if item.uuid() in self._widgetMappings:
            del self._widgetMappings[item.uuid()]
        """
        pass

    def _onItemSelected(self, item):
        """
        Slot raised when a composer item is selected. Load the corresponding field selector
        if the selection is an STDM data field label.
        QComposerLabel is returned as a QObject in the slot argument hence, we have resorted to
        capturing the current selected items in the composition.
        """
        selectedItems = self.composition().selectedComposerItems()

        if len(selectedItems) == 0:
            self._stdmItemPropDock.setWidget(None)

        elif len(selectedItems) == 1:
            composer_item = selectedItems[0]

            if composer_item.uuid() in self._widgetMappings:
                stdmWidget = self._widgetMappings[composer_item.uuid()]

                self.selected_item_uuid = composer_item.uuid()

                if stdmWidget == self._stdmItemPropDock.widget():
                    return
                else:
                    self._stdmItemPropDock.setWidget(stdmWidget)

                #Playing it safe in applying the formatting for the editor controls where applicable
                itemFormatter = None

                if isinstance(composer_item, QgsComposerArrow):
                    itemFormatter = LineFormatter()

                elif isinstance(composer_item, QgsComposerLabel):
                    itemFormatter = DataLabelFormatter()

                elif isinstance(composer_item, QgsComposerMap):
                    itemFormatter = MapFormatter()

                elif isinstance(composer_item, QgsComposerPicture):
                    """
                    Use widget attribute to distinguish type i.e.
                    whether it is a photo, graph etc.
                    """
                    editor_widget = self._widgetMappings[composer_item.uuid()]

                    if isinstance(editor_widget, ComposerPhotoDataSourceEditor):
                        itemFormatter = PhotoFormatter()

                    elif isinstance(editor_widget, ComposerChartConfigEditor):
                        itemFormatter = ChartFormatter()

                elif isinstance(composer_item, QgsComposerAttributeTableV2):
                    itemFormatter = TableFormatter()

                if not itemFormatter is None:
                    itemFormatter.apply(composer_item, self, True)

            else:
                self._stdmItemPropDock.setWidget(None)

        elif len(selectedItems) > 1:
            self._stdmItemPropDock.setWidget(None)

