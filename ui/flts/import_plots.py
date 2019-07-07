"""
/***************************************************************************
Name                 : Import Plots Dialog
Description          : Dialog for importing plots in FLTS.
Date                 : 03/July/2019
copyright            : (C) 2019 by Joseph Kariuki
email                : joehene@gmail.com
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
from PyQt4 import Qt
from PyQt4.QtGui import (
    QWizard
)

from ui_import_plots import Ui_frmImportPlot


class ImportPlotWizard(QWizard, Ui_frmImportPlot):
    """
    Importing plots into the system
    """

    def __init__(self, parent=None):
        QWizard.__init__(self, parent)
        self.setupUi(self)


if __name__ == '__main__':
    import sys

    app = QWizard.QApplication(sys.argv)
    import_plots = QWizard()
    import_plots.show()
    sys.exit(app.exec_())
