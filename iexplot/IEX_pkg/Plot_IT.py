
import numpy as np
from time import sleep

from matplotlib.colors import ListedColormap

from iexplot.plotting import plot_1D, plot_2D, plot_dimage
from iexplot.utilities import _shortlist

from pyimagetool import RegularDataArray,tools
import pyimagetool.cmaps.CMap




def imagetool_cmaps(key=None,**kwargs):
    """
    used to generate cmaps used by pyimagetool
    key = None => prints list of cmap names/keys
    **kwargs:
        ct_reverse
        ct_gamma

    usage:
        plt.imshow(img,cmap=imagetool_cmaps('cold_warm'))
    """
    kwargs.setdefault('ct_reverse',False)
    kwargs.setdefault('ct_gamma',1)

    Cmap = pyimagetool.cmaps.CMap()
    cmap_list = Cmap.update_cmap_list()
    if key == None:
        print('Available cmaps: ',cmap_list)
        return
    if key in cmap_list:
        dat=np.arange(1,2,1)
        dat = Cmap.load_ct(key,kwargs['ct_reverse'], kwargs['ct_gamma'])
        cmp = ListedColormap(dat/255)
        return cmp
    else:
        print(key,'is not a available cmap \n Available cmaps: ',cmap_list)
        return


def pynData_to_ra(d):
    """
    converts a pynData object into a imagetool.RegularDataArray
    """
    
    if len(d.data.shape)==2:
        dataArray = d.data.transpose(1,0)
        scaleArray = (d.scale['x'],d.scale['y'])
        unitArray = (d.unit['x'],d.unit['y'])
        delta = (scaleArray[0][1]-scaleArray[0][0],scaleArray[1][1]-scaleArray[1][0])
        coord_min = [scaleArray[0][0],scaleArray[1][0]]

    elif len(d.data.shape)==3:
        dataArray = d.data.transpose(1,0,2)
        scaleArray = (d.scale['x'],d.scale['y'],d.scale['z'])
        unitArray = (d.unit['x'],d.unit['y'],d.unit['z'])
        delta = (scaleArray[0][1]-scaleArray[0][0],scaleArray[1][1]-scaleArray[1][0],scaleArray[2][1]-scaleArray[2][0])
        coord_min = [scaleArray[0][0],scaleArray[1][0],scaleArray[2][0]]
    else:
        print("don't yet know how to deal with data of shape"+str(d.data.shape))
    
    ra = RegularDataArray(dataArray, delta = delta, coord_min = coord_min, dims = unitArray)

    return ra

def tools_plot_inline(tools, IT_num, plot_name,**kwargs):
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

    
        it = tools.obj(IT_num)

        img, cursor_info, dim_y, dim_x = tools.export( IT_num, plot_name)
        

        if 'img' in plot_name:
            if kwargs['image_profiles']:
                plot_dimage(img.data.T,img.axes[::-1],(it.data.dims[dim_x],it.data.dims[dim_y]),cmap = kwargs['cmap'])
            else:
                plot_2D(img.data.T,img.axes[::-1],(it.data.dims[dim_x],it.data.dims[dim_y]),cmap = kwargs['cmap'])
        elif 'prof' in plot_name:
            plot_1D(img[0],img[1],xlabel=it.data.dims[dim_x],ylabel = dim_y, **kwargs)


class Plot_IT:
    """
    adds EA plotting methods to IEXnData class
    """
    def __init__(self):
        pass

    def mda_ra(self, scanNum, detNum):
        """
        plot 2D mda data in imagetool

        scanNum = scan number to plot
        type = int

        detNum = detector number to plot
        type = int

        """
        d = self.mda[scanNum].det[detNum]

        
        #transposing data so looks the same in imagetool as it does in the plotting 
        sleep(1)
        ra = pynData_to_ra(d)
        return ra

    def EA_ra(self,scanNum,EAnum=1):
        '''
        plot spectra data in imagetool

        scanNum = scan number to plot
        type = int

        EAnum = which sweep
        type = int
        
        '''
        d = self.mda[scanNum].EA[EAnum]

        
        #transposing data so looks the same in imagetool as it does in the plotting 
        sleep(1)
        ra = pynData_to_ra(d)
        return ra

    def mda_it(self, scanNum, detNum):
        ra = self.mda_ra(scanNum, detNum)
        tools.new(ra)
    
    def EA_it(self,scanNum,EAnum=1):
        ra = self.EA_ra(scanNum,EAnum=1)
        tools.new(ra)

def add_IT(data):
    """
    add imagetool plotting to data
    """
    if isinstance(data,Plot_IT):
        pass
    else:
        class ADD_IT(Plot_IT,data.__class__):
            pass
        data.__class__ = ADD_IT

def remove_it(data):
    """
    removes imagetool plotting to data
    """
    data.__class__= IEX_nData

def new_nd(nd):
    ra = pynData_to_ra(d)
    sleep(1)
    tools.new(nd)
tools.new_nd = new_nd