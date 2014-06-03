"""
/***************************************************************************
Name                 : Property Preview Widget
Description          : Tab widget for previewing a single spatial unit overlaid
                       on either a local map or web sources (Google Maps or
                       OpenLayers).
Date                 : 10/October/2013 
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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from ui_property_preview import Ui_frmPropertyPreview

class PropertyPreviewWidget(QTabWidget, Ui_frmPropertyPreview):
    '''
    Widget for previewing spatial unit on either local map or web source.
    '''
    def __init__(self,parent = None):
        QTabWidget.__init__(self,parent)
        self.setupUi(self)
        self.canvasBgColor = Qt.white
        
        #Set defaults
        self._setDefaults()
        
    def _setDefaults(self):
        '''
        Set default settings
        '''
        self.setCanvasBackgroundColor(self.canvasBgColor)
        #Temp
        self.addProject("D:/Test.qgs")
        
    def setCanvasBackgroundColor(self,color):
        '''
        Set the background color of the map canvas
        '''
        self.localMap.setCanvasColor(color)
        self.canvasBgColor = color
        
    def addProject(self,path):
        '''
        Set the map project to the file location specified in the path
        '''
        fi = QFileInfo(path)
        
        #Check if the file exists
        if not fi.exists():
            #TODO: Add error message to message logger
            return
        
        #Add file path to QgsProject object
        if not QgsProject.instance().read(fi):
            #TODO: Add error message to message logger
            pass
        
        
        
        
        
        
        
        
        
        