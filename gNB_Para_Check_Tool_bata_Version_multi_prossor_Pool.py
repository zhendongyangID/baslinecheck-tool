# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 14:17:11 2019

@author: elopsuc
"""

import zipfile,os,random
import gzip,csv
import pandas as pd
import numpy as np
import math,time
import shutil  
import multiprocessing

def MOparaCheck(dcgkfile,baseline,temID):
    dcgkfile=csv.reader(open(dcgkfile,"r"))
    for MOpara in dcgkfile:
        p=str(MOpara[3])
        o=str(baseline[2])
        valueU=p.upper()
        valuebaseU=o.upper()
        if baseline[0] in MOpara[1] and baseline[1] in MOpara[2] and valuebaseU not in valueU:
            with open(temID+"MO参数核查结果.csv", "a+") as f:
                #line=MOpara[0]+","+MOpara[1]+","+MOpara[2]+","+MOpara[3]+","+baseline[2]+"\n"
                line=",".join([MOpara[0],MOpara[1],MOpara[2],MOpara[3],baseline[2]])
                f.write(line)
                f.write("\n")

        
 
def loghandle(SCbaselinefile,MObaselinefile,MOdumppath,names):
    newdir=random.randint(70000,99999)
    newdir=str(newdir)
    temID=newdir
    newdir=os.getcwd()+"\\"+newdir
    with open(temID+"MO参数核查结果.csv", "w+") as f:
        title="sitename,MO,para,current value,Baseline value\n"
        f.write(title)
    with open(temID+"系统常量参数核查结果.csv", "w+") as f:
        title="sitename,SC,current value,recommand value,Reason\n"
        f.write(title)
    "================================================================================================================================================================"
    
    "================================================================================================================================================================"
    
    for root, dirs, files in os.walk(MOdumppath):
        for name in files:
            mofile=os.path.join(root, name)
            print("正在处理以下MO文件： "+mofile)
            if "modump.zip" in mofile:
                z = zipfile.ZipFile(mofile, "r")
                #打印zip文件中的文件列表
                z.extractall(newdir)
                "=============================================================================================================================================================="
                for filename in z.namelist( ):
                    filename=newdir+"\\"+filename
                    if "_dcg_" in filename:
                      sitesname=filename[:-13]
                "=============================================================================================================================================================="
                for filename in z.namelist( ):
                    filename=newdir+"\\"+filename
                    
                    MOparaOutput(filename,newdir)
                    
                    SCbaslinecheck(SCbaselinefile,filename,sitesname,newdir,names)
                    
                "============================================================================================================================================================="
                #print(sitesname+"dcgkMO.csv")
                #dataset = pd.read_csv(sitesname+"dcgkMO.csv")
                dcgkfile=sitesname+"dcgkMO.csv"
                BaselinesData=csv.reader(open(MObaselinefile,"r"))
                for m in BaselinesData: 
                    #dataset.apply(lambda x:compare(x,m[0],m[1],m[2],temID),axis=1)
                    MOparaCheck(dcgkfile,m,temID)
                    

                shutil.rmtree(temID)
     





def compare(x,mo,para,value,temID):
     value=str(value)
     x[3]=str(x[3])
     value=value.strip()
     x[3]=x[3].strip()
     valueU=value.upper()
     valuesU=x[3].upper()
     if mo in x[1] and para in x[2] and valueU not in valuesU:
         with open(temID+"MO参数核查结果.csv", "a+") as f:
             line=x[0]+","+x[1]+","+x[2]+","+x[3]+","+value+"\n"
             f.write(line)

def SCcompare(x,sitename,temID,names):
    with open(temID+"系统常量参数核查结果.csv", "a+") as f:
        names=names.strip("_modump.zip")
        if math.isnan(x[1]):
            x[3]="gNB中没有写入该SC"
            x[1]=str(x[1])
            x[2]=str(x[2])
            line=names+","+x[0]+","+x[1]+","+x[2]+","+x[3]+"\n"
            f.write(line)
        elif math.isnan(x[2]):
            x[3]="gNB中多写入了该SC"
            x[1]=str(x[1])
            x[2]=str(x[2])
            line=names+","+x[0]+","+x[1]+","+x[2]+","+x[3]+"\n"
            f.write(line)
        elif x[1]!=x[2]:
            x[3]="gNB中该SC与推荐值不一致"
            x[1]=str(x[1])
            x[2]=str(x[2])
            line=names+","+x[0]+","+x[1]+","+x[2]+","+x[3]+"\n"
            f.write(line)
            
            
def SCbaslinecheck(SCbaselinefile,filename,sitesname,temID,names):
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
            SCS.apply(lambda x:SCcompare(x,sitesname,temID,names),axis=1)    
      
    
def MOparaOutput(filename,newdir):
    i=0
    j=0
    MOloc=[]
    sitename=""
    context=""
    if "_dcg_" in filename:
      sitename=filename[:-13]
      Tsitename=filename[:-13]
      
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
                                  #lines=mo+","+para[0]+","+para[1]
                                  lines=",".join([mo,para[0],para[1]])
                                  sitename=sitename.replace(newdir+"\\","")
                                  lines=",".join([sitename,lines])
                                  #lines=sitename+","+lines+"\n"
                                  lines=lines+"\n"
                                  if "==="  not in lines:
                                      context=context+lines
                                          
                                                      
                      j=j+2
      except IndexError:
          with open(Tsitename+"dcgkMO.csv", "w+",newline='') as f:
              f.write(context) 
          
          
def MergeResult(resultname,newresultname):
    SC=pd.DataFrame()
    path=os.getcwd()
    files=os.listdir(path)
    for file in files:
        if resultname in file:
            dataset = pd.read_csv(file,encoding='gbk')
            SC=pd.concat([SC,dataset], axis=0,join='outer',ignore_index=True)
            os.remove(file)
    SC.to_csv(newresultname,index=False,encoding='gbk')

          
"======================================================工具入口========================================================================================================"

"======================================================================================================================================================================="
if __name__ == '__main__':
    
    MObaselinefile=input("请输入MO参数baseline文件及完整路径（CSV格式）： ")
    SCbaselinefile=input("请输入系统常量baseline文件及完整路径（CSV格式）：")
    MOdumppath=input("请输入modump文件完整路径（存放_modump.zip文件的路径，文件可放于子文件内）： ")

    t0=time.perf_counter()
    coreNum=os.cpu_count()
    print("本次核查创建进程数：%d (由本机CPU个数决定)" % coreNum)
    pl=multiprocessing.Pool()
    for root, dirs, files in os.walk(MOdumppath):
        for name in files:
            mofile=os.path.join(root, name)
            if "modump.zip" in mofile:
                pl.apply_async(loghandle,(SCbaselinefile,MObaselinefile,root,name))
    pl.close()
    pl.join()
    resultnameMO="MO参数核查结果"
    newresultnameMO="MO参数_核查结果.csv"
    MergeResult(resultnameMO,newresultnameMO)
    resultnameSC="系统常量参数核查结果"
    newresultnameSC="系统常量参数_核查结果.csv"
    MergeResult(resultnameSC,newresultnameSC)
    t1=time.perf_counter()
    print("本次核查已完成，请查看 系统常量参数_核查结果.csv 与 MO参数_核查结果.csv ，结果存放路径为: "+os.getcwd()+",本次核查总计耗时： %.3f 秒" % (t1-t0))
    time.sleep(10)
