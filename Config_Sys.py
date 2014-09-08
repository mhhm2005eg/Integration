import os,  stat
import shlex, subprocess
import sys, getopt
import logging
import glob
from os.path import basename , dirname
#import CppHeaderParser
import shutil
import datetime

MainProjectName  ="MFC400"
DevPath  = "SMFC4B0_07.00.00"

ChangePackageList={"MFC400":"241130:1","SRLCam":"203064:1"}


ListOfProjects = ["MFC400", "SRLCam"]
PrjOfDevPath = {"SMFC4B0_07.00.00":"MFC400","MFC4T0_B2_01.02":"MFC400","SRLCam4T0_R2.0.0_INT1":"SRLCam","SRLCam4T0_2.1":"SRLCam","SRLCam4T0_2.2":"SRLCam",}
MainProjectName=PrjOfDevPath[DevPath]
ChangePackage=ChangePackageList[MainProjectName]



RFoldersToConfig = ["../02_System/05_Tools/mts_system/mts_measurement/cfg/algo","../02_System/05_Tools/mts_system/mts_measurement/dll/algo","../02_System/05_Tools/mts_system/mts_measurement/sdl/algo"]
AFoldersToConfig = []
ASubsToConfig = []

def SandToProj(Sandbox):
	current = os.path.dirname(os.path.realpath(__file__))
	Up1 = os.path.dirname(current)
	#print(Up1)
	x = Sandbox.replace(Up1,"/nfs/projekte1/PROJECTS/"+MainProjectName)
	return x
	
def ConvertALL():
	for path in RFoldersToConfig:
		AFoldersToConfig.append(os.path.abspath(path))
		ASubsToConfig.append(SandToProj(os.path.abspath(path)))
	

def ConvertFlatToConfigPath(Sub):
	t = Sub.replace("/project.pj","")
	y = t.replace(MainProjectName+"/", "PROJECTS.pj#"+MainProjectName+"#d="+DevPath+"#")
	y = y.replace(MainProjectName+"\\", "PROJECTS.pj#"+MainProjectName+"#d="+DevPath+"#")
	#print(t, MainProjectName)
	#print(y)
	return y
	
def GetRevisionForLabel(DevPath, SharedProject, Label):
		"""
		GetRevisionForLabel( SharedProject, Label)

		Description: Get the revision corresponding to a label

		Parameter: -SharedProject the path from where the shared project is shared
				   -Label serach the revision to this label

		return 0 if label could not be found in this shared project
		"""
		ret_value = "default"
		if DevPath:
			cmdline_info='si viewprojecthistory --batch  --fields=labels,revision --rfilter=labeled ' +' -P  #p='+ConvertFlatToConfigPath(SharedProject)+''
		else:
			cmdline_info='si viewprojecthistory --batch  --fields=labels,revision --rfilter=labeled   --project='+SharedProject
		print cmdline_info
		try:
			proc=subprocess.Popen(cmdline_info, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			stdout_str, stderr_str = proc.communicate()
			#print(stdout_str)
			#print(stderr_str)
			stdout_str_lines = stdout_str.splitlines()
		except OSError,ValueError:
			print formatExceptionInfo()
#		print Label
		for line in stdout_str_lines:
			#print line
			if (len(line) > 1):
				argu = line.split()
				#print (argu)
				if (len(argu) > 2):
					argu[1] = argu[len(argu)-1]
					argu[0] = line.replace(argu[1],"")
					argu[0] = argu[0].rstrip()
					argu[0] = argu[0].replace("\n","")
	#					print argu[0]
					if (len(argu) > 1):
	#					print argu[0]
	#					print argu[1]

						# check if unicode
						try:
							argu[0].decode('ascii')
						except UnicodeDecodeError:
							print("Decoding issue")
				else:
					# an ascii-encoded unicode string
					#print(argu[0],1)
					if (argu[0] == Label):
						ret_value = argu[1]
						#print(cmdline_info)
						break
#						print "Return value " + ret_value
		if ret_value == "default":
			print(stdout_str)
			print(stderr_str)
		return ret_value




def getLabel():
	Label = raw_input('Enter the label: ')
	return Label



def ConfigSub(Sub, CP):
	ProjectToBeConfigured = Sub+"/project.pj"
	RootProjectToBeConfigured = os.path.dirname(Sub)+"/project.pj"
	if CP != "default":
		print("#"*30)
		print("#"*30)
		print(" ---- Start Config-----")
		print("Subproject: "+ProjectToBeConfigured)
		#print("Label: "+Label)
		print("Checkpoint: "+CP)
		Build_Command="si configuresubproject  --type=build --cpid="+ChangePackage+" --subprojectRevision="+CP+" --project="+RootProjectToBeConfigured +" --devpath="+DevPath +" "+ProjectToBeConfigured
		ret = proc=subprocess.Popen(Build_Command, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout_str, stderr_str = proc.communicate()
		if stdout_str :
			print("Out: \n" + stdout_str+"\n")
				
		if stderr_str:
			print("Messages: \n"+stderr_str+"\n")
		print(Build_Command)


def ConfigALL(Label):
	for Sub in ASubsToConfig:
		CP = GetRevisionForLabel(DevPath,Sub+"/project.pj",Label)
		#print(DevPath,Sub,Label)
		if CP != "default":
			ConfigSub(Sub, CP)
			#print("Project : "+ Sub+"\n")
			#print("Label : "+ Label+"\n")
			#print("CP : "+ CP+"\n")
		else:
			print("Invalid Label !!! " +Label)
		









def main():
	L = getLabel()
	ConvertALL()
	ConfigALL(L)
	

main()