import matplotlib.pyplot as plt

from iexplot.iexplot_utilities import _shortlist 
from iexplot.pynData.plottingUtils import *
from iexplot.pynData.pynData import nstack
from iexplot.pynData.pynData_ARPES import *

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

        elif self.dtype == "mdaEA" or "mdaAD":
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
            if EAnum == inf:
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

        EAnum = sweep number (default = 1)
                = inf => will sum all spectra
        if
            dtype="EA"  => y=data.EA[scanNum]
            dtype="mdaEA" or "mdaAD"  => y=data.mda[scanNum]EA[EAnum]
        BE = False uses KE scale
        BE = True use BE=hv-KE-wk
        if wk=None uses metadata
        
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

    def plotEA(self,scanNum,EAnum=inf,BE=True,transpose=False,**kwargs):
        """
        simple plotting for EDC
        if
            dtype="EA"  => y=data.EA[scanNum]
            dtype="mdaEA" or "mdaAD"  => y=data.mda[scanNum]EA[EAnum]
        
        ** kwargs: are matplotlib kwargs like pcolormesh, cmap, vmin, vmax
        
        """  
        kwargs.setdefault('shading','auto')

        img,xscale,yscale,xunit,yunit = self.EAspectra(scanNum, EAnum, BE)

        if transpose == True:
            plot_2D(img.T,[xscale,yscale],[xunit,yunit])
            if BE == True:
                plt.ylim(max(xscale),min(xscale))
        else:
            plot_2D(img,[yscale,xscale],[yunit,xunit])
            if BE == True:
                plt.xlim(max(xscale),min(xscale))
        
    def stack_mdaEA(self,*args,**kwargs):
        """
        creates a FermiMap volume
        *args = scanNum if volume is a single Fermi map scan
                = scanNum, start, stop, countby for series of scans

        **kwargs:      
            EAnum = (start,stop,countby) => to plot a subset of scans
            EDConly = False (default) to stack the full image
                    = True to stack just the 1D EDCs
        """
        kwargs.setdefault('EDConly',False)

        scanNumlist=_shortlist(*args,llist=list(self.mda.keys()),**kwargs)
        nData_list = []
        stack_scale = []
        for scanNum in scanNumlist:
            stack_scale.append(self.mda[scanNum].posy[1])
            stack_unit =self.mda[scanNum].posy[1]
            for EAnum in self.mda[scanNum].EA.keys():
                if kwargs['EDConly']:
                    nData_list.append(self.mda[scanNum].EA[EAnum].EDC)
                else:
                    nData_list.append(self.mda[scanNum].EA[EAnum])
                
        nstack(nData_list,stack_scale,stack_unit=stack_unit, **kwargs)
