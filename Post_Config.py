import os,  stat
import shlex, subprocess
import sys, getopt
import logging
import glob
from os.path import basename , dirname
#import CppHeaderParser
import shutil
import datetime

FoldersToSynch = [".\\04_Engineering\\01_Source_Code\\", ".\\04_Engineering\\03_Workspace\\", ".\\04_Engineering\\\\05_Deliverables\\",]
ScriptsToInvoke = [".\\04_Engineering\\03_Workspace\\algo\\make_all_ecu.cmd",".\\04_Engineering\\03_Workspace\\algo\\make_all_sim.cmd",".\\04_Engineering\\03_Workspace\\algo\\make_all_vis.cmd"]
FilesNotToSynch = [".\\04_Engineering\\03_Workspace\\algo\\make_all.xml"]
FoldersToBeRemoved = [".\\04_Engineering\\04_Build\\algo"]
CLEAN = "STD_ON"

def RemoveFolders():
	for folder in FoldersToBeRemoved:
		folder = os.path.abspath(folder)
		if os.path.isdir(folder):
			try:
				shutil.rmtree(folder, ignore_errors=True)
			except ValueError:
				print("Could not delete folder :"+folder)

def premain():
	if not os.path.exists("log"):
		os.makedirs("log")
	global  Logf
	if os.path.isfile("./log/Build.log"):
		time = str(datetime.datetime.now().time())
		time = time.replace(":", ".")
		os.rename("./log/Build.log", "./log/Build_"+time+".log")
	
	Logf = open("./log/Build.log", "wb+")

def postmain():
	Logf.close()
	
def Kprint(Mess):
	print(Mess+"\n")
	Logf.write(Mess+"\n")
	
def Fprint(Mess):
	Logf.write(Mess+"\n")
def PreSynch():
	for file in FilesNotToSynch:
		file = os.path.abspath(file)
		if os.path.isfile(file):
			if os.path.isfile(file+".bak"):
				os.chmod(file+".bak", stat.S_IWRITE)
			shutil.copy2(file, file+".bak")


def PostSynch():
	for file in FilesNotToSynch:
		file = os.path.abspath(file)
		os.chmod(file, stat.S_IWRITE)
		if os.path.isfile(file+".bak"):
			shutil.copy2(file+".bak", file)
		
def SynchAll():
	PreSynch()
	for folder in FoldersToSynch:
		folder = os.path.abspath(folder)
		folder = folder + "/project.pj"
		Build_Command = "si resync --overwriteChanged "+folder
		Kprint("Synch Project : "+ folder+" ...")
		proc=subprocess.Popen(Build_Command, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout_str, stderr_str = proc.communicate()
		if stdout_str :
			Fprint("Out: \n" + stdout_str+"\n")
				
		if stderr_str:
			Fprint("Messages: \n"+stderr_str+"\n")
	PostSynch()
	
def BuildAll():
	for Script in ScriptsToInvoke:
		Script = os.path.abspath(Script)
		Build_Command = Script + "  "
		Kprint("Building  : "+ Script+" ...")
		BaseFolder = os.path.dirname(Script)
		abspath = os.path.abspath(__file__)
		dname = os.path.dirname(abspath)
		proc=subprocess.Popen(Build_Command, shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=BaseFolder)
		stdout_str = proc.communicate(input='Enter \n')[0]
		if stdout_str :
			Kprint("Out: \n" + stdout_str+"\n")
				
		#if stderr_str:
			#Kprint("Messages: \n"+stderr_str+"\n")
		
def main():
	if CLEAN == "STD_ON":
		RemoveFolders()
	SynchAll()
	BuildAll()
premain()	
main()
postmain()