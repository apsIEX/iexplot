
import matplotlib.pyplot as plt

from iexplot.utilities import _shortlist, make_num_list
from iexplot.plotting import *



class Plot_MDA:
    """
    adds mda plotting functions to IEXnData class
    """    
    def __init__(self):
        pass

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

        if ax == 'x':
            return self.mda[scanNum].posx[posNum].data
        if ax == 'y':
            return self.mda[scanNum].posy[posNum].data
        if ax == 'z':
            return self.mda[scanNum].posz[posNum].data

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
        
        if ax == 'x':
            return self.mda[scanNum].posx[posNum].pv[1] if len(self.mda[scanNum].posx[posNum].pv[1])>0 else self.mda[scanNum].posx[posNum].pv[0]
        elif ax == 'y':
            return self.mda[scanNum].posy[posNum].pv[1] if len(self.mda[scanNum].posy[posNum].pv[1])>0 else self.mda[scanNum].posy[posNum].pv[0]
        elif ax == 'z':
            return self.mda[scanNum].posz[posNum].pv[1] if len(self.mda[scanNum].posz[posNum].pv[1])>0 else self.mda[scanNum].posz[posNum].pv[0]

    def mda_detector(self,scanNum, detNum):
        """
        returns the array for a positioner and positioner pv/desc.
                        
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
            plt.colorbar()
        

    
    def mda_header(self,scanNum):
        """
        returns a dictionary with all the adder info from the mda scan
    
        """
        d = self.mda[scanNum].header.data.mda[19].header.ScanRecord
        return d
    
    def mda_extra_pvs(self,scanNum,search,verbose=True):
        """
        looks through the mda header to return the value of an extra_pv
        search is a string

        """
        
        header = self.mda[scanNum].header.all
        d={}
        for key in list(header.keys()):
            if search.lower() in key.lower():
                if key in header['ourKeys']:
                    return header[key]
                else:
                    d[key]=header[key]

        vals = []
        
        if verbose:
            print('pv','desc','val','unit')
            
        for key in d.keys():

            pv = key
            desc = header[key][0]
            val = header[key][2]
            if type(val)==list:
                val = val[0]
            vals.append(val)
            unit = header[key][1]
        
            if verbose:
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


    def mda_summary(self,*scanNums,**kwargs):
        """
        **kwargs
            separator = '|'
            pv_list = ['positioner','polarization','hv']
        """
        kwargs.setdefault('separator', '|')
        kwargs.setdefault('pv_list',['positioner','polarization','hv'])
        scanNum_list = make_num_list(*scanNums)
    

        for i,scanNum in enumerate(scanNum_list):
            if i==0: 
                verbose = True
            else:
                verbose = False
            
            d = self.mda_scan_summary(scanNum,kwargs['pv_list'],verbose=verbose)

            header = kwargs['separator']
            line = kwargs['separator']
            entry = kwargs['separator']
            for key in d.keys():
                header+=(key+kwargs['separator'])
                line+=('---'+kwargs['separator'])
                entry+=(str(d[key])+kwargs['separator'])
            if i == 0:
                print(header)
                print(line)
            print(entry)
            

    def mda_scan_summary(self,scanNum,pv_list,verbose=False):
        """
        returns a dictionary entry with co
        """
    
        d={}
        d['scanNum']=scanNum
        for key in pv_list:
            try:
                if key.lower() == 'positioner': 
                    rank = self.mda_extra_pvs(scanNum,'rank')
                    separator = ' / '
                    val = ''
                    for i, axis in enumerate(['x','y','z','t'][0:rank]):
                        val += self.mda_positioner_label(scanNum,ax=axis)
                        if (rank > 1) and (i < rank-1):
                            val+=separator    
                    d[key]= val
                elif key.lower() == 'polarization':
                    d[key] = self.mda_polarization(scanNum)
                elif key.lower() == 'hv':
                    d[key] = self.mda_hv(scanNum)
                elif key.lower() == 'id_sp':
                    d[key] = self.mda_id_sp(scanNum)
                else:
                    d[key] = self.mda_extra_pvs(scanNum,key,verbose=False)
            except:
                if verbose:
                    print('pv string '+key+' is not found')
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