#nMDA.py 
#converts mda data using (mda.py) to the form used by (pynData.py)

__version__= 1.0      #JLM 4/27/2021

import re
import ast
import numpy as np

from iexplot.mda.mda import readMDA
from iexplot.pynData.pynData import nData, nData_h5Group_w, nData_h5Group_r



if __name__ == "__main__":
    print(__file__)

def main():
    pass

class _mdaHeader:
    def __init__(self,headerList):
        """
        mda header information
        """
        self.ScanRecord={}
        self.all={}
        SR=True
        for key in headerList:
            self.all.update({key:headerList[key]})
            if re.search('saveData_scanNumber', key) : 
                SR=False
            if SR:
                 self.ScanRecord.update({key:headerList[key]})

    def val(self,desc):
        """ returns the value from the extra pvs saved in the header
        for the pv with desc for the description
        
        examples:
        desc = 'polarization'
        desc = 'x'
        """
        for pv in self.all:
            if desc == self.all[pv][0]:
                return self.all[pv][2][0]

    def pv_val(self,pv):
        """ returns the value of a pv
        """
        return self.all[pv][2][0]
                            
class nmda:
    def __init__(self,*fpath,q=1):
        """
        fpath = full path including filename and extension
        q = 1 (default); quiet if not 1 prints full file path when loading
        
        Usage: 
        mda=nmda(fpath)
        mda.header => mdaheader object
            mda.header.all
            mda.header.ScanRecord
            mda.header. => beamline/endstation defined usefull header info
        
        mda.det => dictionary of positioners
            mda.det[52] => nData object of detector 'D52'; default scaling is the first positioner
            mda.det[52].data => 'D52' detector data array 
            mda.det[52].pv =>(PV,desc,unit)
        
        mda.pos => dictionary of positioners
            mda.pos['x'] => x positioners
        
        mda.scaleSet() => sets the scaling for all detectors in mda.det
            
        
        """
        self.fpath=""
        self.header=None
        self.det=None
        self.pos=None
        self.scanNum=None

        
        #print(fpath)
        
        if fpath:
            self.fpath=fpath[0]
            self._extractAll(q)
        else:
            pass        
        
    
                
    def _extractAll(self,q):
        if(q!=1):
            fpath=self.fpath
            print(fpath)

        #Checking header info   
        try:
            data=readMDA(self.fpath)    # data = scanDim object of mda module
            self.header=_mdaHeader(data[0]) #initialize mdaHeader object

            #making the data a nData objects
            rank=data[0]['rank']
            acqDimSize=data[0]['acquired_dimensions']
            rank=len(data[0]['acquired_dimensions'])

            if acqDimSize[0] == 0: #not aborted before acquisition
                filename=self.header.ScanRecord['filename'].split('/')[-1]
                print("Scan "+filename+" aborted no data taken")
                self.pos=None
                self.det=None

            else:
                filename=self.header.ScanRecord['filename'].split('/')[-1]
                data=readMDA(self.fpath,useNumpy=True)    # data = scanDim object of mda module
                self.scanNum=int(data[0]['scan_number'])
                #creating a dictionary of numpy arrays
                arrays={}
                scales=['x','y','z','t']
                #data[0] : header
                #data[1] : outer most scan
                #data[-1] : inner most scan
                for i in range(1,rank+1):#i -> dim (x,y,z,t)
                    PositionersDim={}
                    nd=nData(np.empty(1))
                    for j in range(data[i].np): #number of positioners for each dim
                        PV=data[i].p[j].name
                        desc=data[i].p[j].desc
                        unit=data[i].p[j].unit
                        #fixing scans which were aborted early (know works for 2D need to test higher D)
                        if i<rank:
                            acq=(acqDimSize[i-1])
                            nd=nData(data[i].p[j].data[0:acq])
                        else:
                            nd=nData(data[i].p[j].data)                       
                        PositionersDim[j]=nd
                        setattr(nd, 'pv', (PV,desc,unit))

                    setattr(self, 'pos'+scales[rank-i], PositionersDim)

                for i in range(data[rank].nd): #number of detectors
                    #Detector Info
                    #detNum=data[2].d[i].fieldName
                    detNum=int(re.sub("[^0-9]", "", data[rank].d[i].fieldName.split(".")[0]))
                    PV=data[rank].d[i].name
                    desc=data[rank].d[i].desc
                    unit= data[rank].d[i].unit
                    
                    #DataArray
                    nd=nData(data[rank].d[i].data)
                    arrays[detNum]=nd
                    setattr(nd, 'pv', (PV,desc,unit)) #data[detNum].pv
                self.det=arrays

                #setting scales
                self._setScale(axis='x',key=0, PosDet="Pos")
                if rank>1:
                    self._setScale(axis='y',key=0, PosDet="Pos")
                if rank>2:
                    self._setScale(axis='z',key=0, PosDet="Pos")
                if rank>3:
                    self._setScale(axis='z',key=0, PosDet="Pos")
        except:
            e=1
            #print("Bad file: "+self.fpath)
        return self
    

        
    def _setScale(self,axis='x',key=0, PosDet="Pos"):
        """
        sets the x scale for all detectors from the 
            PosDet="Pos" positioners; key = index (starting from 0)
            PosDet="Det" detector; key = DetNum 
        """
        scales=['x','y','z','t']
        rank=self.header.ScanRecord['rank']
        
        if PosDet == "Pos":
            nd=getattr(self, "pos"+axis)
            if bool(nd) ==True: #checking in position is empty
                PV=nd[key].pv[0]
                scale=nd[key].data
            
        elif PosDet == "Det":
            if key in self.det[key]: #checking that detNum  exists
                PV=self.det[key].pv[0]
                scale=self.det[key].data

        if rank-scales.index(axis) == 1: #outer most
            scale=scale #(1D =>x; 2D =>y; 3D => z; 4D => t)
        elif rank-scales.index(axis) == 2:
            if rank==2: #2D =>x
                scale=scale[0,:]##
            elif rank==3: #3D =>y
                scale=scale[0,:,0]    
            elif rank==4: #4D =>z
                scale=scale[0,:,0,0]
        elif rank-scales.index(axis) == 3:
            if rank==3: #3D =>x
                scale=scale[0,0,:]
            elif rank==4: #4D =>y
                scale=scale[0,0,:,0]
        elif rank-scales.index(axis) == 4:#4D =>x
            scale=scale[0,0,0,:] 

        #for all detectors update the scale
        for key in self.det:
            d=self.det[key]
            d.updateAx(axis,scale,PV)



    
    def setScaleDet(self,axis='x',detNum=1): 
        """
        sets the scale for all detectors from the detNum detector 
        """
        if detNum in list(self.det.keys()):
            self._setScale(axis=axis,key=detNum, PosDet="Det")
        else:
            print("Not a valid detNum, see "+self.name+".det.keys()")
        
    def setScaleIndex(self,axis='x'): 
        """
        sets the scale for all detectors from the detNum detector 
        """
        detNum=list(self.det.keys())[0]
        size=self.det[detNum].scale[axis].size
        scale=np.linspace(0, size-1, size,dtype=int)
        for key in self.det:
            d=self.det[key]
            d.updateAx(axis,scale,"index")
            

    def detAll(self):
        """
        prints the detector Num and the pv info
        """
        for key in self.det.keys():
            print(str(key)+": "+str(self.det[key].pv))
            
    def posAll(self):
        """
        prints the positioner info
        """
        scales=['x','y','z','t']
        for axis in scales:
            if hasattr(self, "pos"+axis):
                print("pos"+axis+":")
                for key in getattr(self, "pos"+axis):
                    print("\t"+str(key)+": "+str(getattr(self, "pos"+axis)[key].pv))

    def info(self,pv=0):
        """
        self = IEXnData object
        pv: index for .mda.posx[0].pv
            0 => full pv name
            1 => description
            2 => units
        """
        rank=self.header.ScanRecord['rank']
        posx=[]
        for p in self.posx: 
            posx.append(self.posx[p].pv[pv])
        scanNum=int(self.fpath.split('/')[-1].split('.')[0].split('_')[-1])
        print("scanNum: "+str(scanNum),"  rank:"+str(rank),"  posx"+str(posx))


                    

##########################################
# generalized code for saving and loading as part of a large hd5f -JM 4/27/21
# creates/loads subgroups
##########################################
def nmda_h5Group_w(nmda,parent,name):
    """
    for an nData object => nd
    creates an h5 group with name=name within the parent group:
        with all ndata_ARPES attributes saved
    """
    gmda=parent.create_group(name)
    gmda.attrs['fpath'] = nmda.fpath
    
    #mda header
    gheader=gmda.create_group('header')
    for hkey in vars(nmda.header):
        ghkey=gheader.create_group(hkey)
        h1=getattr(nmda.header,hkey)
        if type(h1)==dict:
            for v in  h1:
                ghkey.attrs[v]=str(h1[v])
        else:
            ghkey.attrs[v]=h1

    #det
    gdet=gmda.create_group('det')
    for detNum in nmda.det:
        nd=nmda.det[detNum]
        name="det_"+str(detNum)
        g=nData_h5Group_w(nd,gdet,name)
        g.attrs['pv']=str(nd.pv)

    #posx
    scales=['x','y','z','t']
    for axis in scales:
        if hasattr(nmda,"pos"+axis):
            posn=getattr(nmda,"pos"+axis)
            gpos=gmda.create_group("pos"+axis)
            for posNum in posn:
                nd=posn[posNum]
                name="pos"+axis+"_"+str(posNum)
                g=nData_h5Group_w(nd,gpos,name)
                g.attrs['pv']=str(nd.pv)

    #EA
    gEA = gmda.create_group('EA')
    for EANum in nmda.EA:
        nd = nmda.EA[EANum]
        name="EA_"+str(EANum)
        g = nData_h5Group_w(nd,gEA,name)
        #g.attrs['pv']=str(nd.pv)

    

def nmda_h5Group_r(h):
    """
    """
    d=nmda()
    for attr in ['fpath']:
        #print(ast.literal_eval(h.attrs[attr]))
        setattr(d,attr, h.attrs[attr])
        

    #header
    for hkey in h['header']:
        hdict={}
        for key in h['header'].attrs:
            hdict.update({key,h['header'].attrs[key]})
        setattr(d,'header'+hkey,hdict)
        
    #det
    ddict={}
    detAll={}
    for det in h['det']:
        detNum=int(det.split("_")[-1])
        nd=nData_h5Group_r(h['det'][det])
        setattr(nd,"pv",ast.literal_eval(h['det'][det].attrs['pv']))
        ddict[detNum]=nd
        detAll[detNum]=nd.pv
    setattr(d,'det',ddict)
    setattr(d,'detAll',detAll)
    
    #posx
    scales=['x','y','z','t']
    
    for axis in scales:
        pdict={}
        if "pos"+axis in list(h.keys()):
            for posn in h["pos"+axis]:
                posNum=int(posn.split("_")[-1])
                nd=nData_h5Group_r(h["pos"+axis][posn])
                pdict[posNum]=nd
            setattr(d,"pos"+axis,pdict)


    #EA
    EAdict={}
    EAAll={}
    for EA in h['EA']:
        EANum=int(EA.split("_")[-1])
        nd=nData_h5Group_r(h['EA'][EA])
        EAdict[EANum]=nd
    setattr(d,'EA',EAdict)

    return d
        

