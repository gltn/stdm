"""
/***************************************************************************
Name                 : Advanced Search
Description          : Advanced Search form.
Date                 : 10/June/2018
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
from collections import OrderedDict
import uuid
from PyQt4.QtCore import (
    Qt,
    pyqtSignal
)

from PyQt4.QtGui import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QGridLayout,
    QLabel,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QApplication,
    QPushButton
)

from stdm.ui.admin_unit_manager import VIEW,MANAGE,SELECT

from stdm.data.configuration import entity_model
from stdm.data.configuration.entity import Entity
from stdm.data.configuration.columns import (
    MultipleSelectColumn,
    VirtualColumn
)
from stdm.data.mapping import MapperMixin
from stdm.data.pg_utils import table_column_names
from stdm.utils.util import format_name
from stdm.ui.forms.widgets import (
    ColumnWidgetRegistry,
    UserTipLabel
)

from stdm.ui.forms.documents import SupportingDocumentsWidget
from stdm.ui.notification import NotificationBar

from editor_dialog import EntityEditorDialog

class AdvancedSearch(EntityEditorDialog):
    def __init__(self, entity, parent):

        EntityEditorDialog.__init__(self, entity, parent=parent)
