from qtalchemy import UserAttr
import datetime
from PySide import QtCore, QtGui
from qtalchemy import MapperMixin, LayoutLayout, ButtonBoxButton, LayoutWidget, Message
from qtalchemy import MapperMixin
from tableObject import *
from xmlconfig_reader import XMLTableElement,tableColumns,tableRelations

#     @age.on_get
#     def age_getter(self):
#         return (datetime.date.today()-self.birth_date).days


class ContentView(QtGui.QDialog, MapperMixin):
    def __init__(self,parent,content, cols):
        QtGui.QDialog.__init__(self,parent)
        MapperMixin.__init__(self)
        
        self.content=content
        self.cols=cols
        self.setWindowTitle("Person")
        
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
       
        #self.move((screen.width()-size.width())/2,(screen.height()-size.height())/2)
        width=int((screen.width()-size.width())/2)
        height=int((screen.height()-size.height())/2)
        self.move(width,height)
        self.setGeometry(QtCore.QRect(width,height, width, height))
        
        vbox=QtGui.QVBoxLayout(self)
        top_grid = LayoutLayout(vbox,QtGui.QGridLayout())
        
        cols=tableColumns('source_document')
        colDoc=[]
        for col in cols:
            colDoc.append(col.get('Column label'))
        
        mm=self.mapClass(person)
        mm.addBoundForm(vbox,self.cols)
        mm.connect_instance(content)
        
        mm.addBoundFieldGrid(top_grid,"first_name",0,0)
        mm.addBoundFieldGrid(top_grid,"last_name",0,2)
        self.mm_account = self.mapClass(household)
        self.mm_doc = self.mapClass(source_document)
        
        self.tab = LayoutWidget(vbox,QtGui.QTabWidget())
        self.accounting_tab = QtGui.QWidget()
        self.mm_account.addBoundForm(QtGui.QVBoxLayout(self.accounting_tab),["id","previous_resdence","settlement_period"])
        self.tab.addTab( self.accounting_tab,"household" )
        
        self.doc_tab = QtGui.QWidget()
        self.mm_doc.addBoundForm(QtGui.QVBoxLayout(self.doc_tab),colDoc)
        self.tab.addTab( self.doc_tab,"documents" )
        
        buttons = LayoutWidget(vbox,QtGui.QDialogButtonBox())
        self.close_button = ButtonBoxButton(buttons,QtGui.QDialogButtonBox.Ok)
        self.close_button1 = ButtonBoxButton(buttons,QtGui.QDialogButtonBox.Cancel)
        self.close_button2 = ButtonBoxButton(buttons,QtGui.QDialogButtonBox.Save)
        buttons.accepted.connect(self.btnClose)
        buttons.accepted.connect(self.btnSave)
        
    
    def btnClose(self):
        self.submit() # changes descend to model on focus-change; ensure receiving the current focus
        self.close()
    
    def btnSave(self):
        self.submit() # changes descend to model on focus-change; ensure receiving the current focus
        
        self.close()

    def MessageButtonsToQt(self,flags):
        result = QtGui.QMessageBox.NoButton
        for x in "Ok Cancel Yes No".split(' '):
            if flags & getattr(Message, x):
                result |= getattr(QtGui.QMessageBox, x)
        return result

    def QtToMessageButtons(self,flags):
        result = 0
        for x in "Ok Cancel Yes No".split(' '):
            if flags & getattr(QtGui.QMessageBox, x):
                result |= getattr(Message, x)
        return result

# if "__main__"==__name__:
#     app=QtGui.QApplication([])
#     me=person()
#     tcols=[]
#     cols=tableColumns('person')
#     for colD in cols:
#         tcols.append(colD.get('Column label'))
#     tcols.remove("id")
#     tcols.remove("first_name")
#     tcols.remove("last_name")
#     d=ContentView(None,me,tcols)
#     d.exec_()
    
    