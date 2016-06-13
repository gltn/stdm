"""
/***************************************************************************
Name                 : Widget factories
Description          : Creates appropriate form widgets for an entity.
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
    QLabel,
    QLineEdit,
    QPixmap,
    QTextEdit,
    QWidget
)

from stdm.data.configuration.columns import (
    BaseColumn,
    TextColumn,
    VarCharColumn
)

class UserTipLabel(QLabel):
    """
    Custom label that shows an information icon and a tip containing the
    column user tip value as specified in the configuration.
    """
    def __init__(self, parent=None, user_tip=None):
        QLabel.__init__(self, parent)

        #Set tip icon
        self._set_tip_icon()

        #Initialize user tip
        if user_tip is None:
            self._user_tip = ''
        else:
            self._user_tip = user_tip
            self._update_tip()

    def _set_tip_icon(self):
        #Set the information icon
        self._px = QPixmap(':/plugins/stdm/images/icons/user_tip.png')
        self.setPixmap(self._px)

    def pixmap(self):
        """
        :return: Returns the pixmap object associated with this label.
        Overrides the default implementation.
        :rtype: QPixmap
        """
        return self._px

    @property
    def user_tip(self):
        """
        :return: Returns the user tip corresponding to this label.
        :rtype: str
        """
        return self._user_tip

    @user_tip.setter
    def user_tip(self, value):
        """
        Sets the user tip for this label.
        :param value: User tip text.
        :type value: str
        """
        if not value:
            return

        self._user_tip = value
        self._update_tip()

    def _update_tip(self):
        #Update the tooltip for this label with the value of the 'user-tip var.
        self.setToolTip(self._user_tip)

class ColumnWidgetRegistry(object):
    """
    Base container for widget factories based on column types. It is used to
    create widgets based on column type.
    """
    registered_factories = OrderedDict()

    COLUMN_TYPE_INFO = 'NA'
    _TYPE_PREFIX = ''

    def __init__(self, column):
        """
        Class constructor.
        :param column: Column object corresponding to the widget factory.
        :type column: BaseColumn
        """
        self._column = column

    @property
    def column(self):
        """
        :return: Returns column object associated with this factory.
        :rtype: BaseColumn
        """
        return self._column

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

    def value_formatter(self, value):
        """
        Formats the column value to a more friendly display value. Should be
        implemented by sub-classes for custom behavior.
        :return: Returns a more user-friendly display.
        :rtype: str
        """
        return unicode(value)


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

