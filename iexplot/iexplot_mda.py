def mda_plotting(self,**kwargs):
    setattr(self,'mdaPos',mdaPos(scanNum,posNum=0))
#########################################################################
    def mdaPos(self,scanNum, posNum=0):
        """
        returns the array for a positioner
                        
        usage for 1D data:
        x = mdaPos(305)
        y = mdaDet(305,16)
        
        plt.plot(x,y)
        """
        return self.mda[scanNum].posx[posNum].data
 
    def mdaPos_label(self,scanNum, posNum=0):
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

        return self.mda[scanNum].posx[posNum].pv[1] if len(self.mda[scanNum].posx[posNum].pv[1])>1 else self.mda[scanNum].posx[posNum].pv[0]

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

    
        
    
    def plotmda(self,scanNum, detNum, posNum=0,**kwargs):
        """
        simple plot for an mda scans either 1D or a row/column of a 2D data set
        detector vs positioner
  
        **kwargs
             Norm2One: True/False to normalize spectra between zero and one (default => False)
             offset: y += offset 
             scale: y *= scale
             offset_x: x += offset_x 
             scale_x: x *= scale_x
             
             2D data: plots image by default
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
        
        y=self.mdaDet(scanNum, detNum)
        kwargs['ylabel']=self.mdaDet_label(scanNum, detNum)
        
        x=self.mdaPos(scanNum, posNum)
        kwargs['xlabel']=self.mdaPos_label(scanNum, posNum)
        if len(y.shape)==2:
            if "row" not in kwargs and "column" not in kwargs:
                if kwargs['Norm2One']:
                    print('Norm2One not currently implemented in 2D data, adjust vmin,vmax')
                    del kwargs['Norm2One']
            self.plotmda2D(scanNum, detNum, **kwargs)
                
        else:
            x,y,kwargs=self._reduce2d(x,y, **kwargs)
            self._plot1D(x,y,**kwargs)
    
    def plotmda_detVdet(self,scanNum, y_detNum, x_detNum, **kwargs):
        """
        simple plotting for an mda scan
        detector vs detector
                
        Norm2One: True/False to normalize spectra between zero and one

        **kwargs
             Norm2One: True/False to normalize spectra between zero and one (default => False)
             offset: y += offset 
             scale: y *= scale
             offset_x: x += offset_x 
             scale_x: x *= scale_x
             
             2D data: plots image by default
                row = index for plotting a single row from a 2D data set
                column = index for plotting a single row from a 2D data set
             
            and standard plt.plot **kwargs
            e.g. label=str(scanNum), marker="o"
        """
        kwargs.setdefault("offset",0)
        kwargs.setdefault("scale",1)
        kwargs.setdefault("offset_x",0)
        kwargs.setdefault("scale_x",1)
        
        y=self.mdaDet(scanNum, y_detNum)
        kwargs['ylabel']=self.mdaDet_label(scanNum, y_detNum)
        
        x=self.mdaDet(scanNum, x_detNum)
        kwargs['xlabel']=self.mdaDet_label(scanNum, x_detNum)
        
        if len(y.shape)==2:
            if "row" not in kwargs and "column" not in kwargs:
                if kwargs['Norm2One']:
                    print('Norm2One not currently implemented in 2D data, adjust vmin,vmax')
                    del kwargs['Norm2One']
            self.plotmda2D(scanNum, y_detNum, **kwargs)
                
        else:     
            x,y,kwargs=self._reduce2d(x,y, **kwargs)
            self._plot1D(x,y,**kwargs)
            
    def plotmda2D(self, scanNum, detNum, **plotkwargs):
        """
        plots 2D mda data
        **plotkwargs are the standard matplotlib argument
            cmap
        """
        niceplot(self.mda[scanNum].det[detNum], **plotkwargs)

    def plot_mesh(self,scanNum,**kwargs):
        """
        kwargs:
            det_list => list of detectors to plot 
                    = [16,17] (default)
            title_list => list of titles for each detector
                    = ['TEY','EA'] (default)
        
        """
        kwargs.setdefault('det_list',[16,17])
        kwargs.setdefault('title_list',['TEY','EA'])
        
        plt.figure(figsize=(10,3))
        n=len(kwargs['det_list'])
        for i, det_num in enumerate(kwargs['det_list']):
            plt.subplot(1,n,i+1)
            plt.title(kwargs['title_list'][i])
            self.plotmda(scanNum,kwargs['det_list'][i],**kwargs)
            plt.colorbar()
        
        kwargs.pop('det_list') 
        kwargs.pop('title_list')
            
        plt.show()

    def plot_EAmesh_mda(self,scanNum,detNum,**kwargs):
        """
        plot the scalar values for an scanEAmesh 

        can be used in subplots (i.e. no plt.show)
        """
        kwargs.setdefault('shading','auto')
        MDAscan=self.mda[scanNum]     
        xscale=MDAscan.posy[0].data[0,:]
        xunit=MDAscan.posy[0].pv[1] if len(MDAscan.posy[0].pv[1])>0 else MDAscan.posy[0].pv[0] 
        yscale=MDAscan.posz[0].data[:]
        yunit=MDAscan.posz[0].pv[1] if len(MDAscan.posz[0].pv[1])>0 else MDAscan.posz[0].pv[0] 
        img = MDAscan.det[detNum].data[:,:,0]
        
        plt.pcolormesh(xscale, yscale, img, **kwargs)
        plt.xlabel(xunit)
        plt.ylabel(yunit)