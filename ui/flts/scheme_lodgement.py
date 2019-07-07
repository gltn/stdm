"""
/***************************************************************************
Name                 : Scheme Lodgement Wizard
Description          : Dialog for lodging a new scheme.
Date                 : 01/July/2019
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
from PyQt4.QtGui import (
    QWizard
)

from ui_scheme_lodgement import Ui_LodgeScheme_Wzd


class LodgementWizard(QWizard, Ui_LodgeScheme_Wzd):
    """
    Wizard that incorporates lodgement of all information required for a Land Hold Title Scheme
    """

    def __init__(self, parent=None):
        QWizard.__init__(self, parent)
        self.setupUi(self)


if __name__ == '__main__':
    import sys

    app = QWizard.QApplication(sys.argv)
    wizard = LodgementWizard()
    wizard.show()
    sys.exit(app.exec_())
