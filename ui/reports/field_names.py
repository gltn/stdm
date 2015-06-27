"""
/***************************************************************************
Name                 : STDM Report Builder Field Names Settings Dialog
Description          : Dialog for enabling the user to configure display 
                       settings for the collective field names
Date                 : 07/September/11 
copyright            : (C) 2011 by John Gitau
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
                         QFont, 
                         QColor
                         )
from PyQt4.QtCore import Qt

from reportlab.lib.units import cm

from geraldo import (
                     ObjectValue,
                     Label
                     )

from .report_title_base import TitleBase

class FieldNames(TitleBase):     
    #Class constructor  
    def __init__(self,id,parent = None):              
        TitleBase.__init__(self,id,parent) 
        self.initWidget() 
        self.elTop=0.8
        self.elFont = QFont("Times New Roman",14,75)
        self.elFontColor = QColor(Qt.darkBlue)
    
    def initWidget(self):
        self.label_6.setVisible(False)
        self.txtTitleText.setVisible(False)
        
    def columnStyle(self):
        #Get the geraldo label for the column
        self.compileEntry()
        lblDic=dict(top=self.elTop*cm,style=self.getStyle())        
        return lblDic
               
        