"""
/***************************************************************************
Name                 : ComposerPhotoDatSourceEditor
Description          : Widget for specifying data properties for photos in
                       the document designer.
Date                 : 9/December/2014
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
from PyQt4.QtGui import (
    QWidget
)
from PyQt4.QtCore import QRegExp

from qgis.core import QgsComposerPicture

from stdm.data import supporting_doc_tables_regexp

from ..notification import (
                             NotificationBar,
                             ERROR
                             )
from .referenced_table_editor import LinkedTableProps
from .ui_composer_photo_data_source import Ui_PhotoDataSourceEditor

class ComposerPhotoDataSourceEditor(QWidget, Ui_PhotoDataSourceEditor):
    def __init__(self, composer_wrapper, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)

        self._composer_wrapper = composer_wrapper

        self._notif_bar = NotificationBar(self.vl_notification)

        #Load fields if the data source has been specified
        ds_name = self._composer_wrapper.selectedDataSource()
        self.ref_table.load_data_source_fields(ds_name)

        '''
        Load referenced table list and filter so to only load supporting
        doc tables.
        '''
        self.ref_table.load_link_tables(supporting_doc_tables_regexp())

        #Connect signals
        self._composer_wrapper.dataSourceSelected.connect(self.ref_table.on_data_source_changed)

    def composer_item(self):
        return self._picture_item

    def configuration(self):
        from stdm.composer import PhotoConfiguration

        linked_table_props = self.ref_table.properties()

        ph_config = PhotoConfiguration()
        ph_config.set_linked_table(linked_table_props.linked_table)
        ph_config.set_source_field(linked_table_props.source_field)
        ph_config.set_linked_column(linked_table_props.linked_field)

        return ph_config

    def set_configuration(self, configuration):
        #Load referenced table editor with item configuration settings.
        photo_props = LinkedTableProps(linked_table=configuration.linked_table(),
                                source_field=configuration.source_field(),
                                linked_field=configuration.linked_field())

        self.ref_table.set_properties(photo_props)