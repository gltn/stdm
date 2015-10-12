"""
/***************************************************************************
Name                 : STDM Report Builder Field Settings Dialog
Description          : Dialog for enabling the user to configure display 
                       settings for each report field
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
    def __init__(self, id):              
        TitleBase.__init__(self,id)
        #Set report element parent
        self._rptEl.parent = "Fields"  
        self.__insert_image_ctrl()
        self.columnStyle = {}
        self.elTop = 0.2
        
    def __insert_image_ctrl(self):
        '''
        Insert control for enabling users to specify
        whether the field is an image field
        '''
        self.imgField = QCheckBox(self.scrollAreaWidgetContents)
        self.imgField.setObjectName("imgField")
        self.imgField.setText('Image Field')
        self.verticalLayout.insertWidget(12, self.imgField)
        
    def is_image_field(self):
        #Does the dialog represent an image field
        return self.imgField.isChecked()
        
    def get_object_value(self):
        '''
        Get the object value or image representing the row
        '''        
        att_name = str(self.ID)  
        obj_val = None      
        if self.is_image_field():
            #Set default image size settings then override if the user specifies
            self.elWidth=2
            self.elHeight=1.5
            self.compileEntry()
            obj_val = Image(left=self.elLeft*cm, top=(self.elTop)*cm, width=self.elWidth*cm, height=self.elHeight*cm,
                         get_image=lambda graphic:PILImage.open(str(graphic.instance[att_name])))
        else:
            self.compileEntry()            
            obj_val = ObjectValue(attribute_name=att_name, top=(self.elTop)*cm, left=self.elLeft*cm, 
			    width=self.elWidth*cm, height=self.elHeight*cm, style=self.getStyle())                
	     
        return obj_val
        
    def get_label(self):
        #Get the geraldo label for the column label   
        self.columnStyle['left'] = self.elLeft*cm
        self.columnStyle['text'] = self.elText
        self.columnStyle['width'] = self.elWidth*cm

        lbl = Label()
        for k,v in self.columnStyle.iteritems():
            setattr(lbl,k,v)
        return lbl
    
    def get_settings(self):
        #Override with the addition of the isImage attribute
        rpt_el = super(FieldBase, self).getSettings()
        rpt_el.dialogSettings.isImage = self.imgField.isChecked()        
        
        self._rptEl.dialogSettings = rpt_el.dialogSettings        
            
        return self._rptEl
        
    def Info_message(self, message):            
        #General Info Message Box
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.exec_()   
        
