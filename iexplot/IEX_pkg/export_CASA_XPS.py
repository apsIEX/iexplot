import csv

def EDC_save_as_csv(data,scanNum,BE=True):
    """
    write EDC to a file for loading in CASA XPS
    data = IEXndata object
    """
    x,y,label = data.EA_EDC(scanNum,BE=BE)
    fname = 'EDC_'+str(scanNum).zfill(4)+'.vms'
    rows = zip(x,y)
    with open(fname, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)