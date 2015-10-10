"""
/***************************************************************************
Name                 : PyQT Models
Description          : Contains entity models for using in PyQt widgets 
                       for those controls implementing the Model/View 
                       framework                        
Date                 : 4/June/2013 
opyright             : (C) 2014 by UN-Habitat and implementing partners.
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

from decimal import Decimal

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from modelformatters import LookupFormatter, DoBFormatter

#Standard colors for widgets supporting alternating rows
ALT_COLOR_EVEN = QColor(255,165,79)
ALT_COLOR_ODD  = QColor(135,206,255)
 
class EnumeratorTableModel(QAbstractTableModel):
    '''
    Model for displaying enumerators in a tableview
    '''
    def __init__(self, enum_data, header_data, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.enum_data = enum_data
        self.header_data = header_data
        
    def rowCount(self, parent=QModelIndex()):
        return len(self.enum_data)
    
    def columnCount(self, parent):
        return 4
    
    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role == Qt.DisplayRole or role == Qt.EditRole:
            return QVariant(self.enumdata[index.row()][index.column()])
        elif role == Qt.BackgroundRole:
            if index.row() % 2 == 0:
                #Orange
                return QVariant(ALT_COLOR_EVEN)
            else:
                #Blue
                return QVariant(ALT_COLOR_ODD)
        else:            
            return QVariant()
    
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.headerdata[col])
        return QVariant()
    
    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and role == Qt.EditRole:            
            self.enum_data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        
        return False    
    
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsEditable|Qt.ItemIsSelectable|Qt.ItemIsEnabled
    
    def insertRows(self, position, rows, parent=QModelIndex()):
        if position < 0 or position > len(self.enumdata):
            return False
                
        self.beginInsertRows(parent, position, position + rows - 1)
        
        for i in range(rows):
            self.enum_data.insert(position, ["","","",""])
        
        self.endInsertRows()
        
        return True
    
class DepartmentTableModel(QAbstractTableModel):
    '''
    Model for displaying departments in a tableview
    '''
    def __init__(self, department_data, header_data, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.dpt_data = department_data
        self.header_data = header_data
        
    def rowCount(self, parent=QModelIndex()):
        return len(self.dpt_data)
    
    def columnCount(self, parent=QModelIndex()):
        return 3
    
    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role == Qt.DisplayRole or role == Qt.EditRole:
            return QVariant(self.dptdata[index.row()][index.column()])
        elif role == Qt.BackgroundRole:
            if index.row() % 2 == 0:
                #Orange
                return QVariant(ALT_COLOR_EVEN)
            else:
                #Blue
                return QVariant(ALT_COLOR_ODD)
        else:            
            return QVariant()
    
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.header_data[col])
        return QVariant()
    
    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and role == Qt.EditRole:            
            self.dpt_data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        
        return False    
    
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsEditable|Qt.ItemIsSelectable|Qt.ItemIsEnabled
    
    def insertRows(self, position, rows, parent=QModelIndex()):
        if position < 0 or position > len(self.dptdata):
            return False
                
        self.beginInsertRows(parent, position, position + rows - 1)
        
        for i in range(rows):
            self.dpt_data.insert(position, ["","","",""])
        
        self.endInsertRows()
        
        return True
        
    def removeRows(self, position, count, parent=QModelIndex()):
        if position < 0 or position > len(self.dptdata):
            return False
        
        self.beginRemoveRows(parent, position, position + count - 1)
        
        for i in range(count):            
            del self.dpt_data[position]
            
        self.endRemoveRows()
        
        return True    

class QuestionnaireTableModel(QAbstractTableModel):
    '''
    Model for use in the questionnaire table view
    '''
    def __init__(self, questionnaire_data, header_data, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.quest_data = questionnaire_data
        self.header_data = header_data
        self._wkformatter = WorksiteFormatter()
        self._enumformatter = InvestigatorFormatter()
        self._respformatter = RespondentFormatter()
        
    def rowCount(self, parent = QModelIndex()):
        return len(self.quest_data)
    
    def columnCount(self, parent=QModelIndex()):
        return 8
    
    def data(self, index, role):
        
        index_data = self.quest_data[index.row()][index.column()]
        
        if not index.isValid():
            return QVariant()
        
        elif role == Qt.DisplayRole:
            
            col = index.column()                        
            #Specify formatters for columns with 
            if col == 4: 
                #Worksite formatter               
                return self._wkformatter.set_display(index_data) 
            elif col == 5:
                #Enumerator formatter
                return self._enumformatter.set_display(index_data) 
            elif col == 6:
                return self._respformatter.set_display(index_data)           
            else:
                return QVariant(index_data)
        
        #For columns representing foreign keys then we need to pass the integer value to the editor    
        elif role == Qt.EditRole:
            return QVariant(index_data)
            
        elif role == Qt.BackgroundRole:
            if index.row() % 2 == 0:
                #Orange
                return QVariant(ALT_COLOR_EVEN)
            else:
                #Blue
                return QVariant(ALT_COLOR_ODD)
            
        else:            
            return QVariant()
    
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.header_data[col])
        return QVariant()
    
    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and role == Qt.EditRole:                        
            self.quest_data[index.row()][index.column()] = value            
            self.dataChanged.emit(index, index)
            return True
        
        return False    
    
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsEditable|Qt.ItemIsSelectable|Qt.ItemIsEnabled
    
    def insertRows(self, position, rows, parent=QModelIndex()):
        if position < 0 or position > len(self.quest_data):
            return False
                
        self.beginInsertRows(parent, position, position + rows - 1)
        
        #Initialize column values for the new row
        init_row_vals = ["" for c in range(self.columnCount())]
        
        for i in range(rows):            
            self.quest_data.insert(position, init_row_vals)
        
        self.endInsertRows()
        
        return True
        
    def removeRows(self, position, count, parent=QModelIndex()):
        if position < 0 or position > len(self.quest_data):
            return False
        
        self.beginRemoveRows(parent, position, position + count - 1)
        
        for i in range(count):            
            del self.quest_data[position]
            
        self.endRemoveRows()
        
        return True
    
class UsersRolesModel(QAbstractListModel):
    """
    Model for showing existing system users/roles/contents in a QListView
    """
    def __init__(self, users):
        QAbstractListModel.__init__(self)

        #Cache the users
        self._users = users

    def rowCount(self, parent=QModelIndex()):
        return len(self._users)

    def data(self,index,role = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self._users[index.row()]

        elif role == Qt.FontRole:
            lst_font = QFont("Segoe UI", 10)
            return lst_font
        else:
            return None
        
    def insertRows(self, position, rows, parent=QModelIndex()):
        if position < 0 or position > len(self._users):
            return False
                
        self.beginInsertRows(parent, position, position + rows - 1)
        
        for i in range(rows):            
            self._users.insert(position,"")
        
        self.endInsertRows()
        
        return True
        
    def removeRows(self, row, count, parent=QModelIndex()):
        if row < 0 or row > len(self._users):
            return
        
        self.beginRemoveRows(parent, row, row + count - 1)
        while count != 0:
            del self._users[row]
            count -= 1
        self.endRemoveRows()
        
    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and role == Qt.EditRole:                        
            self._users[index.row()] = value            
            self.dataChanged.emit(index,index)
            return True
        
        return False 
    
class PersonTableModel(QAbstractTableModel):
    '''
    Model for use in the Person table view
    '''
    def __init__(self, person_data, header_data, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.person_data = person_data
        self.header_data = header_data   
        self._gender_formatter = LookupFormatter(CheckGender)
        self._mStat_formatter = LookupFormatter(CheckMaritalStatus) 
        self._age_formatter = DoBFormatter()
        
    def rowCount(self, parent = QModelIndex()):
        return len(self.person_data)
    
    def columnCount(self, parent=QModelIndex()):
        return 11
    
    def data(self, index, role):
        
        index_data = self.person_data[index.row()][index.column()]
        
        if not index.isValid():
            return QVariant()
        
        elif role == Qt.DisplayRole:            
            col = index.column()    
                                
            #Specify formatters for columns whose values are foreign keys            
            if col == 5:
                #Gender formatter
                return self._gender_formatter.set_display(index_data) 
            
            elif col == 6:                        
                #Current age calculation
                return self._age_formatter.set_display(index_data)
            
            elif col == 7:
                return self._mStat_formatter.set_display(index_data) 
                      
            else:
                return QVariant(index_data)
        
        #For columns representing foreign keys then we need to pass the integer value to the editor    
        elif role == Qt.EditRole:
            #Create QDate from Python date then pass it to QVariant constructor where applicable            
            if index.column() == 6: 
                
                if isinstance(index_data, QVariant):        
                    return QVariant(index_data)                 
                else:                                             
                    return QVariant(QDate(index_data))                                             
                               
            else:
                return QVariant(index_data)
            
        elif role == Qt.BackgroundRole:
            if index.row() % 2 == 0:
                #Orange
                return QVariant(ALT_COLOR_EVEN)
            else:
                #Blue
                return QVariant(ALT_COLOR_ODD)
            
        else:            
            return QVariant()
    
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.headerdata[col])
        return QVariant()
    
    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and role == Qt.EditRole:                                   
            self.person_data[index.row()][index.column()] = value            
            self.dataChanged.emit(index,index)
            return True
        
        return False    
    
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        
        return Qt.ItemIsEditable|Qt.ItemIsSelectable|Qt.ItemIsEnabled
    
    def insertRows(self, position, rows, parent=QModelIndex()):
        if position < 0 or position > len(self.person_data):
            return False
                
        self.beginInsertRows(parent, position, position + rows - 1)
        
        #Initialize column values for the new row
        init_row_vals = ["" for c in range(self.columnCount())]
        
        for i in range(rows):            
            self.person_data.insert(position, init_row_vals)
        
        self.endInsertRows()
        
        return True
        
    def removeRows(self, position, count, parent=QModelIndex()):
        if position < 0 or position > len(self.person_data):
            return False
        
        self.beginRemoveRows(parent, position, position + count - 1)
        
        for i in range(count):            
            del self.person_data[position]
            
        self.endRemoveRows()
        
        return True
    
class BaseSTDMTableModel(QAbstractTableModel):
    """
    Generic table model for use in STDM table views.
    """
    def __init__(self, init_data, header_data, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._init_data = init_data
        self._header_data = header_data 
        
    def rowCount(self, parent=QModelIndex()):
        return len(self._init_data)
    
    def columnCount(self, parent=QModelIndex()):
        return len(self._header_data)
    
    def data(self, index, role):
        
        index_data = self._init_data[index.row()][index.column()]
        
        if not index.isValid():
            return None
        
        elif role == Qt.DisplayRole:   
            #Decimal not supported by QVariant so we adapt it to a supported type
            if isinstance(index_data, Decimal):
                return str(index_data)    
            else:
                return index_data
    
        else:            
            return None

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._header_data[section]

        elif orientation == Qt.Vertical and role == Qt.DisplayRole:
            return section + 1
        
        return None
    
    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and role == Qt.EditRole:                                   
            self._init_data[index.row()][index.column()] = value            
            self.dataChanged.emit(index, index)
            return True
        
        return False    
    
    def flags(self,index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        
        return Qt.ItemIsEditable|Qt.ItemIsSelectable|Qt.ItemIsEnabled
    
    def insertRows(self, position, rows, parent=QModelIndex()):
        if position < 0 or position > len(self._init_data):
            return False
                
        self.beginInsertRows(parent, position, position + rows - 1)
        
        #Initialize column values for the new row
        init_row_vals = ["" for c in range(self.columnCount())]
        
        for i in range(rows):            
            self._init_data.insert(position, init_row_vals)
        
        self.endInsertRows()
        
        return True
        
    def removeRows(self, position, count, parent=QModelIndex()):
        if position < 0 or position > len(self._init_data):
            return False
        
        self.beginRemoveRows(parent, position, position + count - 1)
        
        for i in range(count):            
            del self._init_data[position]
            
        self.endRemoveRows()
        
        return True

class VerticalHeaderSortFilterProxyModel(QSortFilterProxyModel):
    """
    A sort/filter proxy model that ensures row numbers in vertical headers
    are ordered correctly.
    """

    def headerData(self, section, orientation, role):
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return section + 1

        return super(VerticalHeaderSortFilterProxyModel, self).headerData(section, orientation, role)

class STRTreeViewModel(QAbstractItemModel):
    """
    Model for rendering social tenure relationship nodes in a tree view.
    """
    def __init__(self, root, parent=None, view=None):
        QAbstractItemModel.__init__(self,parent)
        self._root_node = root
        self._view = view

    def rowCount(self, parent):
        if not parent.isValid():
            parent_node = self._root_node

        else:
            parent_node = parent.internalPointer()

        return parent_node.childCount()

    def columnCount(self, parent=QModelIndex()):
        return self._root_node.columnCount()

    def _getNode(self,index):
        """
        Convenience method for extracting STRNodes from the model index.
        """
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node

        return self._root_node

    def data(self, index, role):
        """
        Data to be displayed in the tree view.
        """
        if not index.isValid():
            return None

        node = self._getNode(index)

        if role == Qt.DisplayRole or role == Qt.EditRole:
            if index.column() >= node.columnCount():
                return None

            return node.data(index.column())

        elif role == Qt.DecorationRole:
            if index.column() == 0:
                if not node.icon() is None and node.depth() > 1:
                    return node.icon()

        elif role == Qt.FontRole:
            if index.column() == 0:
                if node.styleIfChild():
                    if self._view is not None:
                        curr_font = self._view.font()
                        curr_font.setBold(True)
                        return curr_font

        elif role == Qt.ToolTipRole:
            if index.column() >= node.columnCount():
                return None

            return node.data(index.column())

        else:
            return None

    def headerData(self, section, orientation, role):
        """
        Set the column headers to be displayed by the tree view.
        """
        if self._rootNode.columnCount() == 0:
            return

        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._root_node.data(section)

        elif orientation == Qt.Vertical and role == Qt.DisplayRole:
            return section + 1

        return None

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable

    def parent(self, index):
        """
        Returns a QModelIndex reference of the parent node.
        """
        if not index.isValid():
            return QModelIndex() 
        
        node = self._getNode(index)
        
        parent_node = node.parent()
        
        if parent_node == self._root_node or parent_node == None:
            return QModelIndex()
        
        return self.createIndex(parent_node.row(), 0, parent_node)
    
    def index(self, row, column, parent):
        if parent.isValid() and parent.column() != 0:
            return QModelIndex()
        
        parent_node = self._getNode(parent)
        
        child_item = parent_node.child(row)
        
        if child_item:
            return self.createIndex(row, column, child_item)
        else:
            return QModelIndex()
        
    def removeAllChildren(self, position, count, parent=QModelIndex()):
        """
        Removes all children under the node with the specified parent index.
        """
        parent_node = self._getNode(parent)
        success = True
        
        self.beginRemoveRows(parent, position, position + count - 1)
        
        success = parent_node.clear()
          
        self.endRemoveRows()
        
        return success
        
    def removeRows(self, position, count, parent=QModelIndex()):
        """
        Removes count rows starting with the given position under parent from the model.
        """
        parent_node = self._getNode(parent)
        success = True
        
        self.beginRemoveRows(parent, position, position + count - 1)
        
        for row in range(count):
            success = parent_node.removeChild(position)
          
        self.endRemoveRows()
        
        return success
    
    def insertRows(self, position, count, parent=QModelIndex()):
        """
        Insert children starting at the given position for the given parent item.
        """
        parent_node = self._getNode(parent)
        success = True
        
        self.beginInsertRows(parent, position, position + count -1)
        
        '''
        We do not insert any children in this case since the internal methods of the
        conflict node have already inserted the children nodes that contain the 
        information.
        '''
        
        self.endInsertRows()
        
        return success
    
    def removeColumns(self, position, column_count, parent=QModelIndex()):
        success = True
        
        self.beginRemoveColumns(parent, position, position + column_count-1)
        success = self._root_node.removeColumns(position, column_count)
        self.endRemoveColumns()
        
        if self._root_node.column_count() == 0:
            self.removeRows(0, self.rowCount())
        
        return success
    
    def clear(self):
        """
        Removes all items (rows and columns) in the model.
        """
        root_children_num = self._root_node.childCount()
        
        self.beginResetModel()
        
        #Delete each child individually then clear the root node or else there will be indexing issues
        for i in range(root_children_num):
            child_node = self._root_node.child(i)
            child_node._parent = None
            del child_node
                       
        self._root_node.clear()
        #TODO: Clear columns
        self.endResetModel()
        
    def setData(self, index, value, role):
        """
        Sets the role data for the item at index to value.
        """
        if role == Qt.EditRole or role == Qt.DisplayRole:
            node_item = self._getNode(index)
            result = nodeItem.setData(index.column(), value)

            if result:
                self.dataChanged.emit(index, index)

            return result

        return False
<<<<<<< HEAD
        
        
        
        
        
        
        
        
        
        
    
     
            
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
=======
>>>>>>> Peped data/qtmodels
