from PyQt4.QtCore import *
from PyQt4.QtGui import *
from sqlalchemy import exc


class WorkflowManagerModel(QAbstractTableModel):

    def __init__(self, entity_model):
        super(WorkflowManagerModel, self).__init__()
        self._entity_model = entity_model
        self.results = None

    def load(self):
        exception = None
        try:
            entity_object = self._entity_model()
            self.results = entity_object.queryObject().order_by(self._entity_model.id).all()
        except exc.SQLAlchemyError as sql_error:
            exception = sql_error
        except Exception as e:
            exception = e
        finally:
            if exception:
                raise exception

