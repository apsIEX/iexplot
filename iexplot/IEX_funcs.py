from os import path
try:
    from iexcode.instruments.scanRecord import mda_filepath, mda_prefix
    from iexcode.instruments.electron_analyzer import EA_filepath, EA_prefix
except:
    print("iexcode is not loaded: you will need to specify path and prefix when calling IEXdata")




###################################
## default stuff (Users can modify here to load an home not using IEX function)
###################################
def CurrentDirectory(dtype=''):
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
       
    elif "EA" in dtype:
        try:
            path = EA_filepath()
        except:
            path = input("EA filepath needs to be specified")
    else:
        path = input("EA filepath needs to be specified")
    return path
        
def CurrentPrefix(dtype=''):
    """
    Returns the current prefix for:
       if "mda" is in dtype => return mda path
       elif "EA" is in dtype => returns EA path
       
       e.g. dtype=mdaEA => only get mda
    """
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
    else:
        prefix = input("please specify the prefix")
    return prefix

def IEX_scanNum_fpath(scanNum,fullpath=True,**kwargs):
    """
    
    turns a scanNum to file name using IEX default parameters
    fullpath    True => filename including full path
                False => filename only
        **kwargs:
            prefix: default => mda_prefix()
            path:  default => mda_filepath()
            nzeros
            suffix
            ext

    """
    kwargs.setdefault('nzeros',4 )
    kwargs.setdefault('suffix','' )
    kwargs.setdefault('ext','mda')
    
    if 'prefix' not in kwargs:
        try: 
            kwargs['prefix'] = mda_prefix()
        except: 
            kwargs['prefix'] = input('Specify prefix:')
            
    fname = kwargs['prefix']+str.zfill(str(scanNum),kwargs['nzeros'])+kwargs['suffix']+"."+kwargs['ext']
    
    if fullpath:
        if 'path' not in kwargs:
            try: 
                kwargs['path'] = mda_prefix()
            except: 
                kwargs['path'] = input('Specify path to data folder:')
                
        fpath = path.join(kwargs['path'],fname)
        return fpath
    
    else:
        return fname 