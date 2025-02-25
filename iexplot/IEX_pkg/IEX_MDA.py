import os

from iexplot.pynData.nmda import nmda

class IEX_MDA:
    """
    loads IEX mda files and adds plotting methods

    usage: used by IEXdata or can be used alone 
        kwargs = {
            'prefix':'ARPES_',
            'nzeros':4,
            'suffix':'',
            'ext':"mda",
            'path':'/Users/jmcchesn/Documents/NoteBooks/Data/Brahlek/Brahlek_2021_2/mda/'
            }

        short_list=[127]
        data = IEX_MDA()
        data.mda = data.load_scans(short_list,**kwargs)

    """
    def __init__(self,**kwargs):
        """
        """
        self.prefix = ''
        self.nzeros = 4
        self.suffix = ''
        self.ext = 'mda'
        self.path = ''

        self._update_attr(**kwargs)

        pass

    def _update_attr(self, **kwargs):
        for key in kwargs:
            if key in vars(self):
                setattr(self,key,kwargs[key])

    def load_scans(self,short_list,**kwargs):
        """
        child class of IEXData which loads mda files and returns a dictionary of pyndata objects 
        adds header details to attributes 
        
        short_list is a list of scanNum
        
        ** kwargs:
            path (default: self.path)
            prefix (default: self.prefix) 
            nzeros (default: self.nzeros)
            suffix (default: self.suffix)
            ext (default: self.ext)

        filename = prefix + scanNum.zfill(n) + suffix + "." + ext
        fpath = path + filename

        """
        kwargs.setdefault('prefix',self.prefix )
        kwargs.setdefault('nzeros',self.nzeros )
        kwargs.setdefault('suffix',self.suffix )
        kwargs.setdefault('ext',self.ext )
        kwargs.setdefault('path',self.path )
  
        
        kwargs.setdefault('debug',False)
        kwargs.setdefault('verbose',False)

        mda_dict = {}

        #create list of filename to load
        files2load = [kwargs['prefix']+str.zfill(str(scanNum),kwargs['nzeros'])+kwargs['suffix']+"."+kwargs['ext'] for scanNum in short_list]    

        for (i,fname) in enumerate(files2load):
           
            ### File info:
            fullpath = os.path.join(kwargs['path'],fname)
            
            if kwargs["debug"] == True:
                print(fullpath)

            #loading mda file
            mda = nmda(fullpath,**kwargs)
            
            #header
            headerList = mda.header.ScanRecord
            headerList.update(mda.header.all)
            
            ### updating data dictionary
            mda_dict.update({short_list[i]:mda})   
        return mda_dict

