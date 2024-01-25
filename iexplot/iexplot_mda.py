
import matplotlib.pyplot as plt

from iexplot.utilities import _shortlist
from iexplot.plotting import *
from iexplot.pynData.pynData import nstack

class PlotMDA:
    """
    adds mda plotting functions to IEXnData class
    """    
    def __init__(self):
        pass
    
    def mdaPos(self,scanNum,**kwargs):
        """
        returns the array for a positioner

        **kwargs
            posNum=1 (default)
            ax='x' (default)

        usage for 1D data:
        x = mdaPos(305)
        y = mdaDet(305,16)
        
        plt.plot(x,y)
        """
        kwargs.setdefault('posNum',0)
        kwargs.setdefault('ax','x')

        posNum = kwargs['posNum']
        ax = kwargs['ax']

        if ax == 'x':
            return self.mda[scanNum].posx[posNum].data
        if ax == 'y':
            return self.mda[scanNum].posy[posNum].data
        if ax == 'z':
            return self.mda[scanNum].posz[posNum].data

    def mdaPos_label(self,scanNum,**kwargs):
        """
        returns the array for a positioner

        **kwargs
            posNum=1 (default)
            ax='x' (default)   

        usage for 1D data:
        x = mdaPos(305)
        xlabel = mdaPos_label(305)
        
        y = mdaDet(305,16)
        ylabel = mdaDet_label(305,16)
        
        plt.plot(x,y)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        """
        kwargs.setdefault('posNum',0)
        kwargs.setdefault('ax','x')

        posNum = kwargs['posNum']
        ax = kwargs['ax']
        
        if ax == 'x':
            return self.mda[scanNum].posx[posNum].pv[1] if len(self.mda[scanNum].posx[posNum].pv[1])>1 else self.mda[scanNum].posx[posNum].pv[0]
        elif ax == 'y':
            return self.mda[scanNum].posy[posNum].pv[1] if len(self.mda[scanNum].posy[posNum].pv[1])>1 else self.mda[scanNum].posy[posNum].pv[0]
        elif ax == 'z':
            return self.mda[scanNum].posz[posNum].pv[1] if len(self.mda[scanNum].posz[posNum].pv[1])>1 else self.mda[scanNum].posz[posNum].pv[0]

    def mdaDet(self,scanNum, detNum):
        """
        returns the array for a positioner and positioner pv/desc.
                        
        usage for 1D data:
        x = mdaPos(305)
        y = mdaDet(305,16)
        
        """
        return self.mda[scanNum].det[detNum].data

    def mdaDet_label(self,scanNum, detNum):
        """
        returns the array for a positioner
                        
        usage for 1D data:
        x = mdaPos(305)
        xlabel = mdaPos_label(305)
        
        y = mdaDet(305,16)
        ylabel = mdaDet_label(305,16)
        
        plt.plot(x,y)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        """

        return self.mda[scanNum].det[detNum].pv[1] if len(self.mda[scanNum].det[detNum].pv[1])>1 else self.mda[scanNum].det[detNum].pv[0]

        
    def plotmda(self,scanNum,detNum,**kwargs):
        """
        simple plot for an mda scans either 1D or a row/column of a 2D data set
            
        **kwargs
            data kwargs:
                1D: detector vs x-positioner (num = 1; default)
                    posx_Num => to plot verses a different x-positioner number
                    y_detNum => to plot verses a detector

                2D: detector vs positioner1 for both x and y (default)
                    posx_Num => to plot verses a different x-positioner number
                    posy_Num => to plot verses a different y-positioner number
                    x_detNum => x-scale is a detector
                    y_detNum => y-scale is a detector


            plotting kwargs:
                Norm2One: True/False to normalize spectra between zero and one (default => False)
                offset: y += offset 
                scale: y *= scale
                offset_x: x += offset_x 
                scale_x: x *= scale_x
                
            for 2D data: plots image by default
                row = index for plotting a single row from a 2D data set
                column = index for plotting a single row from a 2D data set
                
            and standard plt.plot **kwargs
            e.g. label=str(scanNum), marker="o"
        """
        kwargs.setdefault("offset",0)
        kwargs.setdefault("scale",1)
        kwargs.setdefault("offset_x",0)
        kwargs.setdefault("scale_x",1)
        kwargs.setdefault('Norm2One',False)
        
        d = self.mdaDet(scanNum, detNum)
        
        #2D data
        if len(d.shape)==2:
            #image
            if "row" not in kwargs and "column" not in kwargs:
                if kwargs['Norm2One']:
                    print('Norm2One not currently implemented in 2D data, adjust vmin,vmax')
                    del kwargs['Norm2One']
                #remove any keys not associated with pcolormesh    
                for key in ['offset','scale','offset_x','scale_x','Norm2One']:
                    kwargs.pop(key)
                self.plotmda2D(scanNum, detNum, **kwargs)        
        #1D data
        else:
            self.plotmda1D(scanNum, detNum, **kwargs)
        

    def plotmda1D(self,scanNum, detNum, **kwargs):
        """
        plots 1D mda data
        detNum = detector number for the image data
        
        **kwargs: 
            posx_Num => to plot verses a different x-positioner number
            x_detNum => x-scale is a detector

            row => for the nth row of a 2D array
            column => or the nth column of a 2D array
        """ 
        #x-axis
        if 'x_detNum' in kwargs:
            x = self.mdaDet(scanNum,detNum=kwargs['x_detNum'])
            xunit = self.mdaDet_label(scanNum,detNum=kwargs['x_detNum'])
            del kwargs['x_detNum']
        elif 'posx_Num' in kwargs:
            x = self.mdaPos(scanNum,posNum=kwargs['posx_Num'],ax='x')
            xunit = self.mdaPos_label(scanNum,posNum=kwargs['posx_Num'],ax='x')
            del kwargs['posx_Num']
        else:
            x = self.mdaPos(scanNum,posNum=0,ax='x')
            xunit = self.mdaPos_label(scanNum,posNum=0,ax='x')

        #data
        y = self.mdaDet(scanNum,detNum)

        if len(y.shape)>1:
            if 'row' in kwargs or 'column' in kwargs:
                x,y,kwargs = reduce2d(x,y, **kwargs)

        plot_1D(x,y,**kwargs)
        plt.xlabel(xunit)


    def plotmda2D(self, scanNum, detNum, **kwargs):
        """
        plots 2D mda data
        detNum = detector number for the image data
        
        **kwargs: 
            posx_Num => to plot verses a different x-positioner number
            posy_Num => to plot verses a different y-positioner number
            x_detNum => x-scale is a detector
            y_detNum => y-scale is a detector     
        """
        img = self.mdaDet(scanNum, detNum)
        
        #x-scaling
        if 'x_detNum' in kwargs:
            xscale = self.mdaDet(scanNum,detNum=kwargs['x_detNum'],ax='x')
            xunit = self.mdaDet_label(scanNum,detNum=kwargs['x_detNum'],ax='x')
            del kwargs['x_detNum']
        elif 'posx_Num' in kwargs:
            xscale = self.mdaPos(scanNum,posNum=kwargs['posx_Num'],ax='x')
            xunit = self.mdaPos_label(scanNum,posNum=kwargs['posx_Num'],ax='x')
            del kwargs['posx_Num']
        else:
            xscale = self.mdaPos(scanNum,posNum=0,ax='x')
            xunit = self.mdaPos_label(scanNum,posNum=0,ax='x')
        
        #y-scaling
        if 'y_detNum' in kwargs:
            yscale = self.mdaDet(scanNum,detNum=kwargs['y_detNum'],ax='y')
            yunit = self.mdaDet_label(scanNum,detNum=kwargs['y_detNum'],ax='y')
            del kwargs['y_detNum']
        elif 'posy_Num' in kwargs:
            yscale = self.mdaPos(scanNum,posNum=kwargs['posy_Num'],ax='y')
            yunit = self.mdaPos_label(scanNum,posNum=kwargs['posy_Num'],ax='y')
            del kwargs['posy_Num']
        else:
            yscale = self.mdaPos(scanNum,posNum=0,ax='y')
            yunit = self.mdaPos_label(scanNum,posNum=0,ax='y')
        
        scales = [yscale,xscale]
        units = [yunit,xunit]    
        plot_2D(img,scales,units,**kwargs)
        

    def plot_sample_map(self,scanNum,**kwargs):
        """
        plots the relavent detectors for a sample map with an aspect ration of 1
        kwargs:
            det_list => list of detectors to plot 
            title_list => list of titles for each detector
            figsize => figure size; use to make figure bigger so scales don't overlap (H,V)
                        
            defaults:
            if prefix = 'ARPES_'
                    det_list = [16,17] 
                    title_list = ['TEY','EA'] 

            if prefix = 'Kappa_'
                    det_list = [31,34] 
                    title_list = ['TEY','D4'] 
        """
        if self.prefix == 'ARPES_':
            kwargs.setdefault('det_list',[16,17])
            kwargs.setdefault('title_list',['TEY','EA'])
            
        
        if self.prefix == 'Kappa_':
            kwargs.setdefault('det_list',[31,34])
            kwargs.setdefault('title_list',['TEY','D4'])
        
        det_list = kwargs['det_list']
        kwargs.pop('det_list')

        title_list = kwargs['title_list']
        kwargs.pop('title_list')

        kwargs.setdefault('aspect_ratio',1)
        aspect_ratio = kwargs['aspect_ratio']
        kwargs.pop('aspect_ratio')

        n=len('det_list')
        if 'figsize' in kwargs:
            fig = plt.figure(figsize=kwargs['figsize'])
            kwargs.pop('figsize')
        else:
            fig = plt.figure()

        for i, det_num in enumerate(det_list):
            ax = fig.add_subplot(1,n,i+1)
            ax.set_title(title_list[i])
            ax.set_aspect(aspect_ratio)
            self.plotmda(scanNum,det_list[i],**kwargs)
            plt.colorbar()
        

    
    def header(self,scanNum):
        """
        returns a dictionary with all the adder info from the mda scan
    
        """
        d = self.mda[scanNum].header.data.mda[19].header.ScanRecord
        return d