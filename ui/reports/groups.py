"""
/***************************************************************************
Name                 : STDM Report Builder Field Settings Dialog
Description          : Dialog for enabling the user to configure display 
                       settings for the define groups
Date                 : 10th/November/11 
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
    def __init__(self,id,parent = None):              
        TitleBase.__init__(self,id,parent)
        
        #Set report element parent
        self._rptEl.parent = "Groups"
        
        #Font
        self.elFont = QFont("Times New Roman",14,75)
        
        #Color
        self.elFontColor = QColor(Qt.white)
        self.elWidth = BAND_WIDTH
        self.cboBorder.setCurrentIndex(4)
        
    def setWidth(self):
        #Override the WIDTH specified by the user
        if self.txtTitleWidth.text():
            dWidth = float(self.txtTitleWidth.text())
            self.elWidth=dWidth*cm

    def getReportGroup(self):
        '''
        Get the Geraldo report group object
        '''
        self.compileEntry()
        attName=str(self.ID)
        attName=attName.replace("gp_", "")
        gpStyle=self.getStyle()  
        gpStyle["backColor"]= blue    
        gpStyle["borderRadius"]=2
        gpStyle["borderPadding"]=2
        rptGroup=ReportGroup(attribute_name=attName,\
            band_header=ReportBand(\
                height=0.6*cm,\
                elements=[ObjectValue(attribute_name=attName,top=(self.elTop)*cm,left=self.elLeft*cm,width=self.elWidth,height=self.elHeight*cm,
                        style=gpStyle)],
                borders=self.elBorder))
        return rptGroup
  
               
        