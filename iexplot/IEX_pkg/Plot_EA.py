import matplotlib.pyplot as plt
import numpy as np

from iexplot.utilities import _shortlist, make_num_list 
from iexplot.plotting import plot_1D, plot_2D, plot_3D
from iexplot.pynData.pynData import nstack
from iexplot.pynData.pynData_ARPES import kmapping_energy_scale
#from iexplot.IEX_pkg.Plot_IT import pynData_to_ra
#from pyimagetool import tools

class Plot_EA:
    """
    adds EA plotting methods to IEXnData class
    """
    def __init__(self):
        pass

    def EA_spectra(self,scanNum, EAnum=1, BE=False):
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
        
        
    def EA_EDC(self,scanNum,EAnum=1,BE=False):
        """
        returns x,y,label =  energy scaling, EDC spectra, units_label
            
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
        
    def plot_EDC(self,scanNum,EAnum=1,BE=False,**kwargs):
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
        x,y,xlabel = self.EA_EDC(scanNum,EAnum=EAnum,BE=BE)
                
        plot_1D(x,y,xlabel=xlabel,**kwargs)
        
        if BE:
            plt.xlim(max(x),min(x))

    def plot_EA(self,scanNum,EAnum=1,BE=False,transpose=False,**kwargs):
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

        img,xscale,yscale,xunit,yunit = self.EA_spectra(scanNum, EAnum, BE)

        if transpose == True:
            plot_2D(img.T,[xscale,yscale],[xunit,yunit],**kwargs)
            if BE == True:
                plt.ylim(max(xscale),min(xscale))
        else:
            plot_2D(img,[yscale,xscale],[yunit,xunit],**kwargs)
            if BE == True:
                plt.xlim(max(xscale),min(xscale))


    def EA_beamline(self,scanNum,EAnum=1):
        """
        returns info about beamline
        """
        return self.mda[scanNum].EA[EAnum].extras['beamline'] 
        
    def EA_HVscanInfo(self,scanNum,EAnum=1):
        """
        returns info about Scienta HV settings
        """
        return self.mda[scanNum].EA[EAnum].extras['HVscanInfo'] 
        
    def EA_sample(self,scanNum,EAnum=1):
        """
        returns info about Scienta HV settings
        """
        return self.mda[scanNum].EA[EAnum].extras['sample'] 

    def EA_setting(self,scanNum,EAnum=1):
        """
        returns info about Scienta parameters
        """
        return self.mda[scanNum].EA[EAnum].extras['EAsettings'] 

    def EA_extras(self,scanNum,EAnum=1):
        """
        returns all the metadata in the file
        """
        return self.mda[scanNum].EA[EAnum].extras

    def EA_pass_energy(self,scanNum,EAnum=1):
        """
        returns pass energy
        """
        return self.mda[scanNum].EA[EAnum].extras['EAsettings']['passEnergy'] 
        
    def EA_frames(self,scanNum,EAnum=1):
        """
        returns pass frames
        """
        return self.mda[scanNum].EA[EAnum].extras['EAsettings']['frames'] 

    def EA_KE(self,scanNum,EAnum=1):
        """
        returns KE_center for fixed mode and baby sweep scans
        returne KE_start,KE_stop_KE_step for swept mode scans
        """
        d = self.mda[scanNum].EA[EAnum].extras['EAsettings']
        
        if d['acqMode'] ==2:
            return d['kineticEnergy'] 
            
        if d['acqMode']==1:
            return d['sweptStart'],d['sweptStop'],d['sweptStep']   
        
    def EA_hv(self,scanNum,EAnum=1):
        """
        returns photon energy
        """
        return self.mda[scanNum].EA[EAnum].extras['beamline']['hv'] 

    def EA_exit_slit(self,scanNum,EAnum=1):
        """
        returns exitSlit size
        """
        return self.mda[scanNum].EA[EAnum].extras['beamline']['exitSlit'] 

    def EA_ringCurrent(self,scanNum,EAnum=1):
        """
        returns exitSlit size
        """
        return self.mda[scanNum].EA[EAnum].extras['beamline']['ringCurrent'] 

    def plot_mdaEA_stack(self,*args,**kwargs):
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


    def it_EA(self,scanNum,EAnum=1):
        """
        plot EA in imagetool
        """
        #ra = pynData_to_ra(self.mda[scanNum].EA[EAnum])
        #tools.new(ra)
        pass
    
    def make_EA_list(self, *nums, **kwargs):
            """
            return EA_list, stack_scale, stack_unit, where EA_list is a stack of EA ndata objects
            nums = list of mda scans to be plotted 
            
            **kwargs:      
                    EAnum = (start,stop,countby) => to plot a subset of EA scans
                    index = False (default), stack scale by number
                
            """
            kwargs.setdefault('debug',False) 
            kwargs.setdefault('index',False)
            
            scanNumlist = make_num_list(*nums)
            EA_list = []
            stack_scale=np.empty((0))
            
            if kwargs['debug']:
                print('scanNumlist',scanNumlist)

            for scanNum in scanNumlist:
                if kwargs['debug']:
                    print('scanNumlist: ',scanNumlist)
                if kwargs['index']:
                    stack_scale = np.arange(0,len(scanNumlist))
                    stack_unit = 'index'
                elif len(scanNumlist)==1:
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
                    EAlist = _shortlist(*kwargs['EAnum'],llist = ll,**kwargs)  
                else:
                    EAlist = ll
                 
                if kwargs['debug']:
                    print('EAlist: ',EAlist)

                #populating EA_list with EA/EDC scans
                for EAnum in EAlist:
                    EA_list.append(self.mda[scanNum].EA[EAnum])

                #Truncating stack_scale for number of images        
                stack_scale = stack_scale[0:len(EA_list)]    
            
            if kwargs['debug']:
                print('make_EA_list:',EA_list)

            return EA_list,stack_scale,stack_unit
    
    def stack_mdaEA(self, *scanNum, BE=True,**kwargs):
            """
            returns a volume of stacked spectra/or EDCs based on kwargs
            EDConly = False (default) to stack the full image
                        = True to stack just the 1D EDCs

            *scanNum = scanNum if volume is a single Fermi map scan
                    = mda => start, stop, countby for series of mda scans
                    only debugs for a stack of mda scans...need to try a fermi map AJE

            BE = True/False for constant binding energy /kinetic
        

            **kwargs:      
                EAnum = (start,stop,countby) => to plot a subset of scans (only EAnum = 1 by default)                       
                E_offset = offset value for each scan based on curve fitting in E_units
                            can be an array or a single float for the same offset to all  
                EDConly = True/False (default = False)
                
            """
            kwargs.setdefault('EDConly',False)

            if BE:
                E_unit = 'BE'
            else:
                E_unit = 'KE'

            EA_list, stack_scale, stack_unit = self.make_EA_list(*scanNum, **kwargs)

            d = _stack_mdaEA_from_list(EA_list,stack_scale, E_unit,**kwargs)
            #d.unit['']

            return d

def _stack_mdaEA_from_list(EA_list,stack_scale, E_unit='BE', **kwargs):
        """
        creates a volume of stacked spectra/or EDCs based on kwargs
        Note: does not currently account for scaling (dumb stacking)

        E_unit = 'KE' or 'BE'

        **kwargs:                                   
            E_offset = offset value for each scan based on curve fitting 
                        can be an np.array or float depending if it varies along stack-directions
            EDC_only = False
            
        """
        kwargs.setdefault('EDConly',False)
        kwargs.setdefault('E_offset',0.0)
        kwargs.setdefault('debug',False)
        kwargs.setdefault('array_output',True)

        if type(kwargs['E_offset']) == float:
            if (kwargs['E_offset']) == 0.0:
                #Stacking data
                if len(EA_list) == 1:
                    d = EA_list[0]
                else:
                    if kwargs['EDConly']:
                        EDC_list = [EA.EDC for EA in EA_list] 
                        d = nstack(EDC_list, stack_scale, **kwargs)
                        d.updateAx('x',E_scale,E_unit)
        
                    else:
                        d = nstack(EA_list, stack_scale, **kwargs)
                ax_label={'BE':"Binding Energy (eV)",'KE':"Kinetic Energy (eV)"}       
                d.updateAx('x',E_scale,ax_label[E_unit])
            return d
    
        if type(kwargs['E_offset']) == float:
            E_offset = np.full(len(EA_list),kwargs['E_offset'])
        elif type(kwargs['E_offset']) == int:
            E_offset = np.full(len(EA_list),kwargs['E_offset'])
        else:
            E_offset = kwargs['E_offset']
        
        for n,EA in enumerate(EA_list):
            if n == 0: 
                KE_min = np.min(EA.KEscale)+E_offset[n]
                KE_max = np.max(EA.KEscale)+E_offset[n]
            _KE_min = np.min(EA.KEscale)+E_offset[n]
            _KE_max = np.max(EA.KEscale)+E_offset[n]
            KE_min = min(KE_min, _KE_min)
            KE_max = max(KE_max, _KE_max)
            
        E_delta = EA.KEscale[1]-EA.KEscale[0]
        
        if E_unit == 'BE':
            BE_max = np.max(EA_list[0].BEscale) + np.max(E_offset)
            BE_min = np.min(EA_list[0].BEscale) + np.min(E_offset)
            E_scale = np.arange(BE_max,BE_min,-E_delta)
        else:
            E_scale = np.arange(KE_min,KE_max,E_delta)
            
        angle_scale = EA_list[0].scale['y']

        #BE/KE conversion - usless at the moment

        # Changing offset for each EA img in EA_list

        for i,EA in enumerate(EA_list):
            img = EA.data
            if E_unit == 'BE':
                x_original = EA.BEscale + E_offset[i]
            else:
                x_original = EA.KEscale + E_offset[i]
            y_original = EA.scale['y']
            
            new_X, new_Y = np.meshgrid(E_scale, angle_scale)
            
            points_new = np.stack([new_X.ravel(), new_Y.ravel()], axis=-1)  # Return a flattened list of coordinates in the new interpolated mesh
            
            interpolator = interpolate.interpn(points=(x_original, y_original), values =  np.transpose(img), xi = points_new, method='linear', bounds_error = False, fill_value = 0)

            #Interpolated EA data
            img_interp = interpolator.reshape(new_X.shape)
            if i == 0:
                stack = img_interp
            else:
                stack = np.dstack((stack,img_interp))

        nd = nData(stack)
        nd.updateAx('x',E_scale,E_unit+"(eV)")
        nd.updateAx('y',angle_scale,"Degree")
        return nd
        

 


