
import matplotlib.pyplot as plt

from iexplot.plotting import *
from iexplot.pynData import  nData

from iexplot.pynData.pynData_plot import plot_nd, nd_avg

from iexplot.utilities import  take_closest_value


class Plot_MCA:
    def __init__(self):
        pass
    
    def plot_mca(self,scanNum,**kwargs):
        """
        plots mca data as image associated with an mda scan
        scanNum is mda scanNum
        """
        nd = self.mda[scanNum].MCA
        plot_nd(nd,**kwargs)

    def plot_mca_avg(self,scanNum,ax='y',Cen=np.nan,WidthPix=np.nan,**kwargs):
        """
        scanNum is mda scanNum
        bins 2D data in ax, with Center, and WidthPix 
        if Center=np.nan then center is the midpoint
        if WidthPix=np.nan then whole image is binned 

        **kwargs, normal plot_1D +
            Norm2Edge: True/False to normalize XAS (1D only)
   
        """
        nd = self.mda[scanNum].MCA
        avg = nd_avg(d,ax='y',Cen=np.nan,WidthPix=np.nan,**kwargs)
        x = avg.scale['x']
        y = avg.data

        if 'Norm2Edge'  in kwargs:
            if kwargs['Norm2Edge']:
                plot_Norm2Edge(x,y,**kwargs)
        else:
            plot_1D(x,y,**kwargs)       
        
    def mca_spectra(self,scanNum):
        return self.mda[scanNum].MCA.data
    

    def scale_mca(self,scanNum):
        """
        scales MCA image
        """
        y_scale = self.mda_positioner(scanNum)
        y_unit = self.mda_positioner_label(scanNum)
        mca = self.mda[scanNum].MCA
        #energy = (channel - 12.8)/0.72
        x_scale = np.arange(0,mca.data.shape[1],1)
        x_scale = (x_scale - 12.8)/0.72
        x_unit = 'Emission Energy (eV)'
        
        if type(mca) == nData:
            mca.updateAx('x', x_scale, x_unit)
            mca.updateAx('y', y_scale, y_unit)
            
    def mca_1D(self,scanNum,center,delta):
        """
        Averages the MCA spectra over the range center-delta:center+delta
        where center and delta are in eV
        returns x,y
        """
        x = self.mda_positioner(scanNum)
        em_scale = self.mda[scanNum].MCA.scale['x']
        i0 = np.where(em_scale==take_closest_value(em_scale,center-delta))[0][0]
        i1 = np.where(em_scale==take_closest_value(em_scale,center+delta))[0][0]

        y = np.average(self.mda[scanNum].MCA.data[:,i0:i1],1)
  
        
        return x,y    

    def mca_1D_hv(self,scanNum,hv):
        """
        The emission spectra for a fixed hv
        """
        hv_scale = self.mda_positioner(scanNum)
        x = self.mda[scanNum].MCA.scale['x']

        i = np.where(hv_scale==take_closest_value(hv_scale,hv))[0][0]

        y = self.mda[scanNum].MCA.data[i,:]

        return x,y  