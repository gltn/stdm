from xml2ddl import Xml2Ddl, readMergeDict
#from xml2html import Xml2Html, xml2ddl
sourcePath="C:/test/stdmConfig.xml"
def writeXml(source, dest, dropTable=True):
    cd = Xml2Ddl()
    cd.setDbms("postgres")
    cd.params['drop-tables'] = dropTable
    cd.params['add_key_constraint']=dropTable
           
    #strFilename = path
    xml = readMergeDict(source)
    results = cd.createTables(xml)
    fileN=open(dest,"w")
    for result in results:
        #print result
        fileN.write(result[1])
        fileN.write("\n")

    fileN.close()
    
#def writeHTML():
#    #Generate a html file from the configuration xml
#    x2h = Xml2Html()
#    strFilename = sourcePath
#    xml = xml2ddl.readMergeDict(strFilename)
#    lines = x2h.outputHtml(xml)
#    strOutfile = "C:/test/stdm_schema.html"
#        
#    of = open(strOutfile, "w")
#    for line in lines:
#        of.write("%s\n" % (line))
#    of.close()

def testWriteXml():
    sourcePath="C:/test/stdmConfig.xml"
    destPath="C:/test/stdmConfig.sql"
    writeXml(sourcePath, destPath)

if __name__ == "__main__":
    testWriteXml()
    #writeHTML()
    