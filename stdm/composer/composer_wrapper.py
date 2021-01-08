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

from qgis.PyQt.QtCore import (
    Qt,
    QObject,
    QFile,
    QFileInfo,
    QIODevice
)
from qgis.PyQt.QtWidgets import (
    QToolBar,
    QDockWidget,
    QApplication,
    QMessageBox,
    QInputDialog,
    QAction
)
from qgis.PyQt.QtXml import QDomDocument
from qgis.core import (
    QgsLayoutItem,
    QgsProject,
    QgsLayout,
    QgsLayoutItemPage,
    QgsReadWriteContext
)
from qgis.gui import (
    QgsLayoutView
)

from stdm.composer.chart_configuration import ChartConfigurationCollection
from stdm.composer.composer_data_source import ComposerDataSource
from stdm.composer.composer_item_config import ComposerItemConfig
from stdm.composer.photo_configuration import PhotoConfigurationCollection
from stdm.composer.qr_code_configuration import QRCodeConfigurationCollection
from stdm.composer.spatial_fields_config import SpatialFieldsConfiguration
from stdm.composer.table_configuration import TableConfigurationCollection
from stdm.data.pg_utils import (
    vector_layer
)
from stdm.exceptions import DummyException
from stdm.settings.registryconfig import RegistryConfig
from stdm.ui.composer.composer_chart_config import (
    ComposerChartConfigEditor
)
from stdm.ui.composer.composer_data_source import (
    ComposerDataSourceSelector
)
from stdm.ui.composer.composer_field_selector import (
    ComposerFieldSelector)
from stdm.ui.composer.composer_symbol_editor import (
    ComposerSymbolEditor
)
from stdm.ui.composer.custom_item_gui import StdmCustomLayoutGuiItems
from stdm.ui.composer.photo_data_source import (
    ComposerPhotoDataSourceEditor,
)
from stdm.ui.composer.table_data_source import (
    ComposerTableDataSourceEditor
)
from stdm.utils.case_insensitive_dict import CaseInsensitiveDict
from stdm.utils.util import documentTemplates
from stdm.ui.composer.layout_gui_utils import LayoutGuiUtils
from stdm.composer.layout_utils import LayoutUtils


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
    table_configs = list(config_collection.items()).values()

    v_layers = []

    for conf in table_configs:
        layer_name = conf.linked_table()
        v_layer = vector_layer(layer_name)

        if v_layer is None:
            continue

        if not v_layer.isValid():
            continue

        v_layers.append(v_layer)

    QgsProject.instance().addMapLayers(v_layers, False)

    return v_layers


class ComposerWrapper(QObject):
    """
    Embeds custom STDM tools in a QgsComposer instance for managing map-based
    STDM document templates.
    """

    @staticmethod
    def disable_stdm_items(layout_interface):
        stdm_action_text = StdmCustomLayoutGuiItems.stdm_action_text()
        stdm_actions = [a for a in layout_interface.window().findChildren(QAction) if a.text() in stdm_action_text]
        for a in stdm_actions:
            a.setEnabled(False)

    def __init__(self, layout_interface, iface):
        QObject.__init__(self, layout_interface)

        self._layout_interface = layout_interface
        # self._compView = composerView
        self._stdmTB = layout_interface.window().addToolBar("STDM Document Designer")
        self._stdmTB.setObjectName('stdmDocumentDesigner')
        self._iface = iface
        self._config_items = []

        # Container for custom editor widgets
        self._widgetMappings = {}

        # Hide default dock widgets
        if self.itemDock() is not None:
            self.itemDock().hide()

        if self.atlasDock() is not None:
            self.atlasDock().hide()

        if self.generalDock() is not None:
            self.generalDock().hide()

        # Remove default toolbars
        self._remove_composer_toolbar('mAtlasToolbar')

        self._remove_composer_toolbar('mLayoutToolbar')

        # Create dock widget for configuring STDM data source
        stdmDataSourceDock = QDockWidget(
            QApplication.translate("ComposerWrapper", "STDM Data Source"),
            self.mainWindow())
        stdmDataSourceDock.setObjectName("STDMDataSourceDock")
        stdmDataSourceDock.setMinimumWidth(300)
        stdmDataSourceDock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable)
        self.mainWindow().addDockWidget(Qt.RightDockWidgetArea,
                                        stdmDataSourceDock)

        self._dataSourceWidget = ComposerDataSourceSelector(self.composition())
        stdmDataSourceDock.setWidget(self._dataSourceWidget)
        stdmDataSourceDock.show()

        # Re-insert dock widgets
        if self.generalDock() is not None:
            self.generalDock().show()

        if self.itemDock() is not None:
            self.itemDock().show()

        # Re-arrange dock widgets and push up STDM data source dock widget
        if self.generalDock() is not None:
            self.mainWindow().splitDockWidget(stdmDataSourceDock,
                                              self.generalDock(), Qt.Vertical)

        if self.itemDock() is not None:
            self.mainWindow().splitDockWidget(stdmDataSourceDock,
                                              self.itemDock(), Qt.Vertical)
            if self.generalDock() is not None:
                self.mainWindow().tabifyDockWidget(self.generalDock(),
                                                   self.itemDock())

        # Set focus on composition properties window
        if self.generalDock() is not None:
            self.generalDock().activateWindow()
            self.generalDock().raise_()

        self._selected_item_uuid = str()

        composer_data_source = ComposerDataSource.from_layout(self.composition())
        self._configure_data_controls(composer_data_source)

    def _remove_composer_toolbar(self, object_name):
        """
        Removes toolbars from composer window.
        :param object_name: The object name of the toolbar
        :type object_name: String
        :return: None
        :rtype: NoneType
        """
        widgets = self.mainWindow().findChildren(QToolBar, object_name)
        for widget in widgets:
            self.mainWindow().removeToolBar(widget)

    def _removeActions(self):
        """
        Remove inapplicable actions and their corresponding toolbars and menus.
        """
        removeActions = ["mActionSaveProject", "mActionNewComposer", "mActionDuplicateComposer"]

        composerToolbar = self.composerMainToolBar()
        if composerToolbar is not None:
            saveProjectAction = None

            for itemAction in composerToolbar.actions():
                if itemAction.objectName() == "mActionSaveProject":
                    saveProjectAction = itemAction
                    break

            if saveProjectAction is not None:
                composerMenu = saveProjectAction.menu()

    def configure(self):
        # Create instances of custom STDM composer item configurations
        for ciConfig in ComposerItemConfig.itemConfigurations:
            self._config_items.append(ciConfig(self))

    def addWidgetMapping(self, uniqueIdentifier, widget):
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
        return self._layout_interface.window()

    def stdmToolBar(self):
        """
        Returns the instance of the STDM toolbar added to the QgsComposer.
        """
        return self._stdmTB

    def composerView(self) -> QgsLayoutView:
        """
        Returns the composer view.
        """
        return self._layout_interface.view()

    def composition(self) -> QgsLayout:
        """
        Returns the QgsLayout instance used in the composer view.
        """
        return self._layout_interface.layout()

    def composerMainToolBar(self):
        """
        Returns the toolbar containing actions for managing templates.
        """
        return self.mainWindow().findChild(QToolBar, "mLayoutToolbar")

    def itemDock(self):
        """
        Get the 'Item Properties' dock widget.
        """
        return self.mainWindow().findChild(QDockWidget, "ItemDock")

    def atlasDock(self):
        """
        Get the 'Atlas generation' dock widget.
        """
        return self.mainWindow().findChild(QDockWidget, "AtlasDock")

    def generalDock(self):
        """
        Get the 'Composition' dock widget.
        """
        return self.mainWindow().findChild(QDockWidget, "LayoutDock")

    def create_new_document_designer(self, file_path):
        """
        Creates a new document designer and loads the document template
        defined in file path.
        :param file_path: Path to document template
        :type file_path: str
        """
        if not QFile.exists(file_path):
            QMessageBox.critical(self.mainWindow(),
                                 QApplication.translate("OpenTemplateConfig",
                                                        "Open Template Error"),
                                 QApplication.translate("OpenTemplateConfig",
                                                        "The specified template does not exist."))
            return

        if not [i for i in self.composition().items() if
                isinstance(i, QgsLayoutItem) and not isinstance(i, QgsLayoutItemPage)]:
            self.mainWindow().close()

        layout = LayoutGuiUtils.create_unique_named_layout()
        layout.initializeDefaults()

        # Load template
        try:
            LayoutUtils.load_template_into_layout(layout, file_path)
        except IOError as e:
            QMessageBox.critical(self.mainWindow(),
                                 QApplication.translate("ComposerWrapper",
                                                        "Open Operation Error"),
                                 "{0}\n{1}".format(QApplication.translate(
                                     "ComposerWrapper",
                                     "Cannot read template file."),
                                     str(e)
                                 ))

        self._iface.openLayoutDesigner(layout)

    def xxxloadTemplate(self, filePath):
        """
        Loads a document template into the view and updates the necessary STDM-related composer items.
        """

        try:
            LayoutUtils.load_template_into_layout(self.composition(), filePath)
        except IOError as e:
            QMessageBox.critical(self.mainWindow(),
                                 QApplication.translate("ComposerWrapper",
                                                        "Open Operation Error"),
                                 "{0}\n{1}".format(QApplication.translate(
                                     "ComposerWrapper",
                                     "Cannot read template file."),
                                     str(e)
                                 ))
            return

        if templateDoc.setContent(templateFile):
            table_config_collection = TableConfigurationCollection.create(templateDoc)
            '''
            First load vector layers for the table definitions in the config
            collection before loading the composition from file.
            '''
            load_table_layers(table_config_collection)

            self.clearWidgetMappings()

            # Load items into the composition and configure STDM data controls
            context = QgsReadWriteContext()
            self.composition().loadFromTemplate(templateDoc, context)

            # Load data controls
            composerDS = ComposerDataSource.create(templateDoc)

            # Set title by appending template name
            title = QApplication.translate("STDMPlugin", "STDM Document Designer")

            composer_el = templateDoc.documentElement()
            if composer_el is not None:
                template_name = ""
                if composer_el.hasAttribute("title"):
                    template_name = composer_el.attribute("title", "")
                elif composer_el.hasAttribute("_title"):
                    template_name = composer_el.attribute("_title", "")

                if template_name:
                    win_title = "{0} - {1}".format(title, template_name)
                    self.mainWindow().setWindowTitle(template_name)

            self._configure_data_controls(composerDS)

            # Load symbol editors
            spatialFieldsConfig = SpatialFieldsConfiguration.create(templateDoc)
            self._configureSpatialSymbolEditor(spatialFieldsConfig)

            # Load photo editors
            photo_config_collection = PhotoConfigurationCollection.create(templateDoc)
            self._configure_photo_editors(photo_config_collection)

            # Load table editors
            self._configure_table_editors(table_config_collection)

            # Load chart property editors
            chart_config_collection = ChartConfigurationCollection.create(templateDoc)
            self._configure_chart_editors(chart_config_collection)

            # Load QR code property editors
            qrc_config_collection = QRCodeConfigurationCollection.create(templateDoc)
            self._configure_qr_code_editors(qrc_config_collection)

    def saveTemplate(self):
        """
        Creates and saves a new document template.
        """
        # Validate if the user has specified the data source

        if not LayoutUtils.get_stdm_data_source_for_layout(self.composition()):
            QMessageBox.critical(self.mainWindow(),
                                 QApplication.translate("ComposerWrapper", "Error"),
                                 QApplication.translate("ComposerWrapper", "Please specify the "
                                                                           "data source name for the document composition."))
            return

        # Assert if the referenced table name has been set
        if not LayoutUtils.get_stdm_referenced_table_for_layout(self.composition()):
            QMessageBox.critical(self.mainWindow(),
                                 QApplication.translate("ComposerWrapper", "Error"),
                                 QApplication.translate("ComposerWrapper", "Please specify the "
                                                                           "referenced table name for the selected data source."))
            return

        # If it is a new unsaved document template then prompt for the document name.
        template_path = self.composition().customProperty('variable_template_path', None)

        if template_path is None:
            docName, ok = QInputDialog.getText(self.mainWindow(),
                                               QApplication.translate("ComposerWrapper", "Template Name"),
                                               QApplication.translate("ComposerWrapper",
                                                                      "Please enter the template name below"),
                                               )

            if not ok:
                return

            if ok and not docName:
                QMessageBox.critical(self.mainWindow(),
                                     QApplication.translate("ComposerWrapper", "Error"),
                                     QApplication.translate("ComposerWrapper",
                                                            "Please enter a template name!"))
                self.saveTemplate()

            if ok and docName:
                templateDir = self._composerTemplatesPath()

                if templateDir is None:
                    QMessageBox.critical(self.mainWindow(),
                                         QApplication.translate("ComposerWrapper", "Error"),
                                         QApplication.translate("ComposerWrapper",
                                                                "Directory for document templates cannot not be found."))

                    return

                absPath = templateDir + "/" + docName + ".sdt"

                # Check if there is an existing document with the same name
                caseInsenDic = CaseInsensitiveDict(documentTemplates())
                if docName in caseInsenDic:
                    result = QMessageBox.warning(self.mainWindow(),
                                                 QApplication.translate("ComposerWrapper",
                                                                        "Existing Template"),
                                                 "'{0}' {1}.\nDo you want to replace the "
                                                 "existing template?".format(docName,
                                                                             QApplication.translate("ComposerWrapper",
                                                                                                    "already exists")),
                                                 QMessageBox.Yes | QMessageBox.No)

                    if result != QMessageBox.Yes:
                        return
                    else:
                        # Delete the existing template
                        delFile = QFile(absPath)
                        remove_status = delFile.remove()
                        if not remove_status:
                            QMessageBox.critical(self.mainWindow(),
                                                 QApplication.translate("ComposerWrapper",
                                                                        "Delete Error"),
                                                 "'{0}' {1}.".format(docName,
                                                                     QApplication.translate("ComposerWrapper",
                                                                                            "template could not be removed by the system,"
                                                                                            " please remove it manually from the document templates directory.")))
                            return

                docFile = QFile(absPath)
                template_path = absPath
        else:
            docFile = QFile(template_path)

            # else:
            # return

        docFileInfo = QFileInfo(docFile)

        if not docFile.open(QIODevice.WriteOnly):
            QMessageBox.critical(self.mainWindow(),
                                 QApplication.translate("ComposerWrapper",
                                                        "Save Operation Error"),
                                 "{0}\n{1}".format(QApplication.translate("ComposerWrapper",
                                                                          "Could not save template file."),
                                                   docFile.errorString()
                                                   ))

            return

        templateDoc = QDomDocument()
        template_name = docFileInfo.completeBaseName()

        # Catch exception raised when writing items' elements
        try:
            self._writeXML(templateDoc, template_name)
        except DummyException as exc:
            msg = str(exc)
            QMessageBox.critical(
                self.mainWindow(),
                QApplication.translate("ComposerWrapper", "Save Error"),
                msg
            )
            docFile.close()
            docFile.remove()

            return

        if docFile.write(templateDoc.toByteArray()) == -1:
            QMessageBox.critical(self.mainWindow(),
                                 QApplication.translate("ComposerWrapper", "Save Error"),
                                 QApplication.translate("ComposerWrapper", "Could not save template file."))

            return

        else:
            self.mainWindow().setWindowTitle(template_name)

        self.composition().setCustomProperty('variable_template_path', template_path)

        docFile.close()

    def _writeXML(self, xml_doc, doc_name):
        """
        Write the template configuration into the XML document.
        """
        # Write default composer configuration
        context = QgsReadWriteContext()
        composer_element = self.composition().writeXml(xml_doc, context)
        composer_element.setAttribute("title", doc_name)

        xml_doc.appendChild(composer_element)

        # Write STDM data field configurations
        dataSourceElement = ComposerDataSource.domElement(self, xml_doc)
        composer_element.appendChild(dataSourceElement)

        return

        # TODO!!!!!!

        # Write spatial field configurations
        spatialColumnsElement = SpatialFieldsConfiguration.domElement(self, xml_doc)
        dataSourceElement.appendChild(spatialColumnsElement)

        # Write photo configuration
        photos_element = PhotoConfigurationCollection.dom_element(self, xml_doc)
        dataSourceElement.appendChild(photos_element)

        # Write table configuration
        tables_element = TableConfigurationCollection.dom_element(self, xml_doc)
        dataSourceElement.appendChild(tables_element)

        # Write chart configuration
        charts_element = ChartConfigurationCollection.dom_element(self, xml_doc)
        dataSourceElement.appendChild(charts_element)

        # Write QRCode configuration
        qr_codes_element = QRCodeConfigurationCollection.dom_element(self, xml_doc)
        dataSourceElement.appendChild(qr_codes_element)

    def _configure_data_controls(self, composer_data_source):
        """
        Configure the data source and data field controls based on the composer data
        source configuration.
        """
        if self._dataSourceWidget is not None:
            self._dataSourceWidget.set_data_source(composer_data_source)

            # Set data field controls
            for composerId in composer_data_source.dataFieldMappings().reverse:
                # Use composer item id since the uuid is stripped off
                composerItem = self.composition().itemById(composerId)

                if composerItem is not None:
                    compFieldSelector = ComposerFieldSelector(self, composerItem, self.mainWindow())
                    compFieldSelector.selectFieldName(composer_data_source.dataFieldName(composerId))

                    # Add widget to the collection but now use the current uuid of the composition item
                    self.addWidgetMapping(composerItem.uuid(), compFieldSelector)

    def _configureSpatialSymbolEditor(self, spatial_field_config):
        """
        Configure symbol editor controls.
        """
        if not self._dataSourceWidget is None:
            for item_id, spFieldsMappings in spatial_field_config.spatialFieldsMapping().items():
                mapItem = self.composition().itemById(item_id)

                if mapItem is not None:
                    composerSymbolEditor = ComposerSymbolEditor(mapItem, self.mainWindow())
                    composerSymbolEditor.add_spatial_field_mappings(spFieldsMappings)

                    # Add widget to the collection but now use the current uuid of the composer map
                    self.addWidgetMapping(mapItem.uuid(), composerSymbolEditor)

    def _configure_photo_editors(self, photo_config_collection):
        """
        Creates widgets for editing photo data sources.
        :param photo_config_collection: PhotoConfigurationCollection instance.
        :type photo_config_collection: PhotoConfigurationCollection
        """
        if self._dataSourceWidget is None:
            return

        for item_id, photo_config in photo_config_collection.mapping().items():
            pic_item = self.composition().itemById(item_id)

            if pic_item is not None:
                photo_editor = ComposerPhotoDataSourceEditor(self, self.mainWindow())
                photo_editor.set_configuration(photo_config)

                self.addWidgetMapping(pic_item.uuid(), photo_editor)

    def _configure_chart_editors(self, chart_config_collection):
        """
        Creates widgets for editing chart properties.
        :param chart_config_collection: ChartConfigurationCollection instance.
        :type chart_config_collection: ChartConfigurationCollection
        """
        if self._dataSourceWidget is None:
            return

        for item_id, chart_config in chart_config_collection.mapping().items():
            chart_item = self.composition().itemById(item_id)

            if chart_item is not None:
                chart_editor = ComposerChartConfigEditor(self, self.mainWindow())
                chart_editor.set_configuration(chart_config)

                self.addWidgetMapping(chart_item.uuid(), chart_editor)

    def _configure_table_editors(self, table_config_collection):
        """
        Creates widgets for editing table data sources.
        :param table_config_collection: TableConfigurationCollection instance.
        :type table_config_collection: TableConfigurationCollection
        """
        if self._dataSourceWidget is None:
            return

        for item_id, table_config in table_config_collection.mapping().items():
            table_item = self.composition().itemById(item_id)
            if table_item is not None:
                table_editor = ComposerTableDataSourceEditor(self, table_item, self.mainWindow())

                table_editor.set_configuration(table_config)

                table_editor.ref_table.cbo_ref_table.currentIndexChanged[str].connect(
                    table_editor.set_table_vector_layer)

                self.addWidgetMapping(table_item.uuid(), table_editor)

    def _configure_qr_code_editors(self, qr_code_config_collection):
        """
        Creates widgets for editing QR code properties.
        :param qr_code_config_collection: QRCodeConfigurationCollection instance.
        :type qr_code_config_collection: QRCodeConfigurationCollection
        """
        if self._dataSourceWidget is None:
            return

        for item_id, qrc_config in qr_code_config_collection.mapping().items():
            qrc_item = self.composition().itemById(item_id)

            if qrc_item is not None:
                qrc_editor_cls = qr_code_config_collection.editor_type
                qrc_editor = qrc_editor_cls(self, self.mainWindow())
                qrc_editor.set_configuration(qrc_config)

                self.addWidgetMapping(qrc_item.uuid(), qrc_editor)

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
