import re
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
    def __init__(self):
        """
        """
        pass

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
        try:
            kwargs.setdefault('prefix',self.prefix )
            kwargs.setdefault('nzeros',self.nzeros )
            kwargs.setdefault('suffix',self.suffix )
            kwargs.setdefault('ext',self.ext )
            kwargs.setdefault('path',self.path )
        except:
            #print('Need to specify kwargs:  prefix,nzeros,suffix, ext, path')
            pass
        
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
            self.beamline_header(mda, headerList,**kwargs)
            
            ### updating data dictionary
            mda_dict.update({short_list[i]:mda})   
        return mda_dict

    def beamline_header(self,mda,headerList,**kwargs):
        """
        General IEX beamline information
        """
        kwargs.setdefault('debug',False)

        if kwargs['debug']:
            print('prefix:',kwargs['prefix'])
            print('BL info')

        if 'filename' in headerList:
            setattr(self,'prefix',headerList['filename'].split('/')[-1].split('_')[0]+"_")
   
        #APS_OG
        setattr(mda, 'ID', {key:value[:3] for key, value in headerList.items() if 'ID29' in key}) 
        #APS_U
        setattr(mda, 'ID', {key:value[:3] for key, value in headerList.items() if 'S29ID:' in key}) 
        setattr(mda,'mono',{key:value[:3] for key, value in headerList.items() if 'mono' in key})
        setattr(mda,'energy',{key:value[:3] for key, value in headerList.items() if 'energy' in key.lower()})
        setattr(mda,'BL_motors',{key:value[:3] for key, value in headerList.items() if '29idb:m' in key})
        setattr(mda,'slits',{key:value[:3] for key, value in headerList.items() if 'slit' in key.lower()} )
                          
        ##kappa
        if self.prefix.lower() == "Kappa_".lower():
            if kwargs['debug']:
                print("kappa")
            self.Kappa_header(self,headerList)
            
        #ARPES
        if self.prefix.lower() == "ARPES".lower():
            if kwargs['debug']:
                print("ARPES")
            
            self.ARPES_header(self,headerList)

    def ARPES_header(self,mda,headerList):
        """
        ARPES specific header info
        """    
        sampleInfo={**{key:value[:3] for key, value in headerList.items() if '29idc:m' in key},
                    **{key:value[:3] for key, value in headerList.items() if '29idARPES:LS335' in key}
                }
        setattr(mda, 'sample',sampleInfo)

    def Kappa_header(self,mda,headerList):
        """
        Kappa specific header info
        """
        sampleInfo={**{key:value[:3] for key, value in headerList.items() if '29idKappa:m' in key},
                    **{key:value[:3] for key, value in headerList.items() if '29idKappa:Euler' in key},
                    **{key:value[:3] for key, value in headerList.items() if 'LS331' in key}}
        setattr(mda, 'sample',sampleInfo)
        setattr(mda, 'mirror',{key:value[:3] for key, value in headerList.items() if '29id_m3r' in key})
        setattr(mda, 'centroid',{key:value[:3] for key, value in headerList.items() if 'ps6' in key.lower()})
        
        detkeys=['29idMZ0:scaler1.TP','29idKappa:m9.RBV','29idKappa:userCalcOut10.OVAL','29iddMPA:C0O','29idKappa:userStringSeq6.STR1','29idd:Unidig1Bo0']
        detInfo={**{key:value[:3] for key, value in headerList.items() if '29idd:A' in key},
                **{key:value[:3] for key,value in headerList.items() if key in detkeys}}
        setattr(self, 'det',detInfo)
        
        comment=""
        for i, key in enumerate(list(headerList.keys())):
                if re.search('saveData_comment1', key) : 
                    comment=str(headerList[key][2])
                elif re.search('saveData_comment2', key) : 
                    if headerList[key][2] != '':
                        comment+=' - '+str(headerList[key][2])
        setattr(mda, 'comment',comment)
        
        UBinfo={**{key:value[:3] for key, value in headerList.items() if '29idKappa:UB' in key}}
        setattr(mda, 'UB',UBinfo)
