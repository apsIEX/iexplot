import os
from numpy import inf

def make_nstack_list(obj,*nums,**kwargs):
    """
    obj is ndata object (e.g. data.AD or data.mda or data.mda[scanNum].EA)
    nums is scanNum or EAnum
    **kwargs from make_num_list):
        none
    """
    
    nData_list=[]
    scanNum_list = make_num_list(*nums,**kwargs)
    for scanNum in scanNum_list:
        nData_list.append(obj[scanNum])
    return nData_list

def make_num_list(*nums,**kwargs):
    """
    Making a shortlist based on *num
    *num =>
        nums: for a single scan
        first,last: for all numbers between and including first and last; last can be inf
        first,last,countby: to load a subset
        [num1,num2]: to load a subset does not need to be consecutive  
    """
    kwargs.setdefault('debug',False)
    if kwargs['debug']:
        print('_make_num_list')
        print('nums: ',*nums)

    num_list=[]
    if len(nums) == 1:
        if type(nums[0]) == int:
            num_list = [nums[0]]
        elif type(nums[0]) == list:
            num_list = nums[0]
        else:
            print(nums,'not a valid argument, see doc string')    
            return None
    elif len(nums) >= 2:
        if len(nums) == 2:
            first,last = nums
            countby = 1
        elif len(nums) == 3:
            first,last,countby = nums
        else:
            print(nums,'not a valid argument, see doc string') 
            return None
        for n in range(int(first),int(last+countby),int(countby)):
            num_list.append(n)
    else:
        print(nums,'not a valid argument, see doc string') 
        return None

    return num_list

def _shortlist(*nums,llist,**kwargs):
    """
    Making a shortlist based on *num
    *num =>
        nums: for a single scan
        inf: for all num in longlist
        first,last: for all numbers between and including first and last; last can be inf
        first,last,countby: to load a subset
        [num1,num2]: to load a subset of scans
    kwargs:
        debug=False
    """
    kwargs.setdefault("debug",False)
    
    if kwargs['debug']:
        print('\n_shortlist')
        print("\tnums: ",nums)
        print("\tllist",llist)

    llist.sort()

    ### dealing with inf
    last = llist[-1]
    if inf in nums:
        numslist = list(nums)
        numslist[numslist.index(inf)] = last
        nums = tuple(numslist)

    #creating number list
    num_list = make_num_list(*nums)
    shortlist = []
    for n in num_list: 
        if n in llist:
            shortlist.append(n)
    if kwargs["debug"]:
        print("shortlist: ",shortlist)
    return shortlist

    
def take_closest_value(my_list,my_number):
    """
    Given a list of integers, I want to find which number is the closest to a number x.
    
    Previously: TakeClosest
    """
    return min(my_list, key=lambda x:abs(x-my_number))

#########################################################################################################
def _dirScanNumList(path,prefix,extension):
    """
    returns a list of scanNumbers for all files with prefix and extension in path
    """
    #so that path ends in /
    path = os.path.join(path,'')

    #getting and updating directory info
    allfiles = [f for f in os.listdir(path) if os.path.isfile(path+f)]
    #print(allfiles)

    split=prefix[-1] 
    allfiles_prefix = [x for (i,x) in enumerate(allfiles) if allfiles[i].split(split)[0]==prefix[:-1]] 
    #print(allfiles_prefix)

    allfiles_dtype = [x for (i,x) in enumerate(allfiles_prefix) if allfiles_prefix[i].split('.')[-1]==extension]
    #print(allfiles_dtype)

    allscanNumList = [int(allfiles_dtype[i][allfiles_dtype[i].find('_')+1:allfiles_dtype[i].find('_')+5]) for (i,x) in enumerate(allfiles_dtype)]
    #print(allscanNumList)

    return allscanNumList       

def  _create_dir_shortlist(*scanNums,path,prefix,ext, **kwargs):
    """
  *scanNums =>
        scanNums: for a single scan
        inf: for all num in longlist
        first,last: for all numbers between and including first and last; last can be inf
        first,last,countby: to load a subset
        [num1,num2]: to load a subset of scans
    path = full path to directory of files
    prefix = part of filename up to number
    ext = filename extension

    **kwargs:
        excluded_list 
        overwrite
    """
    kwargs.setdefault('debug',False)
    kwargs.setdefault('overwrite',True)
    kwargs.setdefault('excluded_list',[])

    if kwargs['debug']:
        print("\n_create_shortlist")
        print('\tscans : ',scanNums)
        print('\tkwargs:',kwargs)

    longlist = _dirScanNumList(path,prefix,ext)
    if len(longlist)<1:
        return []
    shortlist = _shortlist(*scanNums,llist=longlist,**kwargs)
    if kwargs['overwrite'] == False: #only load new scans
        shortlist =[x for x in shortlist if x not in kwargs['excluded_list']]
        #remove duplicates if any
        shortlist.sort() 
    return shortlist