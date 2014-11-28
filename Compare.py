import os,  stat
import info

file1="pre_config_shared_projects.xml"
file2="post_config_shared_projects.xml"
Outfile = "COMP.txt"

WD =os.path.abspath(info.MyConf.WD)
os.chdir(WD) 

fi1 = open(file1, "rb")
lines1 = fi1.readlines()
fi2 = open(file2, "rb")
lines2 = fi2.readlines()
fo = open(Outfile, "wb")
labels = []
lst= []
for line in range(len(lines2)):
	if lines1[line] != lines2[line]:
		if "Label Label" in lines2[line]:
			labels.append(lines2[line])
			fo.write(str(line) +": \n")
			fo.write(lines2[line-2] )
			fo.write(lines2[line-1] )
			fo.write(lines1[line] + lines2[line] )
			
lst = list(set(labels))
lst.sort()
if lst:
	fo.write("#"*30+" \n")
	fo.write("#"*30+" \n")
	print("Info. : Labels Modified are : "+str(len(lst))+ " Ones")
	print("Labels Updated as below ... ")
	for i in lst:
		fo.write(str(lst.index(i)+1)+" :"+i)
		print(str(lst.index(i)+1)+" :"+i) 
	fo.write("#"*30+" \n")
	fo.write("#"*30+" \n")
else:
	fo.write("No differences after the configuration ....")
	print("No differences after the configuration ....")
fi1.close()
fi2.close()
fo.close()