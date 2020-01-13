"""
/***************************************************************************
Name                 : STDM Settings Mapping Classes
Description          : Classes that enable the mapping of STDM settings
                       to the corresponding UI widgets for rapid
                       building of settings' widgets.
Date                 : 16/September/2014
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
    QWidget,
    QApplication
)

from stdm.ui.notification import (
    ERROR,
    WARNING,
    SUCCESS
)

from .registryconfig import RegistryConfig


class SettingMapper(object):
    """
    Represents a single mapping of an STDM setting and corresponding UI widget.
    """

    def __init__(self, setting_key, widget, mandatory=False,
                 create_default=True, custom_value_handler=None,
                 get_func=None, set_func=None):
        """
        :param setting_key: Name or path of the configuration key.
        :type setting_key: str
        :param widget: Instance of a Qt Widget.
        :type widget: QWidget
        :param create_default: True to create a default setting if not found;
        False to skip creation - In this case, the mapper will be excluded when
        setting the configuration value.
        :type create_default: bool
        :param custom_value_handler: Instance of a custom value handler can be provided if it does not exist amongst
        those in the registered list.
        :type custom_value_handler: ControlValueHandler
        :param get_func: Function to filter or reformat the return value of the control when 'bindModel' function
        is called.
        :param set_func: Function to filter or reformat a model's values when 'bind_control' function
        is called.
        :param mandatory: Flag to indicate whether a value is required from the input control.
        :type mandatory: bool
        """
        from stdm.ui.helpers import (
            valueHandler,
            ControlValueHandler
        )
        self._key = setting_key
        self._control = widget
        self._create_default = create_default
        self._get_func = get_func
        self._set_func = set_func
        self._mandatory = mandatory

        if not custom_value_handler is None:
            self._value_handler = custom_value_handler()

        else:
            self._value_handler = valueHandler(self._control)()

        if not self._value_handler is None:
            self._value_handler.setControl(self._control)

    def setting_key(self):
        """
        :return: Name or path of the configuration key.
        :rtype: str
        """
        return self._key

    def set_configuration_key(self, key):
        """
        Set name or path of the configuration key.
        :param key: name or path of the configuration key.
        :type key: str
        """
        self._key = key

    def is_mandatory(self):
        """
        :return: 'True' if the key is mandatory; else, 'False'.
        :rtype: False
        """
        return self._mandatory

    def control(self):
        """
        :return: Instance of Qt input widget associated with the mapper.
        :rtype: QWidget
        """
        return self._control

    def value_handler(self):
        """
        :return: Handler for reading/writing the given control's value.
        :rtype: ControlValueHandler
        """
        return self._value_handler

    def has_key(self):
        """
        :return: Check whether the configuration key exists.
        :rtype: bool
        """
        raise NotImplementedError

    def create_key(self):
        """
        Create the configuration key. If there is an existing, its value will
        be overridden.
        :return: True if the key was successfully created; False if it was not.
        :rtype: bool
        """
        raise NotImplementedError

    def configuration_value(self):
        """
        :return: Value of the configuration key. To be implemented by subclasses.
        :rtype: object
        """
        raise NotImplementedError

    def set_configuration_value(self):
        """
        Set the value of the configuration key using the control value.
        """
        raise NotImplementedError

    def bind_control(self):
        """
        Set the value of the control using the configuration's key value.
        """
        conf_value = self.configuration_value()

        if not conf_value is None:
            self._value_handler.setValue(conf_value, self._set_func)

    def bind_configuration_value(self):
        """
        Set the configuration value to the control's value. The handler is
        responsible for adapting the type as required by the setting.
        """
        if not self.has_key() and not self._create_default:
            return

        if not self.has_key() and self._create_default:
            if not self.create_key():
                return

        self.set_configuration_value()


class RegistrySettingMapper(SettingMapper):
    """
    Mapper that uses the registry as the settings repository.
    """

    def __init__(self, *args, **kwargs):
        SettingMapper.__init__(self, *args, **kwargs)
        self._reg_config = RegistryConfig()

    def has_key(self):
        key_mappings = self._reg_config.read([self._key])

        if len(key_mappings) == 0:
            return False

        else:
            return True

    def configuration_value(self):
        if not self.has_key():
            return None

        key_mappings = self._reg_config.read([self._key])

        return key_mappings[self._key]

    def create_key(self):
        # A new key will automatically be created when you set the value.
        return True

    def set_configuration_value(self):
        conf_value = self._value_handler.value(self._get_func)
        self._reg_config.write({self._key: conf_value})


class SettingsWidgetMapper(object):
    """
    Mixin class that enables settings' widgets/dialogs to conveniently read/write
    application settings using a standard approach.
    """

    def __init__(self, context, parent=None):
        """
        :param context: One or two words that summarize the collection of
        configuration settings e.g. Database, document repository, etc.
        :type context: str
        """
        self._context = context
        self._settings_mappers = []

    def context(self):
        """
        :return: Word(s) that summarize the collection of configuration settings
        """
        return self._context

    def add_mapping(self, *args, **kwargs):
        """
        Map a settings key to a QWidget.
        :param args: keyname and corresponding Qt widget.
        :param kwargs: See arguments in the SettingsMapper class
        """
        mapper = kwargs.pop("mapper", None)

        # Use registry mapper if not specified
        if mapper is None:
            mapper = RegistrySettingMapper

        s_mapper = mapper(*args, **kwargs)

        self.add_settings_mapper(s_mapper)

    def add_settings_mapper(self, mapper):
        """
        Add a settings mapper to the widget-wide collection.
        :param mapper: Subclass of a SettingsMapper.
        :type mapper: SettingMapper
        """
        if not isinstance(mapper, SettingMapper):
            return

        mapper.bind_control()
        self._settings_mappers.append(mapper)

    def _capitalize_first_char(self, context):
        if len(context) == 0:
            return

        first_char = context[0]
        other_chars = context[1:]

        return first_char.upper() + other_chars.lower()

    def apply(self):
        """
        Persists the settings specified by the user.
        """
        for s in self._settings_mappers:
            if s.is_mandatory() and s.valueHandler().supportsMandatory():
                if s.valueHandler().value() == s.valueHandler().default():
                    # Notify user
                    msg = WARNING, u"{0} is a required setting.".format(s.setting_key())
                    self.notified.emit([msg])

                    break

            s.bind_configuration_value()

        msg = SUCCESS, QApplication.translate("SettingsWidgetMapper",
                                              "%s settings successfully updated." % (
                                              self._capitalize_first_char(self._context),))
        self.notified.emit([msg])
