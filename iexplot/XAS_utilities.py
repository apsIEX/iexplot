from iexplot.plotting import find_closest

def _Norm2Edge_index(x,**kwargs):
    """
    returns i0,i1,i2,i3
    i0,i1 = index value for closest pre_edge values
    i2,i3 = index value for post_edge values

    if specified in index then just returns the values from kwargs, 
    else finds the closest x value and returns the index

    **kwargs
        pre_edge = ('index',1,6) default
        post_edge = ('index',-6,-1) default
            example using x-scaling  = ('x',416.5,420.01) 
        
    """
    kwargs.setdefault('pre_edge',('index',1,6))
    kwargs.setdefault('post_edge',('index',-6,-1))
    kwargs.setdefault('debug',False)
    
    if kwargs['pre_edge'][0]=='index':
        i0,i1 = kwargs['pre_edge'][1],kwargs['pre_edge'][2]
    elif kwargs['pre_edge'][0]=='x':
        i0, first_value = find_closest(x,kwargs['pre_edge'][1])
        i1, last_value   = find_closest(x,kwargs['pre_edge'][2])
        if kwargs['debug']:
            print(i0, first_value)
            print(i1, last_value)
    else:
        print('Not a valid pre_edge type')
    
    if kwargs['post_edge'][0]=='index':
        i2,i3 = kwargs['post_edge'][1],kwargs['post_edge'][2]
    elif kwargs['post_edge'][0]=='x':
        i2, first_value = find_closest(x,kwargs['post_edge'][1])
        i3, last_value   = find_closest(x,kwargs['post_edge'][2])
        if kwargs['debug']:
            print(i2, first_value)
            print(i3, last_value)
    else:
        print('Not a valid post_edge type')
        
    return i0,i1,i2,i3

    def Norm2Edge(x,y, **kwargs):
    """
    return the Normalized y data for an edge jump
    if the signal is negative it invertes to a positive edge jump

    **kwargs
        pre_edge ='index'/'x',first,last
        post_edge ='index'/'x',first,last
        verbose = True/False, prints edge jump
    """
    kwargs.setdefault('pre_edge',('index',1,6))
    kwargs.setdefault('post_edge',('index',-6,-1))
    kwargs.setdefault('verbose',False)
    kwargs.setdefault('debug',False)
    
    i0,i1,i2,i3 = _Norm2Edge_index(x,**kwargs)
    if kwargs['debug']:
        print('i0,i1,i2,i3 = ',i0,i1,i2,i3 )

    #positive edge jump
    if (y[0] < y[-1]):
        yN = y - np.average(y[i0:i1])
        edge = np.average(yN[i2:i3])
        if kwargs['verbose']:
            print('Edge jump: ', edge)
        return yN/edge
    
    #negative edge jump
    else: 
        yN = y -  np.average(y[i2:i3])
        edge = np.average(yN[i0:i1])
        if kwargs['verbose']:
            print('Edge jump: ', edge)
        return -yN/edge

def plot_Norm2Edge(x,y,**kwargs):
    """
    plots the normalized y data for an edge jump (XAS) vs x
    uses plot_1D

    **kwargs
        pre_edge ='index'/'x',first,last; 'pre_edge'=('index',1,6))
        post_edge ='index'/'x',first,last; post_edge=('index',-6,-1)
        plot_pre_post = True/False to add the pre-edge and post-edge regions to the plot
        verbose = True/False, prints edge jump
    """   
    kwargs.setdefault('pre_edge',('index',1,6))
    kwargs.setdefault('post_edge',('index',-6,-1))
    kwargs.setdefault('plot_pre_post',False)
    kwargs.setdefault('debug',False)
    
    if kwargs['debug']:
        print('plot_Norm2Edge kwargs\t',kwargs,'\n')

    y = Norm2Edge(x,y,**kwargs)
    plot_1D(x,y,**kwargs)
    if kwargs['plot_pre_post']:
        i0,i1,i2,i3 = _Norm2Edge_index(self,scanNum,**kwargs)
        
        plot_1D(x[i0:i1],y[i0:i1],marker="x")
        plot_1D(x[i2:i3],y[i2:i3],marker="x")
