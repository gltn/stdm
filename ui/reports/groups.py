"""
/***************************************************************************
Name                 : STDM Report Builder Field Settings Dialog
Description          : Dialog for enabling the user to configure display 
                       settings for the define groups
Date                 : 10th/November/11 
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

from geraldo import (
                     ObjectValue,
                     Label,
                     ReportGroup,
                     ReportBand,
                     BAND_WIDTH
                     )

from reportlab.lib.units import cm
from reportlab.lib.colors import navy, yellow, red, purple, orange,\
    green, white, blue,grey
    
from .report_title_base import TitleBase

class Groups(TitleBase):     
    #Class constructor  
    def __init__(self, id, parent=None):              
        TitleBase.__init__(self, id, parent)
        
        #Set report element parent
        self._rptEl.parent = "Groups"
        
        #Font
        self.elFont = QFont("Times New Roman",14,75)
        
        #Color
        self.elFontColor = QColor(Qt.white)
        self.elWidth = BAND_WIDTH
        self.cboBorder.setCurrentIndex(4)
        
    def set_width(self):
        #Override the WIDTH specified by the user
        if self.txtTitleWidth.text():
            d_width = float(self.txtTitleWidth.text())
            self.elWidth = d_width * cm

    def get_report_group(self):
        '''
        Get the Geraldo report group object
        '''
        self.compileEntry()
        att_name = str(self.ID)
        att_name = att_name.replace("gp_", "")
        gp_style = self.getStyle()  
        gp_style["backColor"] = blue    
        gp_style["borderRadius"] = 2
        gp_style["borderPadding"] = 2

        rpt_group = ReportGroup(attribute_name=att_name,\
            band_header=ReportBand(\
                height=0.6*cm,\
                elements=[ObjectValue(attribute_name=attName, top=(self.elTop)*cm,
			 left=self.elLeft*cm, width=self.elWidth, height=self.elHeight*cm,
                        style=gpStyle)],
                borders=self.elBorder))
        return rptGroup
  
               
        
