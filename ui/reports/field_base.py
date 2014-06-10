"""
/***************************************************************************
Name                 : STDM Report Builder Field Settings Dialog
Description          : Dialog for enabling the user to configure display 
                       settings for each report field
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
from PyQt4.QtGui import *

from reportlab.lib.units import cm
from reportlab.lib.colors import black

from geraldo import (
                     ObjectValue,
                     Label,
                     Image
                     )

from PIL import Image as PILImage

from .report_title_base import TitleBase

class FieldBase(TitleBase):     
    #Class constructor  
    def __init__(self,id):              
        TitleBase.__init__(self,id)
        #Set report element parent
        self._rptEl.parent = "Fields"  
        self.__insertImageCtrl()
        self.columnStyle={}
        self.elTop=0.2
        
    def __insertImageCtrl(self):
        '''
        Insert control for enabling users to specify
        whether the field is an image field
        '''
        self.imgField = QCheckBox(self.scrollAreaWidgetContents)
        self.imgField.setObjectName("imgField")
        self.imgField.setText('Image Field')
        self.verticalLayout.insertWidget(12,self.imgField)
        
    def isImageField(self):
        #Does the dialog represent an image field
        return self.imgField.isChecked()
        
    def getObjectValue(self):
        '''
        Get the object value or image representing the row
        '''        
        attName=str(self.ID)  
        objVal=None      
        if self.isImageField():
            #Set default image size settings then override if the user specifies
            self.elWidth=2
            self.elHeight=1.5
            self.compileEntry()
            objVal=Image(left=self.elLeft*cm, top=(self.elTop)*cm,width=self.elWidth*cm,height=self.elHeight*cm,
                         get_image=lambda graphic:PILImage.open(str(graphic.instance[attName])))
        else:
            self.compileEntry()            
            objVal=ObjectValue(attribute_name=attName,top=(self.elTop)*cm,left=self.elLeft*cm,width=self.elWidth*cm,height=self.elHeight*cm,style=self.getStyle())                
        return objVal
        
    def getLabel(self):
        #Get the geraldo label for the column label   
        self.columnStyle['left']=self.elLeft*cm
        self.columnStyle['text']=self.elText
        self.columnStyle['width']=self.elWidth*cm
        lbl = Label()
        for k,v in self.columnStyle.iteritems():
            setattr(lbl,k,v)
        return lbl
    
    def getSettings(self):
        #Override with the addition of the isImage attribute
        rptEl = super(FieldBase,self).getSettings()
        rptEl.dialogSettings.isImage = self.imgField.isChecked()        
        
        self._rptEl.dialogSettings = rptEl.dialogSettings        
            
        return self._rptEl
        
    def InfoMessage(self,Message):            
        #General Info Message Box
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(Message)
        msg.exec_()   
               
        