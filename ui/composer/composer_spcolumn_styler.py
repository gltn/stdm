"""
/***************************************************************************
Name                 : Composer Spatial Column Editor
Description          : Widget for defining symbology and labeling properties 
                       for the selected spatial field.
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
    QMessageBox,
    QPushButton,
    QWidget
)
from PyQt4.QtCore import Qt

from qgis.core import (
    QgsSimpleFillSymbolLayerV2,
    QgsSymbolLayerV2Utils
)

from stdm.data.pg_utils import (
    table_column_names
)

from .ui_composer_spcolumn_styler import Ui_frmComposerSpatialColumnEditor

class SpatialFieldMapping(object):
    """
    Symbol and labeling configuration for an individual spatial field.
    """
    def __init__(self,spatialField="",labelField=""):
        self._spatialField = spatialField
        self._labelField = labelField
        self._symbol = None
        self._itemId = ""
        self._layerType = ""
        self._srid = -1
        self._geomType = ""
        self._zoom_level = 4
        
    def setSpatialField(self,spatialField):
        """
        Set the name of the spatial field.
        """
        self._spatialField = spatialField
        
    def spatialField(self):
        """
        Returns the name of the currently configured spatial field.
        """
        return self._spatialField
    
    def setLabelField(self,labelField):
        """
        Set the name of the field that will be used to label the feature.
        """
        self._labelField = labelField
        
    def labelField(self):
        """
        Return the field for labeling the spatial feature.
        """
        return self._labelField
        
    def setSymbolLayer(self, symbol):
        """
        Set the symbol layer associated with the spatial field.
        The symbol should be a subclass of QgsSymbolLayerV2.
        """
        self._symbol = symbol
        
        if not self._symbol is None:
            self._layerType = self._symbol.layerType()
        
    def symbolLayer(self):
        """
        Return the symbol layer configured for the spatial field.
        """
        return self._symbol
    
    def setItemId(self,itemId):
        """
        Returns the composer item id (QgsComposerMap uuid) associated with the spatial field.
        """
        self._itemId = itemId
        
    def itemId(self):
        """
        Returns the composer item id associated with the spatial field.
        """
        return self._itemId
    
    def symbolLayerType(self):
        """
        Returns the symbol layer type associated with the the symbol layer.
        """
        return self._layerType
    
    def srid(self):
        """
        Return the SRID of the referenced spatial column.
        """
        return self._srid
    
    def setSRID(self,srid):
        """
        Set the SRID of the spatial column.
        """
        self._srid = srid
        
    def geometryType(self):
        """
        Return the geometry type string representation of the spatial column.
        """
        return self._geomType
    
    def setGeometryType(self,geomType):
        """
        Set the geometry type of the spatial column.
        """
        self._geomType = geomType
        
    def zoomLevel(self):
        """
        Return the zoom out scale factor that should be applied relative
        to the extents of a spatial unit.
        """
        return self._zoom_level
    
    def setZoomLevel(self,zoomLevel):
        """
        Set zoom out scale factor.
        """
        self._zoom_level = zoomLevel
        
    def toVectorURI(self):
        """
        Returns a QgsVectorLayer URI using the geometry type and SRID information.
        """
        return  "{0}?crs=epsg:{1!s}".format(self._geomType,self._srid)
    
    def toDomElement(self, domDocument):
        """
        Returns a QDomElement with the object instance settings
        """
        spColumnElement = domDocument.createElement("SpatialField")
        spColumnElement.setAttribute("name",self._spatialField)
        spColumnElement.setAttribute("labelField",self._labelField)
        spColumnElement.setAttribute("itemid",self._itemId)
        spColumnElement.setAttribute("srid",self._srid)
        spColumnElement.setAttribute("geomType",self._geomType)

        spColumnElement.setAttribute("zoom",str(self._zoom_level))
        symbolElement = domDocument.createElement("Symbol")
        
        #Append symbol properties element
        if not self._symbol is None:
            prop = self._symbol.properties()
            QgsSymbolLayerV2Utils.saveProperties(prop,domDocument,symbolElement)
            symbolElement.setAttribute("layerType",self._layerType)
        
        spColumnElement.appendChild(symbolElement)
        
        return spColumnElement

class ComposerSpatialColumnEditor(QWidget,Ui_frmComposerSpatialColumnEditor):
    """
    Widget for defining symbology and labeling properties for the selected spatial field.
    """
    def __init__(self, spColumnName, composerWrapper, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)

        self._composerWrapper = composerWrapper
        
        self._spColumnName = spColumnName
        
        self._symbol_editor = None

        self._zoom_out_level = 16

        self.sb_zoom.setValue(self._zoom_out_level)
        
        self._srid = -1
        
        self._geomType = ""
        
        #Load fields if the data source has been specified
        self._dsName = self._composerWrapper.selectedDataSource()
        self._loadFields()
        
        #Connect signals
        self._composerWrapper.dataSourceSelected.connect(self.onDataSourceChanged)
        self.sb_zoom.valueChanged.connect(self.on_zoom_level_changed)
    
    def onDataSourceChanged(self,dataSourceName):
        """
        When the user changes the data source then update the fields.
        """
        self._dsName = dataSourceName
        self._loadFields()  
        
    def setSymbolEditor(self, editor):
        """
        Set the widget's symbol editor.
        """
        self._symbol_editor = editor
        self.styleLayout.addWidget(editor)
        
    def symbolEditor(self):
        """
        Returns the current symbol editor.
        """
        return self._symbol_editor
        
    def symbolLayer(self):
        """
        Returns the symbol layer specified in the symbol editor.
        """
        return self._symbol_editor.symbolLayer()
    
    def setGeomType(self,geomType):
        """
        Set the geometry type of the specified spatial unit.
        """
        self._geomType = geomType
        
    def geomType(self):
        """
        Return the geometry type of the specified spatial unit.
        """
        return self._geomType
    
    def setSrid(self,srid):
        """
        Set the SRID of the specified spatial unit.
        """
        self._srid = srid
        
    def srid(self):
        """
        Return the SRID of the specified spatial unit.
        """
        return self._srid
        
    def spatialFieldMapping(self):
        """
        Returns a SpatialFieldMapping object instance configured to the current settings.
        """
        sp_field_mapping = SpatialFieldMapping(self._spColumnName, self.cboLabelField.currentText())

        sp_field_mapping.setSymbolLayer(self.symbolLayer())
        sp_field_mapping.setSRID(self._srid)
        sp_field_mapping.setGeometryType(self._geomType)
        sp_field_mapping.setZoomLevel(self.sb_zoom.value())
        
        return sp_field_mapping
    
    def applyMapping(self, spatialFieldMapping):
        """
        Configures the widget to use the specified spatial field mapping.
        """
        #Configure widget based on the mapping 
        self._spColumnName = spatialFieldMapping.spatialField()
        self.setLabelField(spatialFieldMapping.labelField())
        self._srid = spatialFieldMapping.srid()
        self._geomType = spatialFieldMapping.geometryType()
        self.sb_zoom.setValue(spatialFieldMapping.zoomLevel())

    def setLabelField(self,labelField):
        """
        Select field label item.
        """
        fieldIndex = self.cboLabelField.findText(labelField)
        
        if fieldIndex != -1:
            self.cboLabelField.setCurrentIndex(fieldIndex)

    def on_zoom_level_changed(self, value):
        """
        Slot raised when the spin box value, representing the zoom level,
        changes.
        """
        if self._zoom_out_level != value:
            self._zoom_out_level = value
        
    def _loadFields(self):
        """
        Load labeling fields/columns.
        """
        if not self._dsName:
            self.cboLabelField.clear()
            return
        
        cols = table_column_names(self._dsName)
        spatialCols = table_column_names(self._dsName,True)
        
        spSet = set(spatialCols)
        nonSpatialCols = [c for c in cols if c not in spSet]
        
        if len(nonSpatialCols) == 0:
            return
        
        self.cboLabelField.clear()
        self.cboLabelField.addItem("")
        
        self.cboLabelField.addItems(nonSpatialCols)