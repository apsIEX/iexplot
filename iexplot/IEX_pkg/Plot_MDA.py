
import re

from IPython.display import display_markdown

import matplotlib.pyplot as plt

from iexplot.utilities import make_num_list
from iexplot.plotting import *
from iexplot.XAS_utilities import plot_Norm2Edge,Norm2Edge
from iexplot.pynData.pynData import nstack


class Plot_MDA:
    """
    adds mda plotting functions to IEXnData class
    """    
    def __init__(self):
        pass

    def mda_positioners_list(self,scanNum):
        """
        prints the positioners associated with the mda file
        """
        self.mda[scanNum].posAll()

    def mda_positioner(self,scanNum,**kwargs):
        """
        returns the array for a positioner

        **kwargs
            posNum=1 (default)
            ax='x' (default)

        usage for 1D data:
        x = mdaPos(305)
        y = mdaDet(305,16)
        
        plt.plot(x,y)
        """
        kwargs.setdefault('posNum',0)
        kwargs.setdefault('ax','x')

        posNum = kwargs['posNum']
        ax = kwargs['ax']

        try:
            mda_pos = getattr(self.mda[scanNum],'pos'+ax)
            return mda_pos[posNum].data
        except:
            print('No mda positioner: pox'+ax+'['+str(posNum)+']')
            print('\n')
            self.mda_positioners_list()

    def mda_positioner_label(self,scanNum,**kwargs):
        """
        returns the array for a positioner

        **kwargs
            posNum=1 (default)
            ax='x' (default)   

        usage for 1D data:
        x = mdaPos(305)
        xlabel = mdaPos_label(305)
        
        y = mdaDet(305,16)
        ylabel = mdaDet_label(305,16)
        
        plt.plot(x,y)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        """
        kwargs.setdefault('posNum',0)
        kwargs.setdefault('ax','x')

        posNum = kwargs['posNum']
        ax = kwargs['ax']
        
        try:
            mda_pos = getattr(self.mda[scanNum],'pos'+ax)
            return mda_pos[posNum].pv[1] if len(mda_pos[posNum].pv[1])>0 else mda_pos[posNum].pv[0]

        except:
            print('No mda positioner: pox'+ax+'['+str(posNum)+']')
            print('\n')
            self.mda_positioners_list()
    
    def mda_detectors_list(self,scanNum):
        """
        list all the detectors for a given mda scan
        """
        self.mda[scanNum].detAll()
        
    
    def mda_detector(self,scanNum, detNum):
        """
        returns the array for a positioner and positioner pv/desc
        usage for 1D data:
        x = mdaPos(305)
        y = mdaDet(305,16)
        
        """
        return self.mda[scanNum].det[detNum].data

    def mda_detector_label(self,scanNum, detNum):
        """
        returns the array for a positioner
                        
        usage for 1D data:
        x = mdaPos(305)
        xlabel = mdaPos_label(305)
        
        y = mdaDet(305,16)
        ylabel = mdaDet_label(305,16)
        
        plt.plot(x,y)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        """

        return self.mda[scanNum].det[detNum].pv[1] if len(self.mda[scanNum].det[detNum].pv[1])>1 else self.mda[scanNum].det[detNum].pv[0]

        
    def plot_mda(self,scanNum,detNum,**kwargs):
        """
        simple plot for an mda scans either 1D or a row/column of a 2D data set
            
        **kwargs
            data kwargs:
                1D: detector vs x-positioner (num = 1; default)
                    posx_Num => to plot verses a different x-positioner number
                    y_detNum => to plot verses a detector

                2D: detector vs positioner1 for both x and y (default)
                    posx_Num => to plot verses a different x-positioner number
                    posy_Num => to plot verses a different y-positioner number
                    x_detNum => x-scale is a detector
                    y_detNum => y-scale is a detector


            plotting kwargs:
                Norm2One: True/False to normalize spectra between zero and one (default => False)
                offset: y += offset 
                scale: y *= scale
                offset_x: x += offset_x 
                scale_x: x *= scale_x

                Norm2Edge: True/False to normalize XAS (1D only)
                
            for 2D data: plots image by default
                row = index for plotting a single row from a 2D data set
                column = index for plotting a single row from a 2D data set
                
            and standard plt.plot **kwargs
            e.g. label=str(scanNum), marker="o"
        """
        kwargs.setdefault("offset",0)
        kwargs.setdefault("scale",1)
        kwargs.setdefault("offset_x",0)
        kwargs.setdefault("scale_x",1)
        kwargs.setdefault('Norm2One',False)
        
        d = self.mda_detector(scanNum, detNum)
        
        #2D data
        if len(d.shape)==2:
            #image
            if "row" not in kwargs and "column" not in kwargs:
                if kwargs['Norm2One']:
                    print('Norm2One not currently implemented in 2D data, adjust vmin,vmax')
                    del kwargs['Norm2One']
                #remove any keys not associated with pcolormesh    
                for key in ['offset','scale','offset_x','scale_x','Norm2One']:
                    kwargs.pop(key)
                self.plot_mda_2D(scanNum, detNum, **kwargs)        
        #1D data
        else:
            self.plot_mda_1D(scanNum, detNum, **kwargs)
        

    def plot_mda_1D(self,scanNum, detNum, **kwargs):
        """
        plots 1D mda data
        detNum = detector number for the image data
        
        **kwargs: 
            posx_Num => to plot verses a different x-positioner number
            x_detNum => x-scale is a detector

            row => for the nth row of a 2D array
            column => or the nth column of a 2D array

            Norm2Edge: True/False to normalize XAS

        """ 
        #x-axis
        if 'x_detNum' in kwargs:
            x = self.mda_detector(scanNum,detNum=kwargs['x_detNum'])
            xunit = self.mda_detector_label(scanNum,detNum=kwargs['x_detNum'])
            del kwargs['x_detNum']
        elif 'posx_Num' in kwargs:
            x = self.mda_positioner(scanNum,posNum=kwargs['posx_Num'],ax='x')
            xunit = self.mda_positioner_label(scanNum,posNum=kwargs['posx_Num'],ax='x')
            del kwargs['posx_Num']
        else:
            x = self.mda_positioner(scanNum,posNum=0,ax='x')
            xunit = self.mda_positioner_label(scanNum,posNum=0,ax='x')

        #data
        y = self.mda_detector(scanNum,detNum)

        if len(y.shape)>1:
            if 'row' in kwargs or 'column' in kwargs:
                x,y,kwargs = reduce2d(x,y, **kwargs)

        if 'Norm2Edge'  in kwargs:
            if kwargs['Norm2Edge']:
                plot_Norm2Edge(x,y,**kwargs)
        else:
            plot_1D(x,y,**kwargs)
                               
        plt.xlabel(xunit)


    def plot_mda_2D(self, scanNum, detNum, **kwargs):
        """
        plots 2D mda data
        detNum = detector number for the image data
        
        **kwargs: 
            posx_Num => to plot verses a different x-positioner number
            posy_Num => to plot verses a different y-positioner number
            x_detNum => x-scale is a detector
            y_detNum => y-scale is a detector     
        """
        img = self.mda_detector(scanNum, detNum)
        
        #x-scaling
        if 'x_detNum' in kwargs:
            xscale = self.mda_detector(scanNum,detNum=kwargs['x_detNum'],ax='x')
            xunit = self.mda_detector_label(scanNum,detNum=kwargs['x_detNum'],ax='x')
            del kwargs['x_detNum']
        elif 'posx_Num' in kwargs:
            xscale = self.mda_positioner(scanNum,posNum=kwargs['posx_Num'],ax='x')
            xunit = self.mda_positioner_label(scanNum,posNum=kwargs['posx_Num'],ax='x')
            del kwargs['posx_Num']
        else:
            xscale = self.mda_positioner(scanNum,posNum=0,ax='x')
            xunit = self.mda_positioner_label(scanNum,posNum=0,ax='x')
        
        #y-scaling
        if 'y_detNum' in kwargs:
            yscale = self.mda_detector(scanNum,detNum=kwargs['y_detNum'],ax='y')
            yunit = self.mda_detector_label(scanNum,detNum=kwargs['y_detNum'],ax='y')
            del kwargs['y_detNum']
        elif 'posy_Num' in kwargs:
            yscale = self.mda_positioner(scanNum,posNum=kwargs['posy_Num'],ax='y')
            yunit = self.mda_positioner_label(scanNum,posNum=kwargs['posy_Num'],ax='y')
            del kwargs['posy_Num']
        else:
            yscale = self.mda_positioner(scanNum,posNum=0,ax='y')
            yunit = self.mda_positioner_label(scanNum,posNum=0,ax='y')
        
        scales = [yscale,xscale]
        units = [yunit,xunit]    
        plot_2D(img,scales,units,**kwargs)
        

    def plot_sample_map(self,scanNum,**kwargs):
        """
        plots the relavent detectors for a sample map with an aspect ration of 1
        kwargs:
            det_list => list of detectors to plot 
            title_list => list of titles for each detector
            figsize => figure size; use to make figure bigger so scales don't overlap (H,V)
                        
            defaults:
            if prefix = 'ARPES_'
                    det_list = [16,17] 
                    title_list = ['TEY','EA'] 

            if prefix = 'Kappa_'
                    det_list = [31,34] 
                    title_list = ['TEY','D4'] 
        """
        if self.prefix == 'ARPES_':
            kwargs.setdefault('det_list',[16,17])
            kwargs.setdefault('title_list',['TEY','EA'])
            
        
        if self.prefix == 'Kappa_':
            kwargs.setdefault('det_list',[31,34])
            kwargs.setdefault('title_list',['TEY','D4'])
        
        det_list = kwargs['det_list']
        kwargs.pop('det_list')

        title_list = kwargs['title_list']
        kwargs.pop('title_list')

        kwargs.setdefault('aspect_ratio',1)
        aspect_ratio = kwargs['aspect_ratio']
        kwargs.pop('aspect_ratio')

        n=len('det_list')
        if 'figsize' in kwargs:
            fig = plt.figure(figsize=kwargs['figsize'])
            kwargs.pop('figsize')
        else:
            fig = plt.figure()

        for i, det_num in enumerate(det_list):
            ax = fig.add_subplot(1,n,i+1)
            ax.set_title(title_list[i])
            ax.set_aspect(aspect_ratio)
            self.plot_mda(scanNum,det_list[i],**kwargs)
            
        
    def mda_stack_1D(self,*scans,detNum=1,pv=None,**kwargs):
        """
        stack a series of 1D mda scans
        """
        stack_scale=[]
        nData_list=[]
        for scanNum in make_num_list(*scans):
            try:
                stack_scale.append(self.mda_extra_pvs(scanNum,pv,verbose=False))
                unit = pv
            except:
                stack_scale.append(scanNum)  
                unit = 'scanNum'
            nData_list.append(self.mda[scanNum].det[detNum])
        
        d = nstack(nData_list, stack_scale, **kwargs)
        d.updateScale('y',stack_scale)
        d.updateUnit('y',pv)
        return d
    
    def mda_extra_pvs_all(self,scanNum):
        """
        returns a dictionary with all the adder info from the mda scan
    
        """
        d = self.mda[scanNum].header.all
        return d
    
    def mda_extra_pvs(self,scanNum,search,**kwargs):
        """
        looks through the mda header to return the value of an extra_pv
        search is a string
        ** kwargs
            verbose
            desc (= True to search pv description)
            
        """
        kwargs.setdefault('verbose', False)
        kwargs.setdefault('desc',False)

        headerList = self.mda[scanNum].header.all

        d = {key:value for key, value in headerList.items() if key not in headerList['ourKeys']}

        if search in headerList['ourKeys']:
            return d[key]

        if kwargs['desc']:
            d = {key:value for key, value in d.items() if search.lower() == value[0].lower()}
        
        else: 
            d = {key:value[:3] for key, value in headerList.items() if search.lower() in key.lower()}

        vals = []
        
        if kwargs['verbose']:
            print('pv','desc','val','unit')
            
        for key in d.keys():

            pv = key
            desc = d[key][0]
            val = d[key][2]
            if type(val)==list:
                val = val[0]
            vals.append(val)
            unit = d[key][1]
        
            if kwargs['verbose']:
                print(pv,desc,val,unit)
        if len(vals) == 1:
            return vals[0]
        elif len(vals) >1:
            return vals
        else: 
            pass

    def mda_hv(self,scanNum):
        """
        returns the photon energy (mono readback) in eV
        """
        search = 'ENERGY_MON'
        return self.mda_extra_pvs(scanNum,search,verbose=False)
    
    def mda_grating(self,scanNum):
        """
        returns the photon energy (mono readback) in eV
        """
        search = 'GRT_DENSITY'

        grt_den = self.mda_extra_pvs(scanNum,search,verbose=False)
        if round(grt_den,0) == 1200:
            return 'MEG'
        elif round(grt_den,0) == 2400:
            return 'HEG'
        else:
            return grt_den

    def mda_polarization(self,scanNum):
        """
        returns the ID polarization
        """
        search = 'ActualMode'
        return self.mda_extra_pvs(scanNum,search,verbose=False)

    def mda_id_sp(self,scanNum):
        """
        returns the ID setpoint in keV
        """
        search = 'EnergySet'
        return self.mda_extra_pvs(scanNum,search,verbose=False)
    
    def mda_BL(self,scanNum):
        """
        returns the extra pvs related to beamline optics
        """
        headerList = self.mda[scanNum].header.all
        d={}
        #APS-OG: ID29 
        #APS-U: S29ID
        d['ID'] = {key:value[:3] for key, value in headerList.items() if 'ID' in key}
        d['mono'] = {key:value[:3] for key, value in headerList.items() if 'mono' in key}
        d['energy'] = {key:value[:3] for key, value in headerList.items() if 'energy' in key.lower()}
        d['BL_motors'] = {key:value[:3] for key, value in headerList.items() if '29idb:m' in key}
        d['slits'] = {key:value[:3] for key, value in headerList.items() if 'slit' in key.lower()} 
        return d

    def mda_slit(self,scanNum):
        """
        """
        headerList = self.mda[scanNum].header.all
        d={}
        slit_pvs={'c': ['29idb:m24.RBV'],
                'd': ['29idb:m26.RBV', '29idb:m27.RBV']
                }
        for branch,pvs in slit_pvs.items():
            vals = []
            for pv in pvs:
                vals.append(self.mda_extra_pvs(scanNum,pv,verbose=False))
            if len(vals)==2:
                vals = abs(vals[1]-vals[0])
            d[branch] = vals
    
        if 'arpes' in self.prefix.lower():
            return d['c']
        elif 'kappa' in self.prefix.lower():
            return d['d']
        elif 'octupole' in self.prefix.lower():
            return d['d']
        else:
            return d
    
    def mda_sample(self,scanNum):
        """
        returns the extra pvs related to sample position and temperature of Kappa and ARPES endstations
        """
        headerList = self.mda[scanNum].header.all
        d={}
        # Kappa
        sampleInfo={**{key:value[:3] for key, value in headerList.items() if '29idKappa:m' in key},
                    **{key:value[:3] for key, value in headerList.items() if '29idKappa:Euler' in key},
                    **{key:value[:3] for key, value in headerList.items() if 'LS331' in key}}
        d.update(sampleInfo)

        # ARPES
        sampleInfo={**{key:value[:3] for key, value in headerList.items() if '29idc:m' in key},
                        **{key:value[:3] for key, value in headerList.items() if '29idARPES:LS335' in key}
                    }
        d.update(sampleInfo)
        return d
    
    def mda_x(self,scanNum):
        """
        returns the sample x position
        """
        search = 'x'
        return self.mda_extra_pvs(scanNum,search,desc=True, verbose=False)
    
    def mda_y(self,scanNum):
        """
        returns the sample y position
        """
        search = 'y'
        return self.mda_extra_pvs(scanNum,search,desc=True, verbose=False)
    
    def mda_z(self,scanNum):
        """
        returns the sample z position
        """
        search = 'z'
        return self.mda_extra_pvs(scanNum,search,desc=True, verbose=False)
    
    def mda_th(self,scanNum):
        """
        returns the sample th position
        """
        search = 'th'
        return self.mda_extra_pvs(scanNum,search,desc=True, verbose=False)
    
    def mda_chi(self,scanNum):
        """
        returns the sample chi position
        """
        search = 'chi'
        return self.mda_extra_pvs(scanNum,search,desc=True, verbose=False)
    
    def mda_phi(self,scanNum):
        """
        returns the sample phi position
        """
        search = 'phi'
        return self.mda_extra_pvs(scanNum,search,desc=True, verbose=False)
    
    def mda_tth(self,scanNum):
        """
        returns the sample tth position
        """
        search = 'tth'
        return self.mda_extra_pvs(scanNum,search,desc=True, verbose=False)
        
    def mda_tthdet(self,scanNum):
        """
        returns the extra pvs related to tth (Kappa only)
        """
        headerList = self.mda[scanNum].header.all
        detkeys=['29idMZ0:scaler1.TP','29idKappa:m9.RBV','29idKappa:userCalcOut10.OVAL','29iddMPA:C0O','29idKappa:userStringSeq6.STR1','29idd:Unidig1Bo0']
        detInfo={**{key:value[:3] for key, value in headerList.items() if '29idd:A' in key},
                **{key:value[:3] for key,value in headerList.items() if key in detkeys}}   
        return detInfo

    def mda_m3r(self,scanNum):
        """
        returns the extra pvs related to m3r
        """
        headerList = self.mda[scanNum].header.all
        d={}
        d.update({key:value[:3] for key, value in headerList.items() if '29id_m3r' in key})
        #cam6 APS-OG
        d.update({key:value[:3] for key, value in headerList.items() if 'ps6' in key.lower()})
        #cam6 APS-U
        d.update({key:value[:3] for key, value in headerList.items() if 'vmb6' in key.lower()})
        return d

    def mda_UBinfo(self,scanNum,**kwargs):
        """
        
        """
        headerList = self.mda[scanNum].header.all
        d={}
        comment=""
        for i, key in enumerate(list(headerList.keys())):
                if re.search('saveData_comment1', key) : 
                    comment=str(headerList[key][2])
                elif re.search('saveData_comment2', key) : 
                    if headerList[key][2] != '':
                        comment+=' - '+str(headerList[key][2])
        d['comment']=comment     
        UBinfo={**{key:value[:3] for key, value in headerList.items() if '29idKappa:UB' in key}}
        print(UBinfo)
        for key in UBinfo.keys():
            d[key]=UBinfo[key]
        return d

    def mda_summary(self,*scanNums,**kwargs):
        """
        makes a markdown table of scan parameters from pv_list
        *scanNum = scanNumbers
        
        **kwargs
            pv_list = ['positioner','polarization','hv']
            round: for floats round to that many decimals (default: 3)
            comment: must be a function of scanNum if not None

        
        """
        kwargs.setdefault('separator', '|')
        kwargs.setdefault('pv_list',['positioner','polarization','hv'])
        kwargs.setdefault('debug',False)
        kwargs.setdefault('round',3)
        kwargs.setdefault('comment',None)
        
        scanNum_list = make_num_list(*scanNums)
        if kwargs['debug']:
            print('scanNum_list:',scanNum_list)

        result = ''
        header = kwargs['separator']
        line = kwargs['separator']

        for i,scanNum in enumerate(scanNum_list):  
            #get scan info
            d = self.mda_scan_summary(scanNum,**kwargs)
            if kwargs['comment'] != None:
                d['comment']=kwargs['comment'](scanNum)
            entry = kwargs['separator']
            for key in d.keys():
                if i == 0:
                    header+=(key+kwargs['separator'])
                    line+=(':-:'+kwargs['separator'])
                entry+=(str(d[key])+kwargs['separator'])
            if i == 0:
                result+=header+'\n'
                result+=line+'\n'
                
            result+=entry+'\n'
        if kwargs['debug']:
            print(result)
        display_markdown(result,raw=True)


    def mda_scan_summary(self,scanNum,**kwargs):
        """
        returns a dictionary entry of extra pvs found in pv_list
        **kwargs
            pv_list (default: ['positioner','polarization','hv'])
            verbose (default: True)
            round if value is float then rounds to that many decimals(default:3)
        """
        kwargs.setdefault('pv_list',['positioner','polarization','hv'])
        kwargs.setdefault('verbose',True)
        kwargs.setdefault('round',3)
        kwargs.setdefault('debug',False)

        d={}
        d['scanNum']=scanNum

        for key in kwargs['pv_list']:
            if 'scanNum' in kwargs['pv_list']:
                pass
            else:
                try:
                    attr = 'mda_'+key.lower()
                    if 'positioner' in key.lower():
                            val = self.mda_positioner_label(scanNum)
                    
                    elif hasattr(self,attr):
                        val = getattr(self,attr)(scanNum)
                    else:
                        val = self.mda_extra_pvs(scanNum,key,verbose=False)
                    try:
                        val = round(val,kwargs['round'])
                    except:
                        pass
                        
                    d[key]=val  
                except:
                    if kwargs['verbose']:
                        print('pv string '+key+' is not found')
            if kwargs['debug']:
                print(d)
        return d

    
    
    def it_mda(self,scanNum,detNum):
        """
        plot 2D mda data in imagetool

        scanNum = scan number to plot
        type = int

        detNum = detector number to plot
        type = int

        """
        #info 
        #ra = pynData_to_ra(self.mda[scanNum].det[detNum])        
        #tools.new(ra)
        pass