# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 14:17:11 2019

@author: elopsuc
"""

import zipfile,os
import gzip,csv
import pandas as pd
import numpy as np
import math,time
def main():
	def compare(x,mo,para,value):
		 value=str(value)
		 x[3]=str(x[3])
		 value=value.strip()
		 x[3]=x[3].strip()
		 valueU=value.upper()
		 valuesU=x[3].upper()
		 if mo in x[1] and para in x[2] and valueU not in valuesU:
			 with open("MO参数核查结果.csv", "a+") as f:
				 line=x[0]+","+x[1]+","+x[2]+","+x[3]+","+value+"\n"
				 f.write(line)

	def SCcompare(x,sitename):
		with open("系统常量参数核查结果.csv", "a+") as f:
			#print(sitename)
			if math.isnan(x[1]):
				x[3]="gNB中没有写入该SC"
				x[1]=str(x[1])
				x[2]=str(x[2])
				line=sitename+","+x[0]+","+x[1]+","+x[2]+","+x[3]+"\n"
				f.write(line)
			elif math.isnan(x[2]):
				x[3]="gNB中多写入了该SC"
				x[1]=str(x[1])
				x[2]=str(x[2])
				line=sitename+","+x[0]+","+x[1]+","+x[2]+","+x[3]+"\n"
				f.write(line)
			elif x[1]!=x[2]:
				x[3]="gNB中该SC与推荐值不一致"
				x[1]=str(x[1])
				x[2]=str(x[2])
				line=sitename+","+x[0]+","+x[1]+","+x[2]+","+x[3]+"\n"
				f.write(line)
				
				
	def SCbaslinecheck(SCbaselinefile,filename,sitesname):
		if "rnclog" in filename:
			newcol=["SC","Recommended value"]
			
			SCbase = pd.read_csv(SCbaselinefile)
			SCbase=pd.DataFrame(SCbase,columns=newcol)
			with open(filename,"r") as f:
				i=0            
				SC =pd.DataFrame(columns=('SC','value'))
				for context in f:
					
					if "m_sysConstStr" in context and i<1:                    
						i=i+1
						context=context[20:]
						context=context.split(",")
						for subcontext in context:
							subcontext=subcontext.split(":")
							subcontext[1]=subcontext[1].strip("\n")
							subcontext[1]=float(subcontext[1])
							SC=SC.append(pd.DataFrame({'SC':[subcontext[0]],'value':[subcontext[1]]}))
		 
				SCS=pd.merge(SC, SCbase, how='outer',on=["SC"])
				SCS["Reason"]=None
				SCS.apply(lambda x:SCcompare(x,sitesname),axis=1)    
		  
		
	def MOparaOutput(filename):
		i=0
		j=0
		MOloc=[]
		sitename=""
		if "_dcg_" in filename:
		  sitename=filename[:-13]
		  g_file = gzip.GzipFile(filename)
		  xe=g_file.readlines()
		  xe=[i.decode('utf-8') for i in xe]
		  for x in xe:
			  if "==========" in x:
				  MOloc.append(i)
			  i=i+1
		  try:
			  with open(sitename+"dcgkMO.csv", "w+",newline='') as f:
				  for k in MOloc:
					  if j % 2==0:
						  mo1st=MOloc[j]+2
						  mo2nd=MOloc[j+2]
						  mo=xe[mo1st]
						  mo=mo.strip("\n")
						  mo=mo.replace(",","  ")
						  for c in range(mo1st,mo2nd):
							  mo=mo.strip()
							  xe[c]=xe[c].strip()
							  
							  if mo !=xe[c] and xe[c].startswith("MO    ")==False:
								  para=xe[c]
								  para=para.replace(",","  ") 
								  if"         " in para:
									  para=para.split("         ",1)
									  para[1]=para[1].strip()
									  lines=mo+","+para[0]+","+para[1]
									  lines=sitename+","+lines+"\n"
									  if "==="  not in lines:
										  f.write(lines)
								  
						  j=j+2
		  except IndexError:
			  print("OK")
			  f.close()
			  
			  
	"======================================================工具入口========================================================================================================"
	MObaselinefile=input("请输入MO参数baseline文件及完整路径（CSV格式）")
	SCbaselinefile=input("请输入系统常量baseline文件及完整路径（CSV格式）")
	MOdumppath=input("请输入modump文件完整路径（存放_modump.zip文件的路径，文件可放于子文件内）")
	t0=time.perf_counter()
	with open("MO参数核查结果.csv", "w+") as f:
		title="sitename,MO,para,current value,Baseline value\n"
		f.write(title)
	with open("系统常量参数核查结果.csv", "w+") as f:
		title="sitename,SC,current value,recommand value,Reason\n"
		f.write(title)
	with open("dcgkMO.csv", "w+",newline='') as f:
		k=0
	"================================================================================================================================================================"

	"================================================================================================================================================================"
	for root, dirs, files in os.walk(MOdumppath):
		for name in files:
			mofile=os.path.join(root, name)
			print("正在处理以下MO文件： "+mofile)
			if "modump.zip" in mofile:
				z = zipfile.ZipFile(mofile, "r")
				#打印zip文件中的文件列表
				z.extractall()
				"=============================================================================================================================================================="
				for filename in z.namelist( ):
					if "_dcg_" in filename:
					  sitesname=filename[:-13]#拿到sitesname
				"=============================================================================================================================================================="
				for filename in z.namelist( ):
					MOparaOutput(filename)
					SCbaslinecheck(SCbaselinefile,filename,sitesname)
				"============================================================================================================================================================="
				dataset = pd.read_csv(sitesname+"dcgkMO.csv")
				BaselinesData=csv.reader(open(MObaselinefile,"r"))
				for m in BaselinesData: 
					dataset.apply(lambda x:compare(x,m[0],m[1],m[2]),axis=1)
				os.remove(sitesname+"dcgkMO.csv")
				for filename in z.namelist( ):
					os.remove(filename)
	t1=time.perf_counter()           
	print("para check has been done!")
	print("总计耗时： "+str(t1-t0)+"秒")
	time.sleep(10)
	"============================================================================================================================================================="


              

if __name__ == '__main__':
	main()


          