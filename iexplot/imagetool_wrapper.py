import numpy as np
import re
import pyimagetool as it

from iexplot.pynData import nData


class TOOLS:
    """
    container for managing imagetool instances
    """
    def __init__(self, info = {}):  
        """
        add doc string here
        """
        self.info = info 
        self.instances = {}
        
        pass

    #Image Tool versioning  
    def list_all(self):
        """
        List all the image tool currently in memory
        """
        d = self._instances()
        print(d.keys())
    
    def obj(self, IT_num):
        """
        returns an ImageTool
        IT_num = number of the ImageTool you want to close
        """
        base = 'tool_'
        name = base + str(IT_num)
        d = self._instances()
        if name in d.keys():
            return d[name]
        else:
            print("ImageTool is not currently loaded, use .list_all() to show loaded tools")

    def show(self, IT_num):
        """
        Shows an ImageTool
        IT_num = number of the ImageTool you want to show
        """
        it=self.obj(IT_num)
        it.show()

    def close(self, IT_num):
        """
        Closes an ImageTool
        IT_num = number of the ImageTool you want to close
        """
        it=self.obj(IT_num)
        it.close()

    def kill(self,IT_num):
        it=self.obj(IT_num)
        try:
            name = it.name
            d = self._instances()
            d.pop(name)
            del it  ### This requires a more complicated process than just using del, need to revisit
        except:
            print("tool_"+str(IT_num)+" doesn't exist")

    def get_properties(self, IT_num,verbose=False):
        '''
        get the properties of the imagetool cursors and bins
        '''
        list = ['index','pos','binwidth']
        dictionary = {}
        tool = self.obj(IT_num)
        for key in list:
            obj = getattr(tool.pg_win.cursor,"_"+key)
            val = []
            for i in range(len(obj)):
                val.append(obj[i]._value)
            dictionary[key]= val
        val = []
        for i,ax in enumerate(['x','y','z']):
            val.append(tool.data.dims[i])
            
        dictionary['axes']=val
        if verbose:
            self.properties_string(it_num,verbose=verbose)
        return dictionary
    
    
    def properties_string(self,it_num,verbose=False):
        """
        returns the properies as a string 
        """
        s = ''
        for key, val in self.get_properties(0).items():
            s+= str(key)+': '+str(val)+'\n'
        if verbose:
            print(s[:-1])
        return s[:-1]

    def cursor_bin(self,IT_num, **kwargs):
        '''
        edits specific values for cursor/binwidth 
        
        kwargs:
            c_x, c_y, c_z = cursor positions in terms of coordinates
                None (default) will use current values
            c = tuple of cursor positions in terms of coordinates (will supercede individual values)
                
            b_x, b_y, b_z = cursor positions in terms of coordinates
                None (default) will use current values
            b = tuple of cursor positions in terms of coordinates (will supercede individual values)
            
        '''
        
        kwargs.setdefault('c_x',None)
        kwargs.setdefault('c_y',None)
        kwargs.setdefault('c_z',None)
        kwargs.setdefault('b_x',None)
        kwargs.setdefault('b_y',None)
        kwargs.setdefault('b_z',None)
        kwargs.setdefault('debug', False)
        
        axis_list=['x','y','z']
        
        if 'c' in kwargs:
            for i,cs in enumerate(kwargs['c']):
                kwargs['c_'+axis_list[i]] = cs
        if 'b' in kwargs:
            for i,cs in enumerate(kwargs['b']):
                kwargs['b_'+axis_list[i]] = cs
        
        tool = self.obj(IT_num)
        info_dict = self.get_properties(IT_num)
        cursor = info_dict['pos']
        binwidth = info_dict['binwidth']
        
        c_new =[]
        b_new=[]
        
        for i, c in enumerate(cursor):
            
            if kwargs['c_'+axis_list[i]] == None:
                c_new.append(cursor[i]) 
            else:
                c_new.append(kwargs['c_'+axis_list[i]])
                
            if kwargs['b_'+axis_list[i]] == None:
                b_new.append(binwidth[i])
            else:
                b_new.append(kwargs['b_'+axis_list[i]])

        if kwargs['debug']:
            print('cursor pos: ',c_new)
            print('bin width: ',b_new)
        
        #updating the pg_win 
        for i,n in enumerate(c_new):
            tool.pg_win.cursor.set_pos(i,n)
            tool.pg_win.cursor._binwidth[i].set_value(b_new[i])        
                    
        return c_new, b_new

    #Image Tool version book keeping - internal
    def _instances(self):
        return self.instances
    
    def _next_it(self):
        """
        Automatically iterates imagetool name each time a new window is created
        """
        v_array = np.empty(0)
        print('instances')
        print(self.instances)
        for key in self.instances.keys():
            base, v = re.split('_',key)
            v_array = np.append(v_array, int(v))
            
        if v_array.shape==(0,):
            v_next = 0
            base = 'tool_'
        else:    
            print(type(v_array),v_array)            
            v_max = np.max(v_array)
            v_next = int(v_max) + 1
            base = 'tool_'
            
        return base, v_next

    def _append_instance(self, tool):
        """
        Adds a new instance of imagetool to the instances dictionary
        """
        base, v_next = self._next_it()
        name = base + str(v_next)
        self.instances[name] = tool
        tool.name = name

        return name
    
    def new(self, d):
        '''
        creates a new instance of imagetool and adds it to the tool class

        d = data of type RegularDataArray or numpy array

        '''
        try: 
            #if type(d) == it.RegularDataArray:
            obj = it.imagetool(d)
            name = self._append_instance(obj)
            obj.setWindowTitle(name)
            obj.show()
            print('name: ',name)
            return(obj)
            
        except: 
            print('Not a valid data type, must be nData or RegularDataArray')

    def export_dictionary(self, img_prof):
        '''
        prof = [ax, unit, dimension]
        img = [ax, dimy, dimx]
        '''
        axis_dict = {'prof_h':['x','Intensity',1], 
                     'prof_v':['y','Intensity',0], 
                     'prof_d':['z','Intensity',2], 
                     'img_main':['xy',0,1], 
                     'img_v':['zy',2,1], 
                     'img_h':['xz',0,2]
                     }
        
        return axis_dict[img_prof]
    

    def export(self, IT_num, plot_name):
        """
        extract data from an individual plot in imagetool

        IT_num = imagetool window number
                
                
        img_prof = 
                    'prof_h' => Intensity vs x 
                    'prof_v' => Intensity vs y 
                    'prof_d' => Intensity vs z
                    'img_main' => Intensity(x,y) 
                    'img_v' => Intensity(z,y) 
                    'img_h' => Intensity(x,z) 
        """


        it = self.obj(IT_num)

        axes, dim_y, dim_x = self.export_dictionary(plot_name)
        data = it.get(axes)
   
        cursor_info = self.get_properties(IT_num)

        return data, cursor_info, dim_y, dim_x


 

    def synch(self,*tool_nums,**kwargs):
        """
        synchs the cursors for several tools based on tool_nums specified.
        the first tool_num is the parent (i.e. those cursor info is used)
        kwargs
            c_x, c_y, c_z = cursor positions in terms of coordinates
                None (default) will use current values
            c = tuple of cursor positions in terms of coordinates (will supercede individual values)

            b_x, b_y, b_z = cursor positions in terms of coordinates
                None (default) will use current values
            b = tuple of cursor positions in terms of coordinates (will supercede individual values)
        """
        
        for i,tool_num in enumerate(tool_nums):
            if i == 0:
                c_new, b_new = self.cursor_bin(tool_num, **kwargs)
            else:
                self.cursor_bin(tool_num, c = c_new, b = b_new)

