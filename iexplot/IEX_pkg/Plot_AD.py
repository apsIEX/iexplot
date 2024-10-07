

import matplotlib.pyplot as plt
import numpy as np
from iexplot.utilities import _shortlist, _make_num_list 
from iexplot.plotting import plot_1D, plot_2D, plot_3D
from iexplot.pynData.pynData import nstack

class Plot_AD():
    """
    adds ADtiff plotting methods to IEXnData class
    """
    
    def __init__(self):
        pass

    def ADmda_array(self,scanNum, ADnum=1):
        """
        returns the array for the Tiff file 
        """
        return self.mda[scanNum].AD[ADnum].data
    
    def ADmda_scale(self,ax,scanNum,ADnum=1):
        """
        ax = 'x','y'...
        """
        return self.mda[scanNum].AD[ADnum].scale[ax]
        
    def ADmda_label(self,ax,scanNum,ADnum=1):
        """
        ax = 'x','y'...
        """
        return self.mda[scanNum].AD[ADnum].unit[ax]
    
    def plot_ADmda(self,scanNum,ADnum=1,**kwargs):
        """
        uses imshow to plot AD data
        ** kwargs are imshow kwargs
        """
        img = self.ADmda_array(scanNum, ADnum)
        plt.imshow(img)
        plt.xlabel(self.ADmda_label('x',scanNum,ADnum))
        plt.ylabel(self.ADmda_label('y',scanNum,ADnum))
    
    def AD_array(self,ADnum):
        return self.AD[ADnum].data
    

    def AD_scale(self,ax,ADnum):
        """
        ax = 'x','y'...
        """
        return self.AD[ADnum].scale[ax]
        
    def AD_label(self,ax,ADnum):
        """
        ax = 'x','y'...
        """
        return self.AD[ADnum].unit[ax]
    
    def plot_AD(self,ADnum,**kwargs):
        """
        uses imshow to plot AD data
        ** kwargs are imshow kwargs
        """
        img = self.AD_array(ADnum)
        plt.imshow(img)
        plt.xlabel(self.AD_label('x',ADnum))
        plt.ylabel(self.AD_label('y',ADnum))
