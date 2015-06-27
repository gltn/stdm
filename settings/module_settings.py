"""
/***************************************************************************
 stdmDialog
                                 A QGIS plugin
 Securing land and property rights for all
                             -------------------
        begin                : 2014-03-04
        copyright            : (C) 2014 by GLTN
        email                : gltn_stdm@unhabitat.org
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
from PyQt4.QtGui import *
class ModuleSettings(object):
    def __init__(self):
        """
        class to provide translation for configuration file text
        :return:
        """

    QApplication.translate("STDMQGISLoader","Party")
    QApplication.translate("STDMQGISLoader","Supporting Document")
    QApplication.translate("STDMQGISLoader","Household")
    QApplication.translate("STDMQGISLoader","spatial Unit")
    QApplication.translate("STDMQGISLoader","Social Tenure Relationship")