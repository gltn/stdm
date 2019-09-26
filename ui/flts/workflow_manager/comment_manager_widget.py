from PyQt4.QtGui import *
from sqlalchemy import exc
from stdm.ui.flts.workflow_manager.model import WorkflowManagerModel
from stdm.ui.flts.workflow_manager.ui_comment_manager import Ui_CommentManagerWidget


class CommentManagerWidget(QWidget, Ui_CommentManagerWidget):
    """
    Manages scheme user comments in the Scheme Lodgment, Scheme Establishment
    and First, Second and Third Examination FLTS modules
    """
    def __init__(self, detail_service, profile, scheme_id, parent=None):
        super(QWidget, self).__init__(parent)
        self.setupUi(self)
        self._load_collections = detail_service['load_collections']
        data_service = detail_service['data_service']
        data_service = data_service(profile, scheme_id)
        self.model = WorkflowManagerModel(data_service)
        self.setObjectName("Comments")
        self._initial_load()

    def _initial_load(self):
        """
        Initial table view data load
        """
        try:
            if self._load_collections:
                self.model.load_collection()
            else:
                self.model.load()
            print(0)
        except (exc.SQLAlchemyError, Exception) as e:
            QMessageBox.critical(
                self,
                self.tr('{} Entity Model'.format(self.model.entity_name)),
                self.tr("{0} failed to load: {1}".format(
                    self.model.entity_name, e
                ))
            )
