"""
/***************************************************************************
Name                 : Third Examination Wizard
Description          : Dialog for performing third examination  on a scheme.
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
from PyQt4.QtCore import (
    Qt
)

from PyQt4.QtGui import (
    QWizard
)

from ui_third_examination import Ui_ThirdExam_Wzd


class ThirdExaminationWizard(QWizard, Ui_ThirdExam_Wzd):
    """
    Performing the third examination on a scheme
    """
    def __init__(self, parent=None):
        QWizard.__init__(self, parent)

        self.setupUi(self)
