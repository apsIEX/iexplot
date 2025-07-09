#IEX_nData.py 
#wrapper to load data from IEX beamline as pynData
#if mda.py is in a location outside of the folder containing these files, you will need to %run first


#__version__= 1.6      #AJE + JLM 9/12/2023 - updated imagetool stuff
#__version__= 2.0      #JLM 7/31/2024 - cleaned up and added ADtiff
import os as os
import re
from numpy import inf
import h5py

from iexplot.utilities import _shortlist,_dirScanNumList, _create_dir_shortlist

from iexplot.IEX_pkg.IEX_MDA import IEX_MDA
from iexplot.IEX_pkg.IEX_EA import IEX_EA
from iexplot.IEX_pkg.IEX_ADtiff import IEX_ADtiff
from iexplot.IEX_pkg.IEX_MCA import IEX_MCA

#IEX data type plotting
from iexplot.IEX_pkg.Plot_MDA import Plot_MDA
from iexplot.IEX_pkg.Plot_EA import Plot_EA
from iexplot.IEX_pkg.Plot_AD import Plot_AD
from iexplot.IEX_pkg.Plot_MCA import Plot_MCA


 #########################################################################################################

 

#########################################################################################################
#########################################################################################################
class IEX_nData(Plot_MDA,Plot_EA,Plot_AD,Plot_MCA):
    """"
    loads IEX (mda, EA, ADtiff) data and returns a dictionary containing pynData objects
        in Igor speak this is your experiment and the pynData objects are the waves

    """

    def __init__(self,*scans, dtype="mdaAD",**kwargs):
        """
        *scans =>
            scanNum: for a single scan
            inf: for all scans in directory
            first,last: for all files between and including first and last; last can be inf
            first,last,countby: to load a subset
            [scanNum1,scanNum2]: to load a subset of scans
        
        dtype: data type
            = "mdaAD" - mda and Area Detector data such as EA, MCA if exist (default, Note:path is to mda files)
            = "mda" - mda only
            = "EA" or "EAnc" for ARPES images only h5 and nc respectively
            = "mpa" - mpa only
            = "ADtiff"  
            
        
        **kwargs
            path: full path to mda files directory (e.g. path="/net/s29data/export/data_29idc/2021_2/Jessica/mda/" )
                path = CurrentDirectory(dtype); default 
 
            prefix: filename prefix (e.g. "ARPES_" or "Kappa_" or "EA_")
                prefix = CurrentDirectory(dtype); default
                   
            suffix: suffix for filename
                suffix = ""; default
                   
            nzerors: number of digit in filename 
                nzerors= 4; default => 0001
            
            overwrite = True/False; to reloaded the data / only loaded unloaded data (default: True)  
            overwrite_AD 

            verbose: prints which scans are loaded (default: False)
            
            debug=False (default); if debug = True then prints lots of stuff to debug the program
            
            ** ADkwargs
            subset: used to load a subset of ADscans when dtype="mdaAD"; same formating as *scans
                subset=(1,inf,1); default => loads all
            AD_filepath
                default is ../dtype/ relative to mda folder
            AD_prefix
                default = "MDAscan"+str.zfill(str(mda_scanNum),self.nzeros)+"_"+str.zfill(str(AD_scanNum)
            
        """
        kwargs.setdefault('overwrite',True)
        kwargs.setdefault('verbose',False)
        kwargs.setdefault('debug',False)
        kwargs.setdefault("nzeros",4)
        kwargs.setdefault("subset",(1,inf,1))
        kwargs.setdefault("suffix",'')
        kwargs.setdefault("AD_overwrite",True)

    
        ### setting attributes
        self._scans = scans
        self.dtype = dtype
        self.nzeros = kwargs['nzeros']
        self.suffix = kwargs['suffix']
        self.ext = ''

        self.path = None
        self.prefix = None
        #setting prefix and path attributes
        self._IEX_path_prefix(**kwargs) 

        ### debug
        if kwargs["debug"]:
            print("\nIEX_nData.__init__")
            print("scans: ",scans)
            print("kwargs:",kwargs)
            print("self.vars")
            for key in vars(self):
                print('\t'+key+': ',getattr(self,key))

        ### loading data
        if scans:  #if loading scans 
            self._load_datasets(*scans, **kwargs)
        else:    #if just adding methods 
            pass
        
    def _IEX_path_prefix(self,**kwargs):
        """
        sets path and prefix to IEX default values
        """  
        kwargs.setdefault('debug',False)
        kwargs.setdefault('verbose',False)

        if kwargs['debug']:
                print("\n _IEX_path_prefix ")

        ### get path and prefix from iex.BL instance
        try:
            from IEX_files_directories import CurrentDirectory, CurrentPrefix
            if 'path' not in kwargs:
                mda_path = CurrentDirectory(self.dtype)
                kwargs['path'] = os.path.join(mda_path,"")
            if 'prefix' not in kwargs:
                kwargs.setdefault("prefix",CurrentPrefix(self.dtype))
            kwargs.update({'verbose':True})
        except:
            pass
        
        ### set path and prefix attributes
        if 'path' in kwargs:
            print(kwargs['path'])
            self.path = os.path.join(kwargs['path'],'')
            print(os.path.join(kwargs['path'],''))
        if 'prefix' in kwargs:
            self.prefix = kwargs['prefix']

        ### set path and prefix attributes
        if (kwargs["verbose"]==False) or kwargs['debug']:
            print("path = "+kwargs["path"])

    
    def _load_datasets(self,*scans,**kwargs):
        """
        loads mda, EA and ADtiff files
        """
        kwargs.setdefault('debug',False)
        kwargs.setdefault('verbose',False)

        ### set AD_key to EA for ARPES mdaAD
        ### set AD_key to MCA for Octupole mdaAD
        if 'tif' in self.dtype:
            AD_key = 'AD'
        elif 'EA' in self.dtype:
            AD_key = 'EA'
        elif ("AD" in self.dtype):
            if self.prefix.lower()=="ARPES_".lower():
                AD_key = "EA" 
            if self.prefix.lower()=="Octupole_".lower():
                AD_key = "MCA"    
            else:
                AD_key = 'AD'
        else:
                AD_key = None
        loadedList=[] 

        if kwargs["debug"] == True:
            print("\n_extractData dtype: ", self.dtype)
            print('\tAD_key = ',AD_key)
       
        iex_MDA = IEX_MDA(**kwargs)
        mda_kwargs = dict(kwargs)
        mda_kwargs.update({'path':self.path,'prefix':self.prefix,'ext':self.ext})

        # mda and mdaAD, mdaEA (Area detector + mda)
        if "mda" in self.dtype:
            #setting up mda only parameters
            mda_kwargs['ext'] = "mda"

            mdapath = os.path.dirname(self.path)
            userpath = os.path.dirname(mdapath)
            if kwargs["debug"]:
                print("\tmdapath: ",mdapath)
                print("\tuserpath: ",userpath) 

            #checking if mda exists 
            if hasattr(self,'mda') == False:
                setattr(self,'mda',{})
            attr = self.mda
            
            #making the list of mda scans to load
            mda_kwargs['excluded_list'] = list(attr.keys()) #files already loaded (only excluded if overwrite==True)
            mda_shortlist = self._create_shortlist(*scans, **mda_kwargs)
            
            if kwargs["debug"]:
                print("\nmda loading shortlist: ",mda_shortlist)
   
            for mda_scanNum in mda_shortlist:
                ### load a single mda scan
                if kwargs['debug']:
                    print ("\nMDAscanNum: ",mda_scanNum) 
                mda_d = iex_MDA.load_scans([mda_scanNum],**mda_kwargs)
                self.mda.update(mda_d)
                loadedList.append(list(mda_d.keys()))
                
                ### loading any associated area detector data
                if ('AD' in self.dtype) or ('EA' in self.dtype) :
                    AD_kwargs = dict(kwargs)
                    AD_kwargs['dtype'] = AD_key
                    AD_kwargs['userpath'] = userpath #extension gets added in _load_AD_data
                    if 'AD_prefix' in kwargs:
                        AD_kwargs['prefix'] = kwargs['AD_prefix']
                    else:
                        AD_kwargs['prefix'] = "MDAscan"+str.zfill(str(mda_scanNum),self.nzeros)+"_"                        

                    #checking if ADattr exists and get already loaded scans
                    if hasattr(self.mda[mda_scanNum],AD_key) == False:
                        setattr(self.mda[mda_scanNum],AD_key,{})
                    ADattr = getattr(self.mda[mda_scanNum],AD_key)
                    AD_kwargs['excluded_list'] = list(ADattr.keys()) 
                    
                    AD_d,AD_shortlist   = self._load_ADdata(self,self.dtype,**AD_kwargs)
                    if kwargs['debug']:
                        print('\nAD_d',AD_d)
                        print('AD_shortlist',AD_shortlist)
                    if len(AD_shortlist) >0:
                        setattr(self.mda[mda_scanNum],AD_key,AD_d)
                        #Add scaling here
                        for AD in AD_d:
                            if (AD.data.shape)
                    else:
                        if kwargs['debug']:
                            print('dtype = '+self.dtype+' has no associated AD data')
                    
                

        #loading EA or AD only
        elif ('AD' in self.dtype) or ('EA' in self.dtype): 
            AD_kwargs = dict(kwargs)
            AD_kwargs.update({'subset':scans})
            if kwargs['debug']:
                print('/n AD or EA data only')
            AD_d,AD_shortlist   = self._load_ADdata(self,self.dtype,**AD_kwargs)
           
            setattr(self,AD_key,AD_d)
            loadedList.append(AD_shortlist)
             
        if (kwargs["verbose"]) or kwargs['debug']:
            print("Loaded "+self.dtype+" scanNums: "+str(loadedList))
        return self
    
    def _create_shortlist(self, *scans, **kwargs):
        """
        requires the following kwargs:
            path
            prefix
            ext
        ** optional kwargs used + _shortlist kwargs:
            nzeros
            excluded_list 
            overwrite
        """
        kwargs.setdefault('debug',False)
        kwargs.setdefault('overwrite',True)
        kwargs.setdefault('excluded_list',[])
        
        shortlist_kwargs = {'debug':kwargs['debug'],
                            'excluded_list':kwargs['excluded_list'],
                            'overwrite':kwargs['overwrite']}
        if kwargs['debug']:
            print('IEX_nData._create_shortlist')
            print(*scans,kwargs['path'],kwargs['prefix'],kwargs['ext'])
        
        shortlist = _create_dir_shortlist(*scans,path=kwargs['path'],prefix=kwargs['prefix'],ext=kwargs['ext'], **shortlist_kwargs)
        return shortlist
    
    def _load_ADdata(self,*scans, **kwargs):
        """

        """
        kwargs.setdefault('debug',False)
        kwargs.setdefault('dtype',self.dtype)
        kwargs.setdefault('path',self.path)
        kwargs.setdefault('prefix',self.prefix)
        kwargs.setdefault('ext','')
        kwargs.setdefault("subset",(1,inf,1))


        if kwargs['debug']:
            print('\n_load_ADdata')
            print('\tkwargs: ',kwargs)

        if 'EA' in kwargs['dtype']:  
            iex_EA = IEX_EA(**kwargs)
            iex_EA.set_by_dtype(kwargs['dtype'])
            kwargs['ext'] = iex_EA.dtype
            load_f = iex_EA.load
        
        elif 'tif' in kwargs['dtype']: 
            iex_ADtiff = IEX_ADtiff()
            kwargs['ext'] = 'TIFF'
            load_f = iex_ADtiff.load

        elif 'mca' in kwargs['dtype'].lower():
            iex_MCA = IEX_MCA(**kwargs)
            if 'userpath' in kwargs:
                kwargs['path'] = os.path.join(kwargs['userpath'],'mca','')
                kwargs.pop('userpath')
            kwargs['ext'] = 'mda'
            load_f = iex_MCA.load

        if len(kwargs['ext']):
            if 'userpath' in kwargs:
                kwargs['path'] = os.path.join(kwargs['userpath'],kwargs['ext'],'')
        
        if kwargs["debug"]:
            print("\tLoading AD_dtype = "+kwargs['dtype'])
            print("\tAD prefix",kwargs['prefix'])
            print("\tAD path: ",kwargs['path'])
            print("\tAD ext: ",kwargs['ext'])

        
        #creating short list
        scans = kwargs['subset']
        shortlist = self._create_shortlist(*scans, **kwargs)
        if kwargs['debug']:
            print('\tAD shortlist: ',shortlist)
        
        ### loading AD data
        if len(shortlist)>0:
            d = load_f(shortlist,**kwargs)
            return d,shortlist  
        else:
            return {},[]                             
                  

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

        key_list = ['dtype','path','prefix','suffix','nzeros']
        for key in kwargs:
            if key in key_list:
                 setattr(self,key,kwargs[key])
            
        for key in key_list:
            kwargs.update({key:getattr(self,key)})
        self._load_datasets(*scans,**kwargs)
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
            
        self._load_datasets(*scans,**kwargs)
        return 
        
    def info(self):
        """
        """
        for attr in ['mda','EA','AD']:
            if hasattr(self,attr):
                message = attr+" scans loaded:"
                scan_list = list(getattr(self,attr).keys())
                print(message)
                print("\t"+str(scan_list))
    
            
 #########################################################################################################
 ##save and loading
 #########################################################################################################
    # def save(self, fname, fdir=''):
    #     """
    #     saves the IEXdata dictionary for later reloading
    #     h5 file
    #         group: mda => contains all the mda scans
    #             group: mda_scanNum
    #                 attr: fpath
    #                 group: header
    #                     attributes with header info
    #                 group: det 
    #                     nDataGroup for each detector
    #                 group: posx
    #                     nDataGroup for each x positioner
    #                 group: posy ...
    #                     nDataGroup for each y positioner
                        
    #         group: EA => contains all the EA scans
    #             group: EA_scanNum
    #                 attr: fpath
    #                 attr: mdafname
    #                 group: header
    #                     attributes with header ino
    #                 group: image 
    #                     nDataGroup for image
    #                 group: EDC
    #                     nDataGroup for EDC
    #                 group: MDC ...
    #                     nDataGroup for MDC
    #                 group: nData_ARPES
    #                     attr: hv, wk, thetaX, thetaY, angOffset, slitDir
    #                     dataset:KEscale,angScale
    
    #     """
    #     #opening the file
    #     if fdir=='':
    #         fdir = os.getcwd()

    #     fpath = os.path.join(fdir, fname+'.h5')
    #     print(fpath)

    #     if os.path.exists(fpath):
    #         print('Warning: Overwriting file {}.h5'.format(fname))
    #     h5 = h5py.File(fpath, 'w')
    #     h5.attrs['creator']= 'IEX_nData'
    #     h5.attrs['version']= 1.0
        
    #     #IEXdata_attrs
    #     IEXdata_attrs=['dtype','path','prefix','nzeros','suffix','ext']
    #     for attr in IEXdata_attrs:
    #         h5.attrs[attr]=getattr(self,attr)
   
        
    #     #mda
    #     gmda=h5.create_group('mda')
    #     for scanNum in self.mda:
    #         nd=self.mda[scanNum]
    #         name=str(scanNum)
    #         nmda_h5Group_w(nd,gmda,name)


    #     h5.close()
    #     return 

                
                
    # def remove_mda(self,*scans):
    #     """
    #     *scans =>
    #         scanNum: for a single scan
    #         inf: for all scans in directory
    #         first,last: for all files between and including first and last; last can be inf
    #         first,last,countby: to load a subset
    #         [scanNum1,scanNum2]: to load a subset of scans
    #     Usage:
    #         remove(mydata.mda,[234,235,299])
    #     """
    #     fullList=list(self.keys())
    #     shortlist=_shortlist(*scans,llist=fullList)

    #     for key in shortlist:
    #         del self[key]
    #     print("removed scans: "+str(shortlist) )
    #     return


# def h5info(f):
#     h5printattrs(f)
#     for group in f.keys():
#         print(group)
#         h5printattrs(f[group])
            
            
# def h5printattrs(f): 
#     for k in f.attrs.keys():
#         print('{} => {}'.format(k, f.attrs[k]))

# def load_IEXnData(fpath):
#     """
#     Loads data saved by IEXnData.save
    
#     """
#     h5 = h5py.File(fpath, 'r')
   
#     #IEXdata
#     mydata=IEXdata()
#     for attr in h5.attrs:
#         setattr(mydata,attr,h5.attrs[attr])  
    
#     #mda
#     gmda=h5['mda']
#     mdaLoaded=[]
#     for scan in gmda.keys():
#         scanNum=int(scan)
#         mydata.mda[scanNum]=nmda_h5Group_r(gmda[scan])
#         mdaLoaded.append(scanNum)  
#     print("mda scans: "+str(mdaLoaded))
        

#     return mydata

 
