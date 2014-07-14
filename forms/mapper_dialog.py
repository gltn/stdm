"""
/***************************************************************************
Name                 : Generic application for forms
Description          : forms generator functions
Date                 : 30/June/2013 
copyright            : (C) 2013 by Solomon Njogu
email                : njoroge.solomon.com
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
from stdm.data import MapperMixin

class MapperDailog(QDialog):
    def __init__(self, parent, model):
        #MapperMixin.__init__(self, model)
        self.model=model
        
    def accept(self):
        self.submit()
        QDialog.accept(self)
        
class CustomFormDailog(MapperDailog):
    def __init__(self,parent,model):
        MapperDailog.__init__(self, parent, model)
        
        self.layout=QFormLayout()
        #self.layout.addRow()
        