import os, sys
from sqlalchemy import *
from sqlalchemy import create_engine, MetaData
#import stdm.data
#from data.tableObject import *
#from data.database import Model
#model=Model()
from xmlconfig_reader import XMLtableObject,tableColumns,tableRelations,AllColumns

header="from sqlalchemy import *\nfrom sqlalchemy import create_engine, MetaData\n\n"\
"from sqlalchemy import Column, Date, Integer, String ,Numeric,Text,Boolean\nfrom qtalchemy import UserAttr\n"\
"from sqlalchemy.orm import relationship, backref\nimport datetime\n\n"

#TEMPLATE="\nclass %s(Model, Base):\n"
TEMPLATE="\nclass %s(object):\n" 
TAB="\t__tablename__ ='%s'\n"
COL="\t%s=UserAttr(%s)\n"
RELATION="\t%s=relationship('%s',backref='%s')\n"

file_temp=os.path.dirname(os.path.abspath(__file__))
python_obj=str(file_temp).replace("\\", "/")+"/tableObject.py"

def createtableObject():
    table=XMLtableObject()
    data=""
    with open(python_obj,"w") as of: 
        of.write(header)
        #of.write(model)
        for t in table:
            #list=readColumnDef(t)
            data=''.join(TEMPLATE %t)
            of.write(data)
            # of.write(TAB %t)
            cols=AllColumns(t)
            for colD in cols:
                colName=str(colD.get('Column label'))
                of.write(COL %(colName,schemaDefualtsTypetoQtAlchemy(colName,colD.get('Data type'),colD.get('Length'))))
            rels=tableRelations(t)
            if rels!=None:
                for rel in rels:
                    of.write(RELATION %(rel.get('Relation Name'), rel.get('Relation to table'),t))
    of.close()
    

def stringFormater(name):
    if name=="integer":
        name='int'
    if name=="character varying":
        name='str'
    if name=="serial":
        name="int"
    if name=="date":
        name='datetime.date'
    return name

def schemaDefualtsTypetoQtAlchemy(colID,colType,size):
    #datalen=""
    if stringFormater(colType)=='int':
        datalen="int,'%s'"%colID
    if stringFormater(colType)=="str":
        datalen="str,'%s'"%(colID)
    if stringFormater(colType)=="datetime.date":
        datalen="datetime.date,'%s'"%colType
    #else:
        #datalen="str,'%s'"%colID
    return datalen

def schemaDefualtsTypetoSQLAlchemy(colID,colType,size):
    datalen=""
    if colID=='id'.lower() and stringFormater(colType)=="int":
        datalen="int"
    if stringFormater(colType)=="int" and colID=="id":
        datalen="int"
    if stringFormater(colType)=="str":
        datalen="'%s',str(%s)"%(colID,size)
    else:
        datalen="'%s'"%colID+","+str(colType).capitalize()
    return datalen


if "__main__"==__name__:
    createtableObject()
    #tableRelations('household')
    