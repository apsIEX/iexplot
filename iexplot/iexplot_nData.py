#IEX_nData.py 
#wrapper to load data from IEX beamline as pynData
#if mda.py is in a location outside of the folder containing these files, you will need to %run first


__version__= 1.6      #AJE + JLM 9/12/2023 - updated imagetool stuff

import os as os
import re
from numpy import inf
import h5py

from iexplot.utilities import _shortlist 
from iexplot.iexplot_mda import PlotMDA
from iexplot.iexplot_EA import PlotEA
from iexplot.imagetool_wrapper import IEX_IT

from iexplot.pynData.nmda import nmda,nmda_h5Group_w,nmda_h5Group_r
from iexplot.pynData.nEA import nEA
from iexplot.pynData.pynData_ARPES import nARPES_h5Group_w, nARPES_h5Group_r
from iexplot.pynData.nADtiff import nTiff   

try:
    from iexcode.instruments.scanRecord import mda_filepath, mda_prefix
    from iexcode.instruments.electron_analyzer import EA_filepath, EA_prefix
except:
    print("iexcode is not loaded: you will need to specify path and prefix when calling IEXdata")


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
            path = mda_filepath()
        except:
            path=input("mda filepath needs to be specified")
        return path

    elif "EA" in dtype:
        try:
            path = EA_filepath()
        except:
            path = input("EA filepath needs to be specified")
        return path
    
        
def CurrentPrefix(dtype):
    #if dtype == "mda" or dtype == "mdaEA":
    if "mda" in dtype:
        try:
            prefix = mda_prefix()
        except:
            prefix = input("please specify the prefix")
        
    elif "EA" in dtype:
        try:
            prefix = EA_prefix()
        except:
            prefix = input("please specify the prefix")
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

 #########################################################################################################

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

#########################################################################################################
#########################################################################################################
class IEXdata(PlotMDA, PlotEA, IEX_IT):
    """"
    loads IEX (mda or EA) data and returns a dictionary containing pynData objects
        in Igor speak this is your experiment and the pynData objects are the waves

    ***** Usage: 
             mydata = IEXdata(first)  => single scan
                    = IEXdata(first,last,countby=1) => for a series of scans
                    = IEXdata(first,inf,overwrite=False) => all unloaded in the directory

             mydata.update(first,last,countby) updates the object mydata by loading scans, syntax is the same as above

             myData.mda = dictionary of all individual mda scans 
             myData.EA = dictionary of all individual EA scans 
             
             mda:
                 myData.mda[scanNum].det[detNum] => nmda object
                 myData.mda[scanNum].header => extra PVs
             EA:
                 myData.EA[scanNum] => EA_nData object" 

            =================================================================================================================
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
        
        if kwargs['debug']:
            print("\n_key2var kwargs:",kwargs)

        return kwargs
        
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
                    
                # elif self.prefix.lower() == "Kappa_".lower():
                #     #MPA tif files
                #     AD_dtype="mpa"
                #     ADext="tif"
                #     ADpath=os.path.join(userpath,AD_dtype,'')
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

        #add plotting 
        #mdaplot(self)
        #if 'EA' in AD_dtype:
        #    EAplot(self)

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
            ### updating data dictionary
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

 
    
            
 #########################################################################################################
 ##save and loading
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

                
                
    def remove_mda(self,*scans):
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
        fullList=list(self.keys())
        shortlist=_shortlist(*scans,llist=fullList)

        for key in shortlist:
            del self[key]
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

 
