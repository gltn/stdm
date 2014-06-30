# -*- coding: utf-8 -*-
"""
/***************************************************************************
 name:                    dataReader Form 
 Descriptions:            provides user with interface to input data on selected module
                                 A QGIS plugin
 Securing land and property rights for all
                             -------------------
        begin                : 2014-03-04
        copyright            : (C) 2014 by GLTN
        email                : gltn_stdm@unhabitat.org
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
from qtalchemy import *
from sqlalchemy import MetaData, Table
from qtalchemy.dialogs import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from sqlalchemy.orm import clear_mappers, Query
#from stdm.data import TableMapper
from stdm.data import STDMDb
#from foreign_key_mapper import ForeignRelationMapper,ForeignKey,LookupEntity
from sqlalchemy.exc import SQLAlchemyError

class STDMForm(BoundDialog):
    def __init__(self,parent,tableCls,columns,Session=None, row=None, row_id=None, flush=True):
        BoundDialog.__init__(self, parent)
        self.session=Session
        self.cols=columns
        
        self.setDataReader(self.session,tableCls,'id')
        vbox=QVBoxLayout()
        self.setLayout(vbox)
        grid=LayoutLayout(vbox,QFormLayout())
                
        self.mm=self.mapClass(tableCls)
        self.mm.addBoundForm(vbox,self.cols)
        
        buttons = LayoutWidget(vbox,QDialogButtonBox())
        self.close_button = ButtonBoxButton(buttons,QDialogButtonBox.Ok)
        self.close_button1 = ButtonBoxButton(buttons,QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        self.geo=WindowGeometry(self, position=False, tabs=None)
        #self.main=tableCls()
        self.readData(row, row_id)
        
    def load(self):
        self.mm.connect_instance(self.main_row)
        self.submit()
        self.setWindowTitle("Editor")

    def actionSave(self):
        title=QApplication.translate("BoundingDialog","Save entity")
        QMessageBox.information(self,title,QApplication.translate("BoundingDialog","information save successfully"))
        
    
class STDMEntityForm(object):
    def __init__(self,table,cols,parent):
        self.Session = STDMDb.instance().session
        self.cols=cols
        self.parent=parent
               
        self.list_display_columns = self.cols
        self.search_columns = ['id']
        self.key_column = table.id
    
        self.table_cls = table
        self.key_column = self.key_column
        self.list_display_columns = self.cols
        self.list_search_columns = self.cols

    def view_row(self,row):
        form = STDMForm(self.parent,self.table_cls,self.list_display_columns,Session=self.Session,row=row)
        form.show() 
        form.exec_()
        #self.Session.close()

 
    itemCommands = CommandMenu('_item_commands')
    @itemCommands.itemAction("&Edit...", default=True, iconFile=":qtalchemy/default-edit.ico")
    def view(self, row):
        try:
            #session, aa = self.session_entity(self.Session,self.table_cls,row)
            aa = self.Session.query(self.table_cls).filter(self.key_column==row.id).one()
            self.view_row(aa)
        except SQLAlchemyError as ex:
            QMessageBox.information(None,QApplication.translate("Dialog","Add data"),str(ex.message))
   
    @itemCommands.itemNew()
    def new(self, row):
        try:
            #session = self.Session()
            aa=self.table_cls()
            self.Session.add(aa)
            self.view_row(aa)
            
        except SQLAlchemyError as ex:
            QMessageBox.information(None,QApplication.translate("Dialog","Add data"),ex.message)
            
    @itemCommands.itemDelete()
    def delete(self, row):
        try:
            aa = self.Session.query(self.table_cls).filter(self.key_column==row.id).one()
            self.Session.delete(aa)
            self.Session.commit()
            self.Session.close()
            QMessageBox.information(None,QApplication.translate("Dialog","Delete Row"),
                                    QApplication.translate("Dialog","Current selection deleted from database"))
        except SQLAlchemyError as ex:
            QMessageBox.information(None,QApplication.translate("Dialog","Add data"),ex.message)
            

