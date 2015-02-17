'''
Created on Mar 28, 2014

@author: njogus
'''
from PyQt4.QtGui import *
from PyQt4.QtCore import *

ALT_COLOR_EVEN = QColor(183, 100, 102)
ALT_COLOR_ODD = QColor(135,206,255)

itemIcon = QIcon(":/plugins/stdm/images/icons/table.png")

class listEntityViewer(QAbstractListModel):
    def __init__(self, list=[], icon =None, parent=None):
        QAbstractListModel.__init__(self,parent)
        self.__list=list
        self._icon = icon
     
    def headerData(self,section, orientation, role):
        if role==Qt.DisplayRole:
            if orientation==Qt.Vertical:
               return  section
            elif orientation == Qt.Horizontal:
                return "STDM Entities"
            else:
                return "Entities"
        
    def rowCount(self,parent):
        return len(self.__list)
    
    def data(self,index,role):
        if role==Qt.ToolTipRole:
            return  self.__list[index.row()]
        
        if role==Qt.EditRole:
            row=index.row()
            return self.__list[row]
                   
        if role==Qt.DecorationRole:
            if self._icon is not None:
                return self._icon
            else:
                return itemIcon
        
        if role==Qt.DisplayRole:
            row=index.row()
            return self.__list[row]
        if role == Qt.BackgroundRole:
            if index.row() % 2 == 0:
                #Orange
                return ALT_COLOR_EVEN
            else:
                #Blue
                return ALT_COLOR_ODD
            
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsEditable|Qt.ItemIsSelectable|Qt.ItemIsEnabled
     
    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and role == Qt.EditRole:                        
            self.__list[index.row()] = value            
            self.dataChanged.emit(index,index)
            return True
        else:
            return False
            
    def insertRows(self, position,rows,parent):
        if position < 0:
            return False    
        self.beginInsertRows(parent, position, position + rows - 1)
        for i in range(rows):            
            self.__list.insert[position]
        self.endInsertRows()
        
    def removeRows(self, rows,count, parent=QModelIndex):
        if rows < 0 or rows > len(self.__list):
            return
        self.beginRemoveRows(parent,rows,count- 1)
        while count != 0:
            del self.__list[rows]
            count -= 1
        self.endRemoveRows()
        

class EntityColumnModel(QAbstractTableModel):
    def __init__(self, header,data, parent=None):
        QAbstractTableModel.__init__(self,parent)
        self._data=data
        self._header=header
               
    def headerData(self,col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._header[col]
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return col+1
        
    def rowCount(self,parent):
        return len(self._data) 
    
    def columnCount(self, parent):
        #return len(self.__list)
        return len(self._header)
    
    def data(self,index,role):
        if not index.isValid():
            return QPyNullVariant
        elif role == Qt.EditRole:
            return self._data[index.row()][index.column()]
        
        if role==Qt.ToolTipRole:
            return  self._data[index.row()][index.column()]
              
        if role==Qt.DecorationRole:
            return self._data[index.row()][index.column()]

        if role==Qt.DisplayRole:
            return self._data[index.row()][index.column()]
        if role == Qt.BackgroundRole:
            if index.row() % 2 == 0:
                #Orange
                return ALT_COLOR_EVEN
            else:
                #Blue
                return ALT_COLOR_ODD
        
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsEditable|Qt.ItemIsSelectable|Qt.ItemIsEnabled
    
    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and role == Qt.EditRole:            
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index,index)
            return True
        return False   
                        
    def insertRows(self,position,rows,parent = QModelIndex()):
        if position < 0 or position > len(self._data):
            return False
                
        self.beginInsertRows(parent, position, position + rows - 1)
        
        for i in range(rows):
            self._data.insert(position,["","","","",""])
        
        self.endInsertRows()
        return True

    def removeRows(self, position,rows, parent=QModelIndex):
        if position < 0 or position > len(self._data):
            return False
        self.beginRemoveRows(parent,position,position + rows - 1)
        for i in range(count):            
            del self._data[position]
        self.endRemoveRows()
        return True
