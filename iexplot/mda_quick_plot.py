

from os import listdir
from os.path import join, isfile, dirname

### Data analysis:
from scipy.optimize import curve_fit
from scipy.special import erfc
import numpy.polynomial.polynomial as poly
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from math import *

try:
    from netCDF4 import Dataset
except:
    print('netCDF4 not loaded')

##### APS / 29ID-IEX:
from iexplot.fitting import fit_gaussian, fit_lorentzian,fit_box,fit_step,fit_poly
from iexplot.mda import readMDA,scanDim
try:
    import iexcode.instruments.cfg as iex
    from iexcode.instruments.scanRecord import last_mda,mda_filepath,mda_prefix
    from iexcode.instruments.AD_utilities import AD_filepath,AD_prefix
    from iexcode.instruments.AUX100_diode import current2flux   
except:
    print('iexcode not install. You will need to specify path and prefix')


##############################################################################################################
##############################                  Plot Tiff,JPEG,PNG               ##############################
##############################################################################################################
def plot_image(fpath,h=20,v=10,**kwargs):
    """
    fpath = full path to image file
          = '/home/beams/29IDUSER/Documents/User_Folders/UserName/TifFile.tif'
    
    ** kwargs are imshow kwargs:
        cmap = colormap; examples => 'gray','BuPu','Inferno'
        vmin,vmax, adjust max and min of colormap
    """
    
    image = mpimg.imread(fpath)
    plt.figure(figsize=(h,v))
    plt.imshow(image,**kwargs)
    plt.axis('off')
    plt.show()
    

def plot_images(fpath_1,fpath_2,h=20,v=10):
    """
    fpath = the full path to the image file
    filepath = '/home/beams/29IDUSER/Documents/User_Folders/UserName/TifFile.tif'
    """
    print(fpath_1)
    print(fpath_2)
    image1 = mpimg.imread(fpath_1)
    image2 = mpimg.imread(fpath_2)
    plt.figure(figsize=(h,v))
    plt.subplot(1,2,1), plt.imshow(image1,cmap='gray')
    plt.axis('off')
    plt.subplot(1,2,2), plt.imshow(image2,cmap='gray')
    plt.axis('off')
    plt.tight_layout()
    plt.show()




###############################################################################################
####################################         PLOT MDA        ###################################
###############################################################################################
def plot_mda(*ScanDet,**kwArg):

    """
    Plot mda scans: *ScanDet = (scan,det,scan,det...),(scan,det,scan,det...),title=(subplot_title1,subplot_title2)
                             =            subplot1,                subplot2
    Optional data analysis keywords arguments:
        Flux conversion (for diode only): flux= 3(D## for mono rbv, typically 3).
        Norm option: norm = 'yes' normalizes all the scans to 1 (default: None)
        NormDet = 1 for SR current, 14  for Mesh (D-branch); Normalize by the mesh does not work with norm='yes'
        DivScan = ?
    Optional graphical keywords arguments:
        sizeH = 1,1.5,... increase horizontal figure size
        sizeV = 1,1.5,... increase vertical figure size
        marker = 'x','+','o','v','^','D',...    (default:None)
        markersize = 1,2,3,...        (default: 5)
        linewidth = 0.5,1,2...         (default: 1)
        linestyle = '-','--','-.',':'     (default: solid '-')
        color = 'r','b','m','c','g','y'...    (default: jupyter colors series)
        legend = 'best',Supper left', 'lower right'...        (default: None)
        log = 'log'   (default: None = linear)
        xrange = [x1,x2]   (default: None = Autoscale)
        yrange = [y1,y2]   (default: None = Autoscale)
        xlabel = 'mxLabel'        (default: pv name)
        ylabel = 'myLabel'        (default: pv name)
        ytickstyle = 'sci' for y axes    (default: 'plain')
        xtickstyle = 'sci' for y axes    (default: 'plain')
    filepath: by default plot scans for the current data folder (as defined in BL_ioc() ScanRecord SaveData)
    or specified folder path:
        e.g. user : filepath='/net/s29data/export/data_29idc/2018_2/UserName/mda/'
        e.g. staff: filepath='/net/s29data/export/data_29idb/2018_2/mda/'
    prefix: by default, uses prefix as defined in ScanRecord ("mda_")
    scanIOC: by default, uses the IOC for the current branch as define in BL_IOC()
    """
    kwArg.setdefault('marker',None)
    kwArg.setdefault('markersize',5)
    kwArg.setdefault('linewidth',1)
    kwArg.setdefault('linestyle','-')    
    kwArg.setdefault('color',None)
    kwArg.setdefault('nticks',None)
    kwArg.setdefault('sizeH',1)
    kwArg.setdefault('sizeV',1)  
    kwArg.setdefault('title','')
    kwArg.setdefault('filepath',None)
    kwArg.setdefault('prefix',None)
    kwArg.setdefault('norm',None)     
    kwArg.setdefault('flux',None)
    kwArg.setdefault('NormDet',None)
    kwArg.setdefault('scanIOC',None)
    kwArg.setdefault('legend',None)     
    kwArg.setdefault('vs_index',None)
    kwArg.setdefault('vs_det',None)
    kwArg.setdefault('save',True)
    
    mkr=kwArg['marker']
    ms=kwArg['markersize']
    lw=kwArg['linewidth']
    ls=kwArg['linestyle']
    c=kwArg['color']
    path=kwArg['filepath']
    prefix=kwArg['prefix']
    scanIOC=kwArg['scanIOC']
    save=kwArg['save']
    
    if 'legend' in kwArg:
        if kwArg['legend'] == 'center left':
            hsize=7
            
    if type(ScanDet[0]) is not tuple:
        ScanDet=(tuple(ScanDet),)
        m=1
    else: m= len(ScanDet)

    def SubplotsLayout(m,sizeH,sizeV):
        if m >1:
            ncols=2
        else:
            ncols=1
        nrows=max(sum(divmod(m,2)),1)
        hsize=ncols*5*sizeH
        vsize=nrows*4*sizeV
        if nrows==1: 
            vsize=nrows*3.5*kwArg['sizeV']
        return nrows,ncols,hsize,vsize

        
    try:
        nrows,ncols,hsize,vsize=SubplotsLayout(m,kwArg['sizeH'],kwArg['sizeV'])

        fig, axes = plt.subplots(nrows,ncols,figsize=(hsize,vsize))    # HxV
        axes=np.array(axes)

        for (n,ax) in zip(list(range(m)),axes.flat):
            for (i,j) in zip(ScanDet[n][0::2],ScanDet[n][1::2]):
                if type(j) is tuple:
                    p,k,l=j
                    x,y,x_name,y_name=mda_1D(i,p,k,l,path,prefix)

                elif kwArg['flux'] is not None:
                    x,y,x_name,y_name=mda_Flux(i,j,kwArg['flux'],path,prefix,scanIOC)
                elif kwArg['norm'] is not None:
                    x,y,x_name,y_name=mda_1D_unscaled(i,j,path,prefix,scanIOC)
                elif kwArg['NormDet'] is not None:
                    x,y,x_name,y_name=mda_NormDet(i,j,kwArg['NormDet'],1,0,path,prefix,scanIOC)
                elif kwArg['vs_index'] is not None:
                    x,y,x_name,y_name=mda_1D_Xindex(i,j,1,0,path,prefix)
                elif kwArg['vs_det'] is not None:
                    x,y,x_name,y_name=mda_1D_vsDet(i,j,kwArg['vs_det'],1,0,path,prefix)
                #elif DivScan is not None:
                #    x,y,x_name,y_name=mda_DivScan(i,j,DivScan,DivDet,1,0,path,prefix,scanIOC)
                else:
                    x,y,x_name,y_name=mda_1D(i,j,1,0,path,prefix)
                ax.plot(x,y,label="mda_"+str(i),color=c,marker=mkr,markersize=ms,linewidth=lw,linestyle=ls)
                ax.grid(color='lightgray', linestyle='-', linewidth=0.5)

                #modifying graph
                if kwArg['legend'] != None:
                    if kwArg['legend'] == 'center left':
                        box = ax.get_position()
                        ax.set_position([box.x0, box.y0, box.width * 0.6, box.height])
                        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
                        myleft=0.1
                        myright=0.55
                    else:
                        ax.legend(kwArg['legend'], frameon=True)
                if 'ytickstyle' in kwArg:
                    ax.ticklabel_format(style=kwArg['ytickstyle'], axis='y', scilimits=(0,0))
                if 'xtickstyle' in kwArg:
                    ax.ticklabel_format(style=kwArg['xtickstyle'], axis='x', scilimits=(0,0))
                if 'log' in kwArg:
                    ax.set_yscale('log')
                if 'xrange' in kwArg:
                    ax.set_xlim(kwArg['xrange'][0],kwArg['xrange'][1])
                if 'xrange' in kwArg:
                    ax.set_ylim(kwArg['yrange'][0],kwArg['yrange'][1])
                if 'xlabel' in kwArg:
                    x_name=kwArg['xlabel']
                if 'ylabel' in kwArg:
                    y_name=kwArg['ylabel']
                if kwArg['nticks'] != None: 
                    tck=kwArg['nticks']-1
                    ax.locator_params(tight=None,nbins=tck)


            if 'title' in kwArg:
                mytitle=kwArg['title']
                if type(mytitle) is not tuple:
                    ax.set(xlabel=x_name,ylabel=y_name,title=mytitle)
                else:
                    p=len(mytitle)
                    if n == p:
                        ax.set(xlabel=x_name,ylabel=y_name,title='')
                    else:
                        ax.set(xlabel=x_name,ylabel=y_name,title=mytitle[n])
        #        ax.text(0.5, 1.025,mytitle,horizontalalignment='center',fontsize=14,transform = ax.transAxes)
            ax.grid(color='lightgray', linestyle='-', linewidth=0.5)

        if ncols==1 and nrows==1 and kwArg.get('legend')!='center left':
            fig.subplots_adjust(wspace=0.5,hspace=0.5,left=0.25,right=0.88,top=0.85,bottom=0.22)
        elif ncols==1 and kwArg.get('legend')=='center left':
            fig.subplots_adjust(wspace=0.5,hspace=0.5,left=myleft,right=myright,top=0.85,bottom=0.22)
        else:
            fig.subplots_adjust(wspace=0.5,hspace=0.5,left=0.125,right=0.9,top=0.85,bottom=0.15)

        plt.tight_layout()
        if save:
            try:
                fname=join('/home/beams/29IDUSER/Documents/User_Folders/','lastfigure.png')
                print(fname)
                plt.savefig(fname)
            except:
                pass
        plt.show()
    except:
        pass

def plot_mda2D(ScanNum,DetectorNum,title=None,color=None,filepath=None,prefix=None):
    try:
        x,y,z,xName,yName,zName=mda_2D(ScanNum,DetectorNum,filepath,prefix)
        fig, ax0 = plt.subplots()
        if color is None:
            color='gnuplot'
        img = ax0.imshow(z, cmap=color, interpolation = 'nearest', extent = [min(x), max(x), max(y), min(y)], aspect = 'auto')
        fig.colorbar(img)
        if title is None:
            plt.title(zName)
        else:
            plt.title(title)
        ax0.set_xlabel(xName)
        ax0.set_ylabel(yName)
    #    ax0.set_ylim(y.max(),y.min())
        plt.show()
    except:
        pass

def plot_mda_series(*ScanDet,**kwArg):
    """plot_mda_series(1217, 1226,   1,   39 ,0.025, **kwArg)
                    (first,last,countby,det,offset,**kwArg)
    Optional data analysis keywords arguments:
        Flux conversion (for diode only): flux= 3(User) or 25(Staff).
        Norm option: norm = 'yes' normalizes all the scans to 1 (default: None)
        NormDet= 1 for SR current, 14  for Mesh (D-branch); Normalize by the mesh does not work with norm='yes'
    Optional graphical keywords arguments:
        sizeH = 1,1.5,... increase horizontal figure size
        sizeV = 1,1.5,... increase vertical figure size
        marker = 'x','+','o','v','^','D',...    (default:None)
        markersize = 1,2,3,...        (default: 5)
        linewidth = 0.5,1,2...         (default: 1)
        linestyle = '-','--','-.',':'     (default: solid '-')
        color = 'r','b','m','c','g','y'...    (default: jupyter colors series)
        legend = 'best',Supper left', 'lower right'...        (default: None)
        log = 'log'   (default: None = linear)
        xrange = [x1,x2]   (default: None = Autoscale)
        yrange = [y1,y2]   (default: None = Autoscale)
        xlabel = 'mxLabel'        (default: pv name)
        ylabel = 'myLabel'        (default: pv name)
        ytickstyle = 'sci' for y axes    (default: 'plain')
        xtickstyle = 'sci' for y axes    (default: 'plain')
    filepath: by default plot scans for the current data folder (as defined in BL_ioc() ScanRecord SaveData)
    or specified folder path:
        e.g. user : filepath='/net/s29data/export/data_29idc/2018_2/UserName/mda/'
        e.g. staff: filepath='/net/s29data/export/data_29idb/2018_2/mda/'
    prefix: by default, uses prefix as defined in ScanRecord ("mda_")
    scanIOC: by default, uses the IOC for the current branch as define in BL_IOC()
    """

    if type(ScanDet[0]) is not tuple:
        ScanDet=(tuple(ScanDet),)
        m=1
    else: m= len(ScanDet)

    scanlist=""
    j=0
    offset=0
    for n in range(m):
        print(n)
        print(m)
        print(ScanDet)
        det=ScanDet[n][3]
        if len(ScanDet)>4 and isinstance(ScanDet[n][3],str)== False:
            offset=ScanDet[n][4]
        for scanNum in range(ScanDet[n][0],ScanDet[n][1]+ScanDet[n][2],ScanDet[n][2]):
            scanlist+=str(scanNum)+',(det,1,'+str(offset)+'),'
            j+=offset
        cmd="plot_mda("+scanlist+")"
    if kwArg is not None:
        for key, value in list(kwArg.items()):
            if type(value) == str:
                cmd=cmd+(key+'=\"'+value+'\",')
            else:
                cmd=cmd+(key+'='+str(value)+',')
    if cmd[-1]==",":
        cmd=cmd[:-1]
    cmd=cmd+")"
    if kwArg is not None:
        for key, value in list(kwArg.items()):
            if key=='q':
                print('det=',det)
                print(cmd)
    exec(cmd)



def plot_mda_lists(*ScanDet,**kwArg):
    """
    Plot mda scans: *ScanDet = (scanNum_list,detNum_list),(scanNum_list,detNum_list)
                             =            subplot1,                subplot2
    Optional data analysis keywords arguments:
        Flux conversion (for diode only): flux= 3(User) or 25(Staff).
        Norm option: norm = 'yes' normalizes all the scans to 1 (default: None)
        NormDet= 1 for SR current, 14  for Mesh (D-branch); Normalize by the mesh does not work with norm='yes'
    Optional graphical keywords argudef plot_mdaments:
        sizeH = 1,1.5,... increase horizontal figure size
        sizeV = 1,1.5,... increase vertical figure size
        marker = 'x','+','o','v','^','D',...    (default:None)
        markersize = 1,2,3,...        (default: 5)
        linewidth = 0.5,1,2...         (default: 1)
        linestyle = '-','--','-.',':'     (default: solid '-')
        color = 'r','b','m','c','g','y'...    (default: jupyter colors F)
        legend = 'best',Supper left', 'lower right'...        (default: None)
        log = 'log'   (default: None = linear)
        xrange = [x1,x2]   (default: None = Autoscale)
        yrange = [y1,y2]   (default: None = Autoscale)
        xlabel = 'mxLabel'        (default: pv name)
        ylabel = 'myLabel'        (default: pv name)
        ytickstyle = 'sci' for y axes    (default: 'plain')
        xtickstyle = 'sci' for y axes    (default: 'plain')
    filepath: by default plot scans for the current data folder (as defined in BL_ioc() ScanRecord SaveData)
    or specified folder path:
        e.g. user : filepath='/net/s29data/export/data_29idc/2018_2/UserName/mda/'
        e.g. staff: filepath='/net/s29data/export/data_29idb/2018_2/mda/'
    prefix: by default, uses prefix as defined in ScanRecord ("mda_")
    scanIOC: by default, uses the IOC for the current branch as define in BL_IOC()
    """
    
    args={
        'marker':None,
        'markersize':5,
        'linewidth':1,
        'linestyle':'-',
        'color':None,
        'nticks':None,
        'sizeH':1,
        'sizeV':1,
        'title':'',
        'filepath':None,
        'prefix':None,
        'norm':None,
        'flux':None,
        'NormDet':None,
        'scanIOC':None,
        'legend':None,
        'vs_index':None,

    }
    
    args.update(kwArg)
    
    mkr=args['marker']
    ms=args['markersize']
    lw=args['linewidth']
    ls=args['linestyle']
    c=args['color']
    path=args['filepath']
    prefix=args['prefix']
    scanIOC=args['scanIOC']
  
    if 'legend' in args:
        if args['legend'] == 'center left':
            hsize=7
            
    #setting up the subplot
    if type(ScanDet[0]) is not tuple:
        ScanDet=(tuple(ScanDet),)
        m=1
    else: m= len(ScanDet)
        
    def SubplotsLayout(m):
        if m >1:
            ncols=2
        else:
            ncols=1
        nrows=max(sum(divmod(m,2)),1)
        hsize=ncols*5*args['sizeH']
        vsize=nrows*4*args['sizeV']
        if nrows==1: vsize=nrows*3.5*args['sizeV']
        return nrows,ncols,hsize,vsize
    
    try:
        nrows,ncols,hsize,vsize=SubplotsLayout(m)
        fig, axes = plt.subplots(nrows,ncols,figsize=(hsize,vsize))    # HxV
        axes=np.array(axes)


        for (n,ax) in zip(list(range(m)),axes.flat): #n=subplot tuple
            scanNum_list=ScanDet[n][0]
            detNum_list=ScanDet[n][1]

            if type(scanNum_list) is int:
                scanNum_list=[scanNum_list]
            if type(detNum_list) is int:
                detNum_list=[detNum_list]
                for i in range(1,len(scanNum_list)):
                    detNum_list.append(detNum_list[0])
            if type(args['filepath']) is not list:
                filepath_list=[args['filepath']]
                for i in range(1,len(scanNum_list)):
                    filepath_list.append(filepath_list[0])
            else: filepath_list=args['filepath']
            if type(args['prefix']) is not list:
                prefix_list=[args['prefix']]
                for i in range(1,len(scanNum_list)):
                    prefix_list.append(prefix_list[0]) 
            else: prefix_list=args['prefix']
            if type(args['scanIOC']) is not list:
                scanIOC_list=[args['scanIOC']]
                for i in range(1,len(scanNum_list)):
                    scanIOC_list.append(scanIOC_list[0]) 
            else: scanIOC_list=args['scanIOC']
            #loading the data
            for index in range(0,len(scanNum_list)):
                i=scanNum_list[index]
                j=detNum_list[index]
                path=filepath_list[index]
                prefix=prefix_list[index]
                scanIOC=scanIOC_list[index]
                #print(i)
                if type(j) is tuple:
                    p,k,l=j
                    x,y,x_name,y_name=mda_1D(i,p,k,l,path,prefix)
                elif args['flux'] is not None:
                    x,y,x_name,y_name=mda_Flux(i,j,args['flux'],path,prefix,scanIOC)
                elif args['norm'] is not None:
                    x,y,x_name,y_name=mda_1D_unscaled(i,j,path,prefix,scanIOC)
                elif args['NormDet'] is not None:
                    x,y,x_name,y_name=mda_NormDet(i,j, args['NormDet'],1,0,path,prefix,scanIOC)
                else:
                    x,y,x_name,y_name=mda_1D(i,j,1,0,path,prefix,scanIOC)
                #adding to graph
                ax.grid(color='lightgray', linestyle='-', linewidth=0.5)
                ax.plot(x,y,label="mda_"+str(i),color=c,marker=mkr,markersize=ms,linewidth=lw,linestyle=ls)

            #modifying graph
            if args['legend'] != None:
                if args['legend'] == 'center left':
                    box = ax.get_position()
                    ax.set_position([box.x0, box.y0, box.width * 0.6, box.height])
                    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
                    myleft=0.1
                    myright=0.55
                else:
                    ax.legend(args['legend'], frameon=True)
            if 'ytickstyle' in args:
                ax.ticklabel_format(style=args['ytickstyle'], axis='y', scilimits=(0,0))
            if 'xtickstyle' in args:
                ax.ticklabel_format(style=args['xtickstyle'], axis='x', scilimits=(0,0))
            if 'log' in args:
                ax.set_yscale('log')
            if 'xrange' in kwArg:
                ax.set_xlim(args['xrange'][0],args['xrange'][1])
            if 'yrange' in kwArg:
                ax.set_ylim(args['yrange'][0],args['yrange'][1])
            if 'xlabel' in args:
                x_name=args['xlabel']
            if 'ylabel' in args:
                y_name=args['ylabel']
            if args['nticks'] != None: 
                tck=args['nticks']-1
                ax.locator_params(tight=None,nbins=tck)

            if 'title' in args:
                if type(args['title']) is not str:
                    mytitle=args['title'][n]
                else:
                    mytitle=args['title']
            ax.set(xlabel=x_name,ylabel=y_name,title=mytitle)
        #adjusting subplots
        if ncols==1 and nrows==1 and kwArg.get('legend')!='center left':
            fig.subplots_adjust(wspace=0.5,hspace=0.5,left=0.25,right=0.88,top=0.85,bottom=0.22)
        elif ncols==1 and kwArg.get('legend')=='center left':
            fig.subplots_adjust(wspace=0.5,hspace=0.5,left=myleft,right=myright,top=0.85,bottom=0.22)
        else:
            fig.subplots_adjust(wspace=0.5,hspace=0.5,left=0.125,right=0.9,top=0.85,bottom=0.15)
        #show plot
        plt.tight_layout()
        plt.show()

    except:
        pass




###############################################################################################
##################################### Fitting  #######################################
###############################################################################################
def fit_mda(scanNum,detNum,fit_type,**kwargs):
    """
    fits an mda scan and returns center value
    fit_type = 'gauss','lorz','erf','poly','box'
    

    **kwargs:
        hkl_positionner = 'H','K','L','tth','th','chi','phi'
        plot: True/False plots the data and the fit (default=True)
        xrange=[x_first,x_last] to fit subrange 
        coefs_0=[Amplitude,x0,sigma,bkgd] to specifiy initial guesses, otherwise autoguess
        filepath: to load data in a different path
        prefix: to load data with a different prefix

    """
    kwargs.setdefault('hkl_positioner',False)
    kwargs.setdefault('title','')
    kwargs.setdefault('plot',True)
    kwargs.setdefault('filepath',None)
    kwargs.setdefault('prefix',None)
    title=kwargs['title']


    if kwargs['hkl_positioner']:
        hkl_positioner=kwargs['hkl_positioner']
        d={'h':46,'k':47,'l':48,'tth':54,'th':55,'chi':56,'phi':57}
        x,y,x_name,y_name=mda_1D_vsDet(scanNum,detNum,d[hkl_positioner.lower()],1,0,kwargs['filepath'],kwargs['prefix'])
    else:
        x,y,x_name,y_name=mda_1D(scanNum,detNum,1,0,kwargs['filepath'],kwargs['prefix'])
    
    if iex.BL.endstation_name.lower() == 'kappa' and fit_type != 'poly':
        try:
            title=title + ' centroid = '+str(centroid_avg(scanNum))
        except:
            pass

    x = np.array(x)
    y = np.array(y)

    if kwargs['plot'] == True:
        plt.figure(figsize=(5,4))
        plt.xlabel(x_name)
        plt.ylabel(y_name)
        plt.grid(color='lightgray', linestyle='-', linewidth=0.5)
        plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

    if fit_type == 'gauss':
        x_fit,y_fit,coefs,covar,fit_vals = fit_gaussian(x,y,**kwargs)
        
    elif fit_type == 'lorz':
        x_fit,y_fit,coefs,covar,fit_vals = fit_lorentzian(x,y,**kwargs)

    elif fit_type == 'erf':
        x_fit,y_fit,coefs,covar,fit_vals = fit_step(x,y,**kwargs)

    
    elif fit_type == 'box':
        x_fit,y_fit,coefs,covar,fit_vals = fit_box(x,y,**kwargs)

    elif fit_type == 'poly':
        x_fit,y_fit,coefs,covar,fit_vals = fit_poly(x,y,**kwargs)

    else:
        print('not a valid fit function')

    return fit_vals['center']


def fit_centroid(scanNum,detNum=25):
    fit_mda(scanNum,detNum,'poly',plot=False)

def centroid_avg(scanNum,detNum=25):   # det = detector number for centroid position
    avg=round(fit_mda_poly(scanNum,detNum,0,plot=False),2)
    return avg


def fit_mda_gauss(scanNum,detNum,**kwargs):
    fit_type='gauss'
    fit_mda(scanNum,detNum,fit_type,**kwargs)


def fit_mda_lorz(scanNum,detNum,**kwargs):
    fit_type='lorz'
    fit_mda(scanNum,detNum,fit_type,**kwargs)


def fit_mda_erf(scanNum,detNum,**kwargs):
    fit_type='erf'
    fit_mda(scanNum,detNum,fit_type,**kwargs)

def fit_mda_poly(scanNum,detNum,poly_rank=3,**kwargs):
    fit_type='poly'
    kwargs.update({'coefs_0':[poly_rank]})
    fit_mda(scanNum,detNum,fit_type,**kwargs)


def fit_mda_box(scanNum,detNum,**kwargs):
    fit_type='box'
    fit_mda(scanNum,detNum,fit_type,**kwargs)

    
###############################################################################################
######################################### hkl ###################################
###############################################################################################

##############################################################################################################
##############################                  Extracting mda Data               ##############################
##############################################################################################################
def mda_unpack(ScanNum,filepath=None,prefix=None):
    """ Return data file + dictionary D##:("pv",index##)
    filepath: by default plot scans for the current data folder (as defined in BL_ioc() ScanRecord SaveData)
    or specified folder path:
        e.g. filepath='/net/s29data/export/data_29idb/2018_1/mda_b/'
    prefix: by default, uses prefix as defined in ScanRecord
            "mda_" for users, "Kappa_" or "ARPES_" for staff (sometimes)
    """
    try:
        if filepath is None:
            filepath = mda_filepath()
        if prefix is None:
            prefix = mda_prefix()
    except:
        print('Please specify filepath and prefix, BL is not defined')

    mdaFile=join(filepath,prefix+'{:04}.mda'.format(ScanNum))
    data_file = readMDA(mdaFile)
    try:
        D={}
        n=len(data_file)-1
        for i in range(0,data_file[n].nd):
            detector=data_file[n].d[i].fieldName
            D[int(detector[1:])]=(data_file[n].d[i].name,i)
        return (data_file,D)
    except:
        pass
def mda_1D(ScanNum,DetectorNum,coeff=1,bckg=0,filepath=None,prefix=None):
    """ Return x=positionner and y=detector(DetectorNum)
    for a given detector number DYY (as shown in dview). """
    try:
        (data_file,det)=mda_unpack(ScanNum,filepath,prefix)
        index=det[DetectorNum][1]
        x = data_file[1].p[0].data
        y = data_file[1].d[index].data
        x_name = data_file[1].p[0].name
        y_name = data_file[1].d[index].name
        if type(x_name) == bytes:
             x_name=x_name.decode("utf-8")
        if type(y_name) == bytes:
             y_name=y_name.decode("utf-8")
        n=list(zip(x,y))
        d=[n[i] for i, e in enumerate(n) if e != (0.0,0.0)]
        if len(d)<len(n):
            x=x[:len(d)]
            y=y[:len(d)]
        y=[(y[i]+bckg)*coeff for i, e in enumerate(y)]
        #y=[(y[i]*coeff)+bckg for i, e in enumerate(y)]
        return x,y,x_name,y_name
    except:
        print('error')
        pass


def mda_1D_unscaled(ScanNum,DetectorNum,filepath=None,prefix=None):
    """ Return x=positionner and y=detector(DetectorNum)
    for a given detector number DYY (as shown in dview). """
    try:
        (data_file,det)=mda_unpack(ScanNum,filepath,prefix)
        if (data_file,det) == (None,None):
            return(None)
        else:
            index=det[DetectorNum][1]
            x = data_file[1].p[0].data
            y = data_file[1].d[index].data
            x_name = data_file[1].p[0].name
            y_name = data_file[1].d[index].name
            if type(x_name) == bytes:
                 x_name=x_name.decode("utf-8")
            if type(y_name) == bytes:
                 y_name=y_name.decode("utf-8")
            n=list(zip(x,y))
            d=[n[i] for i, e in enumerate(n) if e != (0.0,0.0)]
            if len(d)<len(n):
                x=x[:len(d)]
                y=y[:len(d)]
            bckg=min(y)
            coeff=max(y)-min(y)
            y=[(y[i]-bckg)/coeff for i, e in enumerate(y)]
            return x,y,x_name,y_name
    except:
        pass

def mda_1D_Xindex(ScanNum,DetectorNum,coeff=1,bckg=0,filepath=None,prefix=None):
    """ Return x=index and y=detector(DetectorNum)
    for a given detector number DYY (as shown in dview). """
    try:
        (data_file,det)=mda_unpack(ScanNum,filepath,prefix)
        index=det[DetectorNum][1]
        x = data_file[1].d[0].data
        y = data_file[1].d[index].data
        x_name = data_file[1].d[0].name
        y_name = data_file[1].d[index].name
        if type(x_name) == bytes:
             x_name=x_name.decode("utf-8")
        if type(y_name) == bytes:
             y_name=y_name.decode("utf-8")
        n=list(zip(x,y))
        d=[n[i] for i, e in enumerate(n) if e != (0.0,0.0)]
        if len(d)<len(n):
            y=y[:len(d)]
        x=list(range(1,len(y)+1))
        y=[(y[i]*coeff)+bckg for i, e in enumerate(y)]
        return x,y,x_name,y_name
    except:
        pass

def mda_1D_vsDet(ScanNum,DetectorNum,DetectorNum2,coeff=1,bckg=0,filepath=None,prefix=None):
    """ Return x=index and y=detector(DetectorNum)
    for a given detector number DYY (as shown in dview). """
    try:
        #print(ScanNum,filepath,prefix,scanIOC)
        (data_file,det)=mda_unpack(ScanNum,filepath,prefix)
        index=det[DetectorNum][1]
        index2=det[DetectorNum2][1]
        x = data_file[1].d[0].data
        x2 = data_file[1].d[index2].data
        y = data_file[1].d[index].data
        x_name = data_file[1].d[0].name
        x2_name = data_file[1].d[index2].name
        y_name = data_file[1].d[index].name
        x = data_file[1].p[0].data
        x2= data_file[1].d[index2].data
        y= data_file[1].d[index].data
        if type(x_name) == bytes:
             x_name=x_name.decode("utf-8")
        if type(y_name) == bytes:
             y_name=y_name.decode("utf-8")
        if type(x2_name) == bytes:
             x2_name=x2_name.decode("utf-8")
        n=list(zip(x,y))
        d=[n[i] for i, e in enumerate(n) if e != (0.0,0.0)]
        if len(d)<len(n):
            y=y[:len(d)]
            x2=x2[:len(d)]
        y=[(y[i]*coeff)+bckg for i, e in enumerate(y)]
        return x2,y,x2_name,y_name
    except:
        pass

def mda_Flux(ScanNum,DetectorNum,EnergyNum,filepath=None,prefix=None):
    """ Return x=positionner and y=Flux(DetectorNum)
    for a given diode recorded as detector number DYY (see ## in dview).
    EnergyNum is the detector number for the mono RBV.

    """
    try:
        (data_file,det)=mda_unpack(ScanNum,filepath,prefix)
        index=det[DetectorNum][1]
        Eindex=det[EnergyNum][1]
        x = data_file[1].p[0].data
        y = data_file[1].d[index].data
        energy = data_file[1].d[Eindex].data
        x_name = data_file[1].p[0].name
        y_name = data_file[1].d[index].name
        if type(x_name) == bytes:
             x_name=x_name.decode("utf-8")
        if type(y_name) == bytes:
             y_name=y_name.decode("utf-8")
        n=list(zip(x,y))
        d=[n[i] for i, e in enumerate(n) if e != (0.0,0.0)]
        if len(d)<len(n):
            x=x[:len(d)]
            y=y[:len(d)]
        y=[current2flux(y[i],energy[i],p=None) for (i, e) in enumerate(y)]
        return x,y,x_name,y_name
    except:
        pass



def mda_NormDet(ScanNum,DetectorNum,NormNum,coeff=1,bckg=0,filepath=None,prefix=None):
    """ Return x=positionner and y=detector(DetectorNum)
    for a given detector number DYY (as shown in dview). """
    try:
        (data_file,det)=mda_unpack(ScanNum,filepath,prefix)
        index=det[DetectorNum][1]
        index_Norm=det[NormNum][1]
        x = data_file[1].p[0].data
        y= data_file[1].d[index].data
        y_Norm=data_file[1].d[index_Norm].data
        x_name = data_file[1].p[0].name
        y_name = data_file[1].d[index].name#+"_norm:"+str(NormNum)
        if type(x_name) == bytes:
             x_name=x_name.decode("utf-8")
        if type(y_name) == bytes:
             y_name=y_name.decode("utf-8")

        n=list(zip(x,y))
        d=[n[i] for i, e in enumerate(n) if e != (0.0,0.0)]
        if len(d)<len(n):
            x=x[:len(d)]
            y=y[:len(d)]
        y=[y[i]/y_Norm[i] for i, e in enumerate(y)]
        return x,y,x_name,y_name
    except:
        pass

def mda_DivScan(ScanNum1,DetectorNum1,ScanNum2,DetectorNum2,coeff=1,bckg=0,filepath=None,prefix=None):
    """ Return x=positionner and y=detector(DetectorNum)
    for a given detector number DYY (as shown in dview). """
    try:
        (data_file1,det1)=mda_unpack(ScanNum1,filepath,prefix)
        index1=det1[DetectorNum1][1]
        (data_file2,det2)=mda_unpack(ScanNum2,filepath,prefix)
        index2=det2[DetectorNum2][1]
        x1 = data_file1[1].p[0].data
        y1= data_file1[1].d[index1].data
        y2= data_file2[1].d[index2].data
        x_name = data_file1[1].p[0].name
        y_name = data_file1[1].d[index1].name+"_norm:"+str(ScanNum2)
        if type(x_name) == bytes:
             x_name=x_name.decode("utf-8")
        if type(y_name) == bytes:
             y_name=y_name.decode("utf-8")

        n=list(zip(x1,y1))
        d=[n[i] for i, e in enumerate(n) if e != (0.0,0.0)]
        if len(d)<len(n):
            x1=x1[:len(d)]
            y1=y1[:len(d)]
        y=[y1[i]/y2[i] for i, e in enumerate(y1)]
        return x1,y,x_name,y_name
    except:
        pass



def mda_2D(ScanNum,DetectorNum,filepath=None,prefix=None):
    """ Return x=positionner and y=detector(DetectorNum)
    for a given detector number DYY (as shown in dview). """
    try:
        (data_file,det)=mda_unpack(ScanNum,filepath,prefix)
        index=det[DetectorNum][1]
        x_temp = data_file[2].p[0].data
        y_temp = data_file[1].p[0].data
        z_temp = data_file[2].d[index].data
        x_name = data_file[2].p[0].name
        y_name = data_file[1].p[0].name
        z_name = data_file[2].d[index].name
        if type(x_name) == bytes:
             x_name=x_name.decode("utf-8")
        if type(y_name) == bytes:
             y_name=y_name.decode("utf-8")
        if type(z_name) == bytes:
             z_name=z_name.decode("utf-8")

        n=list(zip(x_temp,y_temp,z_temp))
        d=[n[i] for i, e in enumerate(n) if e != (0.0,0.0,0.0)]
        if len(d)<len(n):
            x_temp=x_temp[:len(d)]
            y_temp=y_temp[:len(d)]
            z_temp=z_temp[:len(d)]
        x = x_temp[0]
        y = y_temp
        z = np.asarray(z_temp)     #2-D array
        return x,y,z,x_name,y_name,z_name
    except:
        pass

###############################################################################################
######################################### Object Oriented #####################################
###############################################################################################

class _mdaData(scanDim):
    
    def __init__(self):
        scanDim.__init__(self)
        self.poslist = None
        self.detlist = None
        
    
    def _getDetIndex(self,d):
        """ 
            d = det Num
        """
        D=self.detlist
        if D==[]:
            print('Data contains no detectors. Try higher dimensions: mydata.dim2[n]')
            index=[None]
        else:
            index=[x for x, y in enumerate(D) if y[1] == 'D'+str(d).zfill(2)]
            if index == []:
                print('Detector '+str(d)+' not found.')
                index=[None]
        return index[0]
        

    
    def plt(self,d):
        d=self._getDetIndex(d)
        if d== None:
            return
        x=self.p[0]
        y=self.d[d]
        if self.dim == 2:
            print('This is a 2D scan; use method mydata.img(n,d)')
            for i in range(len(y.data)):
                plt.plot(x.data[i], y.data[i],label=y.fieldName,marker='+')            # crop aborted scans (curr_pt<npts)
        else:   plt.plot(x.data[:self.curr_pt], y.data[:self.curr_pt],label=y.fieldName,marker='+')            # crop aborted scans (curr_pt<npts)
        plt.xlabel(x.name)
        plt.ylabel(y.name)
        plt.legend()
        plt.grid(color='lightgray', linestyle='-', linewidth=0.5)
        
        
        
    def kappaDet(self,q=None):
        if q is not None:
            print('\nUse detIndex for plot: mydata.dim1[n].d[detIndex].data\nIf D=mydata.dim1[n].kappaDet => detIndex=D[detNum][1]\n')
            print('key = (detIndex, detNum, description, pv)')
        det={}
        D=self.detlist
        for (i,j) in zip([32,33,34,35,31,36,37,38,39,41,42,43,44,45,46,47,48,54,55,56,57],['TEY','D3','D4','MCP','mesh','TEY / mesh','D3 / mesh','D4 / mesh','MCP / mesh','ROI1','ROI2','ROI3','ROI4','ROI5','<H>','<K>','<L>','tth','th','chi','phi']):
            d=self._getDetIndex(i)
            if d != None:
                det[i]=(d,D[d][1],j,D[d][2])
            else:
                det[i]=None
        return det        
    


        
    
class _mdaHeader:
    def __init__(self):
        self.all = None
        self.sample = None
        self.mono = None
        self.ID = None
        self.energy = None
        self.det = None
        self.motor = None
        self.mirror = None
        self.centroid = None
        self.slit=None
        self.comment=None
        
        


class mdaFile:
    
    
    '''mydata=mdaFile(first=0,last=None,name=datasetName,filepath=None,prefix=None)
    
    /net/s29data/export/data_29idb/2020_3/mda/Kappa_0107.mda is a 1-D file; 1 dimensions read in.
    
    mydata.header[n] = dictionary of 163 scan-environment PVs
    
       usage: mydata.header[n]['sampleEntry'] -> ('description', 'unit string', 'value', 'EPICS_type', 'count')
    
    mydata.dim1[n] = 1D data from '29idKappa:scan1' acquired on Oct 20, 2020 19:06:23:
                    33/33 pts; 1 positioners, 65 detectors
    
       usage: mydata.dim1[n].p[2].data -> 1D array of positioner 1 data
     
    Each scan dimension (i.e., dim1, dim2, ...) has the following fields: 
          time      - date & time at which scan was started: Oct 20, 2020 19:06:23
          name      - name of scan record that acquired this dimension: 29idKappa:scan1
          curr_pt   - number of data points actually acquired: 33
          npts      - number of data points requested: 33
          nd        - number of detectors for this scan dimension: 65
          d[]       - list of detector-data structures
          np        - number of positioners for this scan dimension: 1
          p[]       - list of positioner-data structures
          nt        - number of detector triggers for this scan dimension: 1
          t[]       - list of trigger-info structures
     
    Each detector-data structure (e.g., dim[1].d[0]) has the following fields: 
          desc      - description of this detector
          data      - data list
          unit      - engineering units associated with this detector
          fieldName - scan-record field (e.g., 'D01')
     
    Each positioner-data structure (e.g., dim[1].p[0]) has the following fields: 
          desc          - description of this positioner
          data          - data list
          step_mode     - scan mode (e.g., Linear, Table, On-The-Fly)
          unit          - engineering units associated with this positioner
          fieldName     - scan-record field (e.g., 'P1')
          name          - name of EPICS PV (e.g., 'xxx:m1.VAL')
          readback_desc - description of this positioner
          readback_unit - engineering units associated with this positioner
          readback_name - name of EPICS PV (e.g., 'xxx:m1.VAL')
    '''

    def __init__(self,first=1,last=None,name='mydata',filepath=None,prefix=None,q=False):
        if filepath == None:
            filepath = iex.BL.mda.filepath()
        self.path  = filepath
        self._name  = name
        self._first = first
        self._last  = last
        if prefix != None and prefix[-1]=='_':
            self._prefix= prefix[:-1]
        else:
            self._prefix= prefix
            
        self._allFiles = None
        self._allPrefix  = None
        self.loadedFiles = None
        self.scanList  = None
        self.dim1  = None
        self.dim2  = None
        self.dim3  = None
        self.header  = None

        self._extractFiles()
        self._extractData(q)

    def _extractFiles(self):
        allFiles   = [f for f in listdir(self.path) if isfile(join(self.path, f))]
        loadedFiles= [x for (i,x) in enumerate(allFiles) if allFiles[i].split('.')[-1]=='mda']
        allPrefix = [loadedFiles[i][:loadedFiles[i].find('_')] for (i,x) in enumerate(loadedFiles)]
        scanList = [int(loadedFiles[i][loadedFiles[i].find('_')+1:loadedFiles[i].find('_')+5]) for (i,x) in enumerate(loadedFiles)]
        if self._prefix != None:
            allPrefix=[s for s in allPrefix if s == self._prefix]
            scanList = [int(loadedFiles[i][loadedFiles[i].find('_')+1:loadedFiles[i].find('_')+5]) for (i,x) in enumerate(loadedFiles) if loadedFiles[i][:loadedFiles[i].find('_')] == self._prefix]
            loadedFiles   = [s for s in loadedFiles if s[:s.find('_')] == self._prefix]
        else:
            self._prefix=allPrefix[-1]
            if allPrefix[0]!=allPrefix[-1]:
                print('\nWARNING: Found more than one file prefix: {}, {}.\n\nData with the same scan number will be overwriten in the order they are loaded. \nPlease specify the one you want to load with arg prefix="which".\n\n'.format(allPrefix[0],allPrefix[-1]))
        if self._last == None:
            self._last = self._first
        shortlist  = [i for (i,x) in enumerate(scanList) if self._first<=x<=self._last]  
        self._allFiles = allFiles
        self.loadedFiles = [loadedFiles[i] for i in shortlist]  
        self.scanList  = [scanList[i] for i in shortlist]
        self._allPrefix=[allPrefix[i] for i in shortlist]
        
        
    def _extractData(self,q):
        
        allheader = {}
        alldata1 = {}
        alldata2 = {}
        alldata3 = {}
        
        for (i,mda) in enumerate(self.loadedFiles):
            
            ##### File info:
            
            filename=mda
            filepath=self.path
            #print(filepath)
            num=self.scanList[i]
            #print(num)
            fullpath=join(filepath,filename)
            #print(fullpath)
            data=readMDA(fullpath,useNumpy=True)    # data = scanDim object of mda module
            
            ###### Extract header:

            D0 = _mdaHeader()   # initiate D0 = mdaHeader object
            D1 = _mdaData()
            D2 = _mdaData()
            D3 = _mdaData()
            
            D=[]
            
            for d in range(0,4):
                if d in range(0,len(data)): D.append(data[d])
                else: D.append(None)
            
            # D[0]=data[0]
            # D[1]=data[1]
            # D[2]=None if 1D data, data[2] if 2D data
            # D[3]=None if 2D data, data[3] if 3D data
                
            
            D0.all=D[0]
            
            
            if filename[:5] == 'Kappa':
                try:
                    D0.sample={**{key:value[:3] for key, value in D[0].items() if '29idKappa:m' in key},**{key:value[:3] for key, value in D[0].items() if '29idKappa:Euler' in key},**{key:value[:3] for key, value in D[0].items() if 'LS331' in key}}
                    D0.mirror = {key:value[:3] for key, value in D[0].items() if '29id_m3r' in key}
                    D0.centroid={key:value[:3] for key, value in D[0].items() if 'ps6' in key.lower()}
                    D0.det = {key:value[:3] for key, value in D[0].items() if '29idd:A' in key}
                    detkeys=['29idMZ0:scaler1.TP','29idKappa:m9.RBV','29idKappa:userCalcOut10.OVAL','29iddMPA:C0O','29idKappa:userStringSeq6.STR1','29idd:Unidig1Bo0']
                    for k in detkeys: 
                        if k in D[0]: D0.det[k]=D[0][k][:3]
                    D0.ID={key:value[:3] for key, value in D[0].items() if 'ID29' in key}
                    D0.UB={key:value[:3] for key, value in D[0].items() if 'UB' in key}
                    D0.mono={key:value[:3] for key, value in D[0].items() if 'mono' in key}
                    D0.energy={key:value[:3] for key, value in D[0].items() if 'energy' in key.lower()}
                    D0.motor = {key:value[:3] for key, value in D[0].items() if '29idb:m' in key}
                    D0.slit={key:value[:3] for key, value in D[0].items() if 'slit3d' in key.lower()}
                except:
                    pass
            if filename[:5] == 'ARPES':
                try:
                    #D0.sample={**{key:value[:3] for key, value in D[0].items() if '29idKappa:m' in key},**{key:value[:3] for key, value in D[0].items() if '29idKappa:Euler' in key},**{key:value[:3] for key, value in D[0].items() if 'LS331' in key}}
                    #D0.mirror = {key:value[:3] for key, value in D[0].items() if '29id_m3r' in key}
                    #D0.centroid={key:value[:3] for key, value in D[0].items() if 'ps6' in key.lower()}
                    #D0.det = {key:value[:3] for key, value in D[0].items() if '29idd:A' in key}
                    #detkeys=['29idMZ0:scaler1.TP','29idKappa:m9.RBV','29idKappa:userCalcOut10.OVAL','29iddMPA:C0O','29idKappa:userStringSeq6.STR1','29idd:Unidig1Bo0']
                    #for k in detkeys: 
                    #    if k in D[0]: D0.det[k]=D[0][k][:3]
                    D0.ID={key:value[:3] for key, value in D[0].items() if 'ID29' in key}
                    #D0.UB={key:value[:3] for key, value in D[0].items() if 'UB' in key}
                    D0.mono={key:value[:3] for key, value in D[0].items() if 'mono' in key}
                    D0.energy={key:value[:3] for key, value in D[0].items() if 'energy' in key.lower()}
                    D0.motor = {key:value[:3] for key, value in D[0].items() if '29idb:m' in key}
                    D0.slit={key:value[:3] for key, value in D[0].items() if 'slit3c' in key.lower()}
                except:
                    pass

                try:
                    cmt1=D[0]['29id'+self._prefix+':saveData_comment1'][2]
                    cmt2=D[0]['29id'+self._prefix+':saveData_comment2'][2]
                    if cmt2 != '': D0.comment = cmt1+' - '+cmt2
                    else: D0.comment = cmt1
                except:
                    D0.comment = ''
            
            
            ###### Extract data:
            
            DIMS=[D1,D2,D3]
            
            for counter, value in enumerate(DIMS):
                c=counter+1
                if D[c] is not None:
                    value.rank=D[c].rank
                    value.dim=D[c].dim
                    value.npts=D[c].npts
                    value.curr_pt=D[c].curr_pt
                    value.plower_scans=D[c].plower_scans
                    value.name=D[c].name #
                    value.time=D[c].time
                    value.np=D[c].np
                    value.p=D[c].p
                    value.nd=D[c].nd
                    value.d=D[c].d
                    value.nt=D[c].nt
                    value.t=D[c].t
                    value.detlist=[(i,D[c].d[i].fieldName,D[c].d[i].name,D[c].d[i].desc) for i in range(0,D[c].nd)]
                    value.poslist=[(i,D[c].p[i].fieldName,D[c].p[i].name,D[c].p[i].desc) for i in range(0,D[c].np)]
                else:
                    value=None
            
            allheader[num] = D0
            alldata1[num]  = D1
            alldata2[num]  = D2
            alldata3[num]  = D3
            
            d=D.index(None)-1
            if q is False:
                print('Loading {}  as  {}.dim{}[{}]:\n\t\t...{}D data, {}/{} pts; {} positioners, {} detectors'.format(
                    filename,self._name,d,self.scanList[i],D[d].dim,D[d].curr_pt, D[d].npts, D[d].np, D[d].nd))
        
        self.header=allheader
        self.dim1=alldata1
        self.dim2=alldata2
        self.dim3=alldata3
        




    def updateFiles(self,first=0,last=inf,name=None,filepath=None,prefix=None):
        new=mdaFile(first,last,name,filepath,prefix)
        self.loadedFiles=list(dict.fromkeys(self.loadedFiles+new.loadedFiles))
        self._allFiles=list(dict.fromkeys(self._allFiles+new._allFiles))              # merging the 2 list and removing duplicates
        self.scanList=list(dict.fromkeys(self.scanList+new.scanList))
        self._allPrefix=list(dict.fromkeys(self._allPrefix+new._allPrefix))
        self.dim1.update(new.dim1)
        self.dim2.update(new.dim2)
        self.dim3.update(new.dim3)
        self.header.update(new.header)
        return self
    
    

    def plt(self,*argv):
        if self.dim2[argv[0]].dim == 0:              #1D scan
            for index,arg in enumerate(argv):
                if index %2 !=0:
                    pass
                else:
                    n=arg
                    d=argv[index+1]
                    d=self.dim1[n]._getDetIndex(d)
                    x=self.dim1[n].p[0]
                    y=self.dim1[n].d[d]
                    plt.plot(x.data[:self.dim1[n].curr_pt], y.data[:self.dim1[n].curr_pt],label='mda #'+str(n)+' - '+y.fieldName,marker='+')
            plt.xlabel(x.name)
            plt.ylabel(y.name+' - ('+y.fieldName+')')
            plt.legend()
            plt.grid(color='lightgray', linestyle='-', linewidth=0.5)
            plt.show()
        elif self.dim2[argv[0]].dim == 2:              # 2D scan 
            for index,arg in enumerate(argv):
                if index %2 !=0:
                    pass
                else:
                    n=arg
                    d=argv[index+1]
                    d=self.dim2[n]._getDetIndex(d)
                    if d == None:
                        return
                    x=self.dim2[n].p[0]
                    y=self.dim1[n].p[0]
                    z=self.dim2[n].d[d]
                    zlim=self.dim2[n].curr_pt
                    fig, ax0 = plt.subplots()
                    img = ax0.imshow(z.data[:zlim],cmap='gnuplot', interpolation = 'nearest', extent = [min(x.data[0]), max(x.data[0]), min(y.data),max(y.data)], aspect = 'auto')
                    fig.colorbar(img)
                    plt.title(z.name+' - ('+z.fieldName+')')
                    ax0.set_xlabel(x.name)
                    ax0.set_ylabel(y.name)
                    plt.show()








###############################################################################################
####################################         PLOT netCDF        ###################################
###############################################################################################
def nc_unpack(scanNum,**kwargs):
    """
    Returns the full netCDF data file
        meta data (Attributes/Exta PVs) 
            c.variables['Attr_EnergyStep_Swept'][:][0]
        data array is accessed
            nc.variables['array_data'][:][0]
            
    FilePath: by default plot scans for the current data folder (as shown on detector panel)
    or specified folder path ending with '/':
        e.g. user : FilePath='/net/s29data/export/data_29idc/2018_2/UserName/netCDF/'
        e.g. staff: FilePath='/net/s29data/export/data_29idb/2018_2/netCDF/'
    Prefix: by default, uses prefix as shown on detector panel ("EA_")
    """
    ADplugin = '29idcEA:netCDF1:'
    kwargs.setdefault('path',AD_filepath(ADplugin))
    kwargs.setdefault('prefix',AD_prefix(ADplugin))
    fname = kwargs['prefix']+'{:04}.nc'.format(scanNum)
    fpath = join(kwargs['path'],fname)
    nc = Dataset(fpath,mode='r')
    return nc

def EA_data(nc):
    """ Returns: x,xname,ycrop,yname,img,ActualPhotonEnergy,WorkFunction,PE
    """
    LowEnergy=nc.variables['Attr_LowEnergy'][:][0]
    HighEnergy=nc.variables['Attr_HighEnergy'][:][0]
    ActualPhotonEnergy=nc.variables['Attr_ActualPhotonEnergy'][:][0]
    EnergyStep_Swept=nc.variables['Attr_EnergyStep_Swept'][:][0]
    EnergyStep_Swept_RBV=nc.variables['Attr_EnergyStep_Swept_RBV'][:][0]
    EperChannel=nc.variables['Attr_EnergyStep_Fixed_RBV'][:][0]
    GratingPitch=nc.variables['Attr_GratingPitch'][:][0]
    MirrorPitch=nc.variables['Attr_MirrorPitch'][:][0]

    WorkFunction=nc.variables['Attr_Energy Offset'][:][0]

    DetMode=nc.variables['Attr_DetectorMode'][:][0]         # BE=0,KE=1
    AcqMode= nc.variables['Attr_AcquisitionMode'][:][0]        # Swept=0, Fixed=1, BS=2
    LensMode=nc.variables['Attr_LensMode'][:][0]

    PassEnergyMode=nc.variables['Attr_PassEnergy'][:][0]
    PEdict={0:1,1:2,2:5,3:10,4:20,5:50,6:100,7:200,8:500}
    PE=PassEnergyMode

    #ActualPhotonEnergy,WorkFunction,PE=EA_metadata(nc)[0:3]
    data = nc.variables['array_data'][:][0]

    def SelectValue(which,x1,x2):
        if which == 0: value=x1
        if which == 1: value=x2
        return value

    ### Energy Scaling:
    Edelta = SelectValue(DetMode,-EnergyStep_Swept,EnergyStep_Swept)
    if AcqMode == 0:  # Swept
        Ehv=ActualPhotonEnergy
        Estart = SelectValue(DetMode, Ehv-LowEnergy, LowEnergy)
        #Estop  = SelectValue(DetMode, Ehv-HighEnergy, HighEnergy)
    if AcqMode >= 1:  # Fixed or Baby Swept
        Ecenter=nc.variables['Attr_CentreEnergy_RBV'][:][0]
        #print nc.variables#JM was here
        #print Ecenter,Edelta#JM was here
        Estart=Ecenter-(data.shape[1]/2.0)*Edelta
    Eunits=SelectValue(DetMode,"Binding Energy (eV)","Kinetic Energy (eV)")

    x=[Estart+Edelta*i for i,e in enumerate(data[0,:])]
    xname=Eunits

    ### Angular Scaling:
    if LensMode>-1: # Angular Modes  RE changed from >0 (Angular) to >-1 (all mode)
        CenterChannel=571
        FirstChannel=0
        Ddelta =0.0292717
        Dstart = (FirstChannel-CenterChannel)*Ddelta
        y=[Dstart+Ddelta*i for i,e in enumerate(data[:,0])]
        #getting rid of edges with no data
        data=nc.variables['array_data']
        #x1=338;x2=819 #old
        x1=338-100;x2=819-10
        datacrop=data[:,x1:x2]
        ycrop=y[x1:x2]
        yname='Degrees'
    else:
        ycrop,yname=None,'mm'
    return x,xname,ycrop,yname,datacrop,ActualPhotonEnergy,WorkFunction,PE


def EA_spectra(scanNum,EnergyAxis='KE',**kwargs):
    """
    Returns
        x = KE or BE energy scale; BE is calculated based on the wk in the SES and the mono energy
        y = Integrated intensity
        
    **kwargs:
    path: by default plot scans for the current data folder (as shown on detector panel)
    or specified folder path ending with '/':
        e.g. user : FilePath='/net/s29data/export/data_29idc/2018_2/UserName/netCDF/'
        e.g. staff: FilePath='/net/s29data/export/data_29idb/2018_2/netCDF/'
    prefix: by default, uses prefix as shown on detector panel ("EA_")
    
    Useage:
        x,y,img = EA_spectra(1)
        plt.imshow(img,extent = [min(x), max(x), min(y), max(y)], aspect = 'auto')
        plt.show())
    """
    nc=nc_unpack(scanNum,**kwargs)
    x,xname,y,yname,img,hv,wk,PE=EA_data(nc)
    y=np.array(y)
    img=img[0]
    if EnergyAxis == 'KE':
        x=np.array(x)
    else:
        x=hv-wk-np.array(x)
    return x, y, img

def EA_EDC(scanNum,EnergyAxis='KE',FilePath=None,Prefix=None):
    """
    Returns
        x = KE or BE energy scale; BE is calculated based on the wk in the SES and the mono energy
        y = Integrated intensity
    FilePath: by default plot scans for the current data folder (as shown on detector panel)
    or specified folder path ending with '/':
        e.g. user : FilePath='/net/s29data/export/data_29idc/2018_2/UserName/netCDF/'
        e.g. staff: FilePath='/net/s29data/export/data_29idb/2018_2/netCDF/'
    Prefix: by default, uses prefix as shown on detector panel ("EA_")
    
    Simple plot:   x,y=EA_Spectrum(ScanNum);plt.plot(x,y);plt.xlim(min(x),xmax(x));plt.show()
"""
    x, ang, img = EA_spectra(scanNum, EnergyAxis,FilePath,Prefix)
    y = np.asarray([sum(img[:,i]) for i in range(img.shape[1])])
    return x, y

def EA_metadata(ScanNum,FilePath=None,Prefix=None):
    """ Returns: ActualPhotonEnergy,WorkFunction,GratingPitch,MirrorPitch
    """
    nc=nc_unpack(ScanNum,FilePath,Prefix)
    # SES parameters
    LowEnergy=nc.variables['Attr_LowEnergy'][:][0]
    HighEnergy=nc.variables['Attr_HighEnergy'][:][0]
    EnergyStep_Swept=nc.variables['Attr_EnergyStep_Swept'][:][0]
    EnergyStep_Swept_RBV=nc.variables['Attr_EnergyStep_Swept_RBV'][:][0]
    EperChannel=nc.variables['Attr_EnergyStep_Fixed_RBV'][:][0]
    WorkFunction=nc.variables['Attr_Energy Offset'][:][0]
    DetMode=nc.variables['Attr_DetectorMode'][:][0]         # BE=0,KE=1
    AcqMode= nc.variables['Attr_AcquisitionMode'][:][0]        # Swept=0, Fixed=1, BS=2
    LensMode=nc.variables['Attr_LensMode'][:][0]
    PassEnergyMode=nc.variables['Attr_PassEnergy'][:][0]
    PEdict={0:1,1:2,2:5,3:10,4:20,5:50,6:100,7:200,8:500}
    PE=PassEnergyMode

    TEY=nc.variables['Attr_TEY'][:][0]

    # Mono parameters
    ActualPhotonEnergy=nc.variables['Attr_ActualPhotonEnergy'][:][0]
    GratingPitch=nc.variables['Attr_GratingPitch'][:][0]
    MirrorPitch=nc.variables['Attr_MirrorPitch'][:][0]
    Grating_Density=nc.variables['Attr_Grating_Density'][:][0]
    Grating_Slot=nc.variables['Attr_Grating_Slot'][:][0]
    GRT_Offset_1=nc.variables['Attr_GRT_Offset_1'][:][0]
    GRT_Offset_2=nc.variables['Attr_GRT_Offset_2'][:][0]
    GRT_Offset_3=nc.variables['Attr_GRT_Offset_3'][:][0]
    MIR_Offset_1=nc.variables['Attr_MIR_Offset_1'][:][0]
    b2_GRT1=nc.variables['Attr_b2-GRT1'][:][0]
    b2_GRT2=nc.variables['Attr_b2-GRT2'][:][0]
    b2_GRT3=nc.variables['Attr_b2-GRT3'][:][0]

    offset=[MIR_Offset_1,GRT_Offset_1,GRT_Offset_2,GRT_Offset_3]
    b2=[0,b2_GRT1,b2_GRT2,b2_GRT3]

    return WorkFunction,ActualPhotonEnergy,MirrorPitch,GratingPitch,Grating_Density,Grating_Slot,offset,b2


def Get_EDCmax(ScanNum,EnergyAxis='KE',FilePath=None,Prefix=None):
    x,y=EA_EDC(ScanNum, EnergyAxis,FilePath,Prefix)
    maxY= max(y)
    maxX=round(x[np.where(y == max(y))][0],3)
    return maxX,maxY  # energy position, intensity of the peak



def EDC_Series(first,last,countby, EnergyAxis='BE',title="",norm=None,FilePath=None,Prefix=None):
    """
    Plots a seriew of EA_Spectrum
    """
    if title == "":
        title="Scans: "+str(first)+"/"+str(last)+"/"+str(countby)
    fig = plt.figure(figsize=(6,6))
    a1 = fig.add_axes([0,0,1,1])
    for ScanNum in range(first,last+countby,countby):
        x,y=EA_EDC(ScanNum, EnergyAxis,FilePath,Prefix)
        if norm is not None: maxvalue=max(y)
        else: maxvalue=1
        plt.plot(x,y/maxvalue,label='#'+str(ScanNum))
        plt.legend(ncol=2, shadow=True, title=title, fancybox=True)    
        plt.grid(color='lightgray', linestyle='-', linewidth=0.5)
    a1.plot
    if EnergyAxis == 'BE':
        a1.set_xlim(max(x),min(x))
    plt.show()
    

def plot_nc(*ScanNum,**kwgraph):
    """
    ScanNum = Scan number to be plotted: single scan, or range (first,last,countby) to average.
    kwgraph = EDC / FilePath / Prefix
        - Transmission mode: angle integrated EDC.
        - Angular mode:
            default: band map only
            EDC = 'y' : angle integrated EDC only
            EDC = 'both': angle integrated EDC + band map
            EnergyAxis = KE (default) or BE (BE uses work function from SES)
    FilePath: by default plot scans for the current data folder (as shown on detector panel)
    or specified folder path ending with '/':
        e.g. user : FilePath='/net/s29data/export/data_29idc/2018_2/UserName/netCDF/'
        e.g. staff: FilePath='/net/s29data/export/data_29idb/2018_2/netCDF/'
    Prefix: by default, uses prefix as shown on detector panel ("EA_")

    """
    FilePath,Prefix,EDC,EnergyAxis,avg=None,None,None,'KE',None
    if kwgraph is not None:
        for key, value in list(kwgraph.items()):
            if key=='FilePath': FilePath=value
            if key=='Prefix':   Prefix=value
            if key=='EDC':   EDC=value
            if key=='EnergyAxis':   EnergyAxis=value
            if key=='avg':  avg=1
    #Get lens mode
    nc=nc_unpack(ScanNum[0],FilePath,Prefix)
    LensMode=nc.variables['Attr_LensMode'][:][0]        
    #Loading Scans ()
    first=ScanNum[0]
    if len(ScanNum)==1:
        last =ScanNum[0]
        countby=1
    else:
        last=ScanNum[1]
        countby=ScanNum[2]
    for n in range(first,last+countby,countby):
        x,intensity=EA_EDC(n,EnergyAxis,FilePath,Prefix)
        x,y,img =EA_spectra(n,EnergyAxis,FilePath,Prefix)
        if n == first:
            Spectra=intensity
            Img=img
        else:
            if avg == 1: #Summing the Scans
                print('averaging')
                Spectra=np.add(Spectra, intensity)
                Img=np.add(Img,img)

    #Getting plot size
    if LensMode == 0 or EDC != None and EDC != 'both': #Integrated Angle only
        hsize,vsize=6,3.5
    elif LensMode >0 and EDC == None:
        hsize,vsize=6,4
    elif LensMode >0 and EDC == 'both':
        hsize,vsize=6,8
    if kwgraph is not None:
        for key, value in list(kwgraph.items()):
            if key=='hsize': hsize=value
            if key=='vsize': vsize=value
    #plotting\
    if LensMode == 0 or EDC != None and EDC != 'both': #Integrated Angle only
        #print('p-DOS only')
        fig, ax = plt.subplots(figsize=(hsize,vsize))    # HxV
        ax.plot(x,Spectra)
        if EnergyAxis == "BE":
            ax.set_xlim(max(x),min(x))
        else:
            ax.set_xlim(min(x),max(x))
        ax.set(xlabel=EnergyAxis,ylabel='Intensity')
        ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        ax.grid(color='lightgray', linestyle='-', linewidth=0.5)
    elif LensMode >0 and EDC is None: #Imgage Only
        #print('Image Only')
        fig, ax = plt.subplots(figsize=(hsize,vsize))    # HxV
        if EnergyAxis == 'BE':
            fig=ax.imshow(Img,extent = [max(x), min(x), min(y), max(y)], aspect = 'auto')
        else:
            fig=ax.imshow(Img,extent = [min(x), max(x), min(y), max(y)], aspect = 'auto')
        ax.set(xlabel=EnergyAxis,ylabel="Angle")
    elif LensMode >0 and EDC == 'both':
        #print('both')
        fig, axes = plt.subplots(2,1,figsize=(hsize,vsize))    # HxV
        axes=np.array(axes)
        for (n,ax) in zip(list(range(2)),axes.flat):
            if n == 0:
                ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
                ax.grid(color='lightgray', linestyle='-', linewidth=0.5)
                ax.plot(x,Spectra)
                if EnergyAxis == "BE":
                    ax.set_xlim(max(x),min(x))
                else:
                    ax.set_xlim(min(x),max(x))
                ax.set(xlabel=EnergyAxis,ylabel='Intensity')
            if n == 1:
                if EnergyAxis == 'BE':
                    ax.imshow(Img,extent = [max(x), min(x), min(y), max(y)], aspect = 'auto')
                else:
                    ax.imshow(Img,extent = [min(x), max(x), min(y), max(y)], aspect = 'auto')
                ax.set(xlabel=EnergyAxis,ylabel='Angle')
    plt.tight_layout()
    plt.show()


def plot_nc_Sum(first,last,**kwgraph):

    FilePath,Prefix=None,None
    if kwgraph is not None:
        for key, value in list(kwgraph.items()):
            if key=='FilePath': FilePath=value
            if key=='Prefix':   Prefix=value
    for n in range(first,last+1):
        print(n)
        nc=nc_unpack(n,FilePath,Prefix)
        x,xname,ycrop,yname,img,hv,wk,PE=EA_data(nc)
        LensMode=nc.variables['Attr_LensMode'][:][0]
        if n == first:
            datasum = nc.variables['array_data']
            x,xname,ycrop,yname,img,hv,wk,PE=EA_data(nc)
        else:
            data = nc.variables['array_data']
            tmp=datasum
            datasum=np.add(tmp,data)
    crop_data=data[:,338:819]
    fig, ax = plt.subplots(figsize=(6,4))    # HxV
    fig=ax.imshow(crop_data.squeeze(),extent = [min(x), max(x), min(ycrop), max(ycrop)], aspect = 'auto')
    plt.show()

