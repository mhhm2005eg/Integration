import os,  stat
import shlex, subprocess
import sys, getopt
import logging
import glob
from os.path import basename , dirname
#import CppHeaderParser
import shutil
import datetime



def Configure():
	Build_Command = "run_config.cmd "
	proc=subprocess.Popen(Build_Command, shell=False,stdin=subprocess.PIPE,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	proc.stdin.write("2\n")
	proc.stdin.write("y\n")
	while True:
		x = proc.stdout.readline()
		if x:
			print(x)
		else:
			break
	#stdout_str, stderr_str = proc.communicate()
	#if stdout_str :
		#print("Out: \n" + stdout_str+"\n")
	#if stderr_str:
		#print("Messages: \n"+stderr_str+"\n")
	#stdout_str = proc.communicate(input='2\n')[0]
	#stdout_str = proc.communicate(input='y\n')[0]
	#if stdout_str :
		#print("Out: \n" + stdout_str+"\n")

def main():
	Configure()
	os.system("Compare.py")
	os.system("Post_Config.py")
	os.system("Check_mod.py")





main()