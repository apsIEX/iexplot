# **Loading the data using IEXdata:
the data is loaded into a dictionary to future access

## **initializing the dictionary
loading a single scan
	'''
  data = IEXdata(scanNum,path=path,prefix=prefix)
  '''
loading a series of scans (last = inf loads to the last scan in the directory)
	data = IEXdata(first,last,path=path,prefix=prefix)
