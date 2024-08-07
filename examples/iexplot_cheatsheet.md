
- [**Loading the data using IEXdata**](#loading-the-data-using-iexdata)
    - [**Initializing the data dictionary**](#initializing-the-data-dictionary)
    - [**Updating the data dicitionary**](#updating-the-data-dicitionary)
- [**Plotting and accessing the data**](#plotting-and-accessing-the-data)
  - [**mda scans**](#mda-scans)
  - [**EA scans**](#ea-scans)
  - [**imagetool**](#imagetool)

---

# **<font color = 2061aa>Loading the data using IEXdata</font>**
The data is loaded into a dictionary to future access
<br>
<br>


## **<font color = 8a99ad>Initializing the data dictionary</font>**
---

loading a single scan

    data = IEXdata(scanNum,path=path,prefix=prefix)
  
loading a series of scans (last = inf loads to the last scan in the directory)

    data = IEXdata(first,last,path=path,prefix=prefix)
<br>
<br>

## **<font color = 8a99ad>Updating the data dicitionary</font>**
---
Load a single scan, default is to reload (overwrite) if the scan is already loaded

    data.update(scanNum)   

Only loads unloaded data in the range first,last inclusive

    data.update(first,last,overwrite=False)    

---

# **<font color = 2061aa>Plotting and accessing the data</font>**

For the full data structure see iexplot/examples/IEX_nData. Below are a list of common functions/methods to access the data


## **<font color = 8a99ad>mda scans</font>**
---

Plotting of 1D and 2D mda scans #(AJE make function data.plot(scaNum,detNum))
    
    data.plotmda(scanNum,detNum)


Plotting the results of scan_sample_map with relevant detectors

    plot_sample_map(scanNum,detNum)

Positioners - list all #(AJE make function data.posAll(scaNum))

    data.mda[scanNum].posAll  

Positioners - extract data #(AJE rename data.posx(scaNum,posNum)m data.posx_label)

    x = data.mdaPos(scanNum,posNum=1) 
    x_label = data.mdaPos_label(scanNum)

Detectors - list all #(AJE make function mda_detAll(scaNum))

    data.mda[scanNum].detAll  

Detector data #(AJE rename data.det(scaNum,detNum))

    y = data.mdaDet(scanNum,detNum) 
    y_label = data.mdaDet_label(scanNum,detNum)

Metadata / header #(AJE make function data.header(scaNum))

    data.mda[scanNum]header(scanNum)

  


    
## **<font color = 8a99ad>EA scans</font>**
---

Plotting spectra image

    data.plotEA(scanNum)

Plotting angle integrated (EDC)

    data.plotEDC(scanNum,EAnum)

spectra (image)

    img,xscale,yscale,x_label_,y_label = data.EAspectra(scanNum)

EDCs (angle-integrated spectra)

    x,y,x_label = data.EAspectraEDC(scanNum)
    
Metadata / header
    data.EAheader_all(scanNum,EAnum)
    data.EAheader_sample(scanNum,EAnum)
    data.EAheader_HVscanInfo(scanNum,EAnum)
    data.EAheader_beamline(scanNum,EAnum)

Stacking EA spectra or EDCs

    data.stack_mdaEA(*scanNum)

## **<font color = 8a99ad>imagetool</font>**
---
### **Plotting**

Plotting single mda scan

    data.it_mda(scanNum, detNum)

Plotting single or stacked EA scans

    data.it_mdaEA(scanNum, E_unit = 'KE')

Creating a new IT window from pynData object d

    tool.new(d)

### **Cursor/Bin**

Retrieve cursor position and binwidth of an IT window:

    tool.get_it_properties(IT_num)

Set cursor position and binwidth of an IT window:

    tool.cursor_bin(IT_num, **kwargs)

Link multiple IT windows to set cursor position and binwidth to the same values

    tool.synch(*tool_nums, **kwargs)




### **Exporting Data**
---

Exporting an image/profile from an imagetool window

    tool.plot_export(IT_num, plot_name)

Exporting data from an imagetool window

    tool.export(IT_num, img_prof, plot_name)



### **Versioning** 
---

Retrieving list of all current imagetool instances

    data.IT_list()

Showing a specific instance of imagetool

    data.IT_show(IT_num)

### **Other useful functions**

Use an individual color from a colormap (index "i" out of length "size")

    color = colormap_colors(i, size, cmap_name)



