
import matplotlib.pyplot as plt

from iexplot.plotting import *
from iexplot.pynData.pynData_plot import plot_nd, plot_nd_avg

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
        """
        nd = self.mda[scanNum].MCA
        plot_nd_avg(nd,ax='y',Cen=np.nan,WidthPix=np.nan)
        
    def mca_spectra(self,scanNum):
        return self.mda[scanNum].MCA.data