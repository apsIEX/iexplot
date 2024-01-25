import matplotlib.pyplot as plt

import numpy as np
from iexplot.utilities import _shortlist, _make_num_list 
from iexplot.plotting import plot_1D, plot_2D, plot_3D
from iexplot.pynData.pynData import nstack
from iexplot.pynData.pynData_ARPES import kmapping_energy_scale

class PlotEA:
    """
    adds EA plotting functions to IEXnData class
    """
    def __init__(self):
        pass

    def EAspectra(self,scanNum, EAnum=1, BE=False):
        """
        returns the array for an EAspectra, and x and y scaling    
        usage:
            plt.imgshow(data.EAspectra))
            
        """
        if self.dtype == "EA":
            EA=self.EA[scanNum]
            img = EA.data


        elif self.dtype == "mdaEA" or "mdaAD":
            if EAnum == np.inf:
                EA = self.mda[scanNum].EA[1]
                img = np.nansum(tuple(self.mda[scanNum].EA[EAnum].data for EAnum in self.mda[scanNum].EA.keys()),axis=0)
            else:
                EA = self.mda[scanNum].EA[EAnum]
                img = EA.data

        yscale = EA.scale['y']
        yunit = EA.unit['y']
        
        if BE:
            xscale = EA.BEscale
            xunit = 'Binding Energy (eV)'
        else:
            xscale = EA.KEscale
            xunit = 'Kinetic Energy (eV)'
            
        return img,xscale,yscale,xunit,yunit
        
        
    def EAspectraEDC(self,scanNum,EAnum=1,BE=False):
        """
        returns x,y energy scaling, EDC spectra
            
        usage:
            plt.plot(data.EAspectraEDC(151))    
        """
        if self.dtype == "EA":
            EA=self.EA[scanNum]
            y = EA.EDC.data

        elif self.dtype == "mdaEA" or "mdaAD":
            if EAnum == np.inf:
                EA = self.mda[scanNum].EA[1]
                y = np.nansum(tuple(self.mda[scanNum].EA[EAnum].EDC.data for EAnum in self.mda[scanNum].EA.keys()),axis=0)
            else:
                EA = self.mda[scanNum].EA[EAnum]
                y = EA.EDC.data

        if BE:
            x = EA.BEscale
            xlabel = 'Binding Energy (eV)'
        else:
            x = EA.KEscale
            xlabel = 'Kinetic Energy (eV)'

        return x,y,xlabel
        
    def plotEDC(self,scanNum,EAnum=1,BE=False,**kwargs):
        """
        simple plotting for EDC

        EAnum = scan/sweep number 
                = inf => will sum all spectra

        BE = False; Kinetic Energy scaling
        BE = True; Binding Energy scaling
           where BE = hv-KE-wk (wk=None uses workfunction defined in the metadata)
        
        *kwargs are the matplot lib kwargs plus the following
            Norm2One: True/False to normalize spectra between zero and one
            offset: y += offset 
            scale: y *= scale
            offset_x: x += offset_x 
            scale_x: x *= scale_x
        """
        kwargs.setdefault("Norm2One",False)
        kwargs.setdefault("offset",0)
        kwargs.setdefault("scale",1)
        kwargs.setdefault("offset_x",0)
        kwargs.setdefault("scale_x",1)
        
        x=0;y=0            
        x,y,xlabel = self.EAspectraEDC(scanNum,EAnum=EAnum,BE=BE)
                
        plot_1D(x,y,xlabel=xlabel,**kwargs)
        
        if BE:
            plt.xlim(max(x),min(x))

    def plotEA(self,scanNum,EAnum=1,BE=False,transpose=False,**kwargs):
        """
        simple plotting for EA spectra

        EAnum = scan/sweep number 
                = inf => will sum all spectra

        BE = False; Kinetic Energy scaling
        BE = True; Binding Energy scaling
           where BE = hv-KE-wk (wk=None uses workfunction defined in the metadata)
            
        transpose = False => energy is x-axis
                    = True => energy is y-axis

        ** kwargs: are matplotlib kwargs like pcolormesh, cmap, vmin, vmax
        
        """  
        kwargs.setdefault('shading','auto')

        img,xscale,yscale,xunit,yunit = self.EAspectra(scanNum, EAnum, BE)

        if transpose == True:
            plot_2D(img.T,[xscale,yscale],[xunit,yunit],**kwargs)
            if BE == True:
                plt.ylim(max(xscale),min(xscale))
        else:
            plot_2D(img,[yscale,xscale],[yunit,xunit],**kwargs)
            if BE == True:
                plt.xlim(max(xscale),min(xscale))

    def plot_stack_mdaEA(self,*args,**kwargs):
        """
        *args = scanNum if volume is a single Fermi map scan
                = scanNum, start, stop, countby for series of mda scans

        **kwargs:      
            EAnum = (start,stop,countby) => to plot a subset of scans
            EDConly = False (default) to stack the full image
                    = True to stack just the 1D EDCs
            
            **kwargs for plotting: 
                dim3 = third axis for plotting (default: 'z')
                dim2 = second axis for plotting (default: 'y') => vertical in main image
                xCen = cursor x value (default: np.nan => puts in the middle)
                xWidthPix = number of pixels to bin in x
                yCen = cursor y value (default: np.nan => puts in the middle)
                yWidthPix = number of pixels to bin in y
                zCen = cursor y value (default: np.nan => puts in the middle)
                zWidthPix = number of pixels to bin in y
                cmap = colormap ('BuPu'=default)
      

    """
        kwargs.setdefault('array_output',True)

        dataArray,scaleArray,unitArray = self.stack_mdaEA(*args,**kwargs)
        kwargs.pop('array_output')
        if 'EAnum' in kwargs:
            kwargs.pop('EAnum')
        plot_3D(np.array(dataArray),np.array(scaleArray),unitArray,**kwargs)


    def make_EA_list(self, *nums, **kwargs):
            """
            creates an EA_list from list of scans
            
            nums = list of mda scans to be plotted 
            
            **kwargs:      
                    EAnum = (start,stop,countby) => to plot a subset of EA scans
                    EDConly = False (default) to stack the full image
                            = True to stack just the 1D EDCs
                
            """
            kwargs.setdefault('EDConly',False)
            kwargs.setdefault('debug',False) 
            
            scanNumlist = _make_num_list(*nums)
            EA_list = []
            stack_scale=np.empty((0))
            
            for scanNum in scanNumlist:
                if kwargs['debug']:
                    print('scanNumlist: ',scanNumlist)
                if len(scanNumlist)==1:
                    stack_scale = np.concatenate((stack_scale,self.mda[scanNum].posy[0].data))
                    stack_unit =self.mda[scanNum].posy[0].pv[1]
                else:
                    stack_scale = np.append(stack_scale,scanNum)
                    stack_unit='scanNum'

                if kwargs['debug']:
                    print('stack_scale: ',stack_scale)
                    print('stack_unit',stack_unit)


                #creating list of all EA numbers
                ll = list(self.mda[scanNum].EA.keys())
                
                #creating shortlist of selected EAnum
                if 'EAnum' in kwargs:
                    EAlist = _shortlist(kwargs['EAnum'],llist = ll,**kwargs)  
                else:
                    EAlist = ll
                
                if kwargs['debug']:
                    print('EAlist: ',EAlist)

                #populating EA_list with EA/EDC scans
                for EAnum in EAlist:
                    if kwargs['EDConly']:
                        if kwargs['debug']:
                            #print('EDConly')
                            pass
                        EA_list.append(self.mda[scanNum].EA[EAnum].EDC)
                    else:
                        EA_list.append(self.mda[scanNum].EA[EAnum])

                #Truncating stack_scale for number of images        
                stack_scale = stack_scale[0:len(EA_list)]    
                    
            return EA_list, stack_scale
    
def stack_mdaEA(*scanNum,E_unit='BE',**kwargs):
        """
        creates a volume of stacked spectra/or EDCs based on kwargs
        Note: does not currently account for scaling (dumb stacking)

        *scanNum = scanNum if volume is a single Fermi map scan
                = mda => start, stop, countby for series of mda scans
                only debugs for a stack of mda scans...need to try a fermi map AJE

        E_unit = 'BE' or 'KE'

        **kwargs:      
            EAnum = (start,stop,countby) => to plot a subset of scans (only EAnum = 1 by default)
            EDConly = False (default) to stack the full image
                    = True to stack just the 1D EDCs
            
                EAnum = (start,stop,countby) => to plot a subset of EA scans
                            = True to stack just the 1D EDCs
                    
            E_offset = offset value for each scan based on curve fitting in E_units
            E_offset type = np array if an offset is applied, float if no offset is applied
            
        """
        EA_list,stack_scale = _make_num_list(*scanNum,**kwargs)
        _stack_mdaEA_from_list(EA_list,stack_scale, E_unit,**kwargs)

def _stack_mdaEA_from_list(EA_list,stack_scale, E_unit,**kwargs):
        """
        creates a volume of stacked spectra/or EDCs based on kwargs
        Note: does not currently account for scaling (dumb stacking)

        E_unit = 'KE' or 'BE'

        **kwargs:      
            EAnum = (start,stop,countby) => to plot a subset of scans
            EDConly = False (default) to stack the full image
                    = True to stack just the 1D EDCs
                    
            E_offset = offset value for each scan based on curve fitting
            E_offset type = np array if an offset is applied, float if no offset is applied
            
        """
        kwargs.setdefault('E_offset',0.0)
        kwargs.setdefault('debug',False)
        kwargs.setdefault('array_output',True)
        
        EA = EA_list[0]
        
        for n,EA in enumerate(EA_list):
            if n == 0: 
                KE_min = np.min(EA.KEscale)
                KE_max = np.max(EA.KEscale)
            _KE_min = np.min(EA.KEscale)
            _KE_max = np.max(EA.KEscale)
            KE_min = min(KE_min, _KE_min)
            KE_max = max(KE_max, _KE_max)
               
        
            
        #BE/KE conversion
        for i,EAnum in enumerate(EA_list):
            if type(kwargs['E_offset']) == float:
                E_offset = kwargs['E_offset']
            else:
                E_offset = kwargs['E_offset'][i]
            E_scale = kmapping_energy_scale(EAnum, E_unit, E_offset = E_offset) 
            EA_list[i].scale['x'] = E_scale

        if kwargs['debug']:
            print(type(E_offset))  
            print(E_offset)
            
        #Stacking data
        d = nstack(EA_list, stack_scale, **kwargs)
        
        return d    