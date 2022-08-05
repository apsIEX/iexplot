    def EAspectra(self,scanNum, EAnum=1, BE=False):
        """
        returns the array for an EAspectra, and x and y scaling
            
        usage:
            plt.imgshow(data.EAspectra))
            
        """
        EA = self.mda[scanNum].EA[EAnum]
        img = EA.data
        x = EA.scale['x']
        y = EA.scale['y']
        
        if BE:
            hv=EA.hv
            if wk == None:
                if EA.wk == None:
                    wk=0
                else:
                    wk=EA.wk
            x=hv-wk-x
            
        return img, x,y
        
    def EAspectraEDC(self,scanNum, EAnum=1, BE=False):
        """
        returns x,y energy scaling, EDC spectra
            
        usage:
            plt.plot(data.EAspectraEDC(151))
            
        """
        EA = self.mda[scanNum].EA[EAnum]
        x = EA.EDC.scale['x']
        y = EA.EDC.data
        
        if BE:
            hv=EA.hv
            if wk == None:
                if EA.wk == None:
                    wk=0
                else:
                    wk=EA.wk
            x=hv-wk-x
        
        return x,y
        
    def plotEDC(self,scanNum, EAnum=1,**kwargs):
        """
        simple plotting for EDC

        EAnum = sweep number (default = 1)
              = inf => will sum all spectra
        if
            dtype="EA"  => y=data.EA[scanNum]
            dtype="mdaEA" or "mdaAD"  => y=data.mda[scanNum]EA[EAnum]
        BE = False uses KE scale
        BE = True use BE=hv-KE-wk
        if wk=None uses metadata
        
        *kwargs are the matplot lib kwargs plus the following
            BE: True/False for Binding Energy or Kinetic Energy scale (default = False (KE))
            wk: None/value, if None uses the value from the metadata
            ##### additional plotting
            Norm2One: True/False to normalize spectra between zero and one
            offset: y += offset 
            scale: y *= scale
            offset_x: x += offset_x 
            scale_x: x *= scale_x
        """
        kwargs.setdefault("BE",False)
        kwargs.setdefault("wk",None)
        
        kwargs.setdefault("Norm2One",False)
        kwargs.setdefault("offset",0)
        kwargs.setdefault("scale",1)
        kwargs.setdefault("offset_x",0)
        kwargs.setdefault("scale_x",1)
        
        x=0;y=0            
        
        if self.dtype == "EA":
            d=self.EA[scanNum]
            y=d.EDC.data
            x=d.EDC.scale['x']

        elif self.dtype == "mdaEA" or "mdaAD":
            if EAnum == inf:
                EAlist = list(self.mda[scanNum].EA.keys()) 
            else:
                EAlist = [EAnum]

            for EAnum in EAlist:
                d=self.mda[scanNum].EA[EAnum]
                y=d.EDC.data
                x=d.EDC.scale['x']
 
        BE=kwargs["BE"]
        wk=kwargs["wk"]
        if BE:
            hv=d.hv
            if wk == None:
                if d.wk == None:
                    wk=0
                else:
                    wk=d.wk
            x=hv-wk-x
        
        for key in ["BE","wk"]:
            del kwargs[key]
        
        self._plot1D(x,y,**kwargs)
        
        if BE:
            plt.xlim(max(x),min(x))
    
    def plotEA(self,scanNum,EAnum=1,Escale="KE",transpose=False,**kwargs):
        """
        simple plotting for EDC
        if
            dtype="EA"  => y=data.EA[scanNum]
            dtype="mdaEA" or "mdaAD"  => y=data.mda[scanNum]EA[EAnum]
        kwargs: are pcolormesh kwargs e.g cmap, vmin, vmax
        
        """  
        kwargs.setdefault('shading','auto')

        if self.dtype == "EA":
            EA=self.EA[EAnum]

        elif self.dtype == "mdaEA" or "mdaAD":
            EA=self.mda[scanNum].EA[EAnum]

        #wk=0 if type(self.EA[EAnum].wk)==None else self.EA[EAnum].wk
        #hv=EA.hv           
        img=EA.data
        xscale=EA.scale['x']
        #if Escale=="BE":
        #    xscale=hv-wk-xscale
        yscale=EA.scale['y']
        xunit=EA.unit['x']
        yunit=EA.unit['y']

        if transpose == True:
            plt.pcolormesh(yscale, xscale, img.T, **kwargs)
            plt.xlabel(yunit)
            plt.ylabel(xunit)
        else:
            plt.pcolormesh(xscale, yscale, img, **kwargs)
            plt.xlabel(xunit)
            plt.ylabel(yunit)
 
      
  
        

        
  

    def stackmdaEA(self,mdaScanNum,**kwargs):
        """
        makes an ImageTool.RegularArray of EA files in a single mda scan
        mdaScanNum = the scanNum corresponding to the mda scan
        **kwargs:
            subset=(start,stop,countby); default = (1,inf,1)
            EDConly=False; default = False full image
                   = True, EDCs are stacked
        """
        kwargs.setdefault("subset",(1,inf,1))
        kwargs.setdefault("EDConly",False)
        kwargs.setdefault("debug",False)
              
        ra=None
        MDAscan=self.mda[mdaScanNum]
        rank=MDAscan.header.all['rank']
        shortlist=_shortlist(*kwargs['subset'],llist=list(MDAscan.EA.keys()),**kwargs)
        first=shortlist[0]
        Escale=MDAscan.EA[first].scale['x']
        Eunit=MDAscan.EA[first].unit['x']
        Ascale=MDAscan.EA[first].scale['y']
        Aunit=MDAscan.EA[first].unit['y']
        
        if kwargs['EDConly']:
            if rank ==1:
                print("Don't know if ImageTool can deal with 1D data")
            elif rank > 1:
                ROstack=np.vstack(tuple(MDAscan.EA[key].EDC.data for key in shortlist)) 
                stack=np.swapaxes(ROstack,1,0)
                Mscale=MDAscan.posy[0].data[0:list(MDAscan.EA.keys())[-1]]
                Munit=MDAscan.posy[0].pv[1]
                if pd.Series(Mscale).is_unique:
                    if pd.Series(Mscale).is_monotonic_decreasing:
                        Mscale=np.flip(Mscale,0)
                        stack=np.flip(stack,1)
                else: 
                    Mscale=np.arange(0,len(list(MDAscan.EA.keys())))
                ra=RegularDataArray(stack,axes=[Escale,Mscale],dims=[Eunit,Munit])
        else:
            print(Aunit,Eunit)
            if rank == 1:
                stack=MDAscan.EA[shortlist[0]].data
                ra=RegularDataArray(stack,axes=[Ascale,Escale],dims=[Aunit,Eunit])
            elif rank > 1:
                stack=np.dstack(tuple(MDAscan.EA[key].data for key in shortlist))   
                Mscale=MDAscan.posy[0].data[0:list(MDAscan.EA.keys())[-1]]
                Munit=MDAscan.posy[0].pv[1]

                if pd.Series(Mscale).is_unique:
                    if pd.Series(Mscale).is_monotonic_decreasing:
                        Mscale=np.flip(Mscale,0)
                        stack=np.flip(stack,2)
                else: 
                    Mscale=np.arange(0,len(list(MDAscan.EA.keys())))
                ra=RegularDataArray(stack,axes=[Ascale,Escale,Mscale],dims=["angle","energy",Munit])
        return ra 
    
    def stackmdaEA_multi(self,*mdaScanNum,**kwargs):
            """
            makes an ImageTool.RegularArray of multiple mdaEA scans
            *mdaScanNum = first,last,countby or list
            **kwargs:
                EDConly = False (default); stack of full images
                        = True; stack of EDCs 
                EAnum = 1; which EA scan number to use 
                stackScale = None (default); uses the mdaScanNums
                           = (start, delta, units) to specifiy you own
            """
            kwargs.setdefault("EDConly",False)
            kwargs.setdefault("EAnum",1)
            kwargs.setdefault("stackScale",None)
            kwargs.setdefault("debug",False)

            ra=None
            shortlist=_shortlist(*mdaScanNum,llist=list(self.mda.keys()),**kwargs)
            first=shortlist[0]           
            EAnum=kwargs["EAnum"]

            Escale=self.mda[first].EA[kwargs['EAnum']].scale['x']
            Eunit=self.mda[first].EA[kwargs['EAnum']].unit['x']
            Ascale=self.mda[first].EA[kwargs['EAnum']].scale['y']
            Aunit=self.mda[first].EA[kwargs['EAnum']].unit['y']
            if kwargs['stackScale'] == None:
                Mscale=np.array(shortlist) 
                Munit="scanNum"
            else:
                Mscale=np.arange(kwargs['stackScale'][0],kwargs['stackScale'][0]+len(shortlist)*kwargs['stackScale'][1], kwargs['stackScale'][1])
                Munit=kwargs['stackScale'][2]

            if kwargs['EDConly']:       
                ROstack=np.vstack(tuple(self.mda[key].EA[EAnum].EDC.data for key in shortlist)) 
                stack=np.swapaxes(ROstack,1,0)


                if pd.Series(Mscale).is_unique:
                    if pd.Series(Mscale).is_monotonic_decreasing:
                        Mscale=np.flip(Mscale,0)
                        stack=np.flip(stack,1)
                ra=RegularDataArray(stack,axes=[Escale,Mscale],dims=[Eunit,Munit])

            else:
                print(Aunit,Eunit)
                if len(shortlist) == 1:
                    self.mda[shortlist[0]].EA[EAnum].data
                    ra=RegularDataArray(stack,axes=[Ascale,Escale],dims=[Aunit,Eunit])
                elif len(shortlist):
                    try:
                        stack=np.dstack(tuple(self.mda[key].EA[EAnum].data for key in shortlist))   
                    except:
                        print(self.mda.keys())

                    if pd.Series(Mscale).is_unique:
                        if pd.Series(Mscale).is_monotonic_decreasing:
                            Mscale=np.flip(Mscale,0)
                            stack=np.flip(stack,2)
                    else: 
                        Mscale=np.arange(0,len(list(self.mda[shortlist[0]].EA.keys())))

            if len(stack.shape) == 2:
                ra=RegularDataArray(stack,axes=[Escale,Mscale],dims=["energy",Munit])
            else:
                ra=RegularDataArray(stack,axes=[Ascale,Escale,Mscale],dims=["angle","energy",Munit])
            return ra

    def stack_EAmesh(self,scanNum,**kwargs):
        """
        return a 3D regular array with the EA scans stack
        usage:
            ra = data.stack_EAmesh(scanNum)
            plot_ra(ra) => works in Jupyter or Terminal
            it = ImageTool(ra); it.show() => Terminal only
            
        **kwargs:
            subset=(start,stop,countby); default = (1,inf,1)
            EDConly = True:  3D position dependent EDC
                    = False (default): EA spectra stacked vs scanNum
        """
        kwargs.setdefault("subset",(1,inf,1))
        kwargs.setdefault("EDConly",False)
        kwargs.setdefault("debug",False)
        kwargs.setdefault('shading','auto')
        
        ra=None
        MDAscan=self.mda[scanNum]    
        shortlist=_shortlist(*kwargs['subset'],llist=list(MDAscan.EA.keys()),**kwargs)
        
        first=shortlist[0]
        xscale=MDAscan.posy[0].data[0,:]
        xunit=MDAscan.posy[0].pv[1] if len(MDAscan.posy[0].pv[1])>0 else MDAscan.posy[0].pv[0] 
        yscale=MDAscan.posz[0].data[:]
        yunit=MDAscan.posz[0].pv[1] if len(MDAscan.posz[0].pv[1])>0 else MDAscan.posz[0].pv[0]    
        Escale=MDAscan.EA[first].scale['x']
        Eunit=MDAscan.EA[first].unit['x']
        Ascale=MDAscan.EA[first].scale['y']
        Aunit=MDAscan.EA[first].unit['y']
            
        if kwargs['EDConly']: #
            stack=np.stack(tuple(MDAscan.EA[key].EDC.data for key in shortlist))
            #stack = stack.reshape(xscale.shape[0],yscale.shape[0],Escale.shape[0])
            #ra=RegularDataArray(stack,axes=[xscale,yscale,Escale],dims=[xunit,yunit,Eunit])
            stack = stack.reshape(yscale.shape[0],xscale.shape[0],Escale.shape[0])
            ra=RegularDataArray(stack,axes=[yscale,xscale,Escale],dims=[yunit,xunit,Eunit])
        else:
            Mscale = shortlist
            Munit = 'scanNum'
            stack=np.dstack(tuple(MDAscan.EA[key].data for key in shortlist))
            ra=RegularDataArray(stack,axes=[Ascale,Escale,Mscale],dims=["angle","energy",Munit])
        return ra
    