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
#       .wk:        work function of analyzer in eV, setWk(d,val) to update-
#       .EDC        angle integrated pynData object
#       .MDC        energy integrated pynData object
#==============================================================================

#==============================================================================
# imports
#==============================================================================
import numpy as np
from scipy import interpolate


from iexplot.pynData.pynData import nData, nData_h5Group_r, nData_h5Group_w, nstack
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
            'wk':4.0,         # work function of analyzer in eV, setWk(d,val) to update
            'EDC'/'MDC':      # pynData EDC/MDC data
            'spectraInfo':    # dictionary with detector info         
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

        self._BE_calc()

    def get_nARPESattributes(self):
        keys = ['KEscale','BEscale','angScale','angOffset','slitDir','thetaX','thetaY','hv','wk','EDC','MDC','spectraInfo']
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
        self.updateAx('x',np.array(self.KEscale),"Kinetic Energy (eV)")
        self.EDC.updateAx('x',np.array(self.KEscale),"Kinetic Energy (eV)")
    
    def _BE_calc(self,wk=None, hv=None):
        """
        calculates the binding energy and updates self.BEscale
        where BE = hv - KE - wk (above EF BE is negative); KE is orginal KE scaling
            wk=None uses  .wk for the work function (wk ~ hv - KE_FermiLevel)
            hv=None uses  .hv for the photon energy
    
        """
        if wk is None:
            wk=self.wk
        if hv is None:
            hv=self.hv

        KE=np.array(self.KEscale)
        try:
            self.BEscale = KE_to_BE(KE,hv,wk)
        except:
            print('BEscale not calculated')
            print(hv,wk)

    def scaleBE(self,wk=None, hv=None):
        """
        sets the scaling of the specificed axis to original BE scaling
        also sets the EDC scaling to the orginal BE scaling
        where BE = hv - KE - wk (above EF BE is negative); KE is orginal KE scaling
            wk=None uses  .wk for the work function (wk ~ hv - KE_FermiLevel)
            hv=None uses  .hv for the photon energy
    
        """
        self._BE_calc()
        BE = self.BEscale

        self.updateAx('x',BE,"Binding Energy (eV)")
        self.EDC.updateAx('x',BE,"Binding Energy (eV)")
    
    def set_wk(self,val):
        """
        updates the work function can be a single value or an array of the same length as KE
        recalucates the binding energy
        """
        self.wk(val)
        self._BE_calc()
    
#==============================================================================
# adjusting angle scaling
#==============================================================================
    
    def scaleAngle(self,delta=0):
        """
        changest the angle scaling of the data and the MDC
        based on the orginal angle scale and angOffset
            newScale = angScale + angOffset + delta;
            delta=(newCoor-oldCoor); can be value or an array of the same length as angScale
        
        """
        angScale=np.array(self.angScale)
        newScale= angScale + self.angOffset + delta
        self.updateAx('y',newScale,"Angle (deg)")
        self.MDC.updateAx('x',newScale,"Angle (deg)")
    
#==============================================================================
# calculating k scaling
#==============================================================================

def kmap_scan_theta(d,hv=None,wk=None):
    '''
    d type: pynData stack (degrees, KE, theta)
    returns pynData (ky, kx, BE)
    '''
    KE = d.scale['x']
    thetaY = d.scale['y']
    thetaX = d.scale['z']
    
    org = d.data #data(thetaY, KE, thetaX)
    
    kx_scale, ky_scale = nARPES.kScale(nARPES, KE, thetaY, thetaX)
    
    new = np.zeros((len(ky_scale),len(KE),len(kx_scale)))
    new = interpolate.RegularGridInterpolator((ky_scale,KE,kx_scale),org, method = 'linear')
    
    dnew = nData(new.values.transpose(0,2,1))
    
    BE = KE_to_BE(KE,hv,wk)
    nData.updateAx(dnew,'x',kx_scale,'kx')
    nData.updateAx(dnew,'y',ky_scale,'ky')
    nData.updateAx(dnew,'z',BE,'BE')
    
    return dnew

def kmap_scan_hv(d,wk):
    '''
    d type: pynData stack (degrees, KE, hv)
    returns pynData (ky, BE, hv)
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

def kmapping_boundries_slice(EA, V0=10):
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
        kx_min = theta_to_kx(KE_max,thetaX)
        kx_max = theta_to_kx(KE_max,thetaX)
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

def kmapping_boundries(EA_list):
    """
    EA_list = list of pynData_ARPES objects
    
    """
    for n,EA in enumerate(EA_list):
        if n == 0: 
            KE_min, KE_max, kx_min, kx_max, ky_min, ky_max, kz_min, kz_max = kmapping_boundries_slice(EA)
        #else:
        _KE_min, _KE_max, _kx_min, _kx_max, _ky_min, _ky_max, _kz_min, _kz_max = kmapping_boundries_slice(EA)
        KE_min = min(KE_min, _KE_min)
        KE_max = max(KE_max, _KE_max)
        kx_min = min(kx_min, _kx_min)
        kx_max = max(kx_max, _kx_max) 
        ky_min = min(ky_min, _ky_min)
        ky_max = max(ky_max, _ky_max) 
        kz_min = min(kz_min, _kz_min)
        kz_max = max(kz_max, _kz_max) 
    return KE_min, KE_max, kx_min, kx_max, ky_min, ky_max, kz_min, kz_max

def kmapping_energy_scale(EA,E_unit='BE',**kwargs):
    """
    EA is pynData object
    Eunit = 'BE' / 'KE'
    **kwargs (all can be a float or a np.array of the same length as KEscale)
        hv = photon energy, default is EA.hv
        wk = work function, default is EA.wk
        KE_offset = Kinetic energy offset, default = 0
    
    returns EA image scaling in KE or BE including an offsets
    """
    kwargs.setdefault('hv',EA.hv)
    kwargs.setdefault('wk',EA.wk)
    kwargs.setdefault('KE_offset',0.0)
    
    KE = EA.KEscale+kwargs['KE_offset']
    wk = kwargs['wk']
    hv = kwargs['hv']
    
    if E_unit == 'BE':
        E_scale = KE_to_BE(KE,hv,wk)
    elif E_unit == 'KE':
        E_scale = KE
    else:
        print("Eunit is either 'KE' or 'BE'")
    return E_scale
        

def kmapping_stack(EA_list, E_unit='BE',**kwargs):
    """
    """
    kwargs.setdefault('KE_offset',0.0)
    KE_min, KE_max, kx_min, kx_max, ky_min, ky_max, kz_min, kz_max = kmapping_boundries(EA_list)
    EA = EA_list[0]
    
    #energy BE/KE
    BE_min = KE_to_BE(np.min(EA.KEscale),EA.hv,EA.wk)
    BE_max = max(KE_to_BE(KE_max,EA.hv,EA.wk),KE_to_BE(KE_max,EA.hv,EA.wk))
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
            KE_offset = kwargs['KE_offset'][0]
        img = ARPES_angle_k(k_new,EA.data,EA.KEscale,EA.angScale,EA.thetaX,KE_offset,EA.slitDir)
    
        if EA.slitDir == 'H':
            img_y = kmapping_energy_scale(EA,E_unit='BE',KE_offset=KE_offset)
            img_x = k_new     
        elif EA.slitDir == 'V':
            img_x = kmapping_energy_scale(EA,E_unit='BE',KE_offset=KE_offset)
            img_y = k_new
            
        #now we need to interp image into 3D array
        #print('img:',img.shape,img_y.shape, img_x.shape)
        #print('data_new:',data_new.shape,data_yy.shape,data_xx.shape)

        img_xx,img_yy = np.meshgrid(img_x,img_y)
        data_new[:,:,n] = interpolate.griddata((np.ravel(img_xx),np.ravel(img_yy)),np.ravel(img),(data_xx,data_yy),fill_value=np.nan,rescale=True)
            
    return data_new, E_new, k_new
        
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