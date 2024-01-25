import numpy as np
import re
from time import sleep
from lmfit import Parameters
import pyimagetool as it
from iexplot.plotting import plot_1D, plot_2D, plot_dimage
from iexplot.pynData.pynData_ARPES import kmapping_stack
from iexplot.utilities import _shortlist
from iexplot.fitting import fit_voigt, fit_step, find_EF_offset
from iexplot.iexplot_EA import PlotEA, _stack_mdaEA_from_list

class IEX_IT:
    instances = {}

    def __init__(self, info = {}):  
        self.info = info 
        pass

    #Image Tool versioning  
    def IT_list(self):
        """
        List all the image tool currently in memory
        """
        d = self.IT_instances()
        print(d.keys())

    def IT_show(self, IT_num):
        """
        Shows an ImageTool
        IT_num = number of the ImageTool you want to show
        """
        base = 'tool_'
        name = base + str(IT_num)
        d = self.IT_instances()
        if name in d.keys():
            d[name].show()
        else:
            print("ImageTool is not currently loaded, use .IT_list() to show loaded tools")

    #Image Tool version book keeping - internal
    def IT_instances(self):
        return self.instances
    
    def _next_it(self):
        """
        Automatically iterates imagetool name each time a new window is created
        """
        v_array = np.empty(0)
        print('instances')
        print(self.instances)
        for key in self.instances.keys():
            base, v = re.split('_',key)
            v_array = np.append(v_array, int(v))
            
        if v_array.shape==(0,):
            v_next = 0
            base = 'tool_'
        else:    
            print(type(v_array),v_array)            
            v_max = np.max(v_array)
            v_next = int(v_max) + 1
            base = 'tool_'
            
        return base, v_next

    def _append_instance(self, tool):
        """
        Adds a new instance of imagetool to the instances dictionary
        """
        base, v_next = self._next_it()
        name = base + str(v_next)
        self.instances[name] = tool

        return name

    #universal IT plotting functions
    
    
    

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
        x = self.mda[scanNum].posx[0].data[0,:]
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
            fit_type = fitting function used to calculate offset, 'step' or 'Voigt'
            fit_xrange = subrange to apply fitting function over
        
        
        """
        kwargs.setdefault('E_unit','KE')
        kwargs.setdefault('find_E_offset',False)
        kwargs.setdefault('offset_type','step')
        kwargs.setdefault('ang_offset',0.0)
        kwargs.setdefault('kmap',False)
        kwargs.setdefault('array_output', False)
        kwargs.setdefault('EAnum',1)
        kwargs.setdefault('EDConly', False)
        kwargs.setdefault('fit_xrange', [-np.inf,np.inf])

        scanNumlist=_shortlist(*scanNums,llist=list(self.mda.keys()),**kwargs)
        

        EA_list, stack_scale = PlotEA.make_EA_list(self, scanNumlist, EAnum = kwargs['EAnum'], EDConly = kwargs['EDConly'])
        
        if kwargs['find_E_offset']:
            E_offset = find_EF_offset(EA_list, E_unit = kwargs['E_unit'], fit_type = kwargs['fit_type'], xrange = kwargs['fit_xrange'])
        else: 
            E_offset = 0.0

            
        hv_list = []
        for EA in EA_list:
            hv_list.append(EA.hv)
        hv_array = np.array(hv_list)
        
        #adjusting angle scaling
        for EA in EA_list:
            EA.scaleAngle(kwargs['ang_offset'])
        
        if len(EA_list) == 1:
            d = EA_list[0]
        else:
            if kwargs['kmap'] == True:
                d = kmapping_stack(EA_list, E_unit = kwargs['E_unit'], KE_offset = -E_offset)
            else:
                d = _stack_mdaEA_from_list(EA_list,stack_scale, E_unit = kwargs['E_unit'], KE_offset = -E_offset)
        
        if kwargs['array_output'] == True:
            return d
        else:
            self.it_pynData(self,d)
    
    
    

    def it_export(self, it_num, img_prof, output,**kwargs):
        """
        extract data from an individual plot in imagetool

        it_num = imagetool window number
        it_num type = int

        img_prof = name of image being extracted
        img_prof type = string (see axis_dict for options)

        output = how image data will be returned
        output type = string (see output_list for options)
        """

        kwargs.setdefault('cmap','viridis')

        axis_dict = {'prof_h':['x','Intensity',1], 'prof_v':['y','Intensity',0], 'prof_d':['z','Intensity',2], 'img_main':['xy',0,1], 'img_v':['zy',2,1], 'img_h':['xz',0,2]}
        output_list = ('data','plot','profile_plot')
        d = self.IT_instances()
        tool = d['tool_'+str(it_num)]
        #try:
        it_img_name, dim_y, dim_x = axis_dict[img_prof]
        img = tool.get(it_img_name)
        if output in output_list:
            if output == 'data':
                cursor_info = IEX_IT.get_it_properties(tool)
                return img, cursor_info  #add properties and axes here
            if output == 'plot':
                if 'img' in img_prof:
                    plot_2D(img.data.T,img.axes[::-1],(tool.data.dims[dim_x],tool.data.dims[dim_y]),cmap = kwargs['cmap'])
                elif 'prof' in img_prof:
                    plot_1D(img[0],img[1],xlabel=tool.data.dims[dim_x],ylabel = dim_y)
            if output == 'profile_plot':
                if 'img' in img_prof: 
                    plot_dimage(img.data.T,img.axes[::-1],(tool.data.dims[dim_x],tool.data.dims[dim_y]),cmap = kwargs['cmap'])
                elif 'prof' in img_prof:
                    print('Error: cannot output a plot with profile for a profile')
        else:
            print("Error: not a valid output type")
        #except:
        #    print("Error: not a valid image or profile name"+str(axis_dict.keys()))

    def get_it_properties(tool):
        list = ['index','pos','binwidth']
        dictionary = {}
        for key in list:
            obj = getattr(tool.pg_win.cursor,"_"+key)
            val = []
            for i in range(len(obj)):
                val.append(obj[i]._value)
            dictionary[key]= val
        val = []
        for i,ax in enumerate(['x','y','z']):
            val.append(tool.data.dims[i])
            
        dictionary['axes']=val
        return dictionary
    

    

def pynData_to_ra(d):
    """
    converts a pynData object into a imagetool.RegularDataArray
    """
    
    if len(d.data.shape)==2:
        dataArray = d.data.transpose(1,0)
        #scaleArray = (d.scale['y'],d.scale['x'])
        #unitArray = (d.unit['y'],d.unit['x'])
        #dataArray = d.data
        scaleArray = (d.scale['x'],d.scale['y'])
        unitArray = (d.unit['x'],d.unit['y'])
        delta = (scaleArray[0][1]-scaleArray[0][0],scaleArray[1][1]-scaleArray[1][0])
        coord_min = [scaleArray[0][0],scaleArray[1][1]]
    elif len(d.data.shape)==3:
        dataArray = d.data.transpose(1,0,2)
        #scaleArray = (d.scale['y'],d.scale['x'],d.scale['z'])
        #unitArray = (d.unit['y'],d.unit['x'],d.unit['z'])
        #dataArray = d.data
        scaleArray = (d.scale['x'],d.scale['y'],d.scale['z'])
        unitArray = (d.unit['x'],d.unit['y'],d.unit['z'])
        delta = (scaleArray[0][1]-scaleArray[0][0],scaleArray[1][1]-scaleArray[1][0],scaleArray[2][1]-scaleArray[2][0])
        coord_min = [scaleArray[0][0],scaleArray[1][1],scaleArray[2][2]]
    else:
        print("don't yet know how to deal with data of shape"+str(d.data.shape))
    
    ra = it.RegularDataArray(dataArray, delta = delta, coord_min = coord_min, dims = unitArray)

    return ra
