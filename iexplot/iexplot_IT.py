from iexplot.iexplot_nData import IEXdata
from iexplot.pyimagetool import ImageTool, RegularDataArray

def nData2ra(d):
    """
    converts an nData object to a RegularArray which is used by pyImageTool an returns ra
    d = nData object

    """
    img = d.data
    scales = list(d.scale[key] for key in d.scale.keys())
    units = list(d.unit[key] for key in d.unit.keys())
    #note that the scales are reverse between nData and ra
    ra=RegularDataArray(img,axes=scales.reverse(),dims=units.reverse())
    return ra

def IT_mdaEA(mdaScanNum,**kwargs):
    """
    to be run in ipython not in jupyter (cause the kernal to crash)
    multi=False stacks EA files from a single mda scan
    multi=True stacks EA files from multiple mda scans
    **kwargs:
        includes kwargs for loading data IEXdata
            path,prefix,dtype...
        include stackEA kwargs
            subset,EDConly
    """
    data=IEXdata(mdaScanNum, **kwargs)
    ra=data.stack_mdaEA(mdaScanNum,**kwargs)
    
    it=ImageTool(ra,'LayoutComplete')
    it.show()

    return it