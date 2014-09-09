import os
import shlex, subprocess
import sys, getopt
import logging
import sys
import glob
import random
import datetime
from os.path import basename

debug = 0
SOURCE_SB = "SMFC4B0_07.00.00"
Destination_SB = ""
MainProjectName = ""
#CP = "241130:1"
MainDir = ""
ListOfDirs = ["\\06_Algorithm\\04_Engineering\\05_Deliverables\\dll\\algo\\","\\06_Algorithm\\04_Engineering\\05_Deliverables\\sdl\\algo\\","\\06_Algorithm\\04_Engineering\\05_Deliverables\\lib\\", "\\06_Algorithm\\04_Engineering\\05_Deliverables\\cfg\\algo\\joint\\"]

ListOfDirsToSynchNotRecursive = ["/06_Algorithm/"]

class UserInfo:
	def __init__(self, id):
		self.ID=""
		self.cp=""
		self.cpList = []
		
class Sandbox:
	def __init__(self):
		self.DevPath = ""
		self.path=""
		self.LatestCP=""
		self.LatestLabel=""
		self.Project=""
		self.RootProject=""
		self.Sandbox=""
		

		
MyInfo = 	UserInfo(0)
CurrentSandBox = Sandbox		

def dump(obj):
   print("#"*30)
   for attr in dir(obj):
       if hasattr( obj, attr ):
           if attr != "__doc__" and attr != "__init__" and attr != "__module__":
               print("-"*30)
               print( "obj.%s = %s" % (attr, getattr(obj, attr)))
               print("-"*30)
 
def GetSandBoxinfo():
	cmdline_info = "si sandboxinfo"
	try:
		proc=subprocess.Popen(cmdline_info, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout_str, stderr_str = proc.communicate()
		print(stdout_str)
		#print(stderr_str)
		stdout_str_lines = stdout_str.splitlines()
	except OSError,ValueError:
		print formatExceptionInfo()
	
	for Line in stdout_str_lines:
		if "Development Path:" in Line:
			
			DevPath = Line.replace("Development Path:", "")
			DevPath = DevPath.replace(" ", "")
			CurrentSandBox.DevPath = DevPath
			global Destination_SB
			Destination_SB = DevPath
		elif "Revision:" in Line:
			LatestCP = Line.replace("Revision:", "")
			LatestCP = LatestCP.replace(" ", "")
			CurrentSandBox.LatestCP = LatestCP
		elif "Configuration Path:" in Line:
			CurrentSandBox.RootProject=Line.replace("Configuration Path:","")
			x = CurrentSandBox.RootProject.split("#")
			CurrentSandBox.RootProject = x[2]
			global MainProjectName
			MainProjectName = CurrentSandBox.RootProject
		elif "Project Name:" in Line:
			CurrentSandBox.Project=Line.replace("Project Name:","")
			CurrentSandBox.Project = CurrentSandBox.Project.replace(" ", "")
		elif "Variant Sandbox Name:" in Line:
			CurrentSandBox.Sandbox=Line.replace("Variant Sandbox Name:","")
			CurrentSandBox.Sandbox = CurrentSandBox.Sandbox.replace(" ", "")
			global MainDir
			MainDir = os.path.dirname((os.path.dirname(os.path.dirname(CurrentSandBox.Sandbox))))+"/"
			
			print(MainDir)
			#sys.exit("Error message")

			
	dump(CurrentSandBox)


def InitUserInfo():
	Build_Command = "si viewcps --fields=user  "
	proc=subprocess.Popen(Build_Command, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout_str, stderr_str = proc.communicate()
	#print(stdout_str)
	Lines = stdout_str.split()
	x = Lines[2].replace("(","")
	x = x.replace(")","")
	MyInfo.ID = x

	Build_Command = "si viewcps --fields=id --filter=project:"+MainProjectName+"  --filter=user:"+MyInfo.ID+" --filter=state:Open  "
	proc=subprocess.Popen(Build_Command, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout_str, stderr_str = proc.communicate()
	print(stdout_str)
	Lines = stdout_str.split()
	for line in Lines:
		x = line.replace(" ","")
		MyInfo.cp = x
		MyInfo.cpList.append(x)
	
	dump(MyInfo)
	
	
def ResynchAll():
	commandref = "si resync --norecurse "
	for Dir in ListOfDirsToSynchNotRecursive:
		folder = MainDir+Destination_SB+Dir+"project.pj"
		Build_Command = commandref + " -S "+folder
		proc=subprocess.Popen(Build_Command, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout_str, stderr_str = proc.communicate()
		if debug == 0:
			print (Build_Command)
			if stdout_str :
				Kprint("Out: \n" + stdout_str+"\n")
			if stderr_str:
				Kprint("Messages: \n"+stderr_str+"\n")
			else:
				Kprint("Succeded !!!"+"\n")
		return(0)	
def premain():
	if not os.path.exists("log"):
		os.makedirs("log")
	global  Logf
	if os.path.isfile("./log/Build.log"):
		time = str(datetime.datetime.now().time())
		time = time.replace(":", ".")
		os.rename("./log/Build.log", "./log/Build_"+time+".log")
	
	Logf = open("./log/Build.log", "wb+")
	GetSandBoxinfo()
	InitUserInfo()
	ResynchAll()

def postmain():
	Logf.close()
	
def getSubdirsRecursive(abs_path_dir) :  
	#lst = [ name for name in os.listdir(abs_path_dir) if os.path.isdir(os.path.join(abs_path_dir, name)) and name[0] != '.' ]
	lst=[]
	for name in os.listdir(abs_path_dir):
		if os.path.isdir(os.path.join(abs_path_dir, name)) and name[0] != '.':
			#Kprint(name)
			if lst:
				lst.append(str(abs_path_dir)+'/'+str(name))
			else:
			    lst=[str(abs_path_dir)+'/'+str(name)]
			x = getSubdirsRecursive(os.path.join(abs_path_dir, name))
			if 	x:
				for y in x:
					lst.append(str(y))
	lst = list(set(lst))
	lst.sort()
	#Kprint(lst)
	return lst

def GetFIles():
	RetFiles = []
	for Dir in ListOfDirs:
		SOURCE_FOLDER = MainDir+SOURCE_SB+Dir
		if os.path.isdir(SOURCE_FOLDER):
			DirList = getSubdirsRecursive(SOURCE_FOLDER)
			DirList.append(SOURCE_FOLDER)
			for folder in DirList:
				#Kprint(folder)
				temp = glob.glob(str(folder)+'/'+"*")
				
				for file in temp :
					if not ".pj" in file and os.path.isfile(file):
						#Kprint(file)
						RetFiles.append(file)
		else:
			Kprint("Folder does not exist .... ")
			Kprint(SOURCE_FOLDER)
		
	return(RetFiles)

		
def CheckShared(file):
	opt ="  --nolabels --nolocks "
	Build_Command = "si archiveinfo " +opt+ file
	print("-*"*random.randint(0,30))
	Logf.write(Build_Command+"\n")
	proc=subprocess.Popen(Build_Command, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout_str, stderr_str = proc.communicate()
	Lines = stdout_str.split('\n')
	for line in Lines:
		if "Archive Name:" in line:
			if MainProjectName in line:
				#Kprint(line)
				return(0)
			else:
				#Kprint(line)
				return (1)
	if debug == 1:		
		if stdout_str :				
			Kprint("Out: \n" + stdout_str+"\n")
		if stderr_str:
			Kprint("Messages: \n"+stderr_str+"\n")
		else:
			Kprint("Succeded !!!"+"\n")
		return(0)	
		
def GetLocalFiles(FilesList):
	RetFiles = []
	for file in FilesList:
		if not CheckShared(file):
			RetFiles.append(file)
		else:
			Kprint("File is sahred : !!! \n")
			Kprint(file)
	return(RetFiles)
	
def GetRevision(file):
	opt =" --nochangePackage --nolabels --nolocate --lockRecordFormat=project "
	Build_Command = "si revisioninfo " +opt+ file
	Kprint("-*"*30)
	Logf.write(Build_Command+"\n")
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
			Kprint("Out: \n" + stdout_str+"\n")
		if stderr_str:
			Kprint("Messages: \n"+stderr_str+"\n")
		else:
			Kprint("Succeded !!!"+"\n")

def GetArch(file):
	opt ="  --nolabels --nolocks "
	Build_Command = "si archiveinfo " +opt+ file
	Kprint("-*"*30)
	Logf.write(Build_Command+"\n")
	proc=subprocess.Popen(Build_Command, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout_str, stderr_str = proc.communicate()
	Lines = stdout_str.split('\n')
	for line in Lines:
		if "Archive Name:" in line:
			Arch = line.replace("Archive Name:", "");
			Arch = Arch.replace(" ", "");
			return(Arch)
	if debug == 1:		
		if stdout_str :				
			Kprint("Out: \n" + stdout_str+"\n")
		if stderr_str:
			Kprint("Messages: \n"+stderr_str+"\n")
		else:
			Kprint("Succeded !!!"+"\n")

			
def SetRevision(file, ver):
	opt ="    "
	Build_Command = "si updaterevision " +opt+"--changepackageid="+ MyInfo.cp+" --revision="+ver+" "+file 
	Kprint("-*"*30)	
	proc=subprocess.Popen(Build_Command, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout_str, stderr_str = proc.communicate()
	if debug == 0:		
		if stdout_str :				
			Kprint("Out: \n" + stdout_str+"\n")
		if stderr_str:
			Kprint("Messages: \n"+stderr_str+"\n")
		else:
			Kprint("Succeded !!!"+"\n")	
def test():
	x = GetFIles()
	#Kprint(x)
	y= GetLocalFiles(x)
	Kprint(y)
	
def Kprint(Mess):
	print(Mess+"\n")
	Logf.write(Mess+"\n")

def AddArch(Arc):
	command = "si addmemberfromarchive --archive="+Arc+" largeLabel.c"
	
	
def main():
	files = GetFIles()
	LocFiles = GetLocalFiles(files)
	for file in LocFiles:
		DestFile = file.replace(SOURCE_SB, Destination_SB)
		
		SRCRev = GetRevision(file)
		DestRev_old = GetRevision(DestFile)
		ArchSrc = GetArch(file)
		ArchDes = GetArch(DestFile)
		if SRCRev != DestRev_old :
			if not CheckShared(DestFile):

				
				if ArchSrc == ArchDes:
					SetRevision(DestFile, SRCRev)
					DestRev_New = GetRevision(DestFile)
					Kprint(DestFile+" :: "+SRCRev+" "+DestRev_old+" "+DestRev_New)
					if SRCRev == DestRev_New:
						Kprint("Ok !!!")
					else:
						Kprint(" Check please !!! something passed wrong ....")
				else:
					print("Source Arch is : "+str(ArchSrc)+"\n")
					print("Destination Arch is : "+str(ArchDes)+"\n")
		else:
			Kprint("Versions are the same , No action !!! \n")
	
	#CheckShared("D:\\Sandboxs\\SMFC4B0_06.00.00\\06_Algorithm\\04_Engineering\\05_Deliverables\\dll\\algo\\cct_sim\\sim_hil_client.dll	")
	#GetRevision("D:\\Sandboxs\\SMFC4B0_06.00.00\\06_Algorithm\\04_Engineering\\05_Deliverables\\dll\\algo\\cct_sim\\sim_hil_client.dll	")
	#CheckShared("D:\\Sandboxs\\SMFC4B0_06.00.00\\06_Algorithm\\04_Engineering\\05_Deliverables\\dll\\algo\\cct_mo\\fancy_table.dll	")
	
	
def test ():
	InitUserInfo()
	
premain()
main()
postmain()