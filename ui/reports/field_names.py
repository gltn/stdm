"""
/***************************************************************************
Name                 : STDM Report Builder Field Names Settings Dialog
Description          : Dialog for enabling the user to configure display 
                       settings for the collective field names
Date                 : 07/September/11 
copyright            : (C) 2014 by UN-Habitat and implementing partners.
                       See the accompanying file CONTRIBUTORS.txt in the root
email                : stdm@unhabitat.org
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
    def __init__(self, id, parent=None):              
        TitleBase.__init__(self, id, parent) 
        self.init_widget() 
        self.elTop = 0.8
        self.elFont = QFont("Times New Roman",14,75)
        self.elFontColor = QColor(Qt.darkBlue)
    
    def init_widget(self):
        self.label_6.setVisible(False)
        self.txtTitleText.setVisible(False)
        
    def column_style(self):
        #Get the geraldo label for the column
        self.compileEntry()
        lbl_dic = dict(top=self.elTop*cm, style=self.getStyle())        
        return lbl_dic
               
        
