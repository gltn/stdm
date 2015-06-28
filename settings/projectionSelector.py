'''
Name                 : ProjectionSelector
Description          : Load generic projections selector dialog for user to select the srs id  
Date                 : 17/Oct/13
copyright            : (C) 2013 by Solomon Njoroge
email                : njoroge.solomon@yahoo.com
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/

'''
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from qgis.gui import QgsGenericProjectionSelector


class projectionSelector(QDialog):
    def __init__(self,parent):
        super(projectionSelector,self).__init__(parent)
        self.parent=parent
       
      
    def loadAvailableSystems(self):
        coordSys=""
        crsDlg=QgsGenericProjectionSelector(self.parent)
        if crsDlg.exec_()==QDialog.Accepted:
            coordSys=str(crsDlg.selectedAuthId())
        return coordSys