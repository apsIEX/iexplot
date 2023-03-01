
- [**Loading the data using IEXdata**](#loading-the-data-using-iexdata)
    - [**Initializing the data dictionary**](#initializing-the-data-dictionary)
    - [**Updating the data dicitionary**](#updating-the-data-dicitionary)
- [**Plotting and accessing the data**](#plotting-and-accessing-the-data)
  - [**mda scans**](#mda-scans)
  - [**EA scans**](#ea-scans)

---

# **Loading the data using IEXdata**
The data is loaded into a dictionary to future access
<br>
<br>


### **Initializing the data dictionary**
---

loading a single scan

    data = IEXdata(scanNum,path=path,prefix=prefix)
  
loading a series of scans (last = inf loads to the last scan in the directory)

    data = IEXdata(first,last,path=path,prefix=prefix)
<br>
<br>

### **Updating the data dicitionary**
---
Load a single scan, default is to reload (overwrite) if the scan is already loaded

    data.update(scanNum)   

Only loads unloaded data in the range first,last inclusive

    data.update(first,last,overwrite=False)    

# **Plotting and accessing the data**
For the full data structure see iexplot/examples/IEX_nData. Below are a list of common functions/methods to access the data


## **mda scans**
---

Plotting of 1D and 2D mda scans 
    
    data.plotmda(scanNum,detNum)


Plotting the results of scan_sample_map with relevant detectors

    plot_sample_map(scanNum,detNum)

Positioner data

    x = data.mdaPos(scanNum,posNum=1) 
    x_label = mdaPos_label(scanNum)

Detector data

    y = data.mdaDet(scanNum,detNum) 
    y_label = data.mdaDet_label(scanNum,detNum)

Metadata / header

    data.header(scanNum)
    
## **EA scans**
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