# -*- coding: utf-8 -*-
"""
/***************************************************************************
 stdm
                                 A QGIS plugin
 Securing land and property rights for all
                              -------------------
        begin                : 2014-03-04
        copyright            : (C) 2014 by GLTN
        email                : njoroge.solomon@yahoo.com
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
from qtalchemy.dialogs import *
from qtalchemy.widgets import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from sqlalchemy.orm import *
from .data_reader_form import STDMEntity, STDMDb,STDMEntityForm

from qtalchemy.ext.dataviews import BasicQueryManager


class ContentView(QDialog, MapperMixin):
    def __init__(self,parent,table,cols,row=None,Session=None,row_id=None, flush=True):
        QDialog.__init__(self,parent)
        MapperMixin.__init__(self)
        self.session=Session
        self.table=table               
        self.cols=cols
        title=str(self.table).capitalize()
        
        self.table=str(self.table).capitalize()
        #self.setWindowTitle("{0}".format(table))
        
#         #Window resize
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        width=int((screen.width()-size.width())/2)
        height=int((screen.height()-size.height())/2)
        self.move(width,height)
        self.setGeometry(QRect(width/2,(screen.height())/4, width, height))
        
        main = QVBoxLayout(self)
        self.toolbar = LayoutWidget(main, QToolBar())
        
        #self.tableView = LayoutWidget(main, TableView(extensionId=suffixExtId(self,"Table")))
        self.tableView = LayoutWidget(main, TableView())
        '''user can use table column to sort the data, ....'''
        self.Combo = LayoutWidget(main, QComboBox())
        self.refreshBtn = LayoutWidget(main, QLineEdit("Search"))
        if 'id' in self.cols:
            self.cols.remove('id')
        self.Combo.insertItems(0, self.cols)
        
        self.query=self.session.query(table)
        self.model=QueryTableModel(self.query, self.cols,self.session)
        '''need to implement data sorting proxy'''
        
        proxy=QSortFilterProxyModel()
        proxy.setSourceModel(self.model)
        
        self.tableView.setModel(self.model)
        proxy.setFilterKeyColumn(1) 
        self.tableView.setSortingEnabled(True)
        self.tableView.sortByColumn(1,Qt.AscendingOrder)
       
        self.entity = STDMEntityForm(table,self.cols,self)
        self.binding = self.entity.itemCommands.withView(self.tableView, bindDefault=True)
        self.binding.fillToolbar(self.toolbar)
        self.binding.preCommand.connect(self.preCommandSave)
        self.binding.refresh.connect(self.refresh)
               
        self.tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        self.main=table()
        self.load()
    
    def load(self):
        self.submit()
       # self.setWindowTitle("{0}".format(t))
    
    def refresh(self,item):
        #Not sure whether this is necessary but how do we refresh the data
        if self.tableView.model() is not None:
            self.model=QueryTableModel(self.query, self.cols,self.session)
            self.tableView.setModel(self.model)
            self.tableView.model().reset_content_from_session()
            
    def preCommandSave(self,id=None):
        #Not very sure, how to be friendly with the user feedback
        pass
   
    def sortSelection(self,index):
        pass
       
        