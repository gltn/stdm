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
from PyQt4.QtGui import (
                         QToolBar,
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
                       QgsComposerLabel,
                       QgsComposerItem,
                       QgsComposerMap
                       )

from stdm.settings import RegistryConfig
from stdm.ui import (
                     ComposerDataSourceSelector, 
                     ComposerFieldSelector,
                     ComposerSymbolEditor
                     )

from .composer_item_config import ComposerItemConfig
from .composer_data_source import ComposerDataSource
from .spatial_fields_config import SpatialFieldsConfiguration
from .item_formatter import (
                             DataLabelFormatter,
                             LineFormatter,
                             MapFormatter
                             )

class ComposerWrapper(QObject):
    """
    Embeds custom STDM tools in a QgsComposer instance for managing map-based
    STDM document templates.
    """
    dataSourceSelected = pyqtSignal(str)
    
    def __init__(self,composerView):
        QObject.__init__(self,composerView)
        
        self._compView = composerView
        self._stdmTB = self.mainWindow().addToolBar("STDM")
        self._selectMoveAction = None
        
        #Container for custom editor widgets
        self._widgetMappings = {}
        
        #Create dock widget for configuring STDM data source
        self._stdmDataSourceDock = QDockWidget(QApplication.translate("ComposerWrapper","STDM Data Source"),self.mainWindow())
        self._stdmDataSourceDock.setObjectName("STDMDataSourceDock")
        self._stdmDataSourceDock.setMinimumWidth(300)
        self._stdmDataSourceDock.setFeatures(QDockWidget.DockWidgetMovable|QDockWidget.DockWidgetClosable)
        self.mainWindow().addDockWidget(Qt.RightDockWidgetArea,self._stdmDataSourceDock)
        
        dataSourceWidget = ComposerDataSourceSelector()
        self._stdmDataSourceDock.setWidget(dataSourceWidget)
        self._stdmDataSourceDock.show()
        
        #Create dock widget for configuring STDM item properties
        self._stdmItemPropDock = QDockWidget(QApplication.translate("ComposerWrapper","STDM data properties"),self.mainWindow())
        self._stdmItemPropDock.setObjectName("STDMItemDock")
        self._stdmItemPropDock.setMinimumWidth(300)
        self._stdmItemPropDock.setFeatures(QDockWidget.DockWidgetMovable|QDockWidget.DockWidgetClosable)
        self.mainWindow().addDockWidget(Qt.RightDockWidgetArea,self._stdmItemPropDock)
        self._stdmItemPropDock.show()
        
        if self.itemDock() != None:
            self.mainWindow().tabifyDockWidget(self.itemDock(),self._stdmItemPropDock)
            
        if self.atlasDock() != None:
            self.atlasDock().hide()
            
        if self.generalDock() != None:
            self.generalDock().raise_()
            
        #Connect signals
        self.composition().itemRemoved.connect(self._onItemRemoved)
        dataSourceWidget.cboDataSource.currentIndexChanged[str].connect(self.propagateDataSourceSelection)
        self.composerView().selectedItemChanged.connect(self._onItemSelected)
        
        #Current template document file
        self._currDocFile = None
        
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
            ciConfigObj = ciConfig(self)
            
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
    
    def setDocumentFile(self,docFile):
        """
        Sets the document file.
        """
        if not isinstance(docFile,QFile):
            return
        
        self._currDocFile = docFile
    
    def selectedDataSource(self):
        """
        Returns the name of the data source specified by the user.
        """
        return self._stdmDataSourceDock.widget().cboDataSource.currentText()
    
    def selectedDataSourceCategory(self):
        """
        Returns the category (view or table) that the data source belongs to.
        """
        if self.stdmDataSourceDock().widget() != None:
            return self.stdmDataSourceDock().widget().category()
        
        return ""
    
    def propagateDataSourceSelection(self,dataSourceName):
        """
        Propagates the signal when a user select a data source. Listening objects can hook on to it.
        """
        self.dataSourceSelected.emit(dataSourceName)
        
    def loadTemplate(self,filePath):
        """
        Loads a document template into the view and updates the necessary STDM-related controls.
        """
        if not QFile.exists(filePath):
                QMessageBox.critical(self.composerView(), QApplication.translate("OpenTemplateConfig","Open Template Error"), \
                                            QApplication.translate("OpenTemplateConfig","The specified template does not exist."))
                return
            
        templateFile = QFile(filePath)
        
        if not templateFile.open(QIODevice.ReadOnly):
            QMessageBox.critical(self.composerView(), QApplication.translate("ComposerWrapper","Open Operation Error"), \
                                            "{0}\n{1}".format(QApplication.translate("ComposerWrapper","Cannot read template file."), \
                                                      templateFile.errorString()
                                                      ))
            return    
         
        templateDoc = QDomDocument()
        
        if templateDoc.setContent(templateFile):
            #Load items into the composition and configure STDM data controls
            self.composition().loadFromTemplate(templateDoc)
            self.clearWidgetMappings()
            
            #Load data controls
            composerDS = ComposerDataSource.create(templateDoc)
            self._configureDataControls(composerDS)
            
            #Load symbol editors
            spatialFieldsConfig = SpatialFieldsConfiguration.create(templateDoc)
            self._configureSpatialSymbolEditor(spatialFieldsConfig)
            
    def saveTemplate(self):
        """
        Creates and saves a new document template.
        """
        #Validate if the user has specified the data source
        if self.selectedDataSource() == "":
            QMessageBox.critical(self.composerView(), QApplication.translate("ComposerWrapper","Error"), \
                                            QApplication.translate("ComposerWrapper","Please specify the " \
                                                                   "data source name for the document composition."))
            return
            
        #If it is a new unsaved document template then prompt for the document name.
        docFile = self.documentFile()
        
        if docFile == None:
            docName,ok = QInputDialog.getText(self.composerView(), \
                                              QApplication.translate("ComposerWrapper","Template Name"), \
                                              QApplication.translate("ComposerWrapper","Please enter the template name below"), \
                                              )
            if ok and docName != "":
                templateDir = self._composerTemplatesPath()
                
                if templateDir == None:
                    QMessageBox.critical(self.composerView(), QApplication.translate("ComposerWrapper","Error"), \
                                            QApplication.translate("ComposerWrapper","Directory for document templates could not be found."))
                    return
                
                absPath = templateDir + "/" + docName + ".sdt"            
                docFile= QFile(absPath)
            
            else:
                return
        
        docFileInfo = QFileInfo(docFile)    
        
        if not docFile.open(QIODevice.WriteOnly):
            QMessageBox.critical(self.composerView(), QApplication.translate("ComposerWrapper","Save Operation Error"), \
                                            "{0}\n{1}".format(QApplication.translate("ComposerWrapper","Could not save template file."), \
                                                      docFile.errorString()
                                                      ))
            return
                                              
        templateDoc = QDomDocument()
        self._writeXML(templateDoc,docFileInfo.completeBaseName())
        
        if docFile.write(templateDoc.toByteArray()) == -1:
            QMessageBox.critical(self.composerView(), QApplication.translate("ComposerWrapper","Save Error"), \
                                            QApplication.translate("ComposerWrapper","Could not save template file."))
            return
        
        docFile.close()                   
        self.setDocumentFile(docFile)
        
    def _writeXML(self,xmlDoc,docName):
        """
        Write the template configuration into the XML document.
        """        
        #Write default composer configuration
        composerElement = xmlDoc.createElement("Composer")
        composerElement.setAttribute("title",docName)
        composerElement.setAttribute("visible",1)
        
        xmlDoc.appendChild(composerElement)
        
        self.composition().writeXML(composerElement,xmlDoc)
        
        #Write STDM data field configurations
        dataSourceElement = ComposerDataSource.domElement(self, xmlDoc)
        composerElement.appendChild(dataSourceElement)
        
        #Write spatial field configurations
        spatialColumnsElement = SpatialFieldsConfiguration.domElement(self, xmlDoc)
        dataSourceElement.appendChild(spatialColumnsElement)
        
    def _configureDataControls(self,composerDataSource):
        """
        Configure the data source and data field controls based on the composer data
        source configuration.
        """
        if self.stdmDataSourceDock().widget() != None:
            #Set data source
            dataSourceWidget = self.stdmDataSourceDock().widget()
            dataSourceWidget.setCategory(composerDataSource.category())
            dataSourceWidget.setSelectedSource(composerDataSource.name())
            
            #Set data field controls
            for composerId in composerDataSource.dataFieldMappings().reverse:
                #Use composer item id since the uuid is stripped off
                composerItem = self.composition().getComposerItemById(composerId)
                
                if composerItem != None:
                    compFieldSelector = ComposerFieldSelector(self,composerItem,self.composerView())
                    compFieldSelector.selectFieldName(composerDataSource.dataFieldName(composerId))
                    
                    #Add widget to the collection but now use the current uuid of the composition item
                    self.addWidgetMapping(composerItem.uuid(),compFieldSelector)
                    
    def _configureSpatialSymbolEditor(self,spatialFieldConfig):
        """
        Configure symbol editor controls.
        """
        if self.stdmDataSourceDock().widget() != None:
            for itemId,spFieldsMappings in spatialFieldConfig.spatialFieldsMapping().iteritems():
                mapItem =  self.composition().getComposerItemById(itemId)
                
                if mapItem != None:
                    composerSymbolEditor = ComposerSymbolEditor(self,self.composerView())
                    composerSymbolEditor.addSpatialFieldMappings(spFieldsMappings)
                    
                    #Add widget to the collection but now use the current uuid of the composer map
                    self.addWidgetMapping(mapItem.uuid(),composerSymbolEditor)
                        
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
    
    def _onItemSelected(self,item):
        """
        Slot raised when a composer item is selected. Load the corresponding field selector
        if the selection is an STDM data field label.
        QComposerLabel is returned as a QObject in the slot argument hence, we have resorted to 
        capturing the currently selected items in the composition.
        """
        selectedItems = self.composition().selectedComposerItems()
        
        if len(selectedItems) == 0:
            self._stdmItemPropDock.setWidget(None)
        
        elif len(selectedItems) == 1:
            composerItem = selectedItems[0]
            
            if composerItem.uuid() in self._widgetMappings:
                stdmWidget = self._widgetMappings[composerItem.uuid()]
                
                if stdmWidget == self._stdmItemPropDock.widget():
                    return
                
                else:
                    self._stdmItemPropDock.setWidget(stdmWidget)
                    
                #Playing it safe in applying the formatting for the editor controls where applicable
                itemFormatter = None
                if isinstance(composerItem,QgsComposerArrow):
                    itemFormatter = LineFormatter()
                elif isinstance(composerItem,QgsComposerLabel):
                    itemFormatter = DataLabelFormatter()
                elif isinstance(composerItem,QgsComposerMap):
                    itemFormatter = MapFormatter()
                        
                if itemFormatter != None:
                    itemFormatter.apply(composerItem,self,True)
                    
            else:
                self._stdmItemPropDock.setWidget(None)
            
        elif len(selectedItems) > 1:
            self._stdmItemPropDock.setWidget(None)
        
        
        
        
        
        
        
        
        
        
        
        
        
        