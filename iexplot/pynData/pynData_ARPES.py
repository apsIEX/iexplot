#==============================================================================
#==============================================================================
# Domain specific applications - ARPES extensions for pynData
#      Data Format (data.shape = (z,y,x))
#          Axis x:  Energy (eV)
#          Axis y:  Angle (Degrees)
#          Axis z:  Scan axis (Theta, hv, Beta ...)
#
#       .KEscale:   original KE scale
#       .angScale:  original angle scale of detector
#       .angOffset: offset of orignal angular scaling, used for book keeping
#       .slitDir:   slit direction, 'H' or 'V'
#       .thetaX:    polar angle
#       .thetaY:    other angle
#       .hv:        photon energy in eV
#       .wk:        work function of analyzer in eV, setWk(d,val)
#       .E_offset:  energy offset to account for differences between the actual and specified photon energy
#       .EDC        angle integrated pynData object
#       .MDC        energy integrated pynData object
#==============================================================================

#==============================================================================
# imports
#==============================================================================
import numpy as np
from scipy import interpolate

from iexplot.pynData.pynData import nData, nData_h5Group_r, nData_h5Group_w, stack_attributes
from iexplot.utilities import *
from iexplot.plotting import plot_1D
from iexplot.pynData.ARPES_functions import *

###############################################################################################
class nARPES(nData):
         
    def _nARPESattributes(self,metadata,**kwargs):
        """
        self is an pynData object and we will add the following attribute from the metadata dictionary
            'KEscale':[],     # original kinetic scale
            'BEscale':[],     # calculated binding energy scale from KEscale, hv and wk
            'angScale':[],    # original angle scale of detector
            'angOffset':0     # offset of orignal angular scaling, used for book keeping
            'slitDir':'V'     # slit direction, 'H' or 'V'
            'thetaX':0,       # polar angle
            'thetaY':0,       # other angle
            'hv':22.0,        # photon energy in eV
            'wk':4.0,         # work function of analyzer in eV
            'E_offset':0.0,   # energy offset to account for differences between the actual and specified photon energy
            'EDC'/'MDC':      # pynData EDC/MDC data
            'spectraInfo':    # dictionary with detector info   
            'E_offset': 0.0   # energy offset to account for differences between the actual and specified photon energy      
        """
        kwargs.setdefault("debug",False)
        self.KEscale=np.empty(1)
        self.BEscale=np.empty(1)
        self.angScale=np.empty(1)
        self.angOffset=0
        self.slitDir='V'
        self.thetaX=0
        self.thetaY=0
        self.hv=22.0
        self.wk=4.0
        self.E_offset=0.0
        self.EDC=nData(np.empty(1))
        self.MDC=nData(np.empty(1))
        self.spectraInfo={}
        
        if kwargs['debug']:
            print("\n _nARPESattributes")
            print(vars(self))
        for key in vars(self):
            if key in metadata:
                if metadata != None:
                    setattr(self, key, metadata[key])    
        try:
            self._BE_calc()
        except:
            pass

    def _nARPES_attributes_keys(self):
        attr_keys = ['KEscale','BEscale','angScale','angOffset','slitDir','thetaX','thetaY',
         'hv','wk','E_offset','EDC','MDC','spectraInfo']
        return attr_keys

    def nARPES_attributes(self):
        keys = self._nARPES_attributes_keys()
        attr = {}
        for key in keys:
            attr[key] = getattr(self,key)
        return attr
 

    #==============================================================================
    # converting between KE and BE scaling
    #==============================================================================
    def scaleKE(self):
        """
        sets the scaling of the specificed axis to original KE scaling
        also sets the EDC scaling to the orginal KE scaling
        """

        self.updateAx('x',np.array(self.KEscale) + self.E_offset,"Kinetic Energy (eV)")
        self.EDC.updateAx('x',np.array(self.KEscale) + self.E_offset,"Kinetic Energy (eV)")
    
    def _BE_calc(self,**kwargs):
        """
        calculates the binding energy and updates self.BEscale
        the actual photon energy = self.hv + self.EA_offset
        wk is the work function of the analyzer

        where BE = hv + offset - KE - wk (above EF BE is negative); KE is orginal KE scaling

        **kwargs:
            wk to update the work function
            hv to update the photon energy  
            E_offset to update the energy offset

        """
        if 'wk' in kwargs:
            self.wk = kwargs['wk']

        if 'hv' in kwargs:
            self.hv = kwargs['hv']

        if 'E_offset' in kwargs:
            self.E_offset = kwargs['E_offset']

        KE = np.array(self.KEscale)
        
        BE_scale = KE_to_BE(KE,self.hv,self.wk,self.E_offset)
        self.BEscale = BE_scale
        


    def scaleBE(self,**kwargs):
        """
        sets the scaling of the specificed axis to original BE scaling
        also sets the EDC scaling to the orginal BE scaling
        
        **kwargs: 
            wk to update the work function
            hv to update the photon energy 
            E_offset to update the energy offset
     
        where BE = (hv + E_offset) - KE - wk (above EF BE is negative); KE is orginal KE scaling
            actually photon energy = hv - E_offset 
            wk is the work function of the analyzer (not this is frequently pass energy dependent)
    
        """
        self._BE_calc()
        BE = self.BEscale

        self.updateAx('x',BE,"Binding Energy (eV)")
        self.EDC.updateAx('x',BE,"Binding Energy (eV)")
    
    def set_wk(self,wk):
        """
        updates the work function and recalculates the BE scale
        """
        self.wk = wk
        self._BE_calc()
    
    def set_hv(self,hv):
        """
        updates the photon energy and recalculates the BE scale
        """
        self.hv = hv
        self._BE_calc()

    def set_E_offset(self,E_offset):
        """
        updates the energy offset and recalculates the BE scale (does not change KE scale)
        """
        self.E_offset = E_offset
        self._BE_calc()
    
#==============================================================================
# adjusting angle scaling
#==============================================================================
    
    def scaleAngle(self,delta=0):
        """
        changest the angle scaling of the data and the MDC
        based on the orginal angle scale and angOffset
            newScale = angScale + angOffset + delta;
            delta=(oldCoor-newCoor); can be value or an array of the same length as angScale
        
        """
        angScale=np.array(self.angScale)
        newScale= angScale + self.angOffset + delta
        self.updateAx('y',newScale,"Angle (deg)")
        self.MDC.updateAx('x',newScale,"Angle (deg)")
        self.angScale = newScale


#==============================================================================
# stacking spectra/EDCs 
#==============================================================================
def EA_Escale(EA,BE=True,**kwargs):
    """
    EA is pynData object
    BE = True/False for BE/KE scaling

    **kwargs (all can be a float or a np.array of the same length as KEscale)
        hv = photon energy, default is EA.hv
        wk = work function, default is EA.wk
        E_offset = Kinetic energy offset, default = 0, can be a list or array if 
                   different for each point in the stack
    
    returns E_scale, E_unit
    """
    kwargs.setdefault('debug',False)
    
    if BE:
        EA._BE_calc(**kwargs)
        E_scale = EA.BEscale
        E_unit = "Binding Energy (eV)"

    else:
        E_scale = EA.KEscale
        E_unit = "Kinetic Energy (eV)"
    
    return E_scale, E_unit   

def _stack_Escale(EA_list,BE=True,**kwargs):
    """
    returns array np.arange(E_max, E_min, E_delta) (BE=True E_delta is negative)
    
    EA_list = list of EA objects
    E_offsets = np array of of the same length as EA_list with offset values
        new_scale = E_scale + E_offset

    Note is using for interpolation you will need bounds_error = False, fill_value = np.nan
    """

    for n,EA in enumerate(EA_list):
        if 'E_offsets' in kwargs:
            EA.set_E_offset(kwargs['E_offsets'][n])
        E_scale, E_unit = EA_Escale(EA,BE=True)   
       
        if n == 0: 
            E_min = np.min(E_scale)
            E_max = np.max(E_scale)
            
        _E_min = np.min(E_scale)
        _E_max = np.max(E_scale)
        E_min = min(E_min, _E_min)
        E_max = max(E_max, _E_max)

    E_delta = E_scale[1]-E_scale[0]

    if BE:
        E_scale = np.arange(E_max,E_min,E_delta)
            
    else:
        E_scale = np.arange(E_min,E_max,E_delta)

    return E_scale, E_unit


def stack_EAs(EA_list,stack_scale,stack_unit,BE=True, **kwargs):
    """
    creates and returns an ndata stack spectra/EDCs based on EDC_only
    
    EA_list list of EA objects
    stack_scale = list or np array with coordinates for y-scale(z-scale) if EDC_only=True(False)
    stack_unit = units for y-scale(z-scale) if EDC_only=True(False)
    BE = True/False for BE/KE scaling
    
    **kwargs:                                   
        E_offsets = offset value for each scan based on curve fitting 
                    can be an np.array or float depending if it varies along stack-directions
                    sets the EA.E_offset value for each EA object
        EDC_only = True/False image/volume (default: false)
    """
    kwargs.setdefault('EDConly',False)
    
    #adjusting for E_offset keyword
    if 'E_offset' in kwargs:
        kwargs['E_offsets'] = kwargs['E_offset']
        del kwargs['E_offset']
    #allowing for energy offsets corrections
    if 'E_offsets' in kwargs:
        if type(kwargs['E_offsets']) == float:
            kwargs['E_offsets'] = np.full(len(EA_list),kwargs['E_offsets'])
        elif type(kwargs['E_offsets']) == int:
            kwargs['E_offsets'] = np.full(len(EA_list),kwargs['E_offsets'])
        else:
            kwargs['E_offsets'] = np.array(kwargs['E_offsets'])
    
    #defining the energy scale 
    E_scale,E_unit = _stack_Escale(EA_list,BE=BE,**kwargs)
    
    #defining the angle scale    
    angle_scale = EA_list[0].scale['y']
    
    for i,EA in enumerate(EA_list):
        if 'EA_offset' in kwargs:
            EA.set_E_offset(kwargs['E_offset'][i])
        
        x_original = EA_Escale(EA,BE=BE,**kwargs)[0]
        y_original = EA.scale['y']
        
        #Interpolate the data array
        if kwargs['EDConly']:
            img = EA.EDC.data
            interpolator = interpolate.interp1d(x_original, img, kind='linear',bounds_error = False, fill_value = np.nan)
            img_interp = interpolator(E_scale)      
        else:   
            img = EA.data
            new_X, new_Y = np.meshgrid(E_scale, angle_scale)
            points_new = np.stack([new_X.ravel(), new_Y.ravel()], axis=-1)
    
            interpolator = interpolate.interpn(points=(x_original, y_original), values =  np.transpose(img), xi = points_new, method='linear', bounds_error = False, fill_value = np.nan)
            #Interpolated EA data
            img_interp = interpolator.reshape(new_X.shape)
        
        # stack the interpolated 
        if i == 0:
            stack = img_interp
        else:
            if kwargs['EDConly']:
                stack = np.vstack((stack,img_interp))
            else:
                stack = np.dstack((stack,img_interp))
    
    nd = nData(stack)
    stack_attributes(EA_list,nd)

    E_unit = "Binding Energy (eV)" if BE else "Kinetic Energy (eV )"
    nd.updateAx('x',E_scale,E_unit+"(eV)")
    
    if kwargs['EDConly']:
        nd.updateAx('y',stack_scale,stack_unit)
    else:
        nd.updateAx('y',angle_scale,"Degree")
        nd.updateAx('z',stack_scale,stack_unit)
    
    

    return nd

#==============================================================================
# calculating k scaling
#==============================================================================

def kmap_scan_thetaX(EAstack,**kwargs):
    '''
    d type: pynData stack x: KE, y: thetaY, z: thetaX
    returns pynData (x: ky, y: ky, z: BE)
    '''
    KE = EAstack.scale['x']
    thetaY = EAstack.scale['y']
    thetaX = EAstack.scale['z'] #scan direction
    
    org = EAstack.data #data(thetaY, KE, thetaX)
    EA = EAstack.data[:,:,0]
    KE_min, KE_max, kx_min, kx_max, ky_min, ky_max, kz_min, kz_max = kmapping_boundaries_slice(EA)
    
    kx_scale  = np.linspace(kx_min,kx_max,len(list(thetaX)))
    ky_scale  = np.linspace(ky_min,ky_max,len(list(thetaY)))

    new = np.zeros((len(ky_scale),len(KE),len(kx_scale)))
    new = interpolate.RegularGridInterpolator((ky_scale,KE,kx_scale),org, method = 'linear',bounds_error = False, fill_value = np.nan)
    
    dnew = nData(new.values.transpose(0,2,1))
    
    BE = KE_to_BE(KE,EAstack.hv,EAstack.wk,EAstack.E_offset)
    nData.updateAx(dnew,'x',kx_scale,'kx')
    nData.updateAx(dnew,'y',ky_scale,'ky')
    nData.updateAx(dnew,'z',BE,'BE')
    
    return dnew

def kmap_scan_hv(d,wk):
    '''
    d type: pynData stack x: KE, y: thetaY, z: hv
    returns pynData (x: ky, y: ky, z: BE)
    '''
    KE = d.scale['x']
    thetaY = d.scale['y']
    hv = d.scale['z'] 
    thetaX = np.zeros(len(hv))

    org = d.data #data(thetaY, KE, hv)

    kx_scale, ky_scale = nARPES.kScale(nARPES, KE, thetaY, thetaX)

    new = np.zeros((len(ky_scale),len(KE),len(hv)))
    new = interpolate.RegularGridInterpolator((ky_scale,KE,hv),org, method = 'linear')

    dnew = nData(new.values.transpose(1,0,2))
    
    BE = KE_to_BE(KE,hv,wk)
    nData.updateAx(dnew,'x',ky_scale,'ky')
    nData.updateAx(dnew,'y',BE,'BE')
    nData.updateAx(dnew,'z',hv,'hv')

    return dnew

def kmapping_boundaries_slice(EA, V0=10):
    """
    EA = pynData_ARPES object
    """
    #Kinetic Energy
    KE_min = np.min(EA.KEscale)
    KE_max = np.max(EA.KEscale)
    #k_parallel
    if EA.slitDir == 'H':
        thetaX_min = np.min(EA.angScale)+EA.thetaX
        thetaX_max = np.min(EA.angScale)+EA.thetaX
        kx_min = theta_to_kx(KE_max,thetaX_min)
        kx_max = theta_to_kx(KE_max,thetaX_max)    
        thetaY = EA.thetaY
        ky_min = theta_to_ky(KE_max,thetaX_min,thetaY)
        ky_max = theta_to_ky(KE_max,thetaX_max,thetaY)
    elif EA.slitDir == 'V':
        thetaX = EA.thetaX
        kx_min = np.minimum(theta_to_kx(KE_max,thetaX),theta_to_kx(KE_min,thetaX))
        kx_max = np.maximum(theta_to_kx(KE_max,thetaX),theta_to_kx(KE_min,thetaX))
        thetaY_min = np.min(EA.angScale)
        thetaY_max = np.max(EA.angScale)
        ky_min = theta_to_ky(KE_max,thetaX,thetaY_min)
        ky_max = theta_to_ky(KE_max,thetaX,thetaY_max)
    #k_perpendicular    
    #min kz at maximum k magnitudes and smallest KE
    kx = max(abs(kx_min),abs(kx_max)) 
    ky = max(abs(ky_min),abs(ky_max)) 
    kz_min = k_to_kz(kx, ky, KE_min, V0)
    #max kz at min k magnitudes and largest KE
    kx = min(abs(kx_min),abs(kx_max)) 
    ky = min(abs(ky_min),abs(ky_max)) 
    kz_max = k_to_kz(kx, ky, KE_max, V0)
    return  KE_min, KE_max, kx_min, kx_max, ky_min, ky_max, kz_min, kz_max

def kmapping_boundaries(EA_list):
    """
    EA_list = list of pynData_ARPES objects
    
    """
    for n,EA in enumerate(EA_list):
        if n == 0: 
            KE_min, KE_max, kx_min, kx_max, ky_min, ky_max, kz_min, kz_max = kmapping_boundaries_slice(EA)
        #else:
        _KE_min, _KE_max, _kx_min, _kx_max, _ky_min, _ky_max, _kz_min, _kz_max = kmapping_boundaries_slice(EA)
        KE_min = min(KE_min, _KE_min)
        KE_max = max(KE_max, _KE_max)
        kx_min = min(kx_min, _kx_min)
        kx_max = max(kx_max, _kx_max) 
        ky_min = min(ky_min, _ky_min)
        ky_max = max(ky_max, _ky_max) 
        kz_min = min(kz_min, _kz_min)
        kz_max = max(kz_max, _kz_max) 
    return KE_min, KE_max, kx_min, kx_max, ky_min, ky_max, kz_min, kz_max

    

def kmapping_stack(EA_list, BE=True, **kwargs):
    """
    creates a volume of stacked spectra in k-space

    EA_list = list of EA objects

    kwargs =
        KE_offset
    """
    kwargs.setdefault('KE_offset',0.0)

    KE_min, KE_max, kx_min, kx_max, ky_min, ky_max, kz_min, kz_max = kmapping_boundaries(EA_list)
    EA = EA_list[0]
    
    #energy BE/KE
    BE_min = KE_to_BE(np.max(EA.KEscale),EA.hv,EA.wk)
    BE_max = min(KE_to_BE(KE_min,EA.hv,EA.wk),KE_to_BE(KE_min,EA.hv,EA.wk))
    if E_unit == 'KE':
        E_new = np.arange(KE_min,KE_max,abs(BE_min-BE_max))
    if E_unit == 'BE':
        BE_np = EA.data.shape[1]
        E_new = np.linspace(BE_max,BE_min,BE_np) #swap order for plotting
    E_np = E_new.shape[0]
    
    #k
    k_np = EA.angScale.shape[0]
    if EA.slitDir == 'H':
        k_new = np.linspace(kx_min,kx_max,k_np)
    elif EA.slitDir == 'V':
        k_new = np.linspace(ky_min,ky_max,k_np)

    #hv
    z_np = len(EA_list)
    z_new = []
    
    #make new stack
    if EA.slitDir == 'H':
        data_new = np.empty((E_np,k_np,z_np))
        data_xx,data_yy = np.meshgrid(k_new,E_new)
    elif EA.slitDir == 'V':
        data_new = np.empty((k_np,E_np,z_np))
        data_xx,data_yy = np.meshgrid(E_new,k_new)

    for n, EA in enumerate(EA_list):
        #convert single slice
        if type(kwargs['KE_offset']) == float:
            KE_offset = kwargs['KE_offset']
        else:
            KE_offset = kwargs['KE_offset'][n]
        img = ARPES_angle_k(k_new,EA.data,EA.KEscale,EA.angScale,EA.thetaX,KE_offset,EA.slitDir)
        
        E_scale,E_unit = EA_Escale(EA,BE=True,**kwargs)
        if EA.slitDir == 'H':
            img_y = E_scale
            img_x = k_new     
        
        elif EA.slitDir == 'V':
            img_x = E_scale
            img_y = k_new

            
        #now we need to interp image into 3D array
        img_xx,img_yy = np.meshgrid(img_x,img_y)
        data_new[:,:,n] = interpolate.griddata((np.ravel(img_xx),np.ravel(img_yy)),np.ravel(img),(data_xx,data_yy),fill_value=np.nanmin(img),rescale=True,method='nearest')
        
        data_new = np.nan_to_num(data_new, nan = np.nanmin(img))

    d = nData(data_new)
    d.updateAx('x',E_scale,E_unit)
    d.updateAx('y',k_new,'ky')
    stack_attributes(EA_list,d)
    return d
        
##########################################
# generalized code for saving and loading as part of a large hd5f -JM 4/27/21
# creates/loads subgroups    
##########################################
def nARPES_h5Group_w(nd,parent,name):
    """
    for an nData object => nd
    creates an h5 group with name=name within the parent group:
        with all ndata_ARPES attributes saved                   
    """
    #saving ndata array
    g=nData_h5Group_w(nd,parent,name)
    
    #EDC/MDC
    nData_h5Group_w(nd.EDC,g,"EDC")
    nData_h5Group_w(nd.EDC,g,"MDC")
    
    for attr in ['hv','wk','thetaX','thetaY','KEscale','angScale','angOffset']:
        if type(getattr(nd,attr)) == type(None):
            g.require_dataset(attr, data=np.array([]) , dtype='f',shape=np.array([]))
        else:
            g.require_dataset(attr, data=np.array(getattr(nd,attr)) , dtype='f',shape = np.array(getattr(nd,attr)).shape)
    for attr in ['slitDir']:
        g.attrs[attr]=str(getattr(nd,attr))
    return g

def nARPES_h5Group_r(h):
    """           
    """
    d=nData_h5Group_r(h)
    
    #EDC/MDC
    d.EDC=nData_h5Group_r(h['EDC'])
    d.MDC=nData_h5Group_r(h['MDC']) 
    
    
    #val=ast.literal_eval(h5['mda']['mda_'+str(scanNum)]['header'][hkey].attrs[key])
    #for att in dir(your_object):
        #print (att, getattr(your_object,att))
    for attr in ['hv','wk','thetaX','thetaY','KEscale','angScale','angOffset']:
        setattr(d,attr,h[attr])
    for attr in ['slitDir','fpath']:
        if attr in h.attrs:
            setattr(d,attr,(h.attrs[attr]))
    return d   