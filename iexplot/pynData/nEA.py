
#nEA.py 
#loads h5 and netCDF EA data using to the form used by (pynData.py)

__version__= 1.0      #JLM 4/27/2021

import re
import numpy as np
import h5py
try:
    import netCDF4 as nc
except:
    msg = "netCDF4 is not installed try installing by hand \nhttps://github.com/Unidata/netcdf4-python\r"
    print(msg)

from iexplot.pynData.pynData import nData
from iexplot.pynData.pynData_ARPES import nARPES

class nEA_IEXheader:
    """
    Get IEX specific PVs and writes them to the nEA header
    """  
    def __init__(self,metadata):
        self.all=metadata

        pvInfo=self._IEXpvs(metadata)

        beamline = ["hv","grating","ID","polarization","grating","exitSlit","ringCurrent"]
        self.beamline={key: pvInfo[key] for key in beamline}

        sample = ["x","y","z","theta","chi","phi","TA","TB","TEY","TEY2"]
        self.sample={key: pvInfo[key] for key in sample}

        HVscanInfo=['ENERGY:bins','NumBins','SweepBinSize','SweepSteps','ROI:height','ROI:width','sweepStartEnergy',"sweepStepEnergy","sweepStopEnergy"]
        self.HVscanInfo={key: pvInfo[key] for key in HVscanInfo}

        self.EAsettings = None
        

    def _IEXpvs(self,metadata):
        """
        returns dictionary with from extra pvs, used for the ARPES header
        """
        PVs={
        "SESslit":"m8_SESslit",
        "hv":"ActualPhotonEnergy",
        "TA":"T_A",
        "TB":"T_B",
        "TEY":"TEY",
        "TEY2":"TEY2",
        "I0":"",
        "hv":"ActualPhotonEnergy",
        "ID":"ID_Energy_RBV",
        "polarization":"ID_Mode_RBV",
        "grating":"Grating_Density",
        "exitSlit":"Slit3C-Size",
        "ringCurrent":"RingCurrent",
        "x":"m1_X",
        "y":"m2_Y",
        "z":"m3_Z",
        "theta":"m4_Theta",
        "chi":"m5_Chi",
        "phi":"m6_Phi", 
        'ENERGY:bins':"ENERGY:bins",
        "NumBins":"NumBins",
        "SweepBinSize":"SweepBinSize",
        "SweepSteps":"SweepSteps",
        "ROI:height":"ROI:height",
        "ROI:width":"ROI:width",
        "sweepStartEnergy":"sweepStartEnergy",
        "sweepStepEnergy":"sweepStepEnergy",
        "sweepStopEnergy":"sweepStopEnergy",
        }
        pvInfo={}
        for key in PVs:
            if PVs[key] in metadata:
                pvInfo.update({key:metadata[PVs[key]]})
        return pvInfo

class nEA(nARPES):
    """
    nARPES class for IEX beamline
    """
    def __init__(self,*fpath,**kwargs):
        """ 
        Loads and scales data for the EA
        and returns an nData object with appropriate meta data and nARPES methods an attributes
        kwargs:
            dtype: nc => for old Scienta driver pre-2021 
                   h5 => new new Scienta driver 
            nzeros: minimum number of digits in the file name (e.g. EA_0001.nc => nzeros=4 )
            source: string used for book keeping only
            centerChannel: center energy pixel in fixed mode
            firstChannel: 0 unless using an ROI
            degPerPix: angle scaling, (degrees per pixel)
            cropStart: used to crop the angle if not using using ROI to do so
            cropStop: used to crop the angle if not using using ROI to do so
            
            kwargs:
                crop = True (default); crops the data so that only the ROI is load
                     = False; full image
                rawData = False (default); uses the meta data to scale KE and degree
                        = True; camera pixels
        """ 
        kwargs.setdefault('debug',False)
        self.fpath=''
        
        if kwargs['debug']:
            print("\nEA")

        if fpath:
            if kwargs['debug']:
                print("fpath: ",fpath)
            self.fpath=fpath[0]
            EA=self._extractEA(**kwargs)
            varList=vars(EA)
            for key in varList:
                setattr(self, key, varList[key])
            
        else:
            pass        

    def _extractEA(self,**kwargs):
        """
        loads data and returns a nARPES object 
        q=1; quiet if q=0 then printing for debug purposes
        """
        kwargs.setdefault("debug",False)
        kwargs.setdefault("dtype","h5")
        kwargs.setdefault("nzeros",4)
        kwargs.setdefault("source","")
        kwargs.setdefault("centerChannel",512)
        kwargs.setdefault("firstChannel",318-35)
        kwargs.setdefault("degPerPix",0.03)
        kwargs.setdefault("cropStart",318)
        kwargs.setdefault("cropStop",780)
        kwargs.setdefault("source","")
        
        kwargs.setdefault("crop",False)
        kwargs.setdefault("rawData",False)
        if kwargs['debug']:print(self.fpath)

        #metadata will carry around all the various parameters needed
        metadata=kwargs

        fpath=self.fpath
        filename=fpath.split("/")[-1]
        filepath=fpath[:-len(filename)],
        prefix=filename.split("_")[0],
        dtype=filename.split(".")[-1]
        scanNum=int(re.sub("[^0-9]", "", filename.split(".")[0]))
        fileInfo={"filename":filename,
                  "filepath":filepath,
                  "prefix":prefix,
                  "dtype":dtype,
                  "scanNum":scanNum
                 }
        metadata.update({"fileInfo":fileInfo})
        metadata.update({'fpath':fpath})
        if kwargs['debug']:
            print("\nEA._extractEA")
            print("metadata:")
            print(metadata)
        
        #loading the data and copying spectra info into metadata
        if dtype=="h5":
            d = h5py.File(fpath, 'r')
            data = np.array(d['entry']['instrument']['detector']['data'])#(y=energy,x=angle)
            md, headerAll=self._h5PVs_EA(d,**kwargs)
            metadata.update(md)
            if kwargs['debug']==True:
                print("\ndata shape:",data.shape)
        elif dtype == "nc":
            d = nc.Dataset(fpath,mode='r')
            data = d.variables["array_data"][:][0]
            md,headerAll=self._ncPVs_EA(d)
            metadata.update(md) 
            if kwargs['debug']==True:
                print("data shape:",np.shape)
        else:
            print(dtype+" is not a valid dtype")
        
        
        #scaling and cropping
        if kwargs["crop"] == True:
            #cropping the data #(y=energy,x=angle) 
            #EA=nData(data[metadata["cropStart"]:metadata["cropStop"],:])
            EA=nARPES(data[metadata["cropStart"]:metadata["cropStop"],:])
            if kwargs['debug']==True:
                print(EA.data.shape)
        else:
            #EA=nData(data)
            EA=nARPES(data)
            
        self.spectraInfo={}


        if kwargs["rawData"] == False:
            if kwargs['debug']==True:
                print("scaling data")
            KEscale,angScale=self._EAscaling(EA,metadata,**kwargs)
            metadata["KEscale"]=EA.scale['x'].data
            metadata["angScale"]=EA.scale['y'].data
               
        spectraInfo={
                'lensMode':metadata['lensMode'],
                'acqMode':metadata['acqMode'],
                'passEnergy':metadata['passEnergy'],
                'frames':metadata['frames'],
                'sweeps':metadata['sweeps']
                }
        if metadata['acqMode']==0:
            print 
            spectraInfo.update({'sweptStart':metadata["sweptStart"],
                                'sweptStop':metadata["sweptStart"]+metadata["sweptStep"]*np.shape(data)[0],
                                'sweptStep':metadata["sweptStep"]})
        elif metadata["acqMode"] > 0: #Fixed=1, BabySweep=2
             spectraInfo.update({'kineticEnergy':metadata['kineticEnergy']})
        spectraInfo.update({"SESslit":headerAll["m8_SESslit"]})
        metadata.update({'spectraInfo':spectraInfo})
        
        #Calculating EDC/MDC:
        EDC = nData(np.nansum(EA.data[:,:], axis=0))
        ax=list(EA.scale)[0]
        EDC.updateAx('x',EA.scale[ax],EA.unit[ax])
        
        MDC = nData(np.nansum(EA.data[:,:], axis=1))
        ax=list(EA.scale)[1]
        MDC.updateAx('x',EA.scale[ax],EA.unit[ax])
        
        
        setattr(EA,"scanNum",scanNum)
        setattr(EA,"header",nEA_IEXheader(headerAll))
            
        nARPES_metadata={
            "KEscale":EA.scale['x'],
            "angScale":EA.scale['y'],
            'angOffset':0,
            "slitDir":"V",
            'thetaX': EA.header.sample["theta"],
            'thetaY': EA.header.sample["chi"],
            "hv":EA.header.beamline["hv"],
            "wk":metadata["wk"],
            "EDC":EDC,
            "MDC":MDC,
            "spectraInfo":metadata["spectraInfo"]

        }
        EA._nARPESattributes(nARPES_metadata)  
        setattr(EA.header,"EAsettings",metadata["spectraInfo"])      
        
        return EA
    
    def _ncPVs_EA(self,d,**kwargs):
        """ s
        gets the meta data associated with a given hdf5 file, d
        """
        kwargs.setdefault("debug",False)
        metadata={}
        PVs={
                "sweptStart":"LowEnergy",
                "sweptStep":"EnergyStep_Swept",
                "kineticEnergy":"CentreEnergy_RBV",
                "energyPerPixel":"EnergyStep_Fixed_RBV",
                "lensMode":"LensMode", 
                "acqMode":'AcquisitionMode',
                "passEnergy":'PassEnergy',
                "frames":'Frames',
                "sweeps":'NumExposures_RBV',
                "wk":"Energy Offset",
                }
        for key in list(PVs.keys()):
            if kwargs["debug"]:
                    print(key)
            if 'Attr_'+PVs[key] in d.variables.keys():
                if "debug" in kwargs and kwargs["debug"]:
                    print({key:d.variables['Attr_'+PVs[key]][:][0]})
                metadata.update({key:d.variables['Attr_'+PVs[key]][:][0]})
            else:
                metadata.update({key:None})
                if kwargs["debug"]:
                    print({key:d.variables['Attr_'+PVs[key]][:][0]})
            key='lensMode'; strList=['Transmission','Angular']
        
        if kwargs["debug"]:
            print("metadata:",metadata)      
            
        headerAll={key:d.variables['Attr_'+PVs[key]][:][0] for key in d.variables['Attr_'+PVs[key]]}
        return metadata,headerAll           
    
        
    def _h5PVs_EA(self,d,**kwargs):
        """ 
        gets the meta data associated with a given hdf5 file, d
        """
        kwargs.setdefault("debug",False)
        metadata={}
        #getting spectra mode
        SpectraMode=d['entry']['instrument']['NDAttributes']["SpectraMode"][0]
        if kwargs["debug"]:
            ScientaModes=["Fixed","Baby-Sweep","Sweep"]
            print("SpectraMode: ",SpectraMode, ScientaModes[SpectraMode])
        PVs={}
        #Fixed        
        if SpectraMode==0: 
            PVs={"kineticEnergy":"fixedEnergy",
                 "energyPerPixel":"pixelEnergy"
                }

        #Baby-Swept
        elif SpectraMode==1:
            PVs={"kineticEnergy":"babySweepCenter",
                 "energyPerPixel":"babySweepStepSize"
                }
        
        #Swept
        elif SpectraMode==2:
            PVs={"sweptStart":"sweepStartEnergy",
                 "sweptStep":"sweepStepEnergy",
                }
                
        AnalyzerPVs={"lensMode":"LensMode",
                     "acqMode":'SpectraMode',
                     "passEnergy":'PassEnergy',
                     "frames":'ExpFrames',
                     "sweeps":'Sweeps',
                     "wk":"WorkFunction",
                    }
        PVs.update(AnalyzerPVs)
        if kwargs["debug"]:
            print("PVs: ",PVs)
        #getting the metadata
        for key in PVs:
            if PVs[key] in list(d['entry']['instrument']['NDAttributes'].keys()):
                metadata.update({key:d['entry']['instrument']['NDAttributes'][PVs[key]][0]})
            else:
                metadata.update({key:None})
        
        #Scienta driver uses a different state notation make (swept=0,fixed=1,BS=2)
        key='acqMode';strList=[2,1,0]
        metadata.update({key: strList[metadata[key]]}) 
        
        if kwargs["debug"]:
            print("metadata:",metadata)      
            
        headerAll={key:d['entry']['instrument']['NDAttributes'][key][0] for key in d['entry']['instrument']['NDAttributes']}
        return metadata,headerAll
    
    def _EAscaling(self,EA,metadata,**kwargs):
        """
        Scales IEX EA data
        """
        kwargs.setdefault("debug",False)
        #Set energy scale ("KE") (IOC only does DetectorMode=1) Note: acqMod is not the same as SpectraMode
        if metadata["acqMode"] == 0: #Swept=0
            Estart=metadata["sweptStart"]
            Edelta=metadata["sweptStep"]
        if metadata["acqMode"] > 0: #Fixed=1, BabySweep=2
            Estart=metadata["kineticEnergy"]-(EA.data.shape[1]/2.0)*metadata["energyPerPixel"]
            Edelta=metadata["energyPerPixel"]
            
        Eunits="Kinetic Energy (eV)"
        
        if kwargs['debug']:
            print(EA.data.shape)
            print("_EAscaling Estart,Edelta,Eunits",Estart,Edelta,Eunits)
        
        Escale=[Estart+Edelta*i for i,e in enumerate(EA.data[0,:])]
        #Escale=[Estart+Edelta*i for i,e in enumerate(data[0,:])]

        
    
        #Set angle scale 
        angStart = (metadata["firstChannel"]-metadata["centerChannel"])*metadata["degPerPix"]
        angScale=[angStart+metadata["degPerPix"]*i for i,e in enumerate(EA.data[:,0])]
        #angScale=[angStart+metadata["degPerPix"]*i for i,e in enumerate(data[:,0])]
        angUnits="Degrees"
        
        if kwargs['debug']:
            print("_EAscaling angStart,angDelta,angUnits",angStart,metadata["degPerPix"],angUnits)
    
        #pynData data.shape = (y=angle,x=energy) 
        EA.updateAx('x',Escale,Eunits)
        EA.updateAx('y',angScale,angUnits)
        return  Escale,angScale

    


