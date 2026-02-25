import copy
import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate



from iexplot.utilities import _shortlist, make_num_list, get_nested_dict_value 
from iexplot.plotting import plot_1D, plot_2D, plot_3D
from iexplot.pynData.pynData_ARPES import stack_EAs 
from iexplot.fitting import fit_box, fit_gaussian, fit_lorentzian, fit_poly, fit_step, fit_shirley_background

from iexplot.pynData.pynData import stack_attributes

class Plot_EA:
    """
    adds EA plotting methods to IEXnData class
    """
    def __init__(self):
        pass

    def _EA_obj (self,scanNum, EAnum=1,**kwargs):
        
        if EAnum != np.inf:
            EAlist = _shortlist(*EAnum, llist = EAlist,**kwargs)  

        if self.dtype == "EA":
            EA = self.EA
        elif self.dtype == "mdaEA" or "mdaAD": 
            EA = self.mda[scanNum].EA
        return EA
            

    def EA_spectra(self,scanNum, EAnum=1, BE=False,**kwargs):
        """
        returns return img,xscale,yscale,xunit,yunit  
        
        EAnum = np.inf sums all EAs within scanNum
            
        """
        if EAnum != np.inf:
            EA = self._EA_obj(self,scanNum,EAnum)
        else:
            EA = self.EA_spectra_sum(scanNum, EAnum=np.inf,**kwargs)
        
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
    
    
    
    def EA_spectra_sum(self,scanNum, EAnum=np.inf,**kwargs):
        """
        return pyndata object of summed EA data 
        EAnum = np.inf, sums all             
        """
        #creating shortlist of selected EAnum
      
        
        EA = self._EA_obj(self,scanNum,EAnum)
        EAlist = list(EA.keys())

        EAsummed = copy.deepcopy(EA[EAlist[0]])
        
        img = np.nansum(tuple(EA[EAnum].data for EAnum in EAlist),axis=0)
        edc = np.nansum(tuple(EA[EAnum].EDC.data for EAnum in EAlist),axis=0)

        EAsummed.data = img
        EAsummed.EDC.data = edc
        
        return EAsummed
    
    def EA_EDC(self,scanNum,EAnum=1,BE=False,**kwargs):
        """
        returns x,y,label =  energy scaling, EDC spectra, units_label
            
        usage:
            plt.plot(data.EAspectraEDC(151))    
        """

        if EAnum != np.inf:
            EA = self._EA_obj(self,scanNum,EAnum)
        else:
            EA = self.EA_spectra_sum(scanNum, EAnum=np.inf,**kwargs)
        
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
        EA = self._EA_obj(self,scanNum,EAnum)
        return EA.extras['beamline'] 
        
    def EA_HVscanInfo(self,scanNum,EAnum=1):
        """
        returns info about Scienta HV settings
        """
        EA = self._EA_obj(self,scanNum,EAnum)
        return EA[EAnum].extras['HVscanInfo'] 
        
    def EA_sample(self,scanNum,EAnum=1):
        """
        returns info about Scienta HV settings
        """
        EA = self._EA_obj(self,scanNum,EAnum)
        return EA[EAnum].extras['sample'] 

    def EA_setting(self,scanNum,EAnum=1):
        """
        returns info about Scienta parameters
        """
        EA = self._EA_obj(self,scanNum,EAnum)
        return EA[EAnum].extras['EAsettings'] 

    def EA_extras(self,scanNum,EAnum=1):
        """
        returns all the metadata in the file
        """
        EA = self._EA_obj(self,scanNum,EAnum)
        return EA[EAnum].extras

    def EA_pass_energy(self,scanNum,EAnum=1):
        """
        returns pass energy
        """
        EA = self._EA_obj(self,scanNum,EAnum)
        return EA[EAnum].extras['EAsettings']['passEnergy'] 
        
    def EA_frames(self,scanNum,EAnum=1):
        """
        returns pass frames
        """
        EA = self._EA_obj(self,scanNum,EAnum)
        return EA[EAnum].extras['EAsettings']['frames'] 

    def EA_KE(self,scanNum,EAnum=1):
        """
        returns KE_center for fixed mode and baby sweep scans
        returne KE_start,KE_stop_KE_step for swept mode scans
        """
        EA = self._EA_obj(self,scanNum,EAnum)
        d = EA[EAnum].extras['EAsettings']
        
        if d['acqMode'] ==2:
            return d['kineticEnergy'] 
            
        if d['acqMode']==1:
            return d['sweptStart'],d['sweptStop'],d['sweptStep']   
        
    def EA_hv(self,scanNum,EAnum=1):
        """
        returns photon energy
        """
        EA = self._EA_obj(self,scanNum,EAnum)
        return EA[EAnum].extras['beamline']['hv'] 

    def EA_exit_slit(self,scanNum,EAnum=1):
        """
        returns exitSlit size
        """
        EA = self._EA_obj(self,scanNum,EAnum)
        return EA[EAnum].extras['beamline']['exitSlit'] 

    def EA_ringCurrent(self,scanNum,EAnum=1):
        """
        returns exitSlit size
        """
        EA = self._EA_obj(self,scanNum,EAnum)
        return EA[EAnum].extras['beamline']['ringCurrent'] 

    def plot_mdaEA_stack(self,*mdascanNums,**kwargs):
        """
        *mdascanNums = scanNum if volume is a single Fermi map scan
                     = start, stop, countby for series of mda scans

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

        dataArray,scaleArray,unitArray = self.stack_mdaEA(*mdascanNums,**kwargs)
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
            EAnum = (start,stop,countby) => to plot a subset of EA scans (default is to stack all)
            EAavg = True to average all sweeps for each scanNum
            stack_scale kwargs
                index = True, stack scale by posiiton in nums list 
                EA_attr = attribute (hv for example can be anything you see in EA.)
                EA_extras = key from extras dictionary will search through nests (example: x comes from EA.extras['sample']['x'])
                
            
        """
        kwargs.setdefault('debug',False) 
        kwargs.setdefault('index',False)
        kwargs.setdefault('EAavg',False)
        
        scanNumlist = make_num_list(*nums)
        EA_list = []
        
        stack_scale=np.empty((0))
        
        if kwargs['debug']:
            print('scanNumlist',scanNumlist)
        
        #mda scan
        if len(scanNumlist)==1:
            scanNum = scanNumlist[0]
            #get mda dimensions
            rank = self.mda[scanNum].header.ScanRecord['rank']
            if rank == 1:
                stack_scale = list(self.mda[scanNum].EA.keys())
                stack_unit = 'sweeps'
            if rank == 2:
                stack_scale = np.concatenate((stack_scale,self.mda[scanNum].posy[0].data))
                stack_unit =self.mda[scanNum].posy[0].pv[1]
            if rank >2:
                print('rank > 2 not yet implemented')
                return
            if kwargs['debug']:
                print('stack_scale,stack_unit = ',stack_scale,stack_unit,'# mda positioner derived')
        else:
            print('stack_scale,stack_unit = ',stack_scale,stack_unit,' #not from mda positioners')

        #iterating over mda scans       
        for scanNum in scanNumlist:
            #creating list of all EA numbers
            ll = list(self.mda[scanNum].EA.keys())
            
            #creating shortlist of selected EAnum
            EAlist = ll
            if 'EAnum' in kwargs:
                if kwargs['EAnum'] == np.inf:
                    sumEA = True
                else:
                    EAlist = _shortlist(*kwargs['EAnum'],llist = ll,**kwargs)  
                    
            if kwargs['debug']:
                print('EAlist: ',EAlist)
        
            #appending EAs
            if kwargs['EAavg']: #Averaging EAs for each scanNum
                EA_attrlist = [EAlist[0]] #only taking attributes from first EA
                img,xscale,yscale,xunit,yunit = self.EA_spectra(scanNum,EAnum=np.inf)    
                img/len(EAlist)
                EA = copy.deepcopy(self.mda[scanNum].EA[EAlist[0]])
                EA.data = img
                EA.updateAx('x',xscale,xunit)
                EA.updateAx('y',yscale,yunit)
                stack_attributes([self.mda[scanNum].EA[EAlist[0]]],EA)
                EA_list.append(EA)
                
            else: #append each EA
                EA_attrlist = EAlist
                for EAnum in EAlist:
                    if kwargs['debug']:
                        print('scanNum: ',scanNum,'EAnum:',EAnum)
                    
                    EA = self.mda[scanNum].EA[EAnum]
                    EA_list.append(EA)
                
            
            #appending attributes
            for EAnum in EA_attrlist:
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
            kwargs.setdefault('debug',False)

            if BE:
                E_unit = 'BE'
            else:
                E_unit = 'KE'

            EA_list, stack_scale, stack_unit = self.make_EA_list(*scanNum, **kwargs)
            if kwargs['debug']:
                print('stack_scale',stack_scale)

            d = stack_EAs(EA_list,stack_scale,stack_unit,E_unit=E_unit,**kwargs)

            return d




