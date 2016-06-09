"""
/***************************************************************************
Name                 : Widget factories
Description          : Creates appropriate widgets based on column type.
Date                 : 8/June/2016
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

from PyQt4.QtGui import (
    QLineEdit,
    QTextEdit,
    QWidget
)

from stdm.data.configuration.columns import (
    BaseColumn,
    TextColumn,
    VarCharColumn
)

class ColumnWidgetRegistry(object):
    """
    Base container for widget factories based on column types. It is used to
    create widgets based on column type.
    """
    registered_factories = OrderedDict()

    COLUMN_TYPE_INFO = 'NA'
    _TYPE_PREFIX = ''

    @classmethod
    def register(cls):
        """
        Adds the widget factory to the collection based on column type info.
        :param cls: Column widget factory class.
        :type cla: ColumnWidgetRegistry
        """
        ColumnWidgetRegistry.registered_factories[cls.COLUMN_TYPE_INFO] = cls

    @classmethod
    def create(cls, c, parent=None):
        """
        Creates the appropriate widget based on the given column type.
        :param c: Column object for which to create a widget for.
        :type c: BaseColumn
        :param parent: Parent widget.
        :type parent: QWidget
        :return: Returns a widget for the given column type only if there is
        a corresponding factory in the registry, otherwise returns None.
        :rtype: QWidget
        """
        factory = ColumnWidgetRegistry.factory(c.TYPE_INFO)

        if not factory is None:
            return factory._create_widget(c, parent)

        return None

    @classmethod
    def factory(cls, type_info):
        """
        :param type_info: Type info of a given column.
        :type type_info: str
        :return: Returns a widget factory based on the corresponding type
        info, otherwise None if there is no registered factory with the given
        type_info name.
        """
        return ColumnWidgetRegistry.registered_factories.get(
                type_info,
                None
        )

    @classmethod
    def _create_widget(cls, c, parent):
        #For implementation by sub-classes to create the appropriate widget.
        raise NotImplementedError


class VarCharWidgetFactory(ColumnWidgetRegistry):
    """
    Widget factory for VarChar column type.
    """
    COLUMN_TYPE_INFO = VarCharColumn.TYPE_INFO
    _TYPE_PREFIX = 'le_'

    @classmethod
    def _create_widget(cls, c, parent):
        le = QLineEdit(parent)
        le.setObjectName(u'{0)_{1}'.format(cls._TYPE_PREFIX, c.name))
        le.setMaxLength(c.maximum)

        return le

VarCharWidgetFactory.register()


class TextWidgetFactory(ColumnWidgetRegistry):
    """
    Widget factory for Text column type.
    """
    COLUMN_TYPE_INFO = TextColumn.TYPE_INFO
    _TYPE_PREFIX = 'txt_'

    @classmethod
    def _create_widget(cls, c, parent):
        te = QTextEdit(parent)
        te.setObjectName(u'{0)_{1}'.format(cls._TYPE_PREFIX, c.name))

        return te

TextWidgetFactory.register()

