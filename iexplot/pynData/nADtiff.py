import tifffile
from iexplot.pynData import nData
<<<<<<< HEAD

def load_ADtiff(fpath,**kwargs):
=======
class nTiff:
    def __init__(self,*fpath,**kwargs):
        """
        fpath = full path including filename and extension
        
        kwargs:
            verbose (default = False);Verbos prints full file path when loading
            debug=False
        Usage: 
        tif=ntif(fpath)
        """
        kwargs.setdefault('verbose',False)
        kwargs.setdefault('debug',False)
        
        if kwargs['debug']:
            print('\nADtiff')
        
        self.fpath=''
        self.scanNum=None
        self.header={}
        
        if fpath:
            self.fpath=fpath[0]
            self._extractAll(**kwargs)
        else:
            pass
            
            
def read_return_nData(fpath,**kwargs):
>>>>>>> refs/remotes/origin/main
    """
    reads tiff file and associated metadata and returns an pyNdata object
    
    fpath = fpath = the filename with the full path including extension
    
    **kwargs:
        verbose: print the fpath is loaded (default: False)
        debug:
<<<<<<< HEAD
        scale = {'x':(data,unit),'y':(data,unit)}
=======
>>>>>>> refs/remotes/origin/main
    """
    kwargs.setdefault('verbose',False)
    kwargs.setdefault('debug',False)
    
    #read the tiff
    data=tifffile.imread(fpath)
<<<<<<< HEAD
    #make nData object
    AD=nData(data)
    #read the header
    d = _ADtiff_metadata(fpath,**kwargs)
    AD.updateExtras(d)
    #set scaling if in kwargs
    if 'scale' in kwargs:
        for key in kwargs['scale'].keys():
            AD.updateAx(key,kwargs['scale'][key][0],kwargs['scale'][key][1])
    return AD
    
def _ADtiff_metadata(fpath,**kwargs):
=======
    #read the header
    d = read_ADtif_metadata(fpath,**kwargs)
    #make nData object
    tif=nData(data)
    tif.updateExtras(d)
    return tif
    
def read_ADtif_metadata(fpath,**kwargs):
>>>>>>> refs/remotes/origin/main
    """
    reads and returns the metadata as a dictionary
    fpath = the filename with the full path including extension
    """
    kwargs.setdefault('debug',False)
    kwargs.setdefault('verbose',False)
    d={}
    with tifffile.TiffFile(fpath) as tif:
        for page in tif.pages:
            if kwargs['debug']:
                print(page)
            #test extra pvs
            for tag in page.tags:
                try: 
                    tag_name, tag_value = tag.name, tag.value
                    try:
                        tag_name, tag_value  = tag_value.split(':')
                    except:
                        pass
                    d[tag_name]=tag_value
                    if kwargs['verbose']:
                        print('\t', tag_name, ': ', tag_value)
                    
                except:
                    pass
<<<<<<< HEAD
    return d



=======
    return d
>>>>>>> refs/remotes/origin/main
