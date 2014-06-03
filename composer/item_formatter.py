"""
/***************************************************************************
Name                 : Composer item formatters
Description          : Classes for formatting the QgsComposerItems.
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
                         QApplication,
                         QPlainTextEdit,
                         QCheckBox,
                         QPushButton,
                         QRadioButton,
                         QWidget,
                         QLabel,
                         QDoubleSpinBox,
                         QMessageBox
                         )

from qgis.core import (
                       QgsComposerArrow,
                       QgsComposerLabel,
                       QgsComposerMap
                       )

from stdm.ui import (
                     ComposerSymbolEditor,
                     ComposerFieldSelector
                     )
                     
class BaseComposerItemFormatter(object):
    """
    Defines the abstract interface for implementation by subclasses.
    """
    def apply(self,composerItem,composerWrapper,fromTemplate = False):
        """
        Subclasses to implement this method for formatting composer items.
        """
        raise NotImplementedError
    
class LineFormatter(BaseComposerItemFormatter):
    """
    Removes the marker in an arrow composer item to depict a line.
    """
    def apply(self,arrow,composerWrapper,fromTemplate = False):
        """
        This code is not applicable since the method returns a QgsComposerItem instance
        instead of an arrow.
        if not isinstance(arrow,QgsComposerArrow):
            return
        """
        
        #Resorted to use the editor to manually edit the composer item to depict a line
        arrowEditor = composerWrapper.itemDock().widget()
        
        if arrowEditor != None:
            noMarkerRadioButton = arrowEditor.findChild(QRadioButton,"mNoMarkerRadioButton")
            #If exists, force remove of marker
            if noMarkerRadioButton != None:
                noMarkerRadioButton.toggle()
                
            #Hide arrow editor controls
            arrowMarkersGroup = arrowEditor.findChild(QWidget,"mArrowMarkersGroupBox")
            if arrowMarkersGroup != None:
                arrowMarkersGroup.setVisible(False)
                
            #Remove arrowhead width controls
            lblWidth = arrowEditor.findChild(QLabel,"label_2")
            if lblWidth != None:
                lblWidth.setVisible(False)
                
            widthSpinBox = arrowEditor.findChild(QDoubleSpinBox,"mArrowHeadWidthSpinBox")
            if widthSpinBox != None:
                widthSpinBox.setVisible(False)
        
class DataLabelFormatter(BaseComposerItemFormatter):
    """
    Adds text to indicate that the label is an STDM data field.
    """
    def apply(self,label,composerWrapper,fromTemplate = False):
        if not isinstance(label,QgsComposerLabel):
            return
        
        if not fromTemplate:
            #Set display text
            label.setText(QApplication.translate("DataLabelFormatter","[STDM Data Field]"))
        
            #Adjust width
            label.adjustSizeToText()
        
            #Set ID to match UUID
            label.setId(label.uuid())
            
            fieldSelector = ComposerFieldSelector(composerWrapper,label) 
            stdmDock = composerWrapper.stdmItemDock()
            stdmDock.setWidget(fieldSelector)
            
            #Add widget to the composer wrapper widget mapping collection
            composerWrapper.addWidgetMapping(label.uuid(),fieldSelector)
        
        #Get the editor widget for the label
        labelEditor = composerWrapper.itemDock().widget()
        
        #Remove some of the editing controls
        if labelEditor != None:
            textEdit = labelEditor.findChild(QPlainTextEdit,"mTextEdit")
            if textEdit != None:
                textEdit.setVisible(False)
                
            renderHtmlCheck = labelEditor.findChild(QCheckBox,"mHtmlCheckBox")
            if renderHtmlCheck != None:
                renderHtmlCheck.setVisible(False)
                
            expressionBtn = labelEditor.findChild(QPushButton,"mInsertExpressionButton")
            if expressionBtn != None:
                expressionBtn.setVisible(False)
                
class MapFormatter(BaseComposerItemFormatter):
    """
    Add widget for formatting spatial data sources.
    """
    def apply(self,templateMap,composerWrapper,fromTemplate = False):
        if not isinstance(templateMap,QgsComposerMap):
            return
        
        if not fromTemplate:
            #Set ID to match UUID
            templateMap.setId(templateMap.uuid())
        
            #Create styling editor and it to the dock widget
            composerSymbolEditor = ComposerSymbolEditor(composerWrapper)
            stdmDock = composerWrapper.stdmItemDock()
            stdmDock.setWidget(composerSymbolEditor)
                
            #Add widget to the composer wrapper widget mapping collection
            composerWrapper.addWidgetMapping(templateMap.uuid(),composerSymbolEditor)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

