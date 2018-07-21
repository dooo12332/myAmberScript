import os
import argparse

recName=None
recType=None
ligName=None
ligType=None
iscreat=False
isrec=False

#def method
def cLeapIn(recpath,ligpath,recName,recType,ligName,ligType):
    newleap=open(ligpath,'w')
    newleap.writelines('source leaprc.protein.ff14SB\n')
    newleap.writelines('source leaprc.water.tip3p\n')
    if  ligType=='mol2':
        newleap.writelines('loadamberparams frcmod.ionsjc_tip3p\n')
        newleap.writelines('loadamberparams lig.frcmod\n')
    newleap.writelines('pdb =load%s %s/%s%s\n'%(recType[1:4],recpath,recName,recType))
    newleap.writelines('lig =load%s %s%s\n'%(ligType[1:4],ligName,ligType))
    newleap.writelines('com = combine{pdb lig}\n')
    newleap.writelines('charge com\n')
    newleap.writelines('savepdb com com.pdb\n')
    newleap.writelines('saveamberparm com com.prmtop com.inpcrd\n')
    newleap.writelines('saveamberparm pdb pdb.prmtop pdb.inpcrd\n')
    newleap.writelines('saveamberparm lig lig.prmtop lig.inpcrd\n')
    newleap.writelines('solvatebox com TIP3PBOX %s\n'%args.box)
    newleap.writelines('addions com Cl- 0\n')
    newleap.writelines('addions com Na+ 0\n')
    newleap.writelines('savepdb com com_wat.pdb\n')
    newleap.writelines('saveamberparm com com_wat.prmtop com_wat.inpcrd\n')
    newleap.writelines('quit\n')
    newleap.close()

def isHaveStr(strings,filenames):
    for string in strings:
        if  filenames.find(string)!=-1:
            return True
    return False
#end def method

perser=argparse.ArgumentParser(description='manual to this script')
perser.add_argument('-p','--path',type=str,default=os.getcwd(),help='path')
perser.add_argument('-tag',type=str,default=None)
perser.add_argument('-cdir',help='creat dir',action='store_true')
perser.add_argument('-rp','--receptorpath',type=str,default=None,help='path of receptor')
perser.add_argument('-leap',help='tleap',action='store_true')
perser.add_argument('-box',type=int,default=12,help='cutoff of WAT box')
perser.add_argument('-clear',action='store_true',help='bath remove file')
args=perser.parse_args()

aminoacids=['gly','ala','pro','val','leu','ile','met','phe','tyr',
'trp','ser','thr','cys','asn','gln','lys','his','arg','asp','glu']

#creat dir 
if  args.cdir:
    for num in range(20):
        if  (os.path.exists('%s/%s%s_%s'%(args.path,args.tag,num+1,aminoacids[num]))==False):
            os.mkdir('%s//%s%s_%s'%(args.path,args.tag,num+1,aminoacids[num]))
            print('%s//%s%s_%s was creat'%(args.path,args.tag,num+1,aminoacids[num]))
#end creat dir

#tleap
if  args.leap:
    if  args.receptorpath!=None:
        print ('receptor path=%s'%args.receptorpath)
        for root, dirs, files in os.walk(args.receptorpath):  
            for file in files:
                #.find net return true or false,it return location,if not find, return -1
                if os.path.splitext(file)[0].find('recin')!=-1:
                    recName= os.path.splitext(file)[0]
                    recType=os.path.splitext(file)[1]
                    print('find receptor %s'%file)
                    isrec=True
        if  recName==None:
            print('can\'t findn receptor')
    for root,dirs,files in os.walk(args.path):
        for dirss in dirs:
            #print ('iscreat=%s'%iscreat)
            print('now into %s'%dirss)
            os.chdir('./%s/'%dirss)
            print('now in %s'%os.getcwd())
            #is not exists leap.in
            if  os.path.exists('%s/leap.in'%os.getcwd())==False:
                print('there is no leap.in')
                iscreat=True
                #fint rec and lig
                for root, dirs, files in os.walk(os.getcwd()):  
                    for file in files:
                        #.find net return true or false,it return location,if not find, return -1
                        if (os.path.splitext(file)[0].find('recin')!=-1) and isrec==True:
                            recName= os.path.splitext(file)[0]
                            recType=os.path.splitext(file)[1]
                            print('find receptor %s'%file)
                        if  os.path.splitext(file)[0].find('ligin')!=-1:
                            ligName= os.path.splitext(file)[0]
                            ligType=os.path.splitext(file)[1]
                            print('find ligand %s'%file)
            #creat leap.in
            #print (iscreat)
            if  ((recName==None or ligName==None) and iscreat==True):
                print('can\'t find receptor or linand in ,skip this dir')
                 #exit dir
                os.chdir(args.path)
                iscreat=False
                print('\n')
                continue
            elif (iscreat==True and isrec==True):
                print ('now creat leap.in file')
                cLeapIn(args.receptorpath,'%s//leap.in'%os.getcwd(),recName,recType,ligName,ligType)
                if isrec==False:
                    recName=None
                    recType=None
                ligName=None
                ligType=None
            else:
                print('leap.in is aleady exists')    
            #run
            print('now creat tleap.sh file')
            runbash=open('%s/tleap.sh'%os.getcwd(),'w')
            runbash.writelines('#!bash/bin\ntleap -f leap.in >tleap.log')
            runbash.close()
            print('run')
            os.system('bash tleap.sh')
            print('delete tleap.sh')
            os.remove('%s/tleap.sh'%os.getcwd())
            #exit dir
            os.chdir(args.path)
            iscreat=False
            print('\n')
#end tleap

#clear 
clearFile=['com','lig.','leap.']
if  args.clear==True:
    for root,dirs,files in os.walk(args.path):
        for dirss in dirs:
            #print ('iscreat=%s'%iscreat)
            print('now into %s'%dirss)
            os.chdir('./%s/'%dirss)
            print('now in %s'%os.getcwd())
            #is not exists leap.in
            #fint rec and lig
            for root, dirs, files in os.walk(os.getcwd()):  
                for file in files:
                    if  isHaveStr(clearFile,file):
                        print('remove %s%s'%(os.path.splitext(file)[0],os.path.splitext(file)[1]))
                        os.remove(file)
            print('now out this dir')
            os.chdir(args.path)



        














         


        


    

