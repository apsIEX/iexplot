import tifffile
from iexplot.pynData import nData


def load_ADtiff(fpath,**kwargs):
    """
    reads tiff file and associated metadata and returns an pyNdata object
    
    fpath = fpath = the filename with the full path including extension
    
    **kwargs:
        verbose: print the fpath is loaded (default: False)
        debug:
   """
    kwargs.setdefault('verbose',False)
    kwargs.setdefault('debug',False)
    
    #read the tiff
    data=tifffile.imread(fpath)
    #make nData object
    AD=nData(data)
    setattr(AD,'fpath',fpath)
    #read the header
    d = _ADtiff_metadata(fpath,**kwargs)
    AD.updateExtras(d)
    #set scaling if in kwargs
    if 'scale' in kwargs:
        for key in kwargs['scale'].keys():
            AD.updateAx(key,kwargs['scale'][key][0],kwargs['scale'][key][1])
    return AD
    
def _ADtiff_metadata(fpath,**kwargs):
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
    return d