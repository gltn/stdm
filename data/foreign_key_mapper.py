from qtalchemy.dialogs import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from sqlalchemy import MetaData, Table, Column, Integer, ForeignKey
from sqlalchemy.orm import mapper, relationship , clear_mappers
from stdm.data import STDMEntity, STDMDb
from qtalchemy.foreign_key import ForeignKeyReferral
from stdm_entity import LookupTable
import qtalchemy
class ForeignKey(object):
    pass

class ForeignRelationMapper(object):
    def __init__(self):
        self.engine=STDMDb.instance().engine
        self.metadata=MetaData(bind=self.engine)
        
    def referenceTable(self):
        backref=Table('household',self.metadata, autoload=True)
        return backref
    
    def mapperInstance(self,table):
        #self.lookup=self.referenceTable()
        #clear_mappers()
        mapper(LookupTable,table)  
        

class LookupEntity(object):
    def __init__(self,session,parent):
        Session = STDMDb.instance().session
        self.Session = Session()
        self.parent = parent

        self.table_cls = LookupTable
        self.key_column = LookupTable.id
        self.list_display_columns = [LookupTable.rent,LookupTable.income]
        self.list_search_columns = [LookupTable.rent,LookupTable.income]

    itemCommands = qtalchemy.CommandMenu('_item_commands')

    def list_query_converter(self):
        from sqlalchemy.orm import Query
        queryCols = tuple([self.key_column.label('_hidden_id')] + self.list_display_columns)
        return (Query(queryCols).order_by(LookupTable.rent, self.key_column), lambda x: x._hidden_id)

    @itemCommands.itemNew()
    def new(self, id=None):
        session = self.Session()
        a = self.table_cls()
        session.add(a)
        aa = LookupEditor(self.parent, Session=self.Session, row=a)
        aa.show()
        aa.exec_()
        session.close()

class LookupEditor(BoundDialog):
    def __init__(self, parent, row=None, Session=None, row_id=None, flush=True):
        super(LookupEditor, self).__init__(parent)

        self.setDataReader(Session, LookupTable, 'id')
        self.mm = self.mapClass(LookupTable)

        main = QVBoxLayout(self)
        self.mm.addBoundForm(main, ['income','rent'])

        QDB = QDialogButtonBox
        buttonbox = qtalchemy.LayoutWidget(main, QDB(QDB.Ok | QDB.Cancel))
        buttonbox.accepted.connect(self.accept)
        buttonbox.rejected.connect(self.reject)

        self.readData(row, row_id)

    def load(self):
        self.mm.connect_instance(self.main_row)