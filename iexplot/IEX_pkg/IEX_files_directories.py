
try:
    from iexcode.instruments.scanRecord import mda_filepath, mda_prefix
    from iexcode.instruments.electron_analyzer import EA_filepath, EA_prefix
except:
    pass

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
