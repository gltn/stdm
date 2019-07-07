"""
/***************************************************************************
Name                 : Scheme Revision Wizard
Description          : Dialog for revising a scheme.
Date                 : 02/July/2019
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

from ui_scheme_revision import Ui_revision_Wzd


class SchemeRevisionWizard(QWizard, Ui_revision_Wzd):
    """
    Revision of a scheme fo fix any previously detected errors
    """

    def __init__(self, parent=None):
        QWizard.__init__(self, parent)

        self.setupUi(self)


if __name__ == '__main__':
    import sys

    app = QWizard.QApplication(sys.argv)
    scheme_revision = SchemeRevisionWizard()
    scheme_revision.show()
    sys.exit(app.exec_())
