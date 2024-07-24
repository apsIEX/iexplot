import numpy as np
from time import sleep
import pyimagetool as it

from iexplot.pynData.pynData_ARPES import kmapping_stack
from iexplot.utilities import _shortlist
from iexplot.fitting import find_EF_offset
from iexplot.iexplot_EA import PlotEA, _stack_mdaEA_from_list
from iexplot.imagetool_wrapper import TOOLS
from iexplot.plotting import plot_1D, plot_2D, plot_dimage
from iexplot.pynData.pynData import nData

class IEX_nData_IT():
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
        ra = it.RegularDataArray(dataArray.T, delta = [y[1]-y[0],x[1]-x[0]], coord_min = [y[0],x[0]]) 
        TOOL.new(ra)

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
        
        ☃    
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
        
        if kwargs['E_unit'] == 'BE':
            d.unit['x'] = 'Binding Energy (ev)'
        
        TOOL.new(d)
        
    
def plot_TOOL(TOOL, IT_num, plot_name,**kwargs):
        """
        extract data from an individual plot in imagetool
        
        TOOL: an instance of imagetool_wrapper.TOOLS
        IT_num = imagetool window number
                
        plot_name = 
                    'prof_h' => Intensity vs x 
                    'prof_v' => Intensity vs y 
                    'prof_d' => Intensity vs z
                    'img_main' => Intensity(x,y) 
                    'img_v' => Intensity(z,y) 
                    'img_h' => Intensity(x,z) 

        **kwargs:
            cmap = 'viridis' (default)
            image_profiles = False (default),
                            True to include line profiles in images 
        """
        kwargs.setdefault('cmap','viridis')
        kwargs.setdefault('image_profiles',False)

    
        it = TOOL.obj(IT_num)

        img, cursor_info, dim_y, dim_x = TOOL.export( IT_num, plot_name)
        

        if 'img' in plot_name:
            if kwargs['image_profiles']:
                plot_dimage(img.data.T,img.axes[::-1],(it.data.dims[dim_x],it.data.dims[dim_y]),cmap = kwargs['cmap'])
            else:
                plot_2D(img.data.T,img.axes[::-1],(it.data.dims[dim_x],it.data.dims[dim_y]),cmap = kwargs['cmap'])
        elif 'prof' in plot_name:
            plot_1D(img[0],img[1],xlabel=it.data.dims[dim_x],ylabel = dim_y, **kwargs)

def pynData_to_ra(d):
    """
    converts a pynData object into a imagetool.RegularDataArray
    """
    
    if len(d.data.shape)==2:
        dataArray = d.data.transpose(1,0)
        scaleArray = (d.scale['x'],d.scale['y'])
        unitArray = (d.unit['x'],d.unit['y'])
        delta = (scaleArray[0][1]-scaleArray[0][0],scaleArray[1][1]-scaleArray[1][0])
        coord_min = [scaleArray[0][0],scaleArray[1][1]]

    elif len(d.data.shape)==3:
        dataArray = d.data.transpose(1,0,2)
        scaleArray = (d.scale['x'],d.scale['y'],d.scale['z'])
        unitArray = (d.unit['x'],d.unit['y'],d.unit['z'])
        delta = (scaleArray[0][1]-scaleArray[0][0],scaleArray[1][1]-scaleArray[1][0],scaleArray[2][1]-scaleArray[2][0])
        coord_min = [scaleArray[0][0],scaleArray[1][1],scaleArray[2][2]]
    else:
        print("don't yet know how to deal with data of shape"+str(d.data.shape))
    
    ra = it.RegularDataArray(dataArray, delta = delta, coord_min = coord_min, dims = unitArray)

    return ra