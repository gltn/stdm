from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sqlalchemy
from sqlalchemy.schema import (
    Table,
    MetaData
)
from sqlalchemy.orm import (
    mapper,
    class_mapper
)
from stdm.settings import (
    current_profile
)
from stdm.data.database import STDMDb
from stdm.data.pg_utils import (
    geometryType,
    vector_layer
)
from stdm.data.pg_utils import columnType

from ui_gpx_add_attribute_info import Ui_Dialog
from stdm.ui.forms.editor_dialog import EntityEditorDialog

class _ReflectedModel(object):
    """
    Placeholder model for the reflected database table.
    """
    pass

class GPXAttributeInfoDialog(QDialog, Ui_Dialog):

    def __init__(self, iface, curr_layer, non_spatial_columns, sp_table, sp_table_colmn, geom_column_value):
        QDialog.__init__(self, iface.mainWindow())
        self.setupUi(self)
        self.iface = iface
        self.curr_layer = curr_layer
        self._dbSession = STDMDb.instance().session
        self.non_sp_colmns = non_spatial_columns
        self.sp_table = sp_table
        self.curr_profile = current_profile()
        self.sp_table_colmn = sp_table_colmn
        self.entity = self.curr_profile.entity_by_name(sp_table)
        self.geom_column_value = geom_column_value
        self.attribute_dict = {}
        self.geom_type = None
        self.target_geom_col_srid = None
        self.data_reader = None
        self._mapped_class = None

    def _insert_row(self, column_value_mapping):
        """
        Insert a new row using the mapped class instance then mapping column names to the corresponding column values.
        """
        model_instance = self._mapped_class()

        for col, value in column_value_mapping.iteritems():
            if hasattr(model_instance,col):

                setattr(model_instance,col,value)
        #raise NameError(str(dir(modelInstance)))
        try:
            self._dbSession.add(model_instance)
            self._dbSession.commit()
        except Exception as ex:
            raise
        finally:
            self._dbSession.rollback()

    def _map_table(self, dataSourceName):
        """
        Reflect the data source.
        """
        meta = MetaData(bind = STDMDb.instance().engine)
        dsTable = Table(dataSourceName,meta,autoload = True)

        return dsTable


    def init_form(self, model):
        editor = EntityEditorDialog(self.entity, model, self.iface.mainWindow())
        if editor.exec_() == QDialog.Accepted:
            pass
    # your logic
    def create_attribute_info_gui(self):
        """
        Create attribute info table
        """
        grid_column_count = 0

        for column in self.non_sp_colmns:

            column_data_type = str(columnType(self.sp_table, column))

            label_name = "label_{0}".format(column)
            line_edit_name = "line_edit_name_{0}".format(column)

            self.label = QLabel()
            self.label.setObjectName(label_name)
            self.label.setText(column)
            self.gridLayout.addWidget(self.label, grid_column_count, 0, 1, 1)

            self.lineEdit = QLineEdit()
            self.lineEdit.setObjectName(line_edit_name)
            # Check data type of column before assigning default value
            if column_data_type == 'integer':
                self.lineEdit.setText("0")
            elif column_data_type == 'character varying':
                self.lineEdit.setPlaceholderText("NULL")
            elif column_data_type == 'double precision':
                self.lineEdit.setText("0.0")
            elif column_data_type == 'date':
                self.lineEdit.setPlaceholderText("1-1-2000")
            else:
                self.lineEdit.setPlaceholderText("NULL")
            self.gridLayout.addWidget(self.lineEdit, grid_column_count, 1, 1, 1)

            grid_column_count += 1

            self.attribute_dict[self.label.text()] = self.lineEdit

    def accept(self):
        """
        Import GPX to db with user supplied attribute information
        """
        if self._mapped_class == None:

            try:
                primaryMapper = class_mapper(_ReflectedModel)

            except (sqlalchemy.orm.exc.UnmappedClassError,sqlalchemy.exc.ArgumentError):
                #Reflect table and map it to '_ReflectedModel' class only once
                mapper(_ReflectedModel,self._map_table(self.sp_table))

            self._mapped_class = _ReflectedModel

        for column, line_edit in self.attribute_dict.iteritems():

            column_data_type = str(columnType(self.sp_table, column))

            if column_data_type == 'integer':
                if line_edit.text() == '':
                    self.attribute_dict[column] = int(line_edit.setText('0'))
                else:
                    self.attribute_dict[column] = int(line_edit.text())
            elif column_data_type == 'character varying':
                if line_edit.text() == '':
                    self.attribute_dict[column] = line_edit.setText('NULL')
                else:
                    self.attribute_dict[column] = line_edit.text()
            elif column_data_type == 'double precision':
                if line_edit.text() == '':
                    self.attribute_dict[column] = float(line_edit.setText('0.0'))
                else:
                    self.attribute_dict[column] = float(line_edit.text())
            elif column_data_type == 'date':
                self.attribute_dict[column] = int(line_edit.text())
            else:
                self.attribute_dict[column] = int(line_edit.text())

        self.geom_type, self.target_geom_col_srid = geometryType(self.sp_table, self.sp_table_colmn)

        self.attribute_dict[self.sp_table_colmn] = "SRID={0!s};{1}".format(self.target_geom_col_srid,
                                                                           self.geom_column_value)

        self._insert_row(self.attribute_dict)

        self.curr_layer = vector_layer(self.sp_table, geom_column=self.sp_table_colmn)

        self.iface.mapCanvas().setExtent(self.curr_layer.extent())

        self.iface.mapCanvas().refresh()

        self.close()
