import os,  stat
import shlex, subprocess
import sys, getopt
import logging
import glob
from os.path import basename , dirname
#import CppHeaderParser
import shutil
import datetime
import info

AUTO_CP = info.MyConf.AUTO_CP
WD =os.path.abspath(info.MyConf.WD)
os.chdir(WD) 

FoldersToSynch = [".\\05_Testing\\06_Test_Tools\\"]

relFolder = ".\\04_Engineering\\05_Deliverables"
folder = os.path.abspath(relFolder)
Sandbox = folder+"/project.pj"
Proj_NAme = info.MyConf.MainPrj
CP = info.MyConf.cp
user = info.MyConf.user
Label=""
if AUTO_CP == "STD_ON":
    CP = info.MyInfo.cp
ModFiles = []
LocModFiles = []



def PrintTitel(text):
    M = 60
    L = len(text)
    N = M - L
    T = N/2
    print("*"*M)
    print("*"*T+" "*L+"*"*T)
    print("*"*T+text+"*"*T)
    print("*"*T+" "*L+"*"*T)
    print("*"*M)


def CheckShared(file):
    opt ="  --nolabels --nolocks "
    Build_Command = "si archiveinfo " +opt+ file
    #print("-*"*random.randint(0,30))
    proc=subprocess.Popen(Build_Command, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_str, stderr_str = proc.communicate()
    Lines = stdout_str.split('\n')
    for line in Lines:
        if "Archive Name:" in line:
            if Proj_NAme in line:
                #print(line)
                return(0)
            else:
                #print(line)
                return (1)
    if debug == 1:        
        if stdout_str :                
            print("Out: \n" + stdout_str+"\n")
        if stderr_str:
            print("Messages: \n"+stderr_str+"\n")
        else:
            print("Succeded !!!"+"\n")
        return(0)    
        
def GetLocalFiles(FilesList):
    RetFiles = []
    for file in FilesList:
        if not CheckShared(file):
            RetFiles.append(file)
        else:
            print("File is sahred : !!! ")
            print(file)
    return(RetFiles)
    
def GetRevision(file):
    opt =" --nochangePackage --nolabels --nolocate --lockRecordFormat=project "
    Build_Command = "si revisioninfo " +opt+ file
    proc=subprocess.Popen(Build_Command, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_str, stderr_str = proc.communicate()
    Lines = stdout_str.split('\n')
    for line in Lines:
        if "Revision:" in line:
            Rev = line.replace("Revision:", "");
            Rev = Rev.replace(" ", "");
            return(Rev)
    if debug == 1:        
        if stdout_str :                
            print("Out: \n" + stdout_str+"\n")
        if stderr_str:
            print("Messages: \n"+stderr_str+"\n")
        else:
            print("Succeded !!!"+"\n")
def GetLock():
    Build_Command = "si viewlocks --recurse  --sandbox="+Sandbox+" --filter=locked:"+user+" --lockRecordFormat={sandbox}::{member}; " 
    proc=subprocess.Popen(Build_Command, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_str, stderr_str = proc.communicate()
    ListOne = stdout_str.split(";")
    ListTwo = []
    for I in ListOne:
        if I:
            t = I.split("::")
            #print(t)
            str = t[0].replace("project.pj", t[1])
            ListTwo.append(str)
    return(ListTwo)
    #print(stderr_str)

def ViewLock11():
    Build_Command = "si viewsandbox --recurse --fields=indent,name "+ " --lockRecordFormat={revision}{locker} "
    proc=subprocess.Popen(Build_Command, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_str, stderr_str = proc.communicate()
    List = stdout_str.split("\n")
    print(stdout_str)
    print(stderr_str)
    
def CMPLocalSandbox():
    global LocModFiles
    Build_Command = "si viewsandbox --recurse --fields=indent,name,wfdelta "
    proc=subprocess.Popen(Build_Command, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_str, stderr_str = proc.communicate()
    List = stdout_str.split("\n")
    OldLine = ""
    CurrentLine = ""
    for line in List:
        OldLine = CurrentLine
        CurrentLine = line
        if "Working file" in line:
            OldLine = OldLine.replace(" ","")
            ModFiles.append(OldLine)
    LocModFiles = GetLocalFiles(ModFiles)
    #print(LocModFiles)
            #print(line)


def CMPSandbox():
    global LocModFiles
    Build_Command = "si viewsandbox --sandbox="+Sandbox+" --recurse --fields=indent,name,wfdelta "
    proc=subprocess.Popen(Build_Command, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_str, stderr_str = proc.communicate()
    print(stderr_str)
    List = stdout_str.split("\n")
    OldLine = ""
    CurrentLine = ""
    for line in List:
        OldLine = CurrentLine
        CurrentLine = line
        if "Working file" in line:
            OldLine = OldLine.replace(" ","")
            ModFiles.append(OldLine)
    LocModFiles = GetLocalFiles(ModFiles)
    #print(LocModFiles)
            #print(line)
            
MessageDic = {}            
def Checkout(ListOfFiles):
    for file in ListOfFiles:
        Build_Command = "si co --changePackageId="+CP+" "+file
        proc=subprocess.Popen(Build_Command, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_str, stderr_str = proc.communicate()
        MessageDic[file] = stdout_str
        print(stdout_str)
    for key, value in MessageDic.iteritems():
        TextAll = "Checking Out :: "+key+" ->"+value
        #print(value)
        
def Checkin(ListOfFiles):
    PrintTitel("Checkin")
    global Label
    Label=raw_input('Please enter a Label, [-] for Escaping Chickin:')
    
    if Label == "-":
        print("Checkin has been canceled ....")
        return
    for file in ListOfFiles:
        Build_Command = "si ci --changePackageId="+CP+" --yes "+" --label="+Label+" --description="+Label+" "+file
        proc=subprocess.Popen(Build_Command, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_str, stderr_str = proc.communicate()
        MessageDic[file] = stdout_str
        print(stderr_str)
    for key, value in MessageDic.iteritems():
        TextAll = "Checking in :: "+key+" ->"+value
        #print(value)        
def Lock(ListOfFiles):
    PrintTitel("Lock")
    for file in ListOfFiles:
        Build_Command = "si lock --changePackageId="+CP+" "+file
        proc=subprocess.Popen(Build_Command, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_str, stderr_str = proc.communicate()
        MessageDic[file] = stderr_str
        print(stderr_str)
    for key, value in MessageDic.iteritems():
        TextAll = "Locking :: "+key+" ->"+value
        #print(value)
        
def PostCheckinSynch():
    PrintTitel("Synch: MTS env.")
    for folder in FoldersToSynch:
        folder = os.path.abspath(folder)
        Pfolder = folder + "/project.pj"
        Build_Command = "si resync --overwriteChanged -R "+Pfolder
        print("Synch Project : "+ Pfolder+" ...")
        proc=subprocess.Popen(Build_Command, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_str, stderr_str = proc.communicate()
        if stdout_str :
            print("Out: \n" + stdout_str+"\n")
        ans = raw_input('Invoke MTS y/[n]:')        
        if ans == "y":
            print("Invoke MTS : ... \n")
            print(folder+"/run_algo_integration_test.bat")
            MTS = folder+"/run_algo_integration_test.bat"
            Build_Command = MTS
            proc=subprocess.Popen(Build_Command, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=folder)
            stdout_str, stderr_str = proc.communicate()
            if stdout_str :
                print("Out: \n" + stdout_str+"\n")
        #if stderr_str:
            #print("Messages: \n"+stderr_str+"\n")

def UnLock(ListOfFiles):
    PrintTitel("UnLock")
    for file in ListOfFiles:
        Build_Command = "si unlock --action=remove " +file
        proc=subprocess.Popen(Build_Command, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_str, stderr_str = proc.communicate()
        print(stderr_str)
        MessageDic[file] = stderr_str
    for key, value in MessageDic.items():
        TextAll = "UnLocking :: "+key+" ->"+value
        #print(value)
def main():
    #global LocModFiles
    CMPSandbox()
    if LocModFiles:
        Lock(LocModFiles)
        Checkin(LocModFiles)
    else:
        print("No files' differences .... ")
    UnLock(GetLock())
    PostCheckinSynch()

main()
#GetLock()