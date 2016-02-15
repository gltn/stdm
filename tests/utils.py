import sys

from PyQt4.QtGui import QWidget
from PyQt4.QtCore import (
    QCoreApplication,
    QSize
)

from qgis.core import QgsApplication
from qgis.gui import QgsMapCanvas

#Static variable used to hold hand to running QGIS app
QGIS_APP = None
CANVAS = None
PARENT = None


def qgis_app():
    """
    Start QGIS application to test against. Based on code from Inasafe plugin.
    :return: Reference to QGIS application, canvas and parent widget.
    :rtype:(QgsApplication, QWidget, QgsMapCanvas)
    """
    global QGIS_APP

    if QGIS_APP is None:
        gui_flag = True

        QCoreApplication.setOrganizationName('QGIS')
        QCoreApplication.setOrganizationDomain('qgis.org')
        QCoreApplication.setApplicationName('STDM_Testing')

        QGIS_APP = QgsApplication(sys.argv, gui_flag)
        QGIS_APP.initQgis()

    global PARENT
    if PARENT is None:
        PARENT = QWidget()

    global CANVAS
    if CANVAS is None:
        CANVAS = QgsMapCanvas(PARENT)
        CANVAS.resize(QSize(400, 400))

    return QGIS_APP, CANVAS, PARENT