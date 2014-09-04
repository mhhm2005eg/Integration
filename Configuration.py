import os,  stat
import shlex, subprocess
import sys, getopt
import logging
import glob
from os.path import basename , dirname
#import CppHeaderParser
import shutil
import datetime
import configparser
import xml.etree.ElementTree as ET
import copy
DevPath="MFC4T0_B2_01.02"
ChangePackageList={"MFC400":"209686:2","SRLCam":"203064:1"}

CMPList = ["SAC_StereoAutoCalibration", "FSD_FreeSpaceDetection"]
#####################################################
ListOfProjects = ["MFC400", "SRLCam"]
PrjOfDevPath = {"MFC4T0_B1_01.01":"MFC400","MFC4T0_B2_01.02":"MFC400","SRLCam4T0_R2.0.0_INT1":"SRLCam","SRLCam4T0_2.1":"SRLCam","SRLCam4T0_2.2":"SRLCam",}
MainProjectName=PrjOfDevPath[DevPath]
ChangePackage=ChangePackageList[MainProjectName]

class SubProject:
	def __init__(self, ID):
		self.ID = ID
		self.path=""
		self.cmp=""
		self.label=""
		self.New_label=[]
		self.Cp=""
		#self.Rev=""
		self.Typ=""
		
SubProjectList=[]

def dump(obj):
   print("#"*30)
   for attr in dir(obj):
       if hasattr( obj, attr ):
           if attr != "__doc__" and attr != "__init__" and attr != "__module__":
               print("-"*30)
               print( "obj.%s = %s" % (attr, getattr(obj, attr)))
               print("-"*30)

		   
def ReadIni(IniFileName):
	returnValue = {}
	config = configparser.ConfigParser()
	config.read(IniFileName)
	SectionList = config.sections()	
	for section in SectionList:
		for x in config[section]:
			returnValue[x] = config[section][x]
	return (returnValue)
	
def ReadXml(XmlFileName, tag):
	returnValue = {}
	Paths = {}
	CurrentLabel = {}
	 
	SubPros = []
	tree = ET.parse(XmlFileName)
	root = tree.getroot()
	xx=0
	yy=0
	for Cfg in root.findall(tag):
		subPro = SubProject(xx)
		xx=xx+1
		CMPName = Cfg.get('CompName')
		Paths[CMPName] = Cfg.get('Path')
		CurrentLabel[CMPName] = Cfg.find('Label').get('Label')
		subPro.path=Cfg.get('Path')
		subPro.label = Cfg.find('Label').get('Label')
		subPro.Cp = Cfg.find('Revision').get('Revision')
		subPro.Typ = Cfg.find('Type').get('Type')
		subPro.cmp=CMPName
		#returnValue[Cfg.get('name')] = Cfg.text
		SubPros.append(copy.deepcopy(subPro))
		#dump(subPro)
		
	return SubPros

def GetRevisionForLabel(RootProject, SharedProject, Label):
		"""
		GetRevisionForLabel( SharedProject, Label)

		Description: Get the revision corresponding to a label

		Parameter: -SharedProject the path from where the shared project is shared
				   -Label serach the revision to this label

		return 0 if label could not be found in this shared project
		"""
		ret_value = "default"
		cmdline_info='si viewprojecthistory --batch  --fields=labels,revision --rfilter=labeled --project='+SharedProject
#		print SharedProject
		try:
			proc=subprocess.Popen(cmdline_info, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			stdout_str, stderr_str = proc.communicate()
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
							Common.Tell("Decoding issue")
				else:
					# an ascii-encoded unicode string
					#print(argu[0],1)
					if (argu[0] == Label):
						ret_value = argu[1]
						#print(cmdline_info)
						break
#						print "Return value " + ret_value
		return ret_value
def ConfigCompList():
	for folder in BasicDestinationSubProjectList:
		for CMP in ExtendedCompanentNames	:
			#/nfs/projekte1/PROJECTS/MFC400/06_Algorithm/04_Engineering/05_Deliverables/lib/ti_c674x/algo/project.pj
			ProjectToBeConfigured="/nfs/projekte1/PROJECTS/"+PrjOfDevPath[DevPath]+"/06_Algorithm"+folder+CMP+"/project.pj"
			RootProjectToBeConfigured="/nfs/projekte1/PROJECTS/"+PrjOfDevPath[DevPath]+"/06_Algorithm"+folder+"project.pj"
			LabelList = ExtendedLabelsOfCMP[CMP]
			for Label in LabelList:
				CP = GetRevisionForLabel(RootProjectToBeConfigured, ProjectToBeConfigured, Label)
				if CP != "default":
					print()
					print(" ---- Start Config-----")
					print("Subproject: "+ProjectToBeConfigured)
					print("Label: "+Label)
					print("Checkpoint: "+CP)
					Command="si configuresubproject  --type=build --cpid="+ChangePackage+" --subprojectRevision="+CP+" --project="+RootProjectToBeConfigured +" --devpath="+DevPath +" "+ProjectToBeConfigured
					ret = subprocess.call(Command, shell=True)
					print(Command)
				#ret=1
				#if ret == 0:
					#Common.Tell(Command)

def FilterSubproject(Subs, COMPList):
	RetList = []
	for Sub in Subs:
		for CMP in COMPList:
			if Sub.cmp == CMP:
				RetList.append(Sub)
				
	return (RetList)

def printSubProj(Sub):
	att = Sub.__dict__
	for x in att:
		y = eval(x)
		print(y)


LatestFolderStrutureFile = "post_config_shared_projects.xml"
NewCONfigFiles = "shared_project_config_files.xml"

def ParsConfFiles():
	xx = 0
	XmlFileName = NewCONfigFiles
	tag = "FileCfg"
	Files = []
	#ret = ReadXml(NewCONfigFiles, "FileCfg")
	tree = ET.parse(XmlFileName)
	root = tree.getroot()
	SubPros = []
	for Cfg in root.findall(tag):
		Files.append(Cfg.get('File'))
	
	for File in Files:
		tree = ET.parse(File)
		root = tree.getroot()
		Base = root.find("BaseConfig")
		if Base:
			for Cfg in Base.findall("SharedProject"):
				subPro = SubProject(xx)
				xx=xx+1
				subPro.Typ = Cfg.find('Config').get('Type')
				subPro.New_label.append(Cfg.find('Config').get('Label'))
				subPro.cmp = Cfg.get('CompName')
				SubPros.append(copy.deepcopy(subPro))
		Custom = root.find("CustomConfigV2")
		
		if Custom:
			for Cfg in Custom.findall("SharedProject"):
				subPro = SubProject(xx)
				xx=xx+1
				subPro.Typ = Cfg.find('Config').get('Type')
				subPro.cmp = Cfg.get('CompName')
				for x in SubPros:
					if x.cmp == subPro.cmp:
						x.New_label.append( Cfg.find('Config').get('Label'))
						
	return(SubPros)
		

def OrListOfObj(Obj1, Obj2):
	for x in Obj1:
		for y in Obj2:
			if x.cmp == y.cmp:
				for attr in dir(x):
					if hasattr( x, attr ):
						if not getattr(x, attr):
							n = getattr(y, attr)
							setattr(x,attr, n )
	return(Obj1)
def Test():
	ret = ReadXml(LatestFolderStrutureFile, "SharedProjectConfig")
	#for x in ret:
		#dump(x)
	#printSubProj(ret)
	Filtered = FilterSubproject(ret, CMPList)
	for x in Filtered:
		dump(x)
	#print(Filtered)
	#ret = ReadIni("Conf.ini")
	#print(ret)

def main():
	ret1 = ReadXml(LatestFolderStrutureFile, "SharedProjectConfig")
	ret2 =  ParsConfFiles()
	ret = OrListOfObj(ret1, ret2)
	for x in ret:
		dump(x)
main()
#Test()