import numpy as np
from time import sleep
import pyimagetool as it

from iexplot.pynData.pynData_ARPES import kmapping_stack
from iexplot.utilities import _shortlist
from iexplot.fitting import find_EF_offset
from iexplot.iexplot_EA import PlotEA, _stack_mdaEA_from_list
from iexplot.imagetool_wrapper import IEX_IT, pynData_to_ra


class IEX_nData_IT(IEX_IT):
    """
    Subclass of IEX_nData class
    """
    def __init__(self):
        '''
        imagetool stuff for IEX nData
        '''

        pass


    def it_mda(self, scanNum, detNum):
        """
        plot 2D mda data in imagetool

        scanNum = scan number to plot
        type = int

        detNum = detector number to plot
        type = int

        """
        #info 

        dataArray = self.mda[scanNum].det[detNum].data
        x = self.mda[scanNum].posx[0].data[0]
        y = self.mda[scanNum].posy[0].data
        self.plotmda(scanNum, detNum)
        image = it.RegularDataArray(dataArray.T, delta = [y[1]-y[0],x[1]-x[0]], coord_min = [y[0],x[0]]) 
        tool = it.ImageTool(image)
        sleep(10)

        name = self._append_instance(tool)
        tool.setWindowTitle(name)
        tool.show()

    
    def it_pynData(self, d):
        ra = pynData_to_ra(d)
        tool = it.imagetool(ra)
        name = self._append_instance(tool)
        tool.setWindowTitle(name)
        tool.show()
        return(tool)


    def it_mdaEA(self, *scanNums, **kwargs):
        """
        stack and plot 3D mda EA data in imagetool
        
        self = IEXdata object
        
        *scanNums = scanNum if volume is a single Fermi map scan
            = start, stop, countby for series of mda scans    
            
        
        kwargs:
            E_unit = KE or BE
            ang_offset = angle offset
            y_scale = k or angle
            EAnum = (start,stop,countby) => to plot a subset of EA scans
            EDConly = False (default) to stack the full image
                    = True to stack just the 1D EDCs
            find_E_offset   = False (default), does not offset data
                            = True, will apply offset
            E_offset = energy offset, can be array or single float (default = 0.0)
            fit_type = fitting function used to calculate offset, 'step' or 'Voigt'
            fit_xrange = subrange to apply fitting function over
        
        
        """
        kwargs.setdefault('E_unit','KE')
        kwargs.setdefault('find_E_offset',False)
        kwargs.setdefault('E_offset',0.0)
        kwargs.setdefault('fit_type','step')
        kwargs.setdefault('ang_offset',0.0)
        kwargs.setdefault('kmap',False)
        kwargs.setdefault('EAnum',(1,np.inf))
        #kwargs.setdefault('EDConly', False)
        kwargs.setdefault('fit_xrange', [-np.inf,np.inf])
        kwargs.setdefault('debug', False)

        scanNumlist=_shortlist(*scanNums,llist=list(self.mda.keys()),**kwargs)


        EA_list, stack_scale = PlotEA.make_EA_list(self, scanNumlist, **kwargs)
        

        if kwargs['debug']:
            print('EA list:',EA_list)

        if kwargs['find_E_offset']:
            E_offset = find_EF_offset(EA_list, E_unit = kwargs['E_unit'], fit_type = kwargs['fit_type'], xrange = kwargs['fit_xrange'])
        else: 
            E_offset = kwargs['E_offset']

            
        hv_list = []
        for EA in EA_list:
            hv_list.append(EA.hv)
        hv_array = np.array(hv_list)
        
        #adjusting angle scaling
        for EA in EA_list:
            EA.scaleAngle(kwargs['ang_offset'])
        
        if len(EA_list) == 0:
            d = EA_list[0] ### this is nonsense
        else:
            if kwargs['kmap']:
                d = kmapping_stack(EA_list, E_unit = kwargs['E_unit'], KE_offset = -E_offset, debug = kwargs['debug'])
            else:
                d = _stack_mdaEA_from_list(EA_list,stack_scale, E_unit = kwargs['E_unit'], E_offset = -E_offset, debug = kwargs['debug'])
        
        if kwargs['E_unit'] == 'BE': #probably a way to do this more intelligently
            d.unit['x'] = 'Binding Energy (ev)'
        

        tool = self.it_pynData(d)
        return d, tool
    
    