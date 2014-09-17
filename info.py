import os,  stat
import shlex, subprocess
import sys, getopt
import logging
import glob
from os.path import basename , dirname
#import CppHeaderParser
import shutil
import datetime



def dump(obj):
   print("#"*30)
   for attr in dir(obj):
       if hasattr( obj, attr ):
           if attr != "__doc__" and attr != "__init__" and attr != "__module__":
               print("-"*30)
               print( "obj.%s = %s" % (attr, getattr(obj, attr)))
               print("-"*30)
def ConvertFlatToConfigPath(Sub, Obj):
	t = Sub.replace("/project.pj","")
	y = t.replace(Obj.RootProject+"/", "PROJECTS.pj#"+Obj.RootProject+"#d="+Obj.DevPath+"#")
	y = y.replace(Obj.RootProject+"\\", "PROJECTS.pj#"+Obj.RootProject+"#d="+Obj.DevPath+"#")
	#print(t, Obj.RootProject)
	#print(y)
	return y
def GetLabelForRevision(DevPath, SharedProject, Rev, Obj):
		"""
		GetRevisionForLabel( SharedProject, Label)

		Description: Get the revision corresponding to a label

		Parameter: -SharedProject the path from where the shared project is shared
				   -Label serach the revision to this label

		return 0 if label could not be found in this shared project
		"""
		ret_value = "default"
		if DevPath:
			cmdline_info='si viewprojecthistory --batch  --fields=revision,labels --rfilter=labeled ' +' -P  #p='+ConvertFlatToConfigPath(SharedProject, Obj)+''
		else:
			cmdline_info='si viewprojecthistory --batch  --fields=revision,labels  --rfilter=labeled   --project='+SharedProject
		#print cmdline_info
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
					if (argu[0] == Rev):
						ret_value = argu[1]
						#print(cmdline_info)
						break
#						print "Return value " + ret_value
		#if ret_value == "default":
			#print(stdout_str)
			#print(stderr_str)
		return ret_value   
class Sandbox:
	def __init__(self):
		self.DevPath = ""
		self.path=""
		self.LatestCP=""
		self.LatestLabel=""
		self.Project=""
		self.RootProject=""
		self.GetSandBoxinfo()
		
	def GetSandBoxinfo(Obj):
		cmdline_info = "si sandboxinfo"
		try:
			proc=subprocess.Popen(cmdline_info, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			stdout_str, stderr_str = proc.communicate()
			#print(stdout_str)
			#print(stderr_str)
			stdout_str_lines = stdout_str.splitlines()
		except OSError,ValueError:
			print formatExceptionInfo()
		
		for Line in stdout_str_lines:
			if "Development Path:" in Line:
				
				DevPath = Line.replace("Development Path:", "")
				DevPath = DevPath.replace(" ", "")
				Obj.DevPath = DevPath
			elif "Revision:" in Line:
				LatestCP = Line.replace("Revision:", "")
				LatestCP = LatestCP.replace(" ", "")
				Obj.LatestCP = LatestCP
			elif "Configuration Path:" in Line:
				Obj.RootProject=Line.replace("Configuration Path:","")
				x = Obj.RootProject.split("#")
				Obj.RootProject = x[2]
				MainProjectName = Obj.RootProject
			elif "Project Name:" in Line:
				Obj.Project=Line.replace("Project Name:","")
				Obj.Project = Obj.Project.replace(" ", "")
			elif "Variant Sandbox Name:" in Line:
				Obj.path=Line.replace("Variant Sandbox Name:","")
				Obj.path = Obj.path.replace(" ", "")
		Obj.LatestLabel = GetLabelForRevision(Obj.DevPath,Obj.Project, Obj.LatestCP, Obj )

		
		
class UserInfo:
	def __init__(self, id):
		self.ID=""
		self.cp=""
		self.cpList = []
		self.InitUserInfo()
	def InitUserInfo(Obj):
		Build_Command = "si viewcps --fields=user  "
		proc=subprocess.Popen(Build_Command, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout_str, stderr_str = proc.communicate()
		#print(stdout_str)
		Lines = stdout_str.split()
		x = Lines[2].replace("(","")
		x = x.replace(")","")
		Obj.ID = x
		Build_Command = "si viewcps --fields=id --filter=project:"+CurrentSandBox.RootProject+"  --filter=user:"+Obj.ID+" --filter=state:Open  "
		proc=subprocess.Popen(Build_Command, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout_str, stderr_str = proc.communicate()
		#print(stdout_str)
		Lines = stdout_str.split()
		for line in Lines:
			x = line.replace(" ","")
			Obj.cp = x
			Obj.cpList.append(x)
		
		#dump(Obj)
			
			


			 
CurrentSandBox = Sandbox()
MyInfo = 	UserInfo(0)
	

	
#def main():
	#dump(MyInfo)
	#dump(CurrentSandBox)
	
#main()