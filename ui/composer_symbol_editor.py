"""
/***************************************************************************
Name                 : Composer Symbol Editor
Description          : Widget for defining symbology properties for the
                       selected spatial field.
Date                 : 24/May/2014 
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
                         QWidget,
                         QMessageBox,
                         QPushButton,
                         QColorDialog
                         )
from PyQt4.QtCore import Qt

from qgis.core import (
                       QgsVectorLayer,
                       QgsSimpleFillSymbolLayerV2,
                       QgsSimpleLineSymbolLayerV2
                       )
from qgis.gui import (
                      QgsSimpleMarkerSymbolLayerV2Widget,
                      QgsSimpleLineSymbolLayerV2Widget,
                      QgsSimpleFillSymbolLayerV2Widget,
                      QgsColorButton
                      )

from stdm.data import (
                       table_column_names,
                       geometryType
                       )

from .ui_composer_symbol_editor import Ui_frmComposerSymbolEditor
from .composer_spcolumn_styler import ComposerSpatialColumnEditor

class SimpleFillSymbolLayerProxyWidget(QgsSimpleFillSymbolLayerV2Widget):
    """
    We are using this proxy since on changing the fill color, the system crashes.
    This workaround disconnects all signals associated with the fill color button and manually
    reconnects using the 'colorChanged' signal to load color selection dialog.
    """
    def __init__(self,vectorLayer,parent = None):
        QgsSimpleFillSymbolLayerV2Widget.__init__(self,vectorLayer,parent)
        
        #Set symbol layer for the widget
        self._symLayer = QgsSimpleFillSymbolLayerV2()
        self._symLayer.setColor(Qt.cyan)
        self._symLayer.setFillColor(Qt.yellow)
        self.setSymbolLayer(self._symLayer)
        
        self._btnFillColor = self.findChild(QPushButton,"btnChangeColor")
        if self._btnFillColor != None:
            self._btnFillColor.colorChanged.disconnect()
            self._btnFillColor.colorChanged.connect(self.onSetFillColor)

        #Disable data defined properties button
        btnDataProp = self.findChild(QPushButton,"mDataDefinedPropertiesButton")
        if btnDataProp != None:
            btnDataProp.setVisible(False)
            
    def onSetFillColor(self,color):
        self.symbolLayer().setFillColor(color)
        
class ComposerSymbolEditor(QWidget,Ui_frmComposerSymbolEditor):
    """
    Widget for defining symbology properties for the selected spatial field.
    """
    def __init__(self,composerWrapper,parent = None):
        QWidget.__init__(self,parent)
        self.setupUi(self)
        
        self._composerWrapper = composerWrapper
        self._editorMappings = {}
        
        #Load fields if the data source has been specified
        self._dsName = self._composerWrapper.selectedDataSource()
        self._loadFields()
        
        #Connect signals
        self._composerWrapper.dataSourceSelected.connect(self.onDataSourceChanged)
        #self.cboSpatialFields.currentIndexChanged[str].connect(self.onSpatialColumnChanged)
        self.btnAddField.clicked.connect(self.onAddColumnStylerWidget)
        self.btnClear.clicked.connect(self.onClearTabs)
    
    def onDataSourceChanged(self,dataSourceName):
        """
        When the user changes the data source then update the fields.
        """
        self._dsName = dataSourceName
        self._loadFields()  
        
    def onClearTabs(self):
        """
        Slot raised to clear all tabs.
        """
        self.tbFieldProperties.clear()
        self._editorMappings = {}
        
    def spatialFieldMappings(self):
        """
        Returns a list of 'SpatialFieldMapping' objects based on the configured spatial fields.
        """
        spFieldMappings = []
        
        editors = self._editorMappings.values()
        for ed in editors:
            spFieldMapping = ed.spatialFieldMapping()
            spFieldMappings.append(spFieldMapping)
        
        return spFieldMappings
    
    def addSpatialFieldMappings(self,spatialFieldMappings):
        """
        Adds a list of spatial field mapping objects into the symbol editor.
        """
        for sfm in spatialFieldMappings:
            self.addSpatialFieldMapping(sfm)
    
    def addSpatialFieldMapping(self,spFieldMapping):
        """
        Add a style editor tab and apply settings defined in the object.
        """
        styleEditor = self.addStylingWidget(spFieldMapping.spatialField())
        styleEditor.applyMapping(spFieldMapping)
       
    def onAddColumnStylerWidget(self):
        """
        Slot raised to add a styling and editing widget to the field tab widget.
        """
        spColumnName = self.cboSpatialFields.currentText()

        if spColumnName == "":
            return
        
        if spColumnName in self._editorMappings:
            return
        
        self.addStylingWidget(spColumnName)
        
    def addStylingWidget(self,spColumnName): 
        """
        Add a styling widget to the field tab widget.
        """ 
        symbolEditor,geomType,srid = self._buildSymbolWidget(spColumnName)
        
        if symbolEditor == None:
            return None
        
        styleEditor = ComposerSpatialColumnEditor(spColumnName,self._composerWrapper)    
        styleEditor.setSymbolEditor(symbolEditor) 
        styleEditor.setGeomType(geomType)
        styleEditor.setSrid(srid)
        
        self.tbFieldProperties.addTab(styleEditor, spColumnName) 
        
        #Add column name and corresponding widget to the collection
        self._editorMappings[spColumnName] = styleEditor  
        
        return styleEditor  
    
    def _buildSymbolWidget(self,spColumnName):
        """
        Build symbol widget based on geometry type.
        """
        geomType,srid = geometryType(self._dsName,spColumnName)
        if geomType == "":
            return None
        
        vlGeomConfig = "{0}?crs=epsg:{1!s}".format(geomType,srid)
       
        vl = QgsVectorLayer(vlGeomConfig, "stdm_proxy", "memory")
        
        if geomType == "POINT":
            symbolEditor = QgsSimpleMarkerSymbolLayerV2Widget(vl)
            
        elif geomType == "LINESTRING":
            symbolEditor = QgsSimpleLineSymbolLayerV2Widget.create(vl)
            
        elif geomType == "POLYGON":
            symbolEditor = SimpleFillSymbolLayerProxyWidget(vl)
            
        else:
            return None
        
        return (symbolEditor,geomType,srid)
    
    def _loadFields(self):
        """
        Load spatial fields/columns of the given data source.
        """
        if self._dsName == "":
            self.cboSpatialFields.clear()
            return
        
        spatialColumns = table_column_names(self._dsName,True)
        
        if len(spatialColumns) == 0:
            return
        
        self.cboSpatialFields.clear()
        self.cboSpatialFields.addItem("")
        
        self.cboSpatialFields.addItems(spatialColumns)