'''
Created on Mar 28, 2014

@author: njogus
'''
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from stdm.settings import tableIcon


ALT_COLOR_EVEN = QColor(209, 243, 249)
ALT_COLOR_ODD = QColor(241,246,245)

class CheckableListModel(QStandardItemModel):
    def __init__(self, list, icon = None, parent = None):
        QStandardItemModel.__init__(self,parent)
        self.__list = list
        self._icon = icon

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        if self.__list is not None:
            return len(self.__list)
        else:
            return 0

    def setCheckable(self, bool, table = None):
        self._icon =tableIcon
        checkableItems = []
        for text in self.__list:
            item = QStandardItem()
            item.setCheckable(bool)
            item.setCheckState(Qt.Unchecked)
            item.setText(text)
            item.setIcon(self._icon)
            checkableItems.append(item)
        self.appendColumn(checkableItems)

class listEntityViewer(QAbstractListModel):
    """
    Class implementation of list model properties from a python list type
    """
    def __init__(self, list=[], icon =None, parent=None):
        QAbstractListModel.__init__(self,parent)
        self.__list = list
        self._icon = icon
     
    def headerData(self,section, orientation, role):
        if role==Qt.DisplayRole:
            if orientation==Qt.Vertical:
                return  section
            elif orientation == Qt.Horizontal:
                return QApplication.translate("WorkspaceLoader","STDM Entities")
            else:
                return QApplication.translate("WorkspaceLoader","Entities")
        
    def rowCount(self,parent=QModelIndex):
        if self.__list is not None:
            return len(self.__list)
        else:
            return 0
    
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
                return tableIcon
        
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
    """
    Class implementation of table model for representating table columns
    """
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
