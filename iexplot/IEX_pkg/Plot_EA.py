import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate


from iexplot.utilities import _shortlist, make_num_list, get_nested_dict_value 
from iexplot.plotting import plot_1D, plot_2D, plot_3D
from iexplot.pynData.pynData_ARPES import stack_EAs 
from iexplot.fitting import fit_box, fit_gaussian, fit_lorentzian, fit_poly, fit_step, fit_shirley_background

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

    def fit_EDC(self,scanNum,fit_type,EAnum=1,BE=False,**kwargs):
        """
        simple fitting of EDC data
        fit_type = 'box', 'gaussian', 'lorentzian', 'poly', 'step:', 'shirley'

        EAnum = scan/sweep number 
                = inf => will sum all spectra

        BE = False; Kinetic Energy scaling
        BE = True; Binding Energy scaling
           where BE = hv-KE-wk (wk=None uses workfunction defined in the metadata)
        
        """
        kwargs.setdefault('show_legend',False)
        kwargs.setdefault('plot',True)

        x,y,xlabel = self.EA_EDC(scanNum,EAnum=EAnum,BE=BE)
    
        fit_funcs = {
            'box':fit_box,
            'gaussian':fit_gaussian,
            'lorentzian':fit_lorentzian,
            'poly':fit_poly,
            'step:':fit_step,
            'shirley':fit_shirley_background,
        }

        if fit_type not in fit_funcs.keys():
            print('Not a valid fit_type use one of the following'+list(fit_funcs.keys()) )
            #return

        fit_func = fit_funcs[fit_type]
        ff = fit_func(x,y,**kwargs)
        return ff
  

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
            stack_scale kwargs
                index = True, stack scale by posiiton in nums list 
                EA_attr = attribute (hv for example can be anything you see in EA.)
                EA_extras = key from extras dictionary will search through nests (example: x comes from EA.extras['sample']['x'])
                
            
        """
        kwargs.setdefault('debug',False) 
        kwargs.setdefault('index',False)
        
        scanNumlist = make_num_list(*nums)
        EA_list = []
        
        stack_scale=np.empty((0))
        
        if kwargs['debug']:
            print('scanNumlist',scanNumlist)
        
        #mda scan
        if len(scanNumlist)==1:
            stack_scale = np.concatenate((stack_scale,self.mda[scanNum].posy[0].data))
            stack_unit =self.mda[scanNum].posy[0].pv[1]
        else:
            stack_unit = None

        #iterating over mda scans       
        for scanNum in scanNumlist:
            if kwargs['debug']:
                print('scanNumlist: ',scanNumlist)
        
            #creating list of all EA numbers
            ll = list(self.mda[scanNum].EA.keys())
            
            #creating shortlist of selected EAnum
            if 'EAnum' in kwargs:
                EAlist = _shortlist(*kwargs['EAnum'],llist = ll,**kwargs)  
            else:
                EAlist = ll
            
            if kwargs['debug']:
                print('EAlist: ',EAlist)
        
            #iterating over EA scans  
            for EAnum in EAlist:
                EA = self.mda[scanNum].EA[EAnum]
                EA_list.append(EA)
                
                if 'EA_attr' in kwargs:
                    stack_unit = kwargs['EA_attr']
                    try:
                        val = getattr(EA,kwargs['EA_attr'])
                        stack_scale = np.concatenate([stack_scale,[val]])
                    except:
                        print('EA_attr = '+kwargs['EA_attr']+' does not exist')
                        return                  
        
                elif 'EA_extras' in kwargs:
                    val = get_nested_dict_value(EA.extras, kwargs['EA_extras'])
                    stack_scale = np.concatenate([stack_scale,[val]])
                    stack_unit = kwargs['EA_extras']
        
                elif 'index' in kwargs and kwargs['index']:
                    stack_scale = stack_scale[-1]+1
                    stack_unit = 'index'
            
                else:
                    stack_scale = np.append(stack_scale,scanNum)
                    stack_unit='scanNum'
                    
            #Truncating stack_scale for number of images        
            stack_scale = stack_scale[0:len(EA_list)]    
        
        if kwargs['debug']:
            print('make_EA_list:',EA_list)
            print('stack_scale: ',stack_scale)
            print('stack_unit',stack_unit)
        
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

            d = stack_EAs(EA_list,stack_scale,stack_unit,E_unit=E_unit,**kwargs)

            return d

