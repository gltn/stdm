import platform 
import sys, os
import subprocess
import _winreg as reg

#call=subprocess.call(object)
def registryConn(path):
    #open handle to access the local computer and registry, none sets to  default to local computer
    RegConn = reg.ConnectRegistry(None,reg.HKEY_LOCAL_MACHINE)
    pgKey = reg.OpenKey(reg.HKEY_LOCAL_MACHINE,path)
    return pgKey

def registryPath():
    #Get qualified path of postgres installation from registry and return the last install path 
    rootPath=systemPath()
    pgKey=registryConn(rootPath)
    keyOption=[]
    try:
        for i in range(pgKey):
            keyOption.append(reg.EnumKey(pgKey,i))
    except:
        pass
    if len(keyOption)>1:
        return rootPath+"\\"+keyOption[-1:][0]
    
    else:
        return rootPath+"\\"+keyOption[0]
    
def systemPath():
    regPath=""
    if platform.system()=="Windows":
        if platform.processor().index("64",2):
            regPath="SOFTWARE\Wow6432Node\PostgreSQL\Installations"
        else:
            regPath="SOFTWARE\PostgreSQL\Installations"
        return regPath
    
def postgresBase():
    #Return the program files path fromt the registry path
    pgPath=registryPath()
    pgKey=registryConn(pgPath)
    pgInstall=reg.QueryValueEx(pgKey,"Base Directory")
    reg.CloseKey(pgKey)
    pgInstall=pgInstall[0]+"\\bin\\psql"
    pypgPath=str(pgInstall).replace("\\", "/")
    #pypgPath= os.environ["ProgramFiles(x86)"]+'/PostgreSQL/9.2/bin/psql'
    #print pypgPath
    return pypgPath
    
def sqlDataFile():
    dataFile="C:\\test\\STDM_schema_24-01_14.sql"
    compilePath=postgresBase()
    # print compilePath
    argPath=" -U postgres -p 5432 -h localhost -d demo -f "+dataFile
    pgPath= os.path.abspath(compilePath)
    #return os.system(os.path.abspath(compilePath))
    #return os.system("start /wait cmd /c {"+newPath+"}")
#     action=call([pgPath, argPath], shell=True)
#     print "hallo"
#     print sys.stderr, -action
    #process=subprocess.check_call(['C:/Program Files (x86)/PostgreSQL/9.2/bin/psql',' -U postgres -p 5432 -h localhost -d sample -f C:\\test\\STDM_schema_24-01_14.sql'])
      
    
    
# if __name__=="__main__":
#     #getRegistryPath()
#     getpostgresBase()
#     sqlDataFile()
    #sys.stderr(subprocess.check_call(['C:/Program Files (x86)/PostgreSQL/9.2/bin/psql']))

    #sys.stdout(subprocess.check_call(['CMD',"/k "+os.environ["PSQL"]]))
    

    #pipe = sub.Popen("cmd", shell=True, bufsize=bufsize, stdout=PIPE).stdout
    
    
 