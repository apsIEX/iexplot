
import numpy as np
from matplotlib.colors import ListedColormap

from iexplot.plotting import plot_1D, plot_2D, plot_dimage
from iexplot.utilities import _shortlist

from pyimagetool import tools, RegularDataArray
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
        coord_min = [scaleArray[0][0],scaleArray[1][1]]

    elif len(d.data.shape)==3:
        dataArray = d.data.transpose(1,0,2)
        scaleArray = (d.scale['x'],d.scale['y'],d.scale['z'])
        unitArray = (d.unit['x'],d.unit['y'],d.unit['z'])
        delta = (scaleArray[0][1]-scaleArray[0][0],scaleArray[1][1]-scaleArray[1][0],scaleArray[2][1]-scaleArray[2][0])
        coord_min = [scaleArray[0][0],scaleArray[1][1],scaleArray[2][2]]
    else:
        print("don't yet know how to deal with data of shape"+str(d.data.shape))
    
    ra = RegularDataArray(dataArray, delta = delta, coord_min = coord_min, dims = unitArray)

    return ra

def tools_plot_inline(IT_num, plot_name,**kwargs):
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

    def it_mda(self, scanNum, detNum):
        """
        plot 2D mda data in imagetool

        scanNum = scan number to plot
        type = int

        detNum = detector number to plot
        type = int

        """
        d = data.mda[scanNum].det[detNum]

        
        #transposing data so looks the same in imagetool as it does in the plotting 
        ra = pynData_to_ra(d)
        tools.new(ra)

    def it_EA(self,scanNum,EAnum=1)
        '''
        plot spectra data in imagetool

        scanNum = scan number to plot
        type = int

        EAnum = which sweep
        type = int
        
        '''
        d = data.mda[scanNum].EA[EAnum]

        
        #transposing data so looks the same in imagetool as it does in the plotting 
        ra = pynData_to_ra(d)
        tools.new(ra)


# import numpy as np
# from time import sleep

# from iexplot.pynData.pynData_ARPES import kmapping_stack
# from iexplot.utilities import _shortlist
# from iexplot.fitting import find_EF_offset
# from iexplot.iexplot_EA import PLOT_EA, _stack_mdaEA_from_list


# def it_mdaEA_kitchen_sink(self, *scanNums, **kwargs):
#     """
#     stack and plot 3D mda EA data in imagetool
    
#     *scanNums = scanNum if volume is a single Fermi map scan
#         = start, stop, countby for series of mda scans    
        
    
#     kwargs:
#         E_unit = KE or BE
#         ang_offset = angle offset
#         y_scale = k or angle
#         EAnum = (start,stop,countby) => to plot a subset of EA scans
#         EDConly = False (default) to stack the full image
#                 = True to stack just the 1D EDCs
#         find_E_offset   = False (default), does not offset data
#                         = True, will apply offset
#         E_offset = energy offset, can be array or single float (default = 0.0)
#         fit_type = fitting function used to calculate offset, 'step' or 'Voigt'
#         fit_xrange = subrange to apply fitting function over
    
#     ☃    
#     """

#     kwargs.setdefault('E_unit','KE')
#     kwargs.setdefault('find_E_offset',False)
#     kwargs.setdefault('E_offset',0.0)
#     kwargs.setdefault('fit_type','step')
#     kwargs.setdefault('ang_offset',0.0)
#     kwargs.setdefault('kmap',False)
#     kwargs.setdefault('EAnum',(1,np.inf))
#     #kwargs.setdefault('EDConly', False)
#     kwargs.setdefault('fit_xrange', [-np.inf,np.inf])
#     kwargs.setdefault('debug', False)

#     scanNumlist=_shortlist(*scanNums,llist=list(self.mda.keys()),**kwargs)


#     EA_list, stack_scale = PLOT_EA.make_EA_list(self, scanNumlist, **kwargs)
    

#     if kwargs['debug']:
#         print('EA list:',EA_list)

#     if kwargs['find_E_offset']:
#         E_offset = find_EF_offset(EA_list, E_unit = kwargs['E_unit'], fit_type = kwargs['fit_type'], xrange = kwargs['fit_xrange'])
#     else: 
#         E_offset = kwargs['E_offset']

        
#     hv_list = []
#     for EA in EA_list:
#         hv_list.append(EA.hv)
#     hv_array = np.array(hv_list)
    
#     #adjusting angle scaling
#     for EA in EA_list:
#         EA.scaleAngle(kwargs['ang_offset'])
    
#     if len(EA_list) == 0:
#         d = EA_list[0] ### this is nonsense
#     else:
#         if kwargs['kmap']:
#             d = kmapping_stack(EA_list, E_unit = kwargs['E_unit'], KE_offset = -E_offset, debug = kwargs['debug'])
#         else:
#             d = _stack_mdaEA_from_list(EA_list,stack_scale, E_unit = kwargs['E_unit'], E_offset = -E_offset, debug = kwargs['debug'])
    
#     if kwargs['E_unit'] == 'BE':
#         d.unit['x'] = 'Binding Energy (ev)'
    
#     tools.new(d) 

# def it_video(it_name, video_fname,fps,image_folder_path, it_dict = it_dict, **kwargs):
#     '''
#     Automatically sweeps cursors and creates a video of an imagetool window
    
#     By default, will sweep over 10 points
    
#     it_name = str, name of it window in it_dict
    
#     **kwargs:
#         step_size = 5 (default), sweep will use number_of_points to determine step size
#                         int to manually set the spacing between frames
#     '''
    
#     ### should be updated and moved into the code ###
    
    
#     kwargs.setdefault('step_size',5)

        
#     it_address = it_dict[it_name]['address']
#     tool = return_object_from_memory(it_address)
#     window = tool.pg_win
    
#     #select last axis
#     try:
#         sweep_axis = tool.data.axes[2]
#     except:
#         sweep_axis = tool.data.axes[1]
    
    
#     sweep_indices = []
#     length = len(sweep_axis)
    
#     if type(kwargs['step_size']) == int:
#         index = 0
#         while index < length:
#             sweep_indices.append(index)
#             index += kwargs['step_size'] 
#     else:
#         print('Not a valid step size, must be int')
    
#     image_filename_list = []
    
#     #update and save IT window
#     for i in sweep_indices:
#         it_update_linked(it_dict[it_name], c_z = sweep_axis[i])    
        
#         image = window.grab(window.rect())
#         filename = it_dict[it_name]['tool_name']+'_'+str(i)+'.png'
#         image.save(filename)
#         image_filename_list.append(filename)
    
#     #make video
#     make_video(video_fname,fps,image_filename_list,image_folder_path,**kwargs)

    