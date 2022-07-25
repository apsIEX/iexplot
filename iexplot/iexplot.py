#IEX_nData.py 
#wrapper to load data from IEX beamline as pynData
#if mda.py is in a location outside of the folder containing these files, you will need to %run first


__version__= 1.0      #JLM 4/27/2021

import os as os
import re
from time import sleep
import numpy as np
from numpy import inf
import h5py
import pandas as pd
import matplotlib.pyplot as plt

try:
    import netCDF4 as nc
except:
    print("netCDF4 and/or tifffile are not part of the environment")
    
from iexplot.pynData.nmda import nmda,nmda_h5Group_w,nmda_h5Group_r
from iexplot.pynData.nEA import nEA
from iexplot.pynData.pynData_ARPES import nARPES_h5Group_w, nARPES_h5Group_r
from iexplot.pynData.nADtiff import nTiff   
from iexplot.pynData.pynData import niceplot  

try:
    from pyimagetool import ImageTool, RegularDataArray
except:
    print("pyimagetool not imported")

try:
    from IEX_beamline.beamline import BL_ioc
    from IEX_beamline.scanRecord import saveData_get_all 
    from IEX_beamline.AD_utilites import AD_CurrentDirectory, AD_prefix
    from IEX_beamline.EA import EA
except:
    print("ScanFunctions_IEX and ScanFunctions_EA are not loaded: you will need to specify path and prefix when calling IEXdata")


###################################
## default stuff (Users can modify here to load an home not using IEX function)
###################################
def CurrentDirectory(dtype):
    """
    Returns the current directory for:
       if "mda" is in dtype => return mda path
       elif "EA" is in dtype => returns EA path
       
       e.g. dtype=mdaEA => only get mda
    """
    if "mda" in dtype:
        try:
            ioc_pv = BL_ioc()
            path=saveData_get_all(ioc_pv)['filepath']
        except:
            path=input("mda filepath needs to be specified")
        return path

    elif "EA" in dtype:
        try:
            path=AD_CurrentDirectory(EA._savePlugin)
        except:
            path=input("EA filepath needs to be specified")
        return path
    
        
def CurrentPrefix(dtype):
    #if dtype == "mda" or dtype == "mdaEA":
    if "mda" in dtype:
        try:
            ioc_pv = BL_ioc()
            prefix = saveData_get_all(ioc_pv)['baseName']
        except:
            prefix = input("please specify the prefix")
        
    elif "EA" in dtype:
        try:
            prefix=AD_prefix(EA._savePlugin)+"_"
        except:
            prefix="prefix_"
    return prefix

###################################
# IEX variables
def _EAvariables(dtype):
    """
    default variable for EA for IEX as fo 05/10/2021
    """
    EAvar={}
    if dtype == "EA_nc":
        EAvar["EA_dtype"]="nc"
        EAvar["EA_nzeros"]=4
        #default detector values for old nc driver
        EAvar["EA_source"] = "APS_IEX"
        EAvar["EA_centerChannel"] = 571-50
        EAvar["EA_firstChannel"] = 0
        EAvar["EA_degPerPix"] = 0.0292717
        EAvar["EA_cropStart"] = 338-50
        EAvar["EA_cropStop"] = 819-50
        
    elif dtype == "EA":
        EAvar["EA_dtype"] = "h5"
        EAvar["EA_nzeros"] = 4
        #default detector values for old nc driver
        EAvar["EA_source"] = "APS_IEX"
        EAvar["EA_centerChannel"] = 571-50
        EAvar["EA_firstChannel"] = 0
        EAvar["EA_degPerPix"] = 0.0292717
        EAvar["EA_cropStart"] = 338-50
        EAvar["EA_cropStop"] = 819-50
    return EAvar


###################################
    
def _mdaHeader_IEX(cls,headerList,**kwargs):
    """
    General IEX beamline information
    """
    kwargs.setdefault('debug',False)
    
    if kwargs['debug']:
        print('cls.prefix:',cls.prefix)
        print('BL info')
        
    setattr(cls, 'ID', {key:value[:3] for key, value in headerList.items() if 'ID29' in key}) 
    setattr(cls,'mono',{key:value[:3] for key, value in headerList.items() if 'mono' in key})
    setattr(cls,'energy',{key:value[:3] for key, value in headerList.items() if 'energy' in key.lower()})
    setattr(cls,'motor',{key:value[:3] for key, value in headerList.items() if '29idb:m' in key})
    setattr(cls,'slit',{key:value[:3] for key, value in headerList.items() if 'slit' in key.lower()} )
    if 'filename' in headerList:
        setattr(cls,'prefix',headerList['filename'].split('/')[-1].split('_')[0]+"_")
    
    ##kappa
    if cls.prefix.lower() == "Kappa_".lower():
        if kwargs['debug']:
            print("kappa")
        _mdaHeader_Kappa(cls,headerList)
        
    #ARPES
    if cls.prefix.lower() == "ARPES".lower():
        if kwargs['debug']:
            print("ARPES")
        _mdaHeader_ARPES(cls,headerList)

def _mdaHeader_Kappa(cls,headerList):
    """
    Kappa specific header info
    """
    sampleInfo={**{key:value[:3] for key, value in headerList.items() if '29idKappa:m' in key},
                **{key:value[:3] for key, value in headerList.items() if '29idKappa:Euler' in key},
                **{key:value[:3] for key, value in headerList.items() if 'LS331' in key}}
    setattr(cls, 'sample',sampleInfo)
    setattr(cls, 'mirror',{key:value[:3] for key, value in headerList.items() if '29id_m3r' in key})
    setattr(cls, 'centroid',{key:value[:3] for key, value in headerList.items() if 'ps6' in key.lower()})
    detkeys=['29idMZ0:scaler1.TP','29idKappa:m9.RBV','29idKappa:userCalcOut10.OVAL','29iddMPA:C0O','29idKappa:userStringSeq6.STR1','29idd:Unidig1Bo0']
    detInfo={**{key:value[:3] for key, value in headerList.items() if '29idd:A' in key},
             **{key:value[:3] for key,value in headerList.items() if key in detkeys}}
    setattr(cls, 'det',detInfo)
    comment=""
    for i, key in enumerate(list(headerList.keys())):
            if re.search('saveData_comment1', key) : 
                comment=str(headerList[key][2])
            elif re.search('saveData_comment2', key) : 
                if headerList[key][2] != '':
                    comment+=' - '+str(headerList[key][2])
    setattr(cls, 'comment',comment)
    UBinfo={**{key:value[:3] for key, value in headerList.items() if '29idKappa:UB' in key}}
    setattr(cls, 'UB',UBinfo)


def _mdaHeader_ARPES(cls,headerList):
    """
    ARPES specific header info
    """    
    sampleInfo={**{key:value[:3] for key, value in headerList.items() if '29idc:m' in key},
                **{key:value[:3] for key, value in headerList.items() if '29idARPES:LS335' in key}
               
               }
    setattr(cls, 'sample',sampleInfo)



###################################
def _shortlist(*nums,llist,**kwargs):
    """
    Making a shortlist based on *num
    *num =>
        nums: for a single scan
        inf: for all num in longlist
        first,last: for all numbers between and including first and last; last can be inf
        first,last,countby: to load a subset
        [num1,num2]: to load a subset of scans
    kwargs:
        debug=False
    """
    kwargs.setdefault("debug",False)
    
    if kwargs['debug']:
        print("nums: ",nums)
        print("llist",llist)
    llist.sort()
    if type(nums[0]) is list:
        shortlist=nums[0]
    else:
        if len(nums)==1:
            if nums[0] != inf:
                first,last,countby=nums[0],nums[0],1
            else:
                first,last,countby=llist[0],llist[-1],1
        elif len(nums)==2:
            first,last=nums
            countby=1
        elif len(nums)==3:
            first,last,countby=nums
        if last == inf:
            last=llist[-1]
        #print(first,last,countby)
        shortlist=[]

        for n in range(first,last+countby,countby): 
            if n in llist:
                shortlist.append(n)
    if kwargs["debug"]:
        print("shortlist: ",shortlist)
    return shortlist
    
def _dirScanNumList(path,prefix,extension):
    """
    returns a list of scanNumbers for all files with prefix and extension in path
    """

    #getting and updating directory info
    allfiles = [f for f in os.listdir(path) if os.path.isfile(path+f)]
    #print(allfiles)

    split=prefix[-1] 
    allfiles_prefix = [x for (i,x) in enumerate(allfiles) if allfiles[i].split(split)[0]==prefix[:-1]] 
    #print(allfiles_prefix)

    allfiles_dtype = [x for (i,x) in enumerate(allfiles_prefix) if allfiles_prefix[i].split('.')[-1]==extension]
    #print(allfiles_dtype)

    allscanNumList = [int(allfiles_dtype[i][allfiles_dtype[i].find('_')+1:allfiles_dtype[i].find('_')+5]) for (i,x) in enumerate(allfiles_dtype)]
    #print(allscanNumList)

    return allscanNumList        

###################################       
class IEXdata:
    """"
    loads IEX (mda or EA) data and returns a dictionary containing pynData objects
        in Igor speak this is your experiment and the pynData objects are the waves

    ***** Usage: 
             mydata = IEXdata(first)  => single scan
                    = IEXdata(first,last,countby=1) => for a series of scans
                    = IEXdata(first,inf,overwrite=False) => all unloaded in the directory

             mydata.update(firt,last,countby) updates the object mydata by loading scans, syntax is the same as above

             myData.mda = dictionary of all individual mda scans 
             myData.EA = dictionary of all individual EA scans 
             
             mda:
                 myData.mda[scanNum].det[detNum] => nmda object
                 myData.mda[scanNum].header => extra PVs
             EA:
                 myData.EA[scanNum] => EA_nData object" 

        """

    def __init__(self,*scans, dtype="mdaAD",**kwargs):
        """
        *scans =>
            scanNum: for a single scan
            inf: for all scans in directory
            first,last: for all files between and including first and last; last can be inf
            first,last,countby: to load a subset
            [scanNum1,scanNum2]: to load a subset of scans
        
        dtype = "mdaAD" - mda and EA/mpa if exist (default, Note:path is to mda files)
                  = "mda" - mda only
                  = "EA" or "EAnc" for ARPES images only h5 and nc respectively
                  = "mpa" - mpa only
        
        **kwargs
            path: full path to mda files directory (e.g. path="/net/s29data/export/data_29idc/2021_2/Jessica/mda/" )
                path = CurrentDirectory(dtype); default 
 
            prefix: filename prefix (e.g. "ARPES_" or "Kappa_" or "EA_")
                prefix = CurrentDirectory(dtype); default
                   
            suffix: suffix for filename
                suffix = ""; default
                   
            nzerors: number of digit in filename 
                nzerors= 4; default => 0001
            
            overwrite = True/False; if False, only loads unloaded data"  
            
            q=False (default prints filepath and which scans are loaded); q=True turns off printing
            
            debug=False (default); if debug = True then prints lots of stuff to debug the program
            
            subset: used to load a subset of ADscans when dtype="mdaAD"; same formating as *scans
                subset=(1,inf,1); default => loads all
        """
        kwargs.setdefault('overwrite',True)
        kwargs.setdefault('q',False)
        kwargs.setdefault('debug',False)
        kwargs.setdefault("nzeros",4)
        kwargs.setdefault("subset",(1,inf,1))
        
        if kwargs["debug"]:
            print("IEX_nData.__init__")

        self._scans=scans
        self.dtype=dtype
        
        self.mda={}
        self._mdaLoadedFiles =[]
        
        if kwargs["debug"]:
            print("scans: ",scans)
            print("kwargs:",kwargs)
            for key in vars(self):
                print(key,getattr(self,key))
   
        if scans:
            kwargs.update(self._key2var(**kwargs))
            self._extractData(*scans, **kwargs)
        else:
            pass
        
        
    def _key2var(self,**kwargs):
        """
        defines default IEXdata **kwargs and
        sets self.var kwargs 
        """
        kwargs.setdefault('overwrite',True)
        kwargs.setdefault("suffix",'')
        kwargs.setdefault("nzeros",4)
        kwargs.setdefault("debug",False)

        if 'path' not in kwargs:
            kwargs.setdefault("path",CurrentDirectory(self.dtype))
        if 'prefix' not in kwargs:
            kwargs.setdefault("prefix",CurrentPrefix(self.dtype))
        
        if kwargs["debug"]:
            print("\nIEX_nData._key2var kwargs:",kwargs)
            
        if kwargs["q"]==False:
            print("path = "+kwargs["path"])
        
        self.path = os.path.join(kwargs['path'],"")
        self.prefix = kwargs['prefix']
        self.nzeros = kwargs['nzeros']
        self.suffix =kwargs['suffix']
        #if self.dtype == "mdaEA":
        if "mda" in self.dtype:
            self.ext="mda"
        else:
            self.ext=self.dtype
        return kwargs
        if kwargs['debug']:
            print("\n_key2var kwargs:",kwargs)
        
    def _extractData(self,*scans,**kwargs):
        """
        *scans =>
            scanNum: for a single scan
            inf: for all scans in directory
            first,last: for all files between and including first and last; last can be inf
            first,last,countby: to load a subset
            [scanNum1,scanNum2]: to load a subset of scans
        
        **kwargs
            overwrite = True; reloads all data specified by *scans
                      = False; only loads the data specified by *scans which has not already been loaded
            subset = (1,inf,1); default => only for mdaAD
            
        **optional kwargs without default values:              
            ADupdate: used to load only unloaded ADfiles 
        
        """
        kwargs.setdefault('debug',False)
        kwargs.setdefault('overwrite',True)
        kwargs.setdefault('q',False)
        kwargs.setdefault('subset',(1,inf,1))

        
        if "nzeros" in kwargs:
            self.nzeros=kwargs["nzeros"]

        if kwargs["debug"] == True:
            print("IEX_nData._extractData dtype: ", self.dtype)
            
        
        
        loadedList=[]
        ########################################################################
       #loading EA only
        if self.dtype == "EA" or self.dtype =="EA_nc":           
            self.ext=_EAvariables(self.dtype)["EA_dtype"] 
            allscanNumList=_dirScanNumList(self.path,self.prefix,self.ext)
            shortlist=_shortlist(*scans,llist=allscanNumList,**kwargs)
            if kwargs["debug"] == True:
                print("shortlist: ",shortlist)
            loadedList=self._eaIEXdata(self,shortlist,**kwargs) 
        
        # mda and mdaAD
        if "mda" in self.dtype:
            #mda scans
            loadedList=[]
            self.ext="mda"
            MDAallscanNumList=_dirScanNumList(self.path,self.prefix,self.ext)
            MDAshortlist=_shortlist(*scans,llist=MDAallscanNumList,**kwargs)
            mdapath=os.path.dirname(self.path)
            userpath=os.path.dirname(mdapath)
            if kwargs["debug"]:
                print("mdapath: ",mdapath)
                print("userpath: ",userpath)
                
            AD_dtype = ""
            ADext = ""
            ADpath = "" 
            ADprefix = ""
                
            if "AD" in self.dtype:  
                if self.prefix.lower()=="ARPES_".lower():
                    #EA files
                    AD_dtype = "EA"
                    ADext=_EAvariables(AD_dtype)["EA_dtype"]  
                    ADpath=os.path.join(userpath,ADext,'')
                    
                elif self.prefix.lower() == "Kappa_".lower():
                    #MPA tif files
                    AD_dtype="mpa"
                    ADext="tif"
                    ADpath=os.path.join(userpath,AD_dtype,'')
                else:
                    print("no AD associated with this IOC")
                
                if "ADupdate" in kwargs:
                    kwargs_init=kwargs
                    kwargs.update({"overwrite":True}) #overwriting the mda file associated with the AD
                
                if kwargs["debug"]:
                    print(AD_dtype+" path: ",ADpath)
                    print(AD_dtype+" ext: ",ADext)
                
    
            for MDAscanNum in MDAshortlist:
                #load mda scans
                MDAloadedList=self._mdaIEXdata([MDAscanNum],**kwargs)
                loadedList.append(MDAloadedList)
                
                #loading AD data 
                if len(ADpath)>1:
                    ##Getting filename prefix for AD
                    if 'EA' in AD_dtype: 
                        ADprefix="MDAscan"+str.zfill(str(MDAscanNum),self.nzeros)+"_"
                        
                    if 'mpa' in AD_dtype:
                        ADprefix="MDAscan"+str.zfill(str(MDAscanNum),self.nzeros)+"_"
                        
                    if kwargs['debug']:
                        print ("MDAscanNum: ",MDAscanNum)
                        print("ADprefix",ADprefix)
                    
                    #Getting list of all files with ADprefix
                    ADallscanList=_dirScanNumList(ADpath,ADprefix,ADext)
                    if kwargs['debug']:
                        print("ADallscanList",ADallscanList)#Empty
                    
                    #loading AD data
                    if len(ADallscanList)>0:
                        kwargs.update({"MDAscanNum":MDAscanNum})
                        initialVals={}
                        #getting mda attr loading AD files
                        for i,key in enumerate(["path","prefix","ext"]):
                            initialVals.update({key:getattr(self, key)})
                            setattr(self,key,eval('AD'+key))
                        initialVals.update({"overwrite":kwargs['overwrite']})
                        
                        #ADupdate only loads unloaded AD scans
                        if "ADupdate" in kwargs:
                            kwargs.update({"overwrite":False})

                        ADshortlist=_shortlist(*kwargs['subset'],llist=ADallscanList,**kwargs)
                        if kwargs['debug']:
                            print('ADshortlist',ADshortlist)
                            
                        if 'EA' in AD_dtype:
                            if kwargs['debug']:
                                print("Loading EA")   
                            ADloadedList=self._eaIEXdata(self.mda[MDAscanNum],ADshortlist,**kwargs) 
                            
                        elif 'mpa' in AD_dtype:
                            if kwargs['debug']:
                                print("Loading mpa")
                            ADloadedList=self._mpaIEXdata(ADshortlist,**kwargs)
                        if kwargs['debug']:
                            print("\nADloadedList",ADloadedList)

                        #setting mda attr back
                        for i,key in enumerate(["path","prefix","ext"]):
                            setattr(self,key,initialVals[key])
                        kwargs['overwrite']=initialVals['overwrite']
                
        if kwargs["q"] == False:
            print("Loaded "+self.dtype+" scanNums: "+str(loadedList))
        return self
    
    def _mdaIEXdata(self,shortlist,**kwargs):
        """
        loads mda files into IEXdata.mda dictionary
        """
       
        mdaNumList = list(self.mda.keys())    
        if kwargs["overwrite"] == False: #only load new scans
            shortlist =[x for x in shortlist if x not in mdaNumList]  
            
        if kwargs["debug"]:
            print("_mdaIEXdata shortlist: ",shortlist)

        #adding scanNums from shortlist to scanNomList without duplicates
        mdaNumList+= [x for x in shortlist if x not in mdaNumList]
        mdaNumList.sort()

        #create list of filename to load
        files2load = [self.prefix+str.zfill(str(x),self.nzeros)+self.suffix+"."+self.ext for x in shortlist]

        #adding fileNames to loadedFiles without duplicates
        self._mdaLoadedFiles += [x for x in files2load if x not in self._mdaLoadedFiles]
        self._mdaLoadedFiles.sort()        

        #load files and add to / update exp dictionary
        for (i,fname) in enumerate(files2load):
            ##### File info:
            fullpath=self.path+fname
            if kwargs["debug"] == True:
                print(fullpath)
            mda=nmda(fullpath,q=1)
            headerList=mda.header.ScanRecord
            headerList.update(mda.header.all)
            _mdaHeader_IEX(mda.header,headerList)
            self.mda.update({shortlist[i]:mda})
        return shortlist

    def _eaIEXdata(self,obj,shortlist,**kwargs):
        """
        creates a obj.EA dictionary if doesn't exist, and loads EA and EA_nc files into it
            obj = self; (dtype='EA')
            obj = self.mda[MDAscanNum]; (dtype='mdaAD')
            shortlist: list of EAscanNums to load
            
        **kwargs:
            overwrite=False; default
            debug=False; default
        """
        kwargs.setdefault("overwrite",False)
        kwargs.setdefault("debug",False) 
                
        if kwargs["debug"]:
            print('\nIEX_nData._eaIEXdata')
            print('self.dtype:',self.dtype)
            print('kwargs:\n',kwargs)
        
        if hasattr(obj,'EA')==False:
            setattr(obj,'EA',{})
            setattr(obj,"_EALoadedFiles",[])   
        
        EANumList = list(obj.EA.keys())   
        if kwargs["overwrite"] == False: #only load new scans
            shortlist =[x for x in shortlist if x not in EANumList]  
        
        #adding scanNums from shortlist to scanNomList without duplicates
        EANumList+= [x for x in shortlist if x not in EANumList]
        EANumList.sort()

        #create list of filename to load
        files2load = [self.prefix+str.zfill(str(x),self.nzeros)+self.suffix+"."+self.ext for x in shortlist]
        obj._EALoadedFiles += [x for x in files2load if x not in obj._EALoadedFiles]
        obj._EALoadedFiles.sort()
        
        #load files and add to / update exp dictionary
        for (i,fname) in enumerate(files2load):
            ##### File info:
            fullpath=os.path.join(self.path,fname)
            if kwargs["debug"]:
                print("EA fullpath: ",fullpath)
            EA=nEA((fullpath),**kwargs)#nEA(fullpath,**kwargs)              
            obj.EA.update({shortlist[i]:EA})
        return shortlist
                                
    def _mpaIEXdata(self, shortlist,**kwargs):  
        """
        creates a obj.mpa dictionary if doesn't exist, and loads mpa (tif) files into it
            obj = self; (dtype='EA')
            obj = self.mda[MDAscanNum]; (dtype='mdaAD')
            shortlist: list of EAscanNums to load
            
        **kwargs:
            overwrite=False; default
            debug=False; default
        """
        kwargs.setdefault("overwrite",False)
        kwargs.setdefault("debug",False) 
                
        if kwargs["debug"]:
            print('\nIEX_nData._mpaIEXdata')
            print('self.dtype:',self.dtype)
            print('kwargs:\n',kwargs)
        
        if hasattr(self,'mpa')==False:
            setattr(self,'mpa',{})
            setattr(self,"_mpaLoadedFiles",[])   
        
        mpaNumList = list(self.mpa.keys())   
        if kwargs["overwrite"] == False: #only load new scans
            shortlist =[x for x in shortlist if x not in mpaNumList]  
        
        #adding scanNums from shortlist to scanNomList without duplicates
        mpaNumList+= [x for x in shortlist if x not in mpaNumList]
        mpaNumList.sort()

        #create list of filename to load
        files2load = [self.prefix+str.zfill(str(x),self.nzeros)+self.suffix+"."+self.ext for x in shortlist]
        self._mpaLoadedFiles += [x for x in files2load if x not in self._mpaLoadedFiles]
        self._mpaLoadedFiles.sort()
        
        #load files and add to / update exp dictionary
        for (i,fname) in enumerate(files2load):
            ##### File info:
            fullpath=os.path.join(self.path,fname)
            if kwargs["debug"]:
                print("mpa fullpath: ",fullpath)
            mpa=nTiff((fullpath),**kwargs)              
            self.mpa.update({shortlist[i]:mpa})
        return shortlist                                

    def update(self,*scans,**kwargs):
        """
        *scans =>
            scanNum: for a single scan
            inf: for all scans in directory
            first,last: for all files between and including first and last; last can be inf
            first,last,countby: to load a subset
            [scanNum1,scanNum2]: to load a subset of scans
        dtype = mda / EA / EAnc 
        
        **kwargs
            path = CurrentDirectory(dtype)
            prefix = SaveData or ADplugin 
            suffix = ""
            nzerors = number of digit; (4 => gives (0001))
            
            overwrite = True/False; if False, only loads unloaded data"  
            
            See nmda and nEA for additional kwargs
            
            Note: see nmda and nEA for additional dtype specific **kwargs
        """  
        kwargs.setdefault('overwrite',True)
        kwargs.setdefault('debug',False)

        for key in kwargs:
            if key in ['dtype','path','prefix','suffix','nzeros']:
                 setattr(self,key,kwargs[key])
            
        self._extractData(*scans,**kwargs)
        return  
    
    def updateAD(self,*scans,**kwargs):
        """
        updates an mdaAD so that the mda is updated and only the unloaded AD are loaded
            mda with overwrite=True
            AD with overwite=False
        
        *scans =>
            scanNum: for a single scan
            inf: for all scans in directory
            first,last: for all files between and including first and last; last can be inf
            first,last,countby: to load a subset
            [scanNum1,scanNum2]: to load a subset of scans
        dtype = mda / EA / EAnc 
        
        **kwargs
            path = CurrentDirectory(dtype)
            prefix = SaveData or ADplugin 
            suffix = ""
            nzerors = number of digit; (4 => gives (0001))
            
            overwrite = True/False; if False, only loads unloaded data" 
            ADupdate in kwargs
            
            See nmda and nEA for additional kwargs
            
            Note: see nmda and nEA for additional dtype specific **kwargs
        """  
        kwargs.setdefault('overwrite',True)
        kwargs.setdefault('debug',False)
        kwargs.update({"ADupdate":True})

        for key in kwargs:
            if key in ['dtype','path','prefix','suffix','nzeros']:
                 setattr(self,key,kwargs[key])
            
        self._extractData(*scans,**kwargs)
        return 
        
    def info(self):
        """
        """
        print("mda scans loaded:")
        print("\t"+str(list(self.mda.keys())))
        print("EA scans loaded:")
        print("\t"+str(list(self.EA.keys())))
        
        for key in vars(self): 
            if key[0] != "_" and key not in ['mda','EA']: 
                print(key+": "+str(vars(self)[key]))
#########################################################################
    def mdaPos(self,scanNum, posNum=0):
        """
        returns the array for a positioner
                        
        usage for 1D data:
        x = mdaPos(305)
        y = mdaDet(305,16)
        
        plt.plot(x,y)
        """
        return self.mda[scanNum].posx[posNum].data
 
    def mdaPos_label(self,scanNum, posNum=0):
        """
        returns the array for a positioner
                        
        usage for 1D data:
        x = mdaPos(305)
        xlabel = mdaPos_label(305)
        
        y = mdaDet(305,16)
        ylabel = mdaDet_label(305,16)
        
        plt.plot(x,y)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        """

        return self.mda[scanNum].posx[posNum].pv[1] if len(self.mda[scanNum].posx[posNum].pv[1])>1 else self.mda[scanNum].posx[posNum].pv[0]

    def mdaDet(self,scanNum, detNum):
        """
        returns the array for a positioner and positioner pv/desc.
                        
        usage for 1D data:
        x = mdaPos(305)
        y = mdaDet(305,16)
        
        """
        return self.mda[scanNum].det[detNum].data
    
    def mdaDet_label(self,scanNum, detNum):
        """
        returns the array for a positioner
                        
        usage for 1D data:
        x = mdaPos(305)
        xlabel = mdaPos_label(305)
        
        y = mdaDet(305,16)
        ylabel = mdaDet_label(305,16)
        
        plt.plot(x,y)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        """

        return self.mda[scanNum].det[detNum].pv[1] if len(self.mda[scanNum].det[detNum].pv[1])>1 else self.mda[scanNum].det[detNum].pv[0]

    def _plot1D(self,x,y,**kwargs):
        """
        x / y 1D numpy arrays 
        **kwargs
             Norm2One: True/False to normalize graph between zero and one
             offset: y += offset 
             scale: y *= scale
             offset_x: x += offset_x 
             scale_x: x *= scale_x
        """
        kwargs.setdefault('Norm2One',False)
        kwargs.setdefault("offset",0)
        kwargs.setdefault("scale",1)
        kwargs.setdefault("offset_x",0)
        kwargs.setdefault("scale_x",1)
        
        if kwargs['Norm2One']:
            y=(y-min(y))/(max(y)-min(y))
                
        #offset and scaling
        y=y*kwargs["scale"]+kwargs["offset"]
        x=x*kwargs["scale_x"]+kwargs["offset_x"]
            
        #remove nonstandard kwargs
        for key in ["Norm2One","offset","scale","offset_x","scale_x"]:
            del kwargs[key]
            
        if 'xlabel' in kwargs:
            plt.xlabel(kwargs['xlabel'])
            del kwargs['xlabel']
        if 'ylabel' in kwargs:
            plt.ylabel(kwargs['ylabel'])
            del kwargs['ylabel']
            
        plt.plot(x,y,**kwargs)
        
    
    def plotmda(self,scanNum, detNum, posNum=0,**kwargs):
        """
        simple plot for an mda scans either 1D or a row/column of a 2D data set
        detector vs positioner
  
        **kwargs
             Norm2One: True/False to normalize spectra between zero and one (default => False)
             offset: y += offset 
             scale: y *= scale
             offset_x: x += offset_x 
             scale_x: x *= scale_x
             
             2D data: plots image by default
                row = index for plotting a single row from a 2D data set
                column = index for plotting a single row from a 2D data set
             
            and standard plt.plot **kwargs
            e.g. label=str(scanNum), marker="o"
        """
        kwargs.setdefault("offset",0)
        kwargs.setdefault("scale",1)
        kwargs.setdefault("offset_x",0)
        kwargs.setdefault("scale_x",1)
        kwargs.setdefault('Norm2One',False)
        
        y=self.mdaDet(scanNum, detNum)
        kwargs['ylabel']=self.mdaDet_label(scanNum, detNum)
        
        x=self.mdaPos(scanNum, posNum)
        kwargs['xlabel']=self.mdaPos_label(scanNum, posNum)
        if len(y.shape)==2:
            if "row" not in kwargs and "column" not in kwargs:
                if kwargs['Norm2One']:
                    print('Norm2One not currently implemented in 2D data, adjust vmin,vmax')
                    del kwargs['Norm2One']
            self.plotmda2D(scanNum, detNum, **kwargs)
                
        else:
            x,y,kwargs=self._reduce2d(x,y, **kwargs)
            self._plot1D(x,y,**kwargs)
    
    def plotmda_detVdet(self,scanNum, y_detNum, x_detNum, **kwargs):
        """
        simple plotting for an mda scan
        detector vs detector
                
        Norm2One: True/False to normalize spectra between zero and one

        **kwargs
             Norm2One: True/False to normalize spectra between zero and one (default => False)
             offset: y += offset 
             scale: y *= scale
             offset_x: x += offset_x 
             scale_x: x *= scale_x
             
             2D data: plots image by default
                row = index for plotting a single row from a 2D data set
                column = index for plotting a single row from a 2D data set
             
            and standard plt.plot **kwargs
            e.g. label=str(scanNum), marker="o"
        """
        kwargs.setdefault("offset",0)
        kwargs.setdefault("scale",1)
        kwargs.setdefault("offset_x",0)
        kwargs.setdefault("scale_x",1)
        
        y=self.mdaDet(scanNum, y_detNum)
        kwargs['ylabel']=self.mdaDet_label(scanNum, y_detNum)
        
        x=self.mdaDet(scanNum, x_detNum)
        kwargs['xlabel']=self.mdaDet_label(scanNum, x_detNum)
        
        if len(y.shape)==2:
            if "row" not in kwargs and "column" not in kwargs:
                if kwargs['Norm2One']:
                    print('Norm2One not currently implemented in 2D data, adjust vmin,vmax')
                    del kwargs['Norm2One']
            self.plotmda2D(scanNum, y_detNum, **kwargs)
                
        else:     
            x,y,kwargs=self._reduce2d(x,y, **kwargs)
            self._plot1D(x,y,**kwargs)
            
            
    def _reduce2d(self,x,y, **kwargs):
        """
        takes the 2D arrays, x and y and reduces them to 1D arrays removes column/row form kwargs
        **kwargs:
            column
            row
        """
        if "row" in kwargs:
            x=x[kwargs['row'],:]
            y=y[kwargs['row'],:] 
            del kwargs['row']
                
        if "column" in kwargs:
            x=x[:,kwargs['column']]
            y=y[:,kwargs['column']] 
            del kwargs['column']
        return x,y,kwargs
    
    


        
        
        
        
        
        
    def plotmda2D(self, scanNum, detNum, **plotkwargs):
        """
        plots 2D mda data
        **plotkwargs are the standard matplotlib argument
            cmap
        """
        niceplot(self.mda[scanNum].det[detNum], **plotkwargs)
        
    def EAspectra(self,scanNum, EAnum=1, BE=False):
        """
        returns the array for an EAspectra, and x and y scaling
            
        usage:
            plt.imgshow(data.EAspectra))
            
        """
        EA = self.mda[scanNum].EA[EAnum]
        img = EA.data
        x = EA.scale['x']
        y = EA.scale['y']
        
        if BE:
            hv=EA.hv
            if wk == None:
                if EA.wk == None:
                    wk=0
                else:
                    wk=EA.wk
            x=hv-wk-x
            
        return img, x,y
        
    def EAspectraEDC(self,scanNum, EAnum=1, BE=False):
        """
        returns x,y energy scaling, EDC spectra
            
        usage:
            plt.plot(data.EAspectraEDC(151))
            
        """
        EA = self.mda[scanNum].EA[EAnum]
        x = EA.EDC.scale['x']
        y = EA.EDC.data
        
        if BE:
            hv=EA.hv
            if wk == None:
                if EA.wk == None:
                    wk=0
                else:
                    wk=EA.wk
            x=hv-wk-x
        
        return x,y
        
    def plotEDC(self,scanNum, EAnum=1,**kwargs):
        """
        simple plotting for EDC

        EAnum = sweep number (default = 1)
              = inf => will sum all spectra
        if
            dtype="EA"  => y=data.EA[scanNum]
            dtype="mdaEA" or "mdaAD"  => y=data.mda[scanNum]EA[EAnum]
        BE = False uses KE scale
        BE = True use BE=hv-KE-wk
        if wk=None uses metadata
        
        *kwargs are the matplot lib kwargs plus the following
            BE: True/False for Binding Energy or Kinetic Energy scale (default = False (KE))
            wk: None/value, if None uses the value from the metadata
            ##### additional plotting
            Norm2One: True/False to normalize spectra between zero and one
            offset: y += offset 
            scale: y *= scale
            offset_x: x += offset_x 
            scale_x: x *= scale_x
        """
        kwargs.setdefault("BE",False)
        kwargs.setdefault("wk",None)
        
        kwargs.setdefault("Norm2One",False)
        kwargs.setdefault("offset",0)
        kwargs.setdefault("scale",1)
        kwargs.setdefault("offset_x",0)
        kwargs.setdefault("scale_x",1)
        
        x=0;y=0            
        
        if self.dtype == "EA":
            d=self.EA[scanNum]
            y=d.EDC.data
            x=d.EDC.scale['x']

        elif self.dtype == "mdaEA" or "mdaAD":
            if EAnum == inf:
                EAlist = list(self.mda[scanNum].EA.keys()) 
            else:
                EAlist = [EAnum]

            for EAnum in EAlist:
                d=self.mda[scanNum].EA[EAnum]
                y=d.EDC.data
                x=d.EDC.scale['x']
 
        BE=kwargs["BE"]
        wk=kwargs["wk"]
        if BE:
            hv=d.hv
            if wk == None:
                if d.wk == None:
                    wk=0
                else:
                    wk=d.wk
            x=hv-wk-x
        
        for key in ["BE","wk"]:
            del kwargs[key]
        
        self._plot1D(x,y,**kwargs)
        
        if BE:
            plt.xlim(max(x),min(x))
    
    def plotEA(self,scanNum,EAnum=1,Escale="KE",transpose=False,**imkwargs):
        """
        simple plotting for EDC
        if
            dtype="EA"  => y=data.EA[scanNum]
            dtype="mdaEA" or "mdaAD"  => y=data.mda[scanNum]EA[EAnum]
        """  
        
        
        if self.dtype == "EA":
            EA=self.EA[EAnum]

        elif self.dtype == "mdaEA" or "mdaAD":
            EA=self.mda[scanNum].EA[EAnum]
            
        #wk=0 if type(self.EA[EAnum].wk)==None else self.EA[EAnum].wk
        #hv=EA.hv           
        img=EA.data
        xscale=EA.scale['x']
        #if Escale=="BE":
        #    xscale=hv-wk-xscale
        yscale=EA.scale['y']
        xunit=EA.unit['x']
        yunit=EA.unit['y']
            
            
        imkwargs.setdefault("extent",[xscale[0],xscale[-1],yscale[0],yscale[-1]])
        plt.xlabel(xunit)
        plt.ylabel(yunit)
        if transpose == True:
            img = img.t
        plt.imshow(img,aspect='auto',**imkwargs)
      
    

    def stackmdaEA(self,mdaScanNum,**kwargs):
        """
        makes an ImageTool.RegularArray of EA files in a single mda scan
        mdaScanNum = the scanNum corresponding to the mda scan
        **kwargs:
            subset=(start,stop,countby); default = (1,inf,1)
            EDConly=False; default = False full image
                   = True, EDCs are stacked
        """
        kwargs.setdefault("subset",(1,inf,1))
        kwargs.setdefault("EDConly",False)
        kwargs.setdefault("debug",False)
              
        ra=None
        MDAscan=self.mda[mdaScanNum]
        rank=MDAscan.header.all['rank']
        shortlist=_shortlist(*kwargs['subset'],llist=list(MDAscan.EA.keys()),**kwargs)
        first=shortlist[0]
        Escale=MDAscan.EA[first].scale['x']
        Eunit=MDAscan.EA[first].unit['x']
        Ascale=MDAscan.EA[first].scale['y']
        Aunit=MDAscan.EA[first].unit['y']
        
        if kwargs['EDConly']:
            if rank ==1:
                print("Don't know if ImageTool can deal with 1D data")
            elif rank > 1:
                ROstack=np.vstack(tuple(MDAscan.EA[key].EDC.data for key in shortlist)) 
                stack=np.swapaxes(ROstack,1,0)
                Mscale=MDAscan.posy[0].data[0:list(MDAscan.EA.keys())[-1]]
                Munit=MDAscan.posy[0].pv[1]
                if pd.Series(Mscale).is_unique:
                    if pd.Series(Mscale).is_monotonic_decreasing:
                        Mscale=np.flip(Mscale,0)
                        stack=np.flip(stack,1)
                else: 
                    Mscale=np.arange(0,len(list(MDAscan.EA.keys())))
                ra=RegularDataArray(stack,axes=[Escale,Mscale],dims=[Eunit,Munit])
        else:
            print(Aunit,Eunit)
            if rank == 1:
                stack=MDAscan.EA[shortlist[0]].data
                ra=RegularDataArray(stack,axes=[Ascale,Escale],dims=[Aunit,Eunit])
            elif rank > 1:
                stack=np.dstack(tuple(MDAscan.EA[key].data for key in shortlist))   
                Mscale=MDAscan.posy[0].data[0:list(MDAscan.EA.keys())[-1]]
                Munit=MDAscan.posy[0].pv[1]

                if pd.Series(Mscale).is_unique:
                    if pd.Series(Mscale).is_monotonic_decreasing:
                        Mscale=np.flip(Mscale,0)
                        stack=np.flip(stack,2)
                else: 
                    Mscale=np.arange(0,len(list(MDAscan.EA.keys())))
                ra=RegularDataArray(stack,axes=[Ascale,Escale,Mscale],dims=["angle","energy",Munit])
        return ra 
    
    def stackmdaEA_multi(self,*mdaScanNum,**kwargs):
            """
            makes an ImageTool.RegularArray of multiple mdaEA scans
            *mdaScanNum = first,last,countby or list
            **kwargs:
                EDConly = False (default); stack of full images
                        = True; stack of EDCs 
                EAnum = 1; which EA scan number to use 
                stackScale = None (default); uses the mdaScanNums
                           = (start, delta, units) to specifiy you own
            """
            kwargs.setdefault("EDConly",False)
            kwargs.setdefault("EAnum",1)
            kwargs.setdefault("stackScale",None)
            kwargs.setdefault("debug",False)

            ra=None
            shortlist=_shortlist(*mdaScanNum,llist=list(self.mda.keys()),**kwargs)
            first=shortlist[0]           
            EAnum=kwargs["EAnum"]

            Escale=self.mda[first].EA[kwargs['EAnum']].scale['x']
            Eunit=self.mda[first].EA[kwargs['EAnum']].unit['x']
            Ascale=self.mda[first].EA[kwargs['EAnum']].scale['y']
            Aunit=self.mda[first].EA[kwargs['EAnum']].unit['y']
            if kwargs['stackScale'] == None:
                Mscale=np.array(shortlist) 
                Munit="scanNum"
            else:
                Mscale=np.arange(kwargs['stackScale'][0],kwargs['stackScale'][0]+len(shortlist)*kwargs['stackScale'][1], kwargs['stackScale'][1])
                Munit=kwargs['stackScale'][2]

            if kwargs['EDConly']:       
                ROstack=np.vstack(tuple(self.mda[key].EA[EAnum].EDC.data for key in shortlist)) 
                stack=np.swapaxes(ROstack,1,0)


                if pd.Series(Mscale).is_unique:
                    if pd.Series(Mscale).is_monotonic_decreasing:
                        Mscale=np.flip(Mscale,0)
                        stack=np.flip(stack,1)
                ra=RegularDataArray(stack,axes=[Escale,Mscale],dims=[Eunit,Munit])

            else:
                print(Aunit,Eunit)
                if len(shortlist) == 1:
                    self.mda[shortlist[0]].EA[EAnum].data
                    ra=RegularDataArray(stack,axes=[Ascale,Escale],dims=[Aunit,Eunit])
                elif len(shortlist):
                    try:
                        stack=np.dstack(tuple(self.mda[key].EA[EAnum].data for key in shortlist))   
                    except:
                        print(self.mda.keys())

                    if pd.Series(Mscale).is_unique:
                        if pd.Series(Mscale).is_monotonic_decreasing:
                            Mscale=np.flip(Mscale,0)
                            stack=np.flip(stack,2)
                    else: 
                        Mscale=np.arange(0,len(list(self.mda[shortlist[0]].EA.keys())))

            if len(stack.shape) == 2:
                ra=RegularDataArray(stack,axes=[Escale,Mscale],dims=["energy",Munit])
            else:
                ra=RegularDataArray(stack,axes=[Ascale,Escale,Mscale],dims=["angle","energy",Munit])
            return ra

 #########################################################################################################
    
    def save(self, fname, fdir=''):
        """
        saves the IEXdata dictionary for later reloading
        h5 file
            group: mda => contains all the mda scans
                group: mda_scanNum
                    attr: fpath
                    group: header
                        attributes with header info
                    group: det 
                        nDataGroup for each detector
                    group: posx
                        nDataGroup for each x positioner
                    group: posy ...
                        nDataGroup for each y positioner
                        
            group: EA => contains all the EA scans
                group: EA_scanNum
                    attr: fpath
                    attr: mdafname
                    group: header
                        attributes with header ino
                    group: image 
                        nDataGroup for image
                    group: EDC
                        nDataGroup for EDC
                    group: MDC ...
                        nDataGroup for MDC
                    group: nData_ARPES
                        attr: hv, wk, thetaX, thetaY, angOffset, slitDir
                        dataset:KEscale,angScale
    
        """
        #opening the file
        if fdir=='':
            fdir = os.getcwd()

        fpath = os.path.join(fdir, fname+'.h5')
        print(fpath)

        if os.path.exists(fpath):
            print('Warning: Overwriting file {}.h5'.format(fname))
        h5 = h5py.File(fpath, 'w')
        h5.attrs['creator']= 'IEX_nData'
        h5.attrs['version']= 1.0
        
        #IEXdata_attrs
        IEXdata_attrs=['dtype','path','prefix','nzeros','suffix','ext']
        for attr in IEXdata_attrs:
            h5.attrs[attr]=getattr(self,attr)
   
        
        #mda
        gmda=h5.create_group('mda')
        for scanNum in self.mda:
            nd=self.mda[scanNum]
            name='mda_'+str(scanNum)
            nmda_h5Group_w(nd,gmda,name)


            
        #EA
        gEA=h5.create_group('EA')
        for scanNum in self.EA:
            nd=self.EA[scanNum]
            name="EA_"+str(scanNum)
            nARPES_h5Group_w(nd,gEA,name)


        h5.close()
        return

                
                
def remove(cls,*scans):
    """
    *scans =>
        scanNum: for a single scan
        inf: for all scans in directory
        first,last: for all files between and including first and last; last can be inf
        first,last,countby: to load a subset
        [scanNum1,scanNum2]: to load a subset of scans
    Usage:
        remove(mydata.mda,[234,235,299])
    """
    fullList=list(cls.keys())
    shortlist=_shortlist(*scans,llist=fullList)

    for key in shortlist:
        del cls[key]
    print("removed scans: "+str(shortlist) )
    return


def h5info(f):
    h5printattrs(f)
    for group in f.keys():
        print(group)
        h5printattrs(f[group])
            
            
def h5printattrs(f): 
    for k in f.attrs.keys():
        print('{} => {}'.format(k, f.attrs[k]))

def load_IEXnData(fpath):
    """
    Loads data saved by IEXnData.save
    
    """
    h5 = h5py.File(fpath, 'r')
   
    #IEXdata
    mydata=IEXdata()
    for attr in h5.attrs:
        setattr(mydata,attr,h5.attrs[attr])  
    
    #mda
    gmda=h5['mda']
    mdaLoaded=[]
    for scan in gmda.keys():
        scanNum=int(scan.split("_")[-1])
        mydata.mda[scanNum]=nmda_h5Group_r(gmda[scan])
        mdaLoaded.append(scanNum)  
    print("mda scans: "+str(mdaLoaded))
        
    #EA
    gEA=h5['EA']
    EAloaded=[]
    for scan in gEA.keys():
        scanNum=int(scan.split("_")[-1])
        mydata.EA[scanNum]=nARPES_h5Group_r(gEA[scan])
        EAloaded.append(scanNum)
        
    print("EA scans: "+str(EAloaded))
    h5.close()
    
    return mydata


def EAImageTool(mdaScanNum,**kwargs):
    """
    to be run in ipython not in jupyter (cause the kernal to crash)
    multi=False stacks EA files from a single mda scan
    multi=True stacks EA files from multiple mda scans
    **kwargs:
        includes kwargs for loading data IEXdata
            path,prefix,dtype...
        include stackEA kwargs
            subset,EDConly
    """
    global it

    data=IEXdata(mdaScanNum, **kwargs)
    ra=data.stackmdaEA(mdaScanNum,**kwargs)
    
    it=ImageTool(ra,'LayoutComplete')
    it.show()