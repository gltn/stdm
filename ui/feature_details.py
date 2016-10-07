# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Feature Details Viewer
Description          : GUI widget for viewing details of a feature on
                        the map canvas.
Date                 : 10/October/2016
copyright            : (C) 2016 by UN-Habitat and implementing partners.
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

import re
from collections import OrderedDict
from PyQt4.QtGui import (
    QDockWidget,
    QMessageBox,
    QTreeView,
    QStandardItem,
    QAbstractItemView,
    QStandardItemModel,
    QIcon,
    QApplication,
    QColor,
    QScrollArea
)
from PyQt4.QtCore import (
    Qt
)
from qgis.gui import (
   QgsHighlight
)
from qgis.core import (
    QgsFeatureRequest,
    QgsExpression
)
from sqlalchemy.sql import (
    select
)

from stdm.settings import current_profile
from stdm.data.database import (
    STDMDb,
    alchemy_table
)
from stdm.data.pg_utils import (
    spatial_tables,
    foreign_key_parent_tables,
    numeric_varchar_columns,

    data_from_id,
    pg_tables,
    #AdminSpatialUnitSet,
    parent_child_table_data
)
from stdm.utils.util import (
    format_name,
    lookup_id_to_value,
    entity_id_to_model
)

class LayerSelectionHandler:
    def __init__(self, iface, plugin):
        self.layer = None
        self.iface = iface
        self._plugin = plugin
        self.sel_highlight = None

    def selected_features(self):
        """
        Returns a selected feature spatial unit
        id and code as key and value.
        :return: Dictionary
        """
        layer = self.iface.activeLayer()
        if self.feature_layer(layer):
            try:
                self.layer = self.iface.activeLayer()
                selected_features = layer.selectedFeatures()
                features = []

                for feature in selected_features:
                    features.append(feature["id"])
                return features
            except:
                not_feature_table = QApplication.translate(
                    'FeatureDetails',
                    'You have selected feature layer from view. '
                    'Please select a feature layer that uses the '
                    'main feature table.'
                )
                QMessageBox.information(
                    self.iface.mainWindow(),
                    "Error",
                    not_feature_table
                )

    def get_layer_source(self, layer):
        """
        Get the layer table name if the source is from the database.
        :param layer: The layer for which the source is checked
        :type QGIS vectorlayer
        :return: String or None
        """
        source = layer.source()
        vals = dict(re.findall('(\S+)="?(.*?)"? ', source))
        try:
            table = vals['table'].split('.')
            tableName = table[1].strip('"')
            return tableName
        except KeyError:
            return None

    def active_layer_check(self):
        """
        Check if there is active layer and if not, displays
        a message box to select a feature layer.
        :return:
        """
        active_layer = self.iface.activeLayer()
        if active_layer is None:
            no_layer_msg = QApplication.translate(
                'FeatureDetails',
                'Please select a feature layer to view feature details.'
            )
            QMessageBox.critical(
                self.iface.mainWindow(),
                "Error",
                no_layer_msg
            )

    def feature_layer(self, active_layer):
        """
        Check whether the layer is feature layer or not.
        :param active_layer: The layer to be checked
        :type QGIS vectorlayer
        :return: Boolean
        """
        layer_source = self.get_layer_source(active_layer)
        if layer_source in spatial_tables():
            return True
        else:
            not_feature_msg = QApplication.translate(
                'FeatureDetails',
                'You have selected a non-feature layer. '
                'Please select a feature layer to view the details.'
            )
            QMessageBox.information(
                self.iface.mainWindow(),
                "Error",
                not_feature_msg
            )
            return False


    def clear_feature_selection(self):
        """
        Clears selection of layer(s)
        :return: None
        """
        map = self.iface.mapCanvas()
        for layer in map.layers():
            if layer.type() == layer.VectorLayer:
                layer.removeSelection()
        map.refresh()

    def activate_select_tool(self):
        """
        Enables the select tool to be used to select features.
        :return:None
        """
        self.iface.actionSelect().trigger()
        layer_select_tool = self.iface.mapCanvas().mapTool()
        layer_select_tool.activate()

    def clear_sel_highlight(self):
        """
        Removes sel_highlight from the canvas.
        :return:
        """
        if self.sel_highlight is not None:
            self.sel_highlight = None

    def multi_select_highlight(self, index):
        """
        Highlights a feature with rubberBald class when selecting
        features are more than one.
        :param index: Selected QTreeView item index
        :type Integer
        :return: None
        """
        pass

class DetailsModel:
    def __init__(self):

        self.engine = STDMDb.instance().session

    def filter_child_columns(self, table_name, str_table, filter_fk = True):
        """
        Filters the columns to be used as a child by
        filtering out binary, foreign keys and primary keys.
        :param table_name: The name of str table or any relationship table
        :type String
        :param str_table: The alchemy str table object
        :type String
        :param filter_fk: Boolean to filter include or exclude foreign keys
        :type Boolean
        :return: List
        """
        detail_alchemy_column = []
        if filter_fk:
            disp_fk_cols = numeric_varchar_columns(table_name)
            for col in disp_fk_cols:
                if col != 'id' and col != 'geom_polygon':
                    detail_alchemy_column.append(str_table.c[col])
        else:
            pass
            ###TODO replace with current profile table columns
            # config_table_reader = ConfigTableReader()
            # disp_cols = config_table_reader.table_columns(table_name)
            # for col in disp_cols:
            #     if col != 'id' and col != 'geom_polygon':
            #
            #         detail_alchemy_column.append(str_table.c[col])

        return detail_alchemy_column


    def str_tables_data(
            self,
            str_used_table_name,
            str_table,
            str_column_name,
            spatial_unit_id,
            fetchall=True
    ):
        """
        Generate date for str used tables ready to be used for tree view.
        :param str_used_table_name: The name of the table used by
        str eg. feature, person
        :type String
        :param str_table: sqlalchemy table object for str
        :type sqlalchemy table object
        :param str_column_name: the column name of str used tables in str
        eg. spatial_unit_id, party_id
        :type String
        :param spatial_unit_id: The selected feature spatial unit id
        :type Integer
        :return: sqlalchemy result.RowProxy Dictionary
        """

        str_used_table = alchemy_table(str_used_table_name)
        str_child_columns = self.filter_child_columns(
            str_used_table_name, str_used_table, False
        )
        str_child_columns.append(str_used_table.c.id)
        select_str_row = select(str_child_columns).where(
            str_table.c[str_column_name] == str_used_table.c.id
        ).where(
            str_table.c.spatial_unit_id == spatial_unit_id
        ).order_by(str_table.c.id)

        str_result = self.engine.execute(select_str_row)
        if fetchall:
            str_record = str_result.fetchall()
            columns = str_result.keys()

            record_cont = []
            for i, recs in enumerate(str_record):
                data_dic = OrderedDict(zip(columns, recs))

                record_cont.append(data_dic)
            return record_cont
        else:
            str_record = str_result.first()

            return str_record

class DetailsDockWidget(QDockWidget):
    def __init__(self, iface):
        QDockWidget.__init__(self, iface.mainWindow())
    

    def init_dock(self):
        """
        creates dock on right dock widget area and set window title.
        :return: None
        """
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self)

        self.setWindowTitle(
            QApplication.translate(
                'DetailsDockWidget', 'Feature Details'
            )
        )

class DetailsDockWidgetHandler(LayerSelectionHandler, DetailsDockWidget):
    def __init__(self, iface, spatial_unit_dock):
        DetailsDockWidget.__init__(self, iface)

        LayerSelectionHandler.__init__(self, iface, spatial_unit_dock)
        self.spatial_unit_dock = spatial_unit_dock
        self.iface = iface

    def close_dock(self, tool):
        """
        Closes the dock by replacing select tool with pan tool,
        clearing feature selection, and hiding the dock.
        :param tool: Feature detail tool property
        :type QGIS tool
        :return: None
        """
        self.iface.actionPan().trigger()
        tool.setChecked(False)
        self.clear_feature_selection()
        self.hide()
        self.clear_sel_highlight()

    def closeEvent(self, event):
        """
        On close of the dock window, this event is executed
        to run close_dock method
        :param event: The close event
        :type QCloseEvent
        :return: None
        """
        self.close_dock(self._plugin.show_parcel_details_act)

class DetailsTreeView(DetailsModel, DetailsDockWidgetHandler):
    def __init__(self, iface, plugin):

        """
        The method initializes the dockwidget.
        :param iface: QGIS user interface class
        :type class qgis.utils.iface
        :param plugin: The STDM plugin
        :type class
        :return: None
        """
        DetailsDockWidgetHandler.__init__(self, iface, plugin)
        DetailsModel.__init__(self)
        self.view = QTreeView()
        self.view.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )
        self.feature_ids = []
        self.layer_table = None
        self.model = QStandardItemModel()
        self.view.setModel(self.model)
        self.view.setUniformRowHeights(True)
        self.view.setRootIsDecorated(True)
        self.current_profile = current_profile()
        self.view.resizeColumnToContents(100)
        self.view.setHeaderHidden(False)


    def feature_details_activate(self):
        """
        Action for showing feature details.
        :return:
        """
        # Get the active layer.

        # active_layer = self.iface.activeLayer()
        title = QApplication.translate("STDMQGISLoader", "Feature Details")

        select_feature =  QApplication.translate(
            "STDMQGISLoader",
            "Please select a feature to view their details."
        )

       # new_feature_details_dock = FeatureDetails(self.iface, self)
        # create instance for active_layer_check()
        active_layer = self.iface.activeLayer()
        if active_layer is not None:
            # if feature detail dock is not defined or hidden, create empty dock.
            if self is None or \
                    self.isHidden():

                # if the selected layer is not a feature layer, show not
                # feature layer. (implicitly included in the if statement).
                if self.feature_layer(active_layer) == False:
                    self.spatial_unit_dock.feature_details_btn.setChecked(False)
                # If the selected layer is feature layer, get data and
                # display treeview in a dock widget
                else:
                    self.init_dock()
                    self.add_tree_view() ###TODO fix reference of this method
                    self.treeview_error(title, select_feature)
                    # enable the select tool
                    self.activate_select_tool()
                    # pull data, show treeview
                    active_layer.selectionChanged.connect(
                        self.show_tree
                    )

            # if feature_detail dock is open, toggle close
            else:
                self.close_dock(
                    self.spatial_unit_dock.feature_details_btn
                )
                self.feature_details = None
        # if no active layer, show error message and uncheck the feature tool
        else:
            self.active_layer_check()
            self.spatial_unit_dock.feature_details_btn.setChecked(False)

    def add_tree_view(self):
        """
        Adds tree view to the dock widget and sets style.
        :return: None
        """
        self.setWidget(self.view)
        self.view.setEditTriggers(
            QAbstractItemView.NoEditTriggers)

    def init_tree_view(self):
        #clear feature_ids list, model and highlight
        self.model.clear()
        self.clear_sel_highlight() # remove sel_highlight
        self.feature_ids[:] = []

        features = self.selected_features()
        # if the selected feature is over 1,
        # activate multi_select_highlight
        if len(features) > 1 or not features is None:
            self.view.clicked.connect(
                self.multi_select_highlight
            )
        # if there is at least one selected feature
        if len(features) > 0:
            self.init_dock()
            self.add_tree_view()
            self.feature_ids = features

    def show_tree(self):
        self.init_tree_view()
        self.layer_table = self.get_layer_source(
            self.iface.activeLayer()
        )
        self.entity = self.current_profile.entity_by_name(
            self.layer_table
        )

        roots = self.add_parent_tree()
        if roots is None:
            return
        for id, root in roots.iteritems():
            db_model = entity_id_to_model(self.entity, id)
            self.add_children(db_model, root)

    def add_parent_tree(self):
        if len(self.feature_ids) < 1:
            return
        roots = OrderedDict()
        for feature_id in self.feature_ids:
            root = QStandardItem('Feature {}'.format(feature_id))
            self.model.appendRow(root)
            roots[feature_id] = root
        return roots


    def add_children(self, model, parent):

        model_dict = dict(model.__dict__)
        model_dict.pop('_sa_instance_state', None)

        for col, row in model_dict.iteritems():
            child = QStandardItem('{}: {}'.format(col, row))
            parent.appendRow([child])
        self.expand_node(parent)
    #
    # def show_feature_details(self):
    #     """
    #     On select pull the selected feature detail into to a tree view.
    #     :return:
    #     """
    #     # clear existing tree model. Do all model methods after this.
    #     self.model.clear()
    #     self.clear_sel_highlight()  # remove sel_highlight
    #
    #     if self.selected_features() is not None:
    #         features = self.selected_features()
    #     else:
    #         return
    #
    #       #if the selected feature is over 1, activate multi_select_highlight
    #     if len(features) > 1:
    #
    #         self.view.clicked.connect(self.multi_select_highlight)
    #
    #     # if there is at least one selected feature
    #     if len(features) > 0:
    #
    #         self.init_dock()
    #         self.add_tree_view()
    #         count_title = 'Selected Feature(s) (' + str(len(features)) + ')'
    #         self.model.setHorizontalHeaderLabels([count_title])
    #         # create node for every selected feature
    #         root = None
    #         for spatial_unit_id, feature_code in features.iteritems():
    #
    #             root = QStandardItem('Feature '+str(feature_code))
    #             str_table_name = self.current_profile.social_tenure.name
    #             str_table = alchemy_table(str_table_name)
    #             #get unique foreign key tables details.
    #             str_used_tables = set(foreign_key_parent_tables(str_table_name))
    #
    #             str_fk_columns = []  # prepare str fk columns for sqlalchemy
    #             for fk_col in str_used_tables:
    #                 str_fk_columns.append(str_table.c[fk_col[0]])
    #
    #             # get list of all str_alchemy column names with str fk columns
    #             str_columns = self.filter_child_columns(
    #                 str_table_name, str_table, True
    #             )
    #             # get all str table without the fk columns
    #             none_fk_str_columns = [item for item in str_columns
    #                                    if item not in str_fk_columns]
    #             none_fk_str_columns.append(str_table.c.party_id)
    #             # get str node data
    #             select_str = select(
    #                 none_fk_str_columns
    #             ).where(str_table.c.spatial_unit_id == spatial_unit_id)
    #             str_result_str = self.engine.execute(select_str)
    #             #str_record_str = str_result_str.first()
    #             str_record_str = str_result_str.fetchall()
    #
    #             no_str_icon = QIcon(
    #                 ':/plugins/stdm/images/icons/remove.png'
    #             )
    #
    #             # Show No str message if str_record_str is None for a feature
    #             if len(str_record_str) == 0:
    #                 # self.add_tree_view()
    #                 self.treeview_error(
    #                     count_title,
    #                     'Feature '+str(feature_code)+' - No STR defined',
    #                     no_str_icon
    #                 )
    #                 continue
    #
    #             # Create Treeview
    #             for table in str_used_tables:
    #
    #                 str_column_name = table[0]
    #                 str_used_table_name = table[1]
    #                 str_used_pk_id = table[2]
    #
    #                 # Insert data of spatial unit table under the
    #                 # get root (feature) as a child of root
    #                 if str_used_table_name == 'feature':
    #
    #                     feature_str_record = self.str_tables_data(
    #                         str_used_table_name,
    #                         str_table,
    #                         str_column_name,
    #                         spatial_unit_id,
    #                         False
    #                     )
    #                      # add under Feature - root
    #                     self.create_details_tree(
    #                         feature_str_record,
    #                         root,
    #                         'feature',
    #                         spatial_unit_id,
    #                         ['survey']
    #                     )
    #
    #             steam = None
    #             branch = None
    #             for i, str_rec in enumerate(str_record_str):
    #                 print str_rec
    #                 str_icon = QIcon(
    #                     ':/plugins/stdm/images/icons/social_tenure.png'
    #                 )
    #                 steam = QStandardItem(
    #                     str_icon,
    #                     'Social Tenure Relationship'
    #
    #                                  )
    #                 # add social tenure after feature
    #                 # details but before party.
    #                 self.add_steam(steam, root, str_rec)
    #                 self.set_bold(steam)
    #                 for table in str_used_tables:
    #                     print table
    #                     str_column_name = table[0]
    #                     str_used_table_name = table[1]
    #                     str_used_pk_id = table[2]
    #                     # return data for party table.
    #
    #                     if str_used_table_name not in spatial_tables() and \
    #                                     str_rec[str_column_name] is not None:
    #
    #                          # return data for tables other than spatial unit
    #                          # table.
    #                         str_record_2 = self.str_tables_data(
    #                             str_used_table_name,
    #                             str_table,
    #                             str_column_name,
    #                             spatial_unit_id
    #                         )
    #
    #
    #                         if str_record_2[i]['id'] == str_rec[str_column_name]:
    #                             sub_str_icon = QIcon(
    #                                 ':/plugins/stdm/images/icons/table.png'
    #                             )
    #                             branch = QStandardItem(
    #                                 sub_str_icon, format_name(str_used_table_name)
    #                             )
    #                             self.set_bold(branch)   # set bold all branches
    #
    #                             self.add_steam(
    #                                 branch,
    #                                 steam,
    #                                 str_record_2[i],
    #                                 str_used_table_name,
    #                                 str_record_2[i]['id'],
    #                                 ['service_payment']
    #                             )
    #
    #
    #             self.model.appendRow(root)
    #             # expand nodes
    #             self.expand_node(branch)
    #             self.expand_node(steam)
    #
    #             #self.set_bold(steam)
    #             self.set_bold(root)
    #         self.expand_node(root)   # Expand the last selected root-Feature
    #
    #     else:
    #         self.treeview_error(
    #             'Error',
    #             'You have not selected a feature. Please select a \n'
    #             'feature to view the details.'
    #         )
    #


    def set_bold(self, standard_item):
        """
        Make a text of Qstandaritem to bold.
        :param standard_item: Qstandaritem
        :type: Qstandaritem
        :return: None
        """
        font = standard_item.font()
        font.setBold(True)
        standard_item.setFont(font)



    def treeview_error(self, title, message, icon=None):
        """
        Displays error message in feature details treeview.
        :param title: the title of the treeview.
        :type: String
        :param message: The message to be displayed.
        :type: String
        :param icon: The icon of the item.
        :type: Resource string
        :return: None
        """
        not_feature_ft_msg = QApplication.translate(
            'FeatureDetails', message
        )
        if icon== None:
            root = QStandardItem(not_feature_ft_msg)
        else:
            root = QStandardItem(icon, not_feature_ft_msg)
        self.model.setHorizontalHeaderLabels([title])
        self.view.setRootIsDecorated(False)
        self.model.appendRow(root)
        self.view.setRootIsDecorated(True)
    #
    # def create_details_tree(
    #         self,
    #         data,
    #         parent,
    #         parent_name=None,
    #         spatial_unit_id = None,
    #         external_table = None
    # ):
    #     """
    #     Generates feature details tree node.
    #     :param data: The database record from sqlalchemy
    #     :type: sqlalchemy result proxy
    #     :param parent: The parent containing the children
    #     :type: QStandarItem
    #     :param parent_name: The label to be added under parent.
    #     :type: String
    #     :param spatial_unit_id: The id of the selected feature
    #     :type: Integer
    #     :param external_table: list of external tables
    #     using the feature id as foreign key.
    #     :type: List
    #     :return: None
    #     """
    #     self.add_children(
    #         data,
    #         parent,
    #         spatial_unit_id,
    #         external_table,
    #         parent_name
    #     )
    #     self.add_tree_view()
    #     self.view.setAlternatingRowColors(True)
    #
    #
    #
    # def add_children0(
    #         self,
    #         data,
    #         parent,
    #         spatial_unit_id=None,
    #         external_table=None,
    #         parent_name=None
    # ):
    #     """
    #     Add children into tree view.
    #     :param data: The database record from sqlalchemy
    #     :type: sqlalchemy result proxy
    #     :param parent: The parent containing the children
    #     :type: QStandarItem
    #     :param spatial_unit_id: The id of the selected feature
    #     :type: Integer
    #     :param external_table: list of external tables
    #     using the feature id as foreign key.
    #     :type: List
    #     :param parent_name: The label to be added under parent.
    #     :type: String
    #     :return: None
    #     """
    #     # If record_party has values, insert it on the tree
    #
    #     if data is not None:
    #
    #         for col, row in data.items():
    #             if col != 'id' and col[:-3] not in ['feature', 'person', 'institution']:   # hide ids
    #                 if col.find('_id') != -1:
    #                     #if the column is foreign key column, create sub children
    #                     if col[:-3] in pg_tables():
    #                         child = QStandardItem(format_name(col[:-3]))
    #                         if data_from_id(row, col) is not None:
    #                             for col2, row2 in data_from_id(row, col).items():
    #                                 if col2 != 'id':   # hide ids
    #                                     #if column is a fk or lookup column
    #                                     if col2.find('_id') != -1:
    #                                         # foreign keys are not present on all str tables
    #                                         # if the column is foreign key column, create sub children
    #                                         if col2[:-3] in pg_tables():
    #                                             child2 = QStandardItem(format_name(col2[:-3]))
    #                                             if data_from_id(row2, col2) is not None:
    #
    #                                                 for col3, row3 in data_from_id(row2, col2).items():
    #                                                     if col3 != 'id': #hide ids
    #                                                         #if column is a fk or lookup column
    #                                                         if col3.find('_id') != -1:
    #                                                             # if the column is foreign key column, create sub children
    #                                                             if col3[:-3] in pg_tables():
    #                                                                 child3 = QStandardItem('{}: {}'.format(
    #                                                                             format_name(col3),
    #                                                                             row3
    #                                                                             )
    #                                                                 )
    #                                                             # col is a lookup column
    #                                                             else:
    #                                                                 child3 = QStandardItem('{}: {}'.format(
    #                                                                     format_name(col3[:-3]),
    #                                                                      lookup_id_to_value(self.current_profile, col3, row3))
    #                                                                 )
    #                                                             child2.appendRow([child3])
    #                                                          # if it is other column show data as is
    #                                                         else:
    #
    #                                                             child3 = QStandardItem('{}: {}'.format(
    #                                                                         format_name(col3),
    #                                                                         row3
    #                                                                         )
    #                                                             )
    #                                                             child2.appendRow([child3])
    #
    #
    #                                         # col is a lookup column
    #
    #                                         child2 = QStandardItem('{}: {}'.format(
    #                                                 format_name(col2[:-3]),
    #                                                 lookup_id_to_value(self.current_profile, col2, row2)
    #                                             )
    #                                         )
    #                                         child.appendRow([child2])
    #                                     # if it is other column show data as is
    #                                     else:
    #                                         child2 = QStandardItem('{}: {}'.format(
    #                                                 format_name(col2),
    #                                                 row2
    #                                             )
    #                                         )
    #                                     child.appendRow([child2])
    #
    #                             parent.appendRow([child])
    #                     ###TODO format administrative units
    #                     # # Look for Admin unit and format. Only added for feature as it is a feature column
    #                     # elif col.find('admin') != -1:
    #                     #     admin_unit_set = AdminSpatialUnitSet()
    #                     #     sel_admin_unit = admin_unit_set.queryObject().filter(AdminSpatialUnitSet.id == row).first()
    #                     #     if sel_admin_unit is not None:
    #                     #         full_admin_unit = sel_admin_unit.hierarchy_names(', ')
    #                     #     else:
    #                     #         full_admin_unit = 'None'
    #                     #     child = QStandardItem('{}: {}'.format(
    #                     #             'Administrative Unit',
    #                     #              full_admin_unit
    #                     #         )
    #                     #     )
    #                     #     parent.appendRow([child])
    #                     #if the the column is a lookup column or has id in it
    #                     else:
    #                         if col == 'national_id':
    #                             child = QStandardItem('{}: {}'.format(
    #                                     'National ID',
    #                                     row
    #                                 )
    #                             )
    #                             parent.appendRow([child])
    #                         else:
    #                             child = QStandardItem('{}: {}'.format(
    #                                  format_name(col[:-3]),
    #                                  lookup_id_to_value(self.current_profile, col, row))
    #                             )
    #                             parent.appendRow([child])
    #
    #                 #if it is other column show data as is
    #                 else:
    #                     if col == 'area':
    #
    #                         child = QStandardItem('{}: {}'.format(
    #                                 format_name(col),
    #                                 format(row, '.4f')
    #                             )
    #                         )
    #                     else:
    #                         child = QStandardItem('{}: {}'.format(
    #                                 format_name(col),
    #                                 row
    #                             )
    #                         )
    #                     parent.appendRow([child])
    #
    #         #if it is external table
    #
    #         if external_table is not None:
    #             for ext in external_table:
    #
    #                 ext_data_list = parent_child_table_data(spatial_unit_id, ext, parent_name, False)
    #                 # ext_data[0] is the first value which is id
    #
    #                 if ext_data_list is not None:
    #                     for ext_data in ext_data_list:
    #                         rates_payment_data = parent_child_table_data(
    #                             ext_data[0], 'rates_payment', ext, False
    #                         )
    #                         # Index will limit the number of loops
    #                         # for rates payment generation to 1
    #                         index = 0
    #                         # remove id, spatial_unit_id, and column with None data
    #                         # as they are not included in the loop
    #                         ext_data_len = len(filter(None, ext_data)) - 2
    #
    #                         child1 = QStandardItem(format_name(ext))
    #                         if ext_data is not None:
    #                             for col, row in ext_data.items():
    #
    #                                 # if the column is foreign key column,
    #                                 # create sub children eg. surveyor_id
    #                                 if col != 'id' and col != parent_name+'_id' and row != None: #hide ids
    #                                     # add all rates payment rows related to service_payment_id
    #                                     if ext == 'service_payment':
    #
    #                                       # if normal value columns
    #                                         if col.find('_id') == -1:
    #                                             child2 = QStandardItem('{}: {}'.format(
    #                                                     format_name(col),
    #                                                     row
    #                                                 )
    #                                             )
    #                                             child1.appendRow([child2])
    #
    #                                         elif col.find('_id') != -1:
    #                                             if col[:-3] in pg_tables():
    #
    #                                                 child2 =  QStandardItem(format_name(col[:-3]))
    #                                                 # If the table has foreign tables create tree
    #                                                 if data_from_id(row, col) != row:
    #                                                     for col2, row2 in data_from_id(row, col).items():
    #                                                         if col2 != 'id': #hide ids
    #                                                             # if column is a fk or lookup column
    #                                                             if col2.find('_id') != -1:
    #                                                                 # if the column is foreign key column, create sub children
    #                                                                 # Foreign key tables this deep are not present for Turkana case
    #                                                                 # col is a lookup column
    #                                                                 if col2[:-3] not in pg_tables():
    #                                                                     child3 = QStandardItem('{}: {}'.format(
    #                                                                             format_name(col2[:-3]),
    #                                                                             lookup_id_to_value(self.current_profile, col2, row2)
    #                                                                         )
    #                                                                     )
    #                                                                     child2.appendRow([child3])
    #                                                              # if it is other column show data as is
    #                                                             else:
    #                                                                 child3 = QStandardItem('{}: {}'.format(
    #                                                                         format_name(col2),
    #                                                                         row2
    #                                                                     )
    #                                                                 )
    #                                                                 child2.appendRow([child3])
    #                                                 child1.appendRow([child2])
    #                                             # if lookup column
    #                                             else:
    #                                                 child2 = QStandardItem('{}: {}'.format(
    #                                                         format_name(col[:-3]),
    #                                                         lookup_id_to_value(self.current_profile, col, row)
    #                                                     )
    #                                                 )
    #                                                 child1.appendRow([child2])
    #                                         index = index+1
    #
    #                                         # Add rates and services table
    #                                         # create rates payment only in the last loop
    #                                         # after all others are added in the tree
    #                                         if index == ext_data_len:
    #                                             if rates_payment_data is not None:
    #                                                 child2 = QStandardItem("Services Paid")
    #                                                 for ext_data_rates in rates_payment_data:
    #                                                     service_payment_row = list()
    #
    #                                                     for col4, row4 in ext_data_rates.items():
    #
    #                                                         if col4 == 'service_type_id':
    #
    #                                                             service_payment_row.append(lookup_id_to_value(self.current_profile, col4, row4))
    #                                                         if col4 == 'amount':
    #                                                             service_payment_row.append(format_name(col4))
    #                                                             service_payment_row.append(row4)
    #                                                          # if service type and amount are added create node
    #                                                         if len(service_payment_row) == 3:
    #
    #                                                             child3 = QStandardItem('{} - {}: {}'.format(
    #                                                                     *service_payment_row
    #                                                                 )
    #                                                             )
    #                                                             child2.appendRow([child3])
    #                                                 child1.appendRow([child2])
    #
    #                                     # for survey table
    #                                     else:
    #                                         if col[:-3] in pg_tables():
    #                                             child2 =  QStandardItem(format_name(col[:-3]))
    #                                             # If the table has foreign tables create tree
    #                                             if data_from_id(row, col) is not None:
    #                                                 for col2, row2 in data_from_id(row, col).items():
    #                                                     if col2 != 'id': #hide ids
    #                                                         # if column is a fk or lookup column
    #                                                         if col2.find('_id') != -1:
    #                                                             # if the column is foreign key column, create sub children
    #                                                             # Foreign key tables this deep are not present for Turkana case
    #                                                             # col is a lookup column
    #                                                             if col2[:-3] not in pg_tables():
    #                                                                 child3 = QStandardItem('{}: {}'.format(
    #                                                                         format_name(col2[:-3]),
    #                                                                         lookup_id_to_value(self.current_profile, col2, row2)
    #                                                                     )
    #                                                                 )
    #                                                                 child2.appendRow([child3])
    #                                                          # if it is other column show data as is
    #                                                         else:
    #                                                             child3 = QStandardItem('{}: {}'.format(
    #                                                                     format_name(col2),
    #                                                                     row2
    #                                                                 )
    #                                                             )
    #                                                             child2.appendRow([child3])
    #                                             child1.appendRow([child2])
    #                                         # If not fk column
    #                                         else:
    #                                             child2 = QStandardItem('{}: {}'.format(
    #                                                     format_name(col),
    #                                                     row
    #                                                 )
    #                                             )
    #                                             child1.appendRow([child2])
    #                         parent.appendRow([child1])
    #
    # def add_steam(self, child, parent, str_record, parent_name=None, spatial_unit_id = None, external_table = None):
    #     """
    #     Creates a node with children into a parent node.
    #     :param child: node to be added
    #     :type QStandardItem
    #     :param parent: node to hold the child
    #     :type QStandardItem
    #     :param str_record: data used to populate the tree
    #     :type sqlalchemy result proxy
    #     :param parent_name: The label to be added under parent.
    #     :type: String
    #     :param spatial_unit_id: The id of the selected feature
    #     :type: Integer
    #     :param external_table: list of external tables
    #     using the feature id as foreign key.
    #     :type: List
    #     :return: None
    #     """
    #     parent.appendRow([child])
    #     self.create_details_tree(str_record, child,  parent_name, spatial_unit_id, external_table)

    def expand_node(self, parent):
        """
        Make the last tree node expand.
        :param parent: The parent to expand
        :type QStandardItem
        :return:None
        """
        index = self.model.indexFromItem(parent)
        self.view.expand(index)


    def multi_select_highlight(self, index):
        """
        Highlights a feature with rubberBald class when selecting
        features are more than one.
        :param index: Selected QTreeView item index
        :type Integer
        :return: None
        """
        map = self.iface.mapCanvas()
        try:
            # Get the selected item text using the index
            selected_item = self.model.itemFromIndex(index).text()
            # Split the text to get the key and value.
            selected_item = selected_item.split()
            selected_key = selected_item[0]
            selected_value = selected_item[1]
            # If the first word is feature, expand & highlight.
            if selected_key == "Feature":
                self.view.expand(index)  # expand the item
                # Clear any existing highlight
                self.clear_sel_highlight()
                # Insert highlight
                # Create expression to target the selected feature
                expression = QgsExpression(
                    "\"id\"='" + selected_value + "'"
                )
                # Get feature iteration based on the expression
                ft_iteration = self.layer.getFeatures(
                    QgsFeatureRequest(expression)
                )

                # Retrieve geometry and attributes
                for feature in ft_iteration:
                    # Fetch geometry
                    geom = feature.geometry()
                    self.sel_highlight = QgsHighlight(map, geom, self.layer)

                    self.sel_highlight.setFillColor(QColor(255, 128, 0))
                    self.sel_highlight.setWidth(3)
                    self.sel_highlight.show()
                    break
        except AttributeError:
            # pass attribute error on child items such as party
            pass
        except IndexError:
            pass
