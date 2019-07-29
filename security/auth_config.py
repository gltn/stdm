"""
/***************************************************************************
Name                 : Authentication Configuration
Description          : Provides util functions for accessing QGIS's
                       authentication configuration.
Date                 : 23/June/2019
copyright            : (C) 2019 by UN-Habitat and implementing partners.
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
from qgis.core import (
    QgsAuthManager,
    QgsAuthMethodConfig
)


def config_entries():
    """
    :return: Returns a list of tuples with each tuple containing the ID
    and name of an authentication configuration entry stored in QGIS's
    authentication framework.
    :rtype: list
    """
    auth_configs = []
    auth_mgr = QgsAuthManager.instance()
    conf_map = auth_mgr.availableAuthMethodConfigs()
    for id, conf in conf_map.iteritems():
        name = conf.name()
        auth_configs.append((id, name))

    return auth_configs


def auth_config_from_id(config_id):
    """
    Gets authentication configuration object containing the username and
    password for the configuration object with the given ID.
    :param config_id: Configuration ID stored in the QGIS authentication
    framework.
    :return: Returns a QgsAuthMethodConfig object containing the username
    and password else None if the configuration ID is invalid.
    :rtype: QgsAuthMethodConfig
    """
    auth_mgr = QgsAuthManager.instance()
    if not config_id in auth_mgr.configIds():
        return None

    # Object containing authentication information
    auth_config = QgsAuthMethodConfig()
    status, auth_config = auth_mgr.loadAuthenticationConfig(
        config_id,
        auth_config,
        True
    )
    if not status:
        return None

    return auth_config