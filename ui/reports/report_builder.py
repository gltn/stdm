"""
/***************************************************************************
Name                 : STDM Report Builder - LEGACY CODE, NEEDS UPDATE
Description          : Report Builder Dialog
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
import os

import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

from stdm.utils import *
from stdm.data.reports import (
                               STDMReport,
                               STDMGenerator,
                               ReportElements, 
                                STDMReportConfig, 
                                ReportSerializer,
                                DbField, 
                                FieldConfig, 
                                GroupSettings, 
                                SortDir, 
                                FieldSort
                                )
from stdm.data import (
                       table_column_names,
                       unique_column_values,
                       pg_tables,
                       pg_views,
                       process_report_filter
                       )

from stdm.ui.customcontrols import TableComboBox
'''
from stdm.workspace.defaultSetting.config import dbTableConfig
from stdm.workspace.defaultSetting.map_query import CertificateMap
'''
from .report_title_base import TitleBase
from .field_base import FieldBase
from .report_title import Title
from .field_names import FieldNames
from .groups import Groups
from .report_layout import ReportLayout
from .highlighter import SqlHighlighter
from stdm.data import pg_views

from .ui_rpt_builder import Ui_ReportBuilder

class ReportBuilder(QDialog, Ui_ReportBuilder):   
    def __init__(self, config, parent=None): 
        QDialog.__init__(self, parent)
        
        self.setupUi(self)
        
        #Disable supporting tabs
        self.enable_supporting_tabs(False)
        
        #Dynamic class for placing report elements
        self.rpt_elements = ReportElements()
        
        #Get instance of config object    
        self.config = config
        self.progress_dlg = QProgressDialog(self)
        
        #Event handlers
        #Fields Section
        self.btnRptCancel.clicked.connect(self.close)
        self.btnSave.clicked.connect(self.save_report)
        self.btnLoad.clicked.connect(self.load_report)
        self.comboBox.currentIndexChanged[int].connect(self.tab_changed)
        self.btnAddField.clicked.connect(self.add_report_fields)
        self.btnAddAllFields.clicked.connect(self.add_all_fields)
        self.btnRemField.clicked.connect(self.rem_report_fields)
        self.btnRemAllFields.clicked.connect(self.rem_all_fields)
        self.btnUniqVals.clicked.connect(self.fields_get_unique_vals)
        
        #Filter Section
        self.lstFields.itemDoubleClicked.connect(self.filter_insert_rpt_fields)
        self.lstUniqVal.itemDoubleClicked.connect(self.filter_insert_rpt_fields)
        self.btnOpEqual.clicked.connect(self.filter_insert_eq)
        self.btnOpNotEqual.clicked.connect(self.filter_insert_not_eq)
        self.btnOpLike.clicked.connect(self.filter_insert_like)
        self.btnOpGreater.clicked.connect(self.filter_greater_than)
        self.btnOpGreaterEq.clicked.connect(self.filter_greater_eq)
        self.btnOpAnd.clicked.connect(self.filter_insert_and)
        self.btnOpLess.clicked.connect(self.filter_insert_less)
        self.btnOpLess_2.clicked.connect(self.filter_insert_lessEq)
        self.btnOpOr.clicked.connect(self.filter_insert_or)
        self.btnSQLClr.clicked.connect(self.filter_clear_text)
        self.btnSQLVer.clicked.connect(self.filter_verify_query)    
        self.btnGenRpt.clicked.connect(self.generate_report)  
        
        #Display Section
        #self.lblTitleClr.clicked.connect(self.display_title_color)
        self.trRptSettings.itemSelectionChanged.connect(self.display_tree_view_selection)
        
        #Grouping section
        self.btnAddGpField.clicked.connect(self.grouping_add_field)
        self.btnRemGpField.clicked.connect(self.grouping_remove_field)
        
        #Show on Map
        self.btnMap.clicked.connect(self.map_query_from_filter)
        #Initialize dialog with table names
        self.init_rpt_dialog()   
    
    def init_rpt_dialog(self):
        #Initialize the dialog with table names
        self.tab_names = self.config
        user_views = pg_views()
        if user_views:
            for view_name in user_views:
                self.config[view_name.title()] = view_name
        self.tab_names['Social Tenure Relationship'] = 'social_tenure_relations'
        try:
            for name, value in self.config.iteritems():
                self.comboBox.addItem(name, value)
            index = self.comboBox.findText('Social_Tenure_Relations', Qt.MatchExactly)
            if index:
                self.comboBox.removeItem(int(index))
        except Exception as ex:
            self.error_info_message(str(ex.message))
        self.init_stack_widgets()
        
        #Sorting
        self.tbSortFields.verticalHeader().setVisible(False) 
        self.tbSortFields.setAlternatingRowColors(True)
        self.tbSortFields.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        #Fields
        self.listWidget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.listWidget_2.setSelectionMode(QAbstractItemView.MultiSelection)
        
        #General
        self.btnGenRpt.setEnabled(False)
        self.btnSave.setEnabled(False)
        
        #Display
        self.trRptSettings.expandAll()
        
        #Filter
        self.txtSqlParser.setWordWrapMode(QTextOption.WordWrap)
        sqlHL = SqlHighlighter(self.txtSqlParser)
        
        #Grouping
        #Hide inapplicable columns
        self.tbGroupFields.verticalHeader().setVisible(False) 
        self.tbGroupFields.setAlternatingRowColors(True)
        self.tbGroupFields.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        self.init_vars()
    
    def init_vars(self):
        #Initialize data variables   
        self._sortOrder = 0
    
    def init_stack_widgets(self):
        #Instantiate new report display widgets
        title_widgets=["Title"]
        for t in title_widgets:
            stWidg = Title(t)   
            self.stackedWidget.addWidget(stWidg)  
            
        #Add Field Names Widget
        fn_widget = FieldNames(QApplication.translate("ReportBuilder", "Field Names"))
        self.stackedWidget.addWidget(fn_widget)
        
        #Add Layout Tree Node (Under Elements parent node)
        el_elements = self.trRptSettings.findItems(QApplication.translate
                                                   ("ReportBuilder", "Elements"), Qt.MatchExactly, 0)
        if len(el_elements) > 0:
            el_node = el_elements[0]
            lyt_txt = QApplication.translate("ReportBuilder","Layout")
            layout_node = QTreeWidgetItem([lyt_txt])
            el_node.addChild(layout_node)

            #Add Layout Widget
            layout_widget = ReportLayout(lyt_txt)
            self.stackedWidget.addWidget(layout_widget)

            #Select the first item in the tree view
            title_node = el_node.child(0)
            title_node.setSelected(True)

    def reset_controls(self):
        #Reset widgets
        self.listWidget_2.clear()
        self.listWidget.clear()
        self.enable_supporting_tabs(False)
        self.txtSqlParser.clear()
        self.lstUniqVal.clear()
        self.lstFields.clear()
        self.grouping_cleanup_fields()
        self.lstRptFields.clear()  
        self.display_update_report_fields() 
        self.sorting_update_report_fields()  
        self.init_vars()  
    
    def tab_changed(self, item_index):
        #Handler when the table names' combo box items changes    
        self.tabFields=[]
        self.rptFields=[]
        self.reset_controls()
        self.load_tab_fields(item_index)
        self.select_avail_field_item()
    
    def enable_supporting_tabs(self, status):
        '''
        Enable/Disable other tabs only when the report fields
        have been defined by the user
        '''
        self.tab_2.setEnabled(status)
        self.tab_3.setEnabled(status)
        self.tab_4.setEnabled(status)
        self.tab_5.setEnabled(status)
        self.btnGenRpt.setEnabled(status)
        self.btnSave.setEnabled(status)
    
    def load_tab_fields(self, combo_item_index):
        #Load the associated fields from  specified table name
        if isinstance(combo_item_index, str) or isinstance(combo_item_index, unicode):
            combo_item_index = self.comboBox.findData(combo_item_index)

            if combo_item_index == -1:
                QMessageBox.critical(self, QApplication.translate("ReportBuilder", "Report Error"),
                                        QApplication.translate("ReportBuilder","Table does not exist in the drop-down list"))
                return
        self.tabName = self.comboBox.itemData(combo_item_index)
        self.tabFields = table_column_names(self.tabName)
        self.listWidget.addItems(self.tabFields) 
        
        #Set table name in the Fields Query Builder
        self.lblSqlEntity.setText("Select * FROM " + self.tabName + " WHERE:")   
    
    def add_report_fields(self, select_all=False):
        # get selected fields and add to the report collection
        sel_fields = []
        if select_all:
            for i in range(self.listWidget.count()):
                lst_item = self.listWidget.item(i)
                sel_fields.append(lst_item.text())   
        else:        
            sel_items = self.listWidget.selectedItems()
            for sel_item in sel_items:
                sel_fields.append(sel_item.text())
        self.update_selected_report_fields(sel_fields)

    def update_selected_report_fields(self, rpt_fields):
        #Updates the user defined report fields
        for rf in rpt_fields:
            self.rptFields.append(rf)
            self.tabFields.remove(rf)            
        self.update_field_views()
    
    def rem_report_fields(self, select_all=False):
        #Remove items from the report collection
        sel_fields = []
        if select_all:
            for i in range(self.listWidget_2.count()):
                lst_item = self.listWidget_2.item(i)
                sel_fields.append(lst_item.text())   
        else:    
            sel_items=self.listWidget_2.selectedItems()
            for sel_item in sel_items:
                sel_fields.append(sel_item.text())
                
        for sf in sel_fields:           
            self.rptFields.remove(sf)
            self.tabFields.append(sf)            
        
        self.update_field_views()
    
    def select_avail_field_item(self, index=0):
        #Select an item in available fields view
        if index==0:
            sel_item=self.listWidget.item(0)
            self.listWidget.setCurrentItem(sel_item)
        
    def load_rpt_fields_widgets(self):
        '''
        Populate report fields widgets defined in the supporting
        tabs
        '''
        self.reload_rpt_list_widgets(self.lstFields)
        self.reload_rpt_list_widgets(self.lstRptFields)
        self.grouping_cleanup_fields()  
        self.display_update_report_fields() 
        self.sorting_update_report_fields()
    
    def reload_rpt_list_widgets(self, lst_widget_obj):
        #clear and reload report fields widgets
        lst_widget_obj.clear()
        lst_widget_obj.addItems(self.rptFields)
  
    def add_all_fields(self):
        #Handler when the add all fields button is clicked
        self.add_report_fields(True)
    
    def rem_all_fields(self):
        #Handler when the remove all report fields button is clicked
        self.rem_report_fields(True)
  
    def update_field_views(self):
        #Update the available and report fields' widgets
        self.listWidget.clear()
        self.listWidget.addItems(self.tabFields)
        self.listWidget_2.clear()
        self.listWidget_2.addItems(self.rptFields)
        '''
        Check if the report fields have been defined
        and enable the supporting tabs
        '''
        if len(self.rptFields)>0:
            self.enable_supporting_tabs(True)
            self.load_rpt_fields_widgets()
        else:
            self.enable_supporting_tabs(False)        
        
    def fields_get_unique_vals(self):
        #Raised when the get unique values button is clicked
        sel_items = self.lstFields.selectedItems()
        if len(sel_items)>0:
            column_name = sel_items[0].text()
            self.fields_load_unique_vals(self.tabName, str(column_name))
        
    def fields_load_unique_vals(self, table_name, column_name):
        #Get unique column values and load the list
        unique_vals = unique_column_values(table_name, column_name)
        self.lstUniqVal.clear()
        self.lstUniqVal.addItems(unique_vals)
        self.lstUniqVal.sortItems()    
    
    def filter_clear_text(self):
        #Deletes all the text in the text edit
        self.txtSqlParser.clear()
    
    def filter_insert_rpt_fields(self, lst_item):
        '''
        Inserts the clicked report field item into the
        SQL parser text edit.
        '''
        self.txtSqlParser.insertPlainText(lst_item.text())    
    
    def filter_insert_eq(self):
        #Insert Equal operator
        self.txtSqlParser.insertPlainText(" = ")
     
    def filter_insert_not_eq(self):
        #Insert Not Equal to
        self.txtSqlParser.insertPlainText(" <> ")
    
    def filter_insert_like(self):
        #Insert LIKE operator
        self.txtSqlParser.insertPlainText(" LIKE ")
    
    def filter_greater_than(self):
        #Insert greater than
        self.txtSqlParser.insertPlainText(" > ")
    
    def filter_greater_eq(self):
        #Insert Greater than or equal to
        self.txtSqlParser.insertPlainText(" >= ")
    
    def filter_insert_and(self):
        #Insert AND
        #self.filter_AppendOpHTML("AND")    
        self.txtSqlParser.insertPlainText(" AND ")
    
    def filter_insert_less(self):
        self.txtSqlParser.insertPlainText(" < ")
    
    def filter_insert_lessEq(self):
        self.txtSqlParser.insertPlainText(" <= ")
    
    def filter_insert_or(self):
        self.txtSqlParser.insertPlainText(" OR ")    
    
    def filter_build_query(self):
        #Build query set and return results
        column_list = ",".join(self.rptFields)
        filter_stmnt = self.txtSqlParser.toPlainText()
        
        #Check if sorting has been defined
        st_len, st_sql = self.sorting_compile_sort()
        
        #Check if grouping has been defined
        gp_len, gp_query = self.grouping_order_query()
        sort_stmnt = ''
        if gp_len > 0:          
            sort_stmnt = gp_query
            if st_len>0:
                st_sql = st_sql.replace(" ORDER BY","")
                sort_stmnt = sort_stmnt+"," + st_sql
        else:        
            if st_len>0:
                sort_stmnt = st_sql
                
        results=None  
        
        try:        
            results = process_report_filter(self.tabName, column_list, filter_stmnt, sort_stmnt)           
           
        except sqlalchemy.exc.ProgrammingError, sqlalchemy.exc.DataError:
            self.error_info_message(QApplication.translate("ReportBuilder","The SQL statement is invalid!"))
        
        return results       
   
    def map_query_from_filter(self):
        str_query = self.txtSqlParser.toPlainText()
        unit_array = []
        if self.tabName == 'social_tenure_relations':
                mp_part_qry = self.tabName+".spatial_unit_number = spatial_unit.spatial_unit_id"
                if str_query != "":
                    mp_part_qry +=" AND "+ self.tabName+"."+str_query
                else:
                    mp_part_qry = mp_part_qry

                
    def filter_verify_query(self):
        #Verify the query expression    
        if len(self.txtSqlParser.toPlainText())==0:
            self.error_info_message(QApplication.translate("ReportBuilder","No filter has been defined"))
            
        else:
            results = self.filter_build_query()
            
            if results != None:
                res_len = results.rowcount
                msg = QApplication.translate("ReportBuilder","The SQL statement was successfully verified.\n %s record(s) returned.")%str(resLen)
                self.info_message(msg)
            
    def sorting_update_report_fields(self):
        #Update the fields available in the sorting section    
        sort_items=["Ascending", "Descending", "None"]
        
        #Important! Ensure only new values are added without overriding the existing rows
        row = self.tbSortFields.rowCount()
        
        for l in range(len(self.rptFields)):
            f = self.rptFields[l]
            item = self.sorting_get_field_item(f)
            if item == None:            
                #Instantiate row widgets
                field_item = QTableWidgetItem()
                field_item.setText(f)
                
                sort_widget = TableComboBox(row)            
                sort_widget.addItems(sort_items)            
                sort_widget.setCurrentIndex(2)
                sort_widget.currentIndexChanged.connect(lambda:self.sorting_sort_order_changed())
                
                order_item = QTableWidgetItem()
                order_item.setText("") 
                
                #Add widgets to the row 
                self.tbSortFields.insertRow(row)           
                self.tbSortFields.setItem(row, 0, field_item)
                self.tbSortFields.setCellWidget(row, 1, sort_widget)
                self.tbSortFields.setItem(row, 2, order_item)
                row+=1  
                
        self.sorting_cleanup_fields_list()  
    
    def sorting_sort_order_changed(self):
        #Slot method when the user defines a sort order 
        cbo_sender = self.sender()  
        sort_order = str(cbo_sender.currentText())
        row = cbo_sender.row
        order_widget = self.tbSortFields.item(row,2)
        
        if sort_order == "None":
            if self._sortOrder>0:
                self._sortOrder-=1
                #Get the removed sort order value
                rem_val = int(order_widget.text())
                self.sorting_set_sort_order_widget(row, "") 
                self.sorting_update_sort_order(rem_val)           
        else:        
            if str(order_widget.text()) is "":            
                self._sortOrder+=1 
                self.sorting_set_sort_order_widget(row, str(self._sortOrder))   
        
    def sorting_update_sort_order(self, start_val):
        '''
        Update the values of the sorting order when a field
        becomes ineligible 
        ''' 
        num_rows = self.tbSortFields.rowCount()
        for r in range(num_rows):
            order_widget = self.tbSortFields.item(r, 2)
            widg_txt = order_widget.text()
            if str(widg_txt) is not "" and int(widg_txt) > start_val:                            
                old_val = int(widg_txt)
                new_val = old_val-1
                order_widget.setText(str(new_val)) 
  
    def sorting_set_sort_order_widget(self, row, text):
        '''
        Set the sort order value for the specified table widget item
        extracted from the row number in the widget's collection
        ''' 
        order_widg = self.tbSortFields.item(row, 2)
        order_widg.setText(text)
        
    def sorting_get_field_item(self, text):
        #Get the table widget item based on its text attribute
        tab_item = None
        items = self.tbSortFields.findItems(text, Qt.MatchExactly)
        for it in items:
            if str(it.text()) == text:
                tab_item = it
                break
        return tab_item

    def sorting_cleanup_fields_list(self):
        #Remove inapplicable rows from the sort collection
        rem_fields = []

        for i in range(self.tbSortFields.rowCount()):
            field_item = self.tbSortFields.item(i,0)
            rem_fields.append(str(field_item.text()))

        for f in self.rptFields:
            fIndex = getIndex(rem_fields,str(f))
            if fIndex!=-1:
                rem_fields.remove(str(f))

        for r in rem_fields:
            rem_item = self.sorting_get_field_item(r)
            if rem_item is not None:
                row = rem_item.row()
                self.tbSortFields.removeRow(row)

    def sorting_get_field_config(self, field):    
        #Get field SortInfo
        fs = None
        for r in range(self.tbSortFields.rowCount()):
            field_widg = self.tbSortFields.item(r,0)          
            if field == str(field_widg.text()):              
                fs = FieldSort()                        
                dir = str(self.tbSortFields.cellWidget(r,1).currentText())
                if not dir == "None":  
                    fs.order = int(str(self.tbSortFields.item(r,2).text()))                
                    if dir == "Ascending":
                        fs.direction = SortDir.Ascending 
                    elif dir == "Descending":
                        fs.direction = SortDir.Descending
        return fs  
         
    def sorting_compile_sort(self):
        #Compile the user-defined sorting fields to a standard SQL command
        sort_sql =' ORDER BY '
        row_num_order = []
        rows = self.tbSortFields.rowCount()
        #Loop through to put row numbers based on the sort order defined by the user    
        for r in range(rows):
            order_widg = self.tbSortFields.item(r, 2)
            order_txt = str(order_widg.text())
            if order_txt is not "":
                row_index = int(order_txt)-1  
                row_num_order.insert(row_index, r) 
                
        for rn in row_num_order:
            field_widg = self.tbSortFields.item(rn,0)
            sort_field = str(field_widg.text())   
            cbo_order = self.tbSortFields.cellWidget(rn,1)
            sort_order = str(cbo_order.currentText())
            sql_sort_order = ''

            if sort_order == "Ascending":
                sql_sort_order =' ASC,'
            else:
                sql_sort_order =' DESC,'

            sort_sql += sort_field + sql_sort_order
        sort_sql = sort_sql.rstrip(',')
        
        return (len(row_num_order), sort_sql)

    def grouping_add_field(self):
        #Add a report field for grouping
        num_rows = self.tbGroupFields.rowCount()
        
        #Get selected item in the report fields list box
        sel_items = self.lstRptFields.selectedItems()
        for sel_item in sel_items:
            sel_text = sel_item.text()
            self.grouping_add_fieldByName(str(sel_text))
        
    def grouping_add_fieldByName(self, field):
        
        #Method does the heavy lifting of adding the field in the grouping list box and corresponding widget
        tab_fields = [] 
          
        #updatedFields=self.rptFields
        num_rows = self.tbGroupFields.rowCount()      
        tab_fields.append(field)
            
        field_item = QTableWidgetItem()
        field_item.setText(field)
        
        #Add row
        self.tbGroupFields.insertRow(num_rows)
        self.tbGroupFields.setItem(num_rows, 0, field_item)
        num_rows += 1
        
        #Add Widget
        gp_widg = Groups("gp_" + field)
        self.stackedWidget.addWidget(gp_widg) 
        self.grouping_add_field_node(field)
          
        #Clean up
        for t in tab_fields:                
            #updatedFields.remove(t)
            list_items = self.lstRptFields.findItems(t, Qt.MatchExactly)
            for list_item in list_items:              
                self.lstRptFields.takeItem(self.lstRptFields.row(list_item))
                
        return gp_widg          

    def grouping_remove_field(self):
        #Remove the selected group field
        sel_rows = self.tbGroupFields.selectedItems()
        for sel_row in sel_rows:
            sel_text = str(sel_row.text())
            self.grouping_remove_field_references(sel_text)

    def grouping_cleanup_fields(self):
        #Remove all grouping fields and their references
        gp_rows = self.tbGroupFields.rowCount()
        for g in range(gp_rows):
            gp_item = self.tbGroupFields.item(g,0)
            field_name = str(gp_item.text())
            self.grouping_remove_field_references(field_name)
            self.tbGroupFields.removeRow(g)
                
    def grouping_remove_field_references(self, field):
        #Remove grouping widget, tree view item and row
        
        #Remove Item
        gp_items = self.tbGroupFields.findItems(field, Qt.MatchExactly)
        if len(gp_items) > 0:
            rem_item = gp_items[0]
            self.tbGroupFields.removeRow(rem_item.row())        
        #Insert list item
        self.lstRptFields.addItem(field)        
        #Remove settings widget
        gp_widg = self.__display_get_st_widget("gp_" + field)
        self.stackedWidget.removeWidget(gp_widg)        
        #Remove tree node
        self.grouping_remove_field_node(field)
        
    def grouping_add_field_node(self, group_field):
        #Add group field node to the tree view
        tr_groups = self.trRptSettings.findItems("Groups", Qt.MatchExactly,0)[0]
        trn = QTreeWidgetItem([group_field])
        tr_groups.addChild(trn)
    
    def grouping_remove_field_node(self, group_field):
        #Remove group field node in the tree view 
        tr_groups = self.trRptSettings.findItems("Groups", Qt.MatchExactly,0)[0]
        trn = self.display_get_child_node("Groups", group_field)
        tr_groups.removeChild(trn)
    
    def grouping_order_query(self):
        #Order results by the specified grouping fields
        sort_sql = " ORDER BY "
        row_count = self.tbGroupFields.rowCount()
        for r in range(row_count):
            cell_item = self.tbGroupFields.item(r,0)
            cell_txt = str(cell_item.text())
            sort_sql += cell_txt + " ASC,"
        sort_sql = sort_sql.rstrip(',')
        return (row_count, sort_sql)

    def grouping_get_field_config(self, field):
        #Get the group settings for the specified field 
        gs = None      
        for r in range(self.tbGroupFields.rowCount()):
            group_item = self.tbGroupFields.item(r,0)
            group_text = str(group_item.text())
            if group_text == field:              
                gs = GroupSettings()
                gs.isInGroup = True
                gs.order = r              
        return gs
                                        
    def display_update_report_fields(self):
        #Update tree fields list in the display section
        fields_el = self.trRptSettings.findItems(QApplication.translate
                                                 ("ReportBuilder", "Fields"), Qt.MatchExactly,0)
        if len(fields_el) > 0:
            tr_fields = fields_el[0]
            #Check if a report item has been added into the list or not
            for f in self.rptFields:
                rWidg = self.display_get_child_node(QApplication.translate
                                                 ("ReportBuilder", "Fields"), f)
                if rWidg == None:
                    tr = QTreeWidgetItem([f])
                    tr_fields.addChild(tr)
                    #Add settings widget as well
                    self.display_add_field_widget(f)
            #Clean up the field tree items and associated widgets
            self.display_cleanup_fields_list()

    def display_cleanup_fields_list(self):
        #Remove items from the fields tree node that are no longer applicable
        fields_el = self.trRptSettings.findItems(QApplication.translate
                                                 ("ReportBuilder","Fields"), Qt.MatchExactly,0)
        if len(fields_el) == 0:
            return

        tr_fields = fields_el[0]

        lst_fields = []

        for f in range(tr_fields.childCount()):
            tw = tr_fields.child(f)
            lst_fields.append(tw.text(0))
        #Remove (from the list) those items that exist for both report and tree instances
        for r in self.rptFields: 
            fIndex = getIndex(lst_fields, str(r))
            if fIndex != -1:
                lst_fields.remove(str(r))
        #Now clean up the tree node items     
        for obs_item in lst_fields:
            obs_node = self.display_get_child_node(QApplication.translate("ReportBuilder","Fields"), obs_item)
            obs_widg = self.__display_get_st_widget(obs_item)
            if obs_node != None:
                tr_fields.removeChild(obs_node)
            if obs_widg != None:
                self.stackedWidget.removeWidget(obs_widg)    
        
    def display_get_child_node(self, parent_str, child_str):
        #Get the tree item based on the parent and child texts respectively
        tr_parent = self.trRptSettings.findItems(parent_str, Qt.MatchExactly,0)[0]
        c_node=None
        for t in range(tr_parent.childCount()):
            tr_child = tr_parent.child(t)
            if tr_child.text(0) == child_str:
                c_node = tr_child
                break
        return c_node

    def display_get_child_list(self, parent_str):
        #Get the names list of the child nodes for the specified parent node
        tr_parent = self.trRptSettings.findItems(parent_str, Qt.MatchExactly,0)[0]
        child_nodes = []
        for t in range(tr_parent.childCount()):
            tr_child = tr_parent.child(t)
            child_nodes.append(str(tr_child.text(0)))
        return child_nodes
        
    def display_title_color(self):
        #Shows the color dialog and set the title color
        t_color = QColorDialog.getColor(Qt.darkBlue, self,QApplication.translate("ReportBuilder","Select title color"))
        if t_color.isValid():
            t_palette = QPalette(t_color)            
            self.lblTitleClr.setPalette(t_palette)
        
    def display_tree_view_selection(self):
        #Load appropriate widget when the report display's tree view selection changes
        tr_sel = self.trRptSettings.selectedItems()[0]
        search_txt = tr_sel.text(0)
        #Since the groups and field have the same name,return the correct widget
        tr_parent = tr_sel.parent()
        if not tr_parent is None:
            if tr_parent.text(0)=="Groups":
                search_txt="gp_" + search_txt
        #Retrieve widget from the stack widget based on the selected item
        for w in range(self.stackedWidget.count()):
            widg = self.stackedWidget.widget(w)                
            if widg.ID == search_txt:                     
                self.stackedWidget.setCurrentWidget(widg)
                break    
        
    def display_add_field_widget(self, report_item):
        '''
        Create a widget for each report field added by the user and add it to the stack
        only if it does not exist.
        '''
        el_widg = self.__display_get_st_widget(report_item)
        if el_widg == None:        
            field_widg = FieldBase(report_item)    
            self.stackedWidget.addWidget(field_widg)
    
    def __display_get_st_widget(self, widget_id):
        #Get a widget in the stack widget control based on the form identifier
        st_widg = None
        for s in range(self.stackedWidget.count()):
            widg = self.stackedWidget.widget(s)
            if widg.ID == widget_id:
                st_widg = widg
                break
        return st_widg

    def display_auto_width(self):
        #automatically compute the field width
        #Get the paper size defined by the user
        layout_widg = self.__display_get_st_widget(QApplication.translate(
                             "ReportBuilder","Layout"))
        w, h = layoutWidg.PageSize()
        cm_width = w/(72/2.54)
        return (cm_width / len(self.rptFields))

    def display_compile_settings(self):
        #Compile the user defined settings
        self.rpt_elements.headerElements = []
        self.rpt_elements.detailElements = []
        self.rpt_elements.groups = []
        
        #Config File Settings
        self.rpt_elements.footer = self.config.get("ReportMessages","Footer")
        self.rpt_elements.author = self.config.get("ReportMessages","Author")
        self.rpt_elements.subject = self.config.get("ReportMessages","Subject")
        
        #List of image fields
        self.imageFields = []
        
        #Get column style settings
        left = 0
        width = self.display_auto_width()
        col_style = self.__display_get_st_widget(QApplication.translate(
                  "ReportBuilder", "Field Names")).columnStyle()
        column_list = self.display_get_child_list(QApplication.translate(
                    "ReportBuilder", "Fields"))
        
        for field in column_list:
            f_widg = self.__display_get_st_widget(field)
            f_widg.elLeft = left
            f_widg.elWidth = width
            f_widg.columnStyle = col_style
            left += width
            
        for i in range(self.stackedWidget.count()):
            w = self.stackedWidget.widget(i)
            if isinstance(w, Title):
                self.rpt_elements.headerElements.append(w.systemExpression())
                self.rpt_elements.title = w.elText
                self.rpt_elements.headerBorders = w.elBorder
                
            elif isinstance(w, FieldBase):            
                self.rpt_elements.detailElements.append(w.get_object_value()) 
                self.rpt_elements.headerElements.append(w.get_label())                       
                self.rpt_elements.detailBorders = w.elBorder
                
                #Check if it is an image field
                if w.is_image_field():
                    self.imageFields.append(str(w.ID))
                    
            elif isinstance(w,Groups):            
                self.rpt_elements.groups.append(w.get_report_group())
                
            elif isinstance(w,ReportLayout):
                self.rpt_elements.page_size = w.PageSize()
                self.rpt_elements.margin_top = w.TopMargin()
                self.rpt_elements.margin_bottom = w.BottomMargin()
                self.rpt_elements.margin_left = w.LeftMargin()
                self.rpt_elements.margin_right = w.RightMargin()
            '''
            elif isinstance(w,frmFieldNames):
                self.rpt_elements.headerElements.append(w.get_label())
        '''

    def save_report_settings(self, file):
        #Helper for saving user report settings to file
        self.show_hide_progress_dialog(QApplication.translate("ReportBuilder","Saving Report Settings..."))
        
        #Create report config object
        rpt_config = STDMReportConfig(self.tabName)
        #Loop through all report elements' settings
        for i in range(self.stackedWidget.count()):
            w = self.stackedWidget.widget(i)
            
            #Get report element 
            rpt_el = w.get_settings()
            
            #Group dialog settings are not added directly to the collection but through the DBField proxy
            if not rpt_el.parent == "Groups":               
                #Check if it is a definition for database fields
                if rpt_el.parent == "Fields":
                    df = DbField()   
                                   
                    #copy attributes from ReportElement base to DbField object
                    copyattrs(rpt_el, df, ["dialogSettings", "parent", "name"])   
                                                                 
                    #Set field configuration
                    fc = FieldConfig()
                    fc.sortInfo = self.sorting_get_field_config(rpt_el.name)
                    
                    #Set grouping information
                    gi = self.grouping_get_field_config(rpt_el.name)
                    if not gi == None:
                        gp_dialog = self.__display_get_st_widget("gp_" + rpt_el.name)
                        if gp_dialog != None:                          
                            gi.dialogSettings = gp_dialog.getSettings().dialogSettings
                            fc.groupingInfo = gi
                            
                    #Get field index
                    fc.reportOrder = self.rptFields.index(rpt_el.name)
                    df.uiConfiguration = fc              
                    rpt_el = df
                rpt_config.addElement(rpt_el)   
                       
        rpt_config.setFilter(str(self.txtSqlParser.toPlainText()))
        rpt_config.setVersion(1.1)
        
        #Serialize to file 
        rpt_serializer = ReportSerializer(file) 
        rpt_serializer.serialize(rpt_config)
        self.show_hide_progress_dialog("", False)

    def load_settings_activate_controls(self, report_fields):
        #Enable supporting controls in the report builder widget          
                
        #Load report fields
        self.update_selected_report_fields(report_fields)
        #Select the first item in the list    
        self.select_avail_field_item()

    def load_report_settings(self, file):
        #Helper for restoring previously saved report settings
        
        #Deserialize report settings 
        rpt_serializer = ReportSerializer(file) 
        rpt_valid, rpt_conf = rpt_serializer.deserialize()
        #Validate if the object is an STDM Report Settings file      
        if rpt_valid:          
            #Check if the table exists
            tab_exists = self._table_exists(rptConf.table)
            if tab_exists:
                self.show_hide_progress_dialog(QApplication.translate("ReportBuilder", "Restoring Report Settings..."))
                friendly_tabname = rptConf.table
                
                #Force builder reset even if the loaded report refers to the previously loaded table            
                if rptConf.table == self.tabName:
                    self.tab_changed(friendly_tabname)
                else:                  
                    self.tabName = rptConf.table
                    #Set focus to report table in the drop down menu
                    setComboCurrentIndexWithItemData(self.comboBox, friendly_tabname)

                #Validate the fields
                valid_tab_fields = table_column_names(rptConf.table)
                valid_rpt_fields, invalid_rpt_fields = compareLists(valid_tab_fields, rptConf.fields)
                            
                #Configure supporting controls
                self.load_settings_activate_controls(valid_rpt_fields)
                #Set filter statement
                self.txtSqlParser.setText(rptConf.filter)
                
                #Group order container
                gp_info_collection = []
                
                #Sort info container
                sort_info_collection = []
                
                #Iterate report elements
                for r in rptConf.reportElementCollection:
                    if r.parent != "Groups":
                        #Get corresponding widget and load the settings
                        rpt_widg = self.__display_get_st_widget(r.name)
                        if not rpt_widg == None:
                            rpt_widg.loadSettings(r.dialogSettings)
                            
                        #Set grouping and sorting configuration
                        if r.parent == "Fields":
                            gp_info = r.uiConfiguration.groupingInfo
                            if gp_info != None:
                                gp_info.field = r.name
                                gpInfoCollection.append(gpInfo)
                            field_sort = r.uiConfiguration.sortInfo
                            
                            if field_sort.direction != SortDir.Null:
                                field_sort.field = r.name
                                sortInfoCollection.append(fieldSort) 
                                                           
                #Sort GROUPINFO items using the order attribute then add fields to the report builder controls
                gpInfoCollection.sort(key=lambda g: g.order)
                for g in gpInfoCollection:
                    group_dlg = self.grouping_add_fieldByName(g.field)
                    group_dlg.loadSettings(g.dialogSettings) 
                    
                #Order SORTINFO items using the order attribute then add fields to the report builder controls
                sortInfoCollection.sort(key=lambda s: s.order)
                for s in sortInfoCollection:
                    sort_item = self.sorting_get_field_item(s.field)
                    if sort_item is not None:
                        row_index = sortItem.row()
                        dir_combo = self.tbSortFields.cellWidget(row_index,1)

                        if s.direction == SortDir.Ascending:
                            setComboCurrentIndexWithText(dir_combo, "Ascending")

                        elif s.direction == SortDir.Descending:
                            setComboCurrentIndexWithText(dirCombo, "Descending")    
                                                                 
                #Show message of invalid fields
                if len(invalid_rpt_fields) > 0:
                    fields_str = ",".join(invalid_rpt_fields)
                    msg = QApplication.translate("ReportBuilder"," columns do not exist in the current table definition."
                                                                                 "\nThey will not be included in the report")
                    self.error_info_message(field_str + msg)
            else:
                self.show_hide_progress_dialog("", False)
                msg = QApplication.translate("ReportBuilder"," table or view does not exist in the database")
                self.error_info_message(rptConf.table + msg)
        else:
            self.show_hide_progress_dialog("", False)
            filename = str(file.section("/",-1))
            msg = QApplication.translate("ReportBuilder"," is not a valid STDM Report Settings file.\n "
                                                                                    "Please validate the source of the file")
            self.error_info_message(filename + msg)
        
        self.show_hide_progress_dialog("", False)
      
    def show_hide_progress_dialog(self, message, show=True):
        #Generic progress dialog for the report builder window    
        if show:
            self.progress_dlg.setWindowModality(Qt.WindowModal)
            self.progress_dlg.setLabelText(message) 
            self.progress_dlg.setCancelButtonText("")
            self.progress_dlg.setMaximum(0)
            self.progress_dlg.setMinimum(0)
            self.progress_dlg.show()
        else:
            self.progress_dlg.close()
            self.progress_dlg.reset()
  
    def save_report(self):
        #Serialize user report settings to file
        rpt_conf_file = QFileDialog.getSaveFileName(self,QApplication.translate("ReportBuilder","STDM Report")
                                                  ,"",QApplication.translate("ReportBuilder","STDM Report(*.trs)"))
        if rpt_conf_file != "":
            self.save_report_settings(rpt_conf_file)     
          
    def load_report(self):
        #Load previously saved report settings
        rpt_conf_file = QFileDialog.getOpenFileName(self, QApplication.translate("ReportBuilder","STDM Report"),
                                                  "",QApplication.translate("ReportBuilder","STDM Report(*.trs)"))
        if rpt_conf_file != "":
            self.load_report_settings(rpt_conf_file)
              
    def generate_report(self):
        #Generate report
        db_results = self.filter_build_query()
        if db_results.rowcount == 0:
            null_res_msg = QApplication.translate("ReportBuilder","No results "
                                                                  "were returned "
                                                                  "from the data "
                                                                  "source."
                                                                  "\nThe report "
                                                                  "will not be "
                                                                  "generated.")
            self.error_info_message(null_res_msg)

            return

        if not db_results is None:
            #Get user settings
            self.display_compile_settings()
            #Create query set
            tmp_dir, qset = createQuerySet(self.rptFields, db_results, self.imageFields)        
            stdm_rpt = STDMReport(qset, self.rpt_elements)        
            rpt_file = QFileDialog.getSaveFileName(self,QApplication.translate("ReportBuilder","STDM Report"),
                                                  "",QApplication.translate("ReportBuilder","Report Document(*.pdf)"))
                  
            if rpt_file:
                rpt_generator = STDMGenerator(stdm_rpt, rpt_file)
                rpt_generator.generate_report()            
                if self.info_message(QApplication.translate("ReportBuilder",
                                                           "The report has "
                                                           "been successfully created and written to '%s'") % rpt_file) == QMessageBox.Open:
                    os.startfile(rpt_file,'open')
                self.close()
                
    def _table_exists(self, table_name):
        """
        Assert whether the a table or view with the given name exists in the 'public' schema.
        """
        tables = pg_tables()
        views = pg_views()
        tables.extend(views)
        
        table_index = getIndex(tables, table_name)
        
        return False if table_index == -1 else True
        
    def error_info_message(self, message):      
        #Error Message Box
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.exec_() 
    
    def info_message(self, message):      
        #General Info Message Box
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok|QMessageBox.Open)
        return msg.exec_()
