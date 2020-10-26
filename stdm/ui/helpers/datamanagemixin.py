from qgis.PyQt.QtWidgets import (
    QDialogButtonBox,
    QApplication
)

from stdm.ui.admin_unit_manager import MANAGE,VIEW,SELECT

class SupportsManageMixin(object):
    '''
    Mixin class for those dialogs that support data viewing and managing modes.
    It assumes that the dialog has SAVE,CLOSE, CANCEL buttons in the buttonbox.
    '''
    def __init__(self, mode=MANAGE):
        self._mode = mode
        self._onStateChanged()

    def setManageMode(self,enableManage):
        '''
        :param enableManage: True to set the selector to manage mode or false to disable i.e.
        for viewing purposes only.
        '''
        if enableManage:
            self._mode = MANAGE

        else:
            self._mode = VIEW

        self._onStateChanged()

    def _onStateChanged(self):
        '''
        Configure controls upon changing the state of the widget.
        '''
        if self._mode == SELECT:
            self.buttonBox.button(QDialogButtonBox.Save).setText(
                QApplication.translate(
                    "SupportsManageMixin",
                    "Select")
            )
            self.buttonBox.button(QDialogButtonBox.Save).setVisible(True)
            self.buttonBox.button(QDialogButtonBox.Cancel).setVisible(False)
            self.buttonBox.button(QDialogButtonBox.Close).setVisible(True)

        else:
            self.buttonBox.button(QDialogButtonBox.Save).setVisible(False)
            self.buttonBox.button(QDialogButtonBox.Cancel).setVisible(False)
            self.buttonBox.button(QDialogButtonBox.Close).setVisible(True)















