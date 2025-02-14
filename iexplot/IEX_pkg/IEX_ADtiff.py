import os

from iexplot.pynData.nADtiff import load_ADtiff


class IEX_ADtiff:
    """
    """
    def __init__(self,**kwargs):
        """
        """
        pass

    def load(self,shortlist,**kwargs):
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
        kwargs.setdefault('debug',False)
        kwargs.setdefault('verbose',False)

        if kwargs['debug']:
            print('\nIEX_ADtiff.load')

        try:
            kwargs.setdefault('prefix',self.prefix )
            kwargs.setdefault('nzeros',self.nzeros )
            kwargs.setdefault('suffix',self.suffix )
            kwargs.setdefault('ext',self.ext )
            kwargs.setdefault('path',self.path )
            if kwargs['debug']:
                print('kwargs: ',kwargs)
        except:
            pass

        d = {}
    
        #create list of filename to load
        files2load = [kwargs['prefix']+str.zfill(str(x),kwargs['nzeros'])+kwargs['suffix']+"."+kwargs['ext'] for x in shortlist]
        
        for (i,fname) in enumerate(files2load):
            ### File info:
            fpath = os.path.join(kwargs['path'],fname)
            
            if kwargs["debug"] == True:
                print("AD_tiff full path: ",fpath)

            ### loading AD tiff file with header
            AD = load_ADtiff((fpath),**kwargs)
            d.update({shortlist[i]:AD})
    
        return d