"""
/***************************************************************************
Name                 : TranslatorDialogBase
Description          : Abstract class for implementation by translator dialog.
                       Basically ensures that an instance of a source value
                       translator is returned.
Date                 : 24/October/2014
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

from stdm.data.importexport.value_translators import ValueTranslatorManager
from stdm.settings import current_profile
from stdm.utils.util import (
    profile_user_tables
)

__all__ = ["TranslatorDialogBase", "TranslatorWidgetManager"]


class TranslatorDialogBase(object):
    """
    Abstract class for implementation by translator dialog. Basically ensures
    that an instance of a source value translator is returned.
    """

    def __init__(self,source_cols, dest_table, 
                 dest_col, src_col):
        self._source_cols = source_cols
        self._dest_table = dest_table
        self._dest_col = dest_col
        self._src_col = src_col
        self._current_profile = current_profile()
        self._config_key = ""

    def source_columns(self):
        """
        :return: Columns names in the source table.
        :rtype: list
        """
        return self._source_cols

    def entity(self):
        """
        :return: Returns the entity object corresponding to the destination
        table.
        :rtype: Entity
        """
        if self._current_profile is None:
            return None

        return self._current_profile.entity_by_name(
            self._dest_table
        )

    def selected_source_column(self):
        """
        :return: The currently selected source column.
        """
        return self._src_col

    def destination_table(self):
        """
        :return: Name of the selected destination table.
        :rtype: str
        """
        return self._dest_table

    def destination_column(self):
        """
        :return: Name of the selected destination column.
        :rtype: str
        """
        return self._dest_col

    def config_key(self) -> str:
        return self._config_key

    def value_translator(self):
        """
        :return: Instance of a source value translator object.
        :rtype: SourceValueTranslator
        """
        raise NotImplementedError

    def db_tables(self):
        """
        Returns both textual and spatial table names.
        """
        curr_profile = current_profile()

        tables = list(profile_user_tables(
            self._current_profile,
            False,
            True
        ).keys())

        return tables

    def set_config_key(self, config_key: str):
        self._config_key = config_key

    def config_key(self) -> str:
        return self._config_key


class TranslatorWidgetManager(object):
    """
    This class manages multiple instances of value translator widgets or
    dialogs.
    """

    def __init__(self, parent=None):
        self._parent = parent
        self._widgets = {}

    def add_widget(self, key, translator_widget):
        """
        Add translator widget to the collection.
        :param key: Widget identifier. In mose cases, this should be based
        on the destination column name.
        :type key: str
        :param translator_widget: Sub-class of
        :class: 'stdm.ui.importexport.TranslatorDialogBase' base class
        :type translator_widget: TranslatorDialogBase
        """
        if not isinstance(translator_widget, TranslatorDialogBase):
            raise TypeError("Instance of 'TranslatorDialogBase' expected.")

        self._widgets[key] = translator_widget

    def set_translators(self, translator_widgets):
        """
        Set the list of translator widgets to be used for this class instance.
        :param translator_widgets: Collection of subclasses of
        :class: 'stdm.ui.importexport.TranslatorDialogBase' base class.
        :type translator_widgets: dict
        """
        for key, translator_widget in translator_widgets:
            self.add_widget(key, translator_widget)

    def translator_widget(self, name):
        """
        :param name: Name of the referencing column.
        :return: Translator widget with the given name.
        :rtype: TranslatorDialogBase
        """
        return self._widgets.get(name, None)

    def clear(self):
        """
        Removes all translator widgets from the collection.
        """
        self._widgets = {}

    def widgets(self) -> dict:
        return self._widgets

    def remove_translator_widget(self, name):
        """
        Removes a translator widget with the given name from the collection.
        :param name: Name of the referencing column.
        :type name:str
        :return: 'True' if a widget with the corresponding name was found, 'False'
        if not found.
        :rtype: bool
        """
        if not self.translator_widget(name) is None:
            del self._widgets[name]

            return True

        return False

    def translator_manager(self):
        """
        :return: Returns an instance of a
        'stdm.data.importexport.ValueTranslatorManager' class based on the
        translators in the widgets contained in this class.
        """
        trans_mgr = ValueTranslatorManager(self._parent)

        translators = [trans_widg.value_translator() for trans_widg in self._widgets.values()]
        trans_mgr.set_translators(translators)

        return trans_mgr
