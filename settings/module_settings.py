"""
/***************************************************************************
Name                 : Module Settings
Description          : GUI classes for managing and viewing supporting
                       documents.
Date                 : 04/03/2014
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
from PyQt4.QtGui import QApplication


class ModuleSettings(object):

    def __init__(self):
        """
        class to provide translation for configuration file text
        :return:
        """

    QApplication.translate("STDMQGISLoader", "Party")
    QApplication.translate("STDMQGISLoader", "Supporting Document")
    QApplication.translate("STDMQGISLoader", "Household")
    QApplication.translate("STDMQGISLoader", "spatial Unit")
    QApplication.translate("STDMQGISLoader", "Social Tenure Relationship")
