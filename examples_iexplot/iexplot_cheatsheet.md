
- [**Loading the data using IEXdata**](#loading-the-data-using-iexdata)
    - [**Initializing the data dictionary**](#initializing-the-data-dictionary)
    - [**Updating the data dicitionary**](#updating-the-data-dicitionary)
- [**Plotting and accessing the data**](#plotting-and-accessing-the-data)
  - [**mda scans**](#mda-scans)
  - [**EA scans**](#ea-scans)
  - [**imagetool**](#imagetool)

---

# **<font color = 2061aa>Imports</font>**

    %config Completer.use_jedi = False  #for autocomplete
    %gui qt #qt must be run before imports
    
    from iexplot import * 
<br>

    %matplotlib qt for interactive plotting 
    %matplotlib inline to plot inline 
<br>

# **<font color = 2061aa>Loading the data using IEXdata</font>**
The data is loaded into a dictionary to future access

dtype = 'mda' (default), 'mdaEA' (use for ARPES)
<br>
<br>


## **<font color = 8a99ad>Initializing the data dictionary</font>**



loading a single scan

    data = IEXdata(scanNum,path=path,prefix=prefix,dtype='mdaEA')
  
loading a series of scans (last = inf loads to the last scan in the directory)

    data = IEXdata(first,last,path=path,prefix=prefix)
<br>


## **<font color = 8a99ad>Updating the data dicitionary</font>**
---
Load a single scan, default is to reload (overwrite) if the scan is already loaded

    data.update(scanNum)   

Only loads unloaded data in the range first,last inclusive

    data.update(first,last,overwrite=False)    


# **<font color = 2061aa>Plotting and accessing mda data</font>**

For the full data structure see iexplot/examples/IEX_nData. Below are a list of common functions/methods to access the data


## **<font color = 8a99ad>mda plotting and fitting</font>**
---

Plotting of 1D and 2D mda scans
    
    data.plot_mda(scanNum,detNum)

Quick fitting of 1D  mda scans #(AJE make function data.plot(scaNum,detNum))

    data.fit_mda(scanNum, detNum, fit_type)

Plotting the results of scan_sample_map with relevant detectors

    plot_sample_map(scanNum,detNum)

## **<font color = 8a99ad>mda positioners and detectors</font>**
Positioners - list all

    data.mda_positioners_list(scanNum)

Positioners - extract data #(AJE rename data.posx(scaNum,posNum)m data.posx_label)

    x = data.mda_positioner(scanNum,posNum=1) 
    x_label = data.mda_positioner_label(scanNum)

Detectors - list all

    data.mda_detectors_list(scanNum)

Detector data 

    y = data.mda_detector(scanNum, detNum)
    y_label = data.mda_detector_label

Metadata / header 

    data.mda_extra_pvs_all(scanNum)
    val = data.mda_extra_pvs(scanNum, search)

  


    
## **<font color = 8a99ad>EA scans</font>**
---

Plotting spectra image

    data.plot_EA(scanNum)

Plotting angle integrated (EDC) or fitting

    data.plot_EDC(scanNum)
    data.fit_EDC(scanNum)

spectra (image)

    img,xscale,yscale,x_label_,y_label = data.EA_spectra(scanNum)

EDCs (angle-integrated spectra)

    x,y,x_label = data.EA_EDC(scanNum)
    
Metadata / header

    data.EA_extras(scanNum,EAnum=1) #all metadata
    data.EA_exit_slit(scanNum,EAnum=1)
    data.EA_ringCurrent(scanNum,EAnum=1)
    data.EA_pass_energy(scanNum,EAnum=1)
    data.EA_sample(scanNum,EAnum=1)


Stacking EA spectra or EDCs

    stack = data.stack_mdaEA(*scanNum)
    k_stack = data.stack_mdaEA_kmap(*scanNum)

## **<font color = 8a99ad>imagetool</font>**
---
### **Plotting**
Creating a new IT window from numpy array or regular array

    tool.new(d)

Regular array from nData
    tools.new_nd(nd) #example is nd = data.stack_mdaEA


### **Adding imagetool plotting to data**

    add_IT(data)

Plotting single mda or EA scans

    data.it_mda(scanNum, detNum)
    data.it_EA(scanNum)

### **Cursor/Bin**



    tools.get_it_properties(IT_num) # gets cursor position and binwidth of an imagetool

    tools.cursor_bin(IT_num, **kwargs) #set cursor position and binwidth of an imagetool

Link multiple IT windows to set cursor position and binwidth to the same values

    tools.synch(*tool_nums, **kwargs)




### **Exporting Data**
---

Exporting an image/profile from an imagetool window

    tools.plot_export(IT_num, plot_name)

Exporting data from an imagetool window

    tools.export(IT_num, img_prof, plot_name)



### **Versioning** 
---

Retrieving list of all current imagetool instances

    tools.list()

Showing a specific instance of imagetool

    tools.show(IT_num)

### **Other useful functions**

Use an individual color from a colormap (index "i" out of length "size")

    color = colormap_colors(i, size, cmap_name)

legend outside

    plt.legend(bbox_to_anchor=(1,1))
    
    


