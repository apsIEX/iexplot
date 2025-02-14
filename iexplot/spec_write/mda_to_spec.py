#Load needed python routines

import glob
import time
import numpy as np

from iexplot.mda import readMDA


def Filelist(path,prefix,scan_type,scan_details_list,**kwargs):
    """
    Gets number list from data directory

    filepath = path + prefix + filenum + suffix

    scan_type => Function
    scan_details_list =>
    """
    kwargs.update({'prefix':prefix})

    sf = path + prefix
    
    filenum  =  []
    for file in glob.glob(sf+'*'):
        filenum.append(int(file.split('/')[-1].split('_')[-1].split('.')[0]))
    filenum = np.sort(np.array(filenum))
    for file in filenum:
        print('Scan number: {}  {} {}'.format(str(file),scan_type(file,path,**kwargs),scan_details_list(file,path,**kwargs)))
        
def MakeSpecFile(spec_fpath,path,data_read,scan_type,scan_details_list):
    """
    Create spec file header
        structure: #F filename
                   #D date and time
                   #C Comment

    spec_fpath is full path with name for spec file with extension
    """
    kwargs.setdefault('spec_filename',)

    print('Creating spec file {}'.format(spec_fpath))
    sttime=time.time()

    sfile = open(spec_fpath, 'w')
    currenttime = time.asctime( time.localtime(time.time()) )
    comment = 'Made by python'
    sfile.writelines('#F {}\n'.format(spec_fpath))
    sfile.writelines('#D {}\n'.format(currenttime))
    sfile.writelines('#C {}\n'.format(comment))
    sfile.writelines('\n')

    filenum  =  []
    for file in glob.glob(sf+'*'):
        filenum.append(int(file.split('/')[-1].split('_')[-1].split('.')[0]))
    filenum = np.sort(np.array(filenum))
    for scan in filenum:
        print('Scan# {}'.format(scan))
        data = data_read(scanNum,path,**kwargs)
        dim=int(data[0]['acquired_dimensions'][0]) #using table scan writes full array
           
        #Write out current scan header
        sfile.writelines('#S {} {}\n'.format(data[0]['scan_number'],Scantype(sf,scan,Kappa=Kappa).split(' ')[0]))
        sfile.writelines('#D {}\n'.format(data[1].time))
        for key in data[0].keys():
            sfile.writelines('# {}\n'.format(data[0][key]))
        sfile.writelines('\n')
        #Column labels
        sfile.writelines('#L   ')
        sfile.writelines('{}   '.format(Scantype(sf,scan).split(' ')[0]))
        try:
            detnums = find_detectors(scanNum,endstation,path,**kwargs)
        except:
            detnums = {}
        for key in detnums.keys():
            sfile.writelines('{}   '.format(key))
        sfile.writelines('\n')
        #Write data
        try:
            for i in range(len(data[1].p[0].data[0:dim])):
                sfile.writelines('{}   '.format(data[1].p[0].data[i]))
                for key in detnums.keys():
                    sfile.writelines('{}   '.format(data[1].d[detnums[key]].data[i]))
                sfile.writelines('\n')
        except:
            sfile.writelines('\n') # for scans with no data

    sfile.close()
    print('File written in {} secs'.format(time.time()-sttime))

def UpdateSpecFile(sf,specfilename,specpath = '',**kwargs): 
    sfile = open(specpath+specfilename, 'r')
    file = sfile.readlines()
    sfile.close()
    numscans = 0
    for line in file:
        if '#S' in line:
            numscans += 1
    del file
    print('{} has {} scans'.format(specfilename,numscans))
    filenum  =  []
    for file in glob.glob(sf+'*'):
        filenum.append(int(file.split('/')[-1].split('_')[-1].split('.')[0]))
    filenum = np.sort(np.array(filenum))
    print('mda directory has {} scans'.format(filenum[-1]))
    if filenum[-1] > numscans:
        print('Updating file')
        newscans = filenum[numscans-1:]
        sfile = open(specpath+specfilename, 'a')
        for scan in newscans:
            data=readMDA(sf+'{:04}.mda'.format(scan))
            dim=int(data[0]['acquired_dimensions'][0]) #using table scan writes full array
            #Write out current scan header
            sfile.writelines('#S {} {}\n'.format(data[0]['scan_number'],Scantype(sf,scan).split(' ')[0]))
            sfile.writelines('#D {}\n'.format(data[1].time))
            for key in data[0].keys():
                sfile.writelines('# {}\n'.format(data[0][key]))
            sfile.writelines('\n')
            #Column labels
            sfile.writelines('#L   ')
            sfile.writelines('{}   '.format(Scantype(sf,scan).split(' ')[0]))
            try:
                detnums = find_detectors(scanNum,endstation,path,**kwargs)
            except:
                detnums = {}
            for key in detnums.keys():
                sfile.writelines('{}   '.format(key))
            sfile.writelines('\n')
            #Write data
            try:
                for i in range(len(data[1].p[0].data[0:dim])):
                    sfile.writelines('{}   '.format(data[1].p[0].data[i]))
                    for key in detnums.keys():
                        sfile.writelines('{}   '.format(data[1].d[detnums[key]].data[i]))
                    sfile.writelines('\n')
            except:
                sfile.writelines('\n')
        sfile.close()
        print('File updated')
    else:
        print('File is up to date')