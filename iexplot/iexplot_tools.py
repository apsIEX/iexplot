from iexplot.pynData.pynData import *
from iexplot.pyimagetool import ImageTool, RegularDataArray






def nData_stack(*args,**kwargs):
    """
    *args set of nData objects, where the first is the base object 

    **kwargs
        scaleList
    """
    kwargs.setdefault('ax','z')
    mscale = []
    for i,d in enumerate(args):
        if i == 0:
            stack = d.data
            scales = list(d.scale[key] for key in d.scale.keys())
            units = list(d.unit[key] for key in d.unit.keys())
            mscale.append(i)
        else:
            if len(stack.shape) == 1 : #appending 1D data

            
            

  
def EAImageTool(mdaScanNum,**kwargs):
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
    global it

    data=IEXdata(mdaScanNum, **kwargs)
    ra=data.stackmdaEA(mdaScanNum,**kwargs)
    
    it=ImageTool(ra,'LayoutComplete')
    it.show()

