from numpy import inf


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
        print("nums: ",nums)
        print("llist",llist)
    llist.sort()
    if type(nums[0]) is list:
        shortlist=nums[0]
    else:
        if len(nums)==1:
            if nums[0] != inf:
                first,last,countby=nums[0],nums[0],1
            else:
                first,last,countby=llist[0],llist[-1],1
        elif len(nums)==2:
            first,last=nums
            countby=1
        elif len(nums)==3:
            first,last,countby=nums
        if last == inf:
            last=llist[-1]
        #print(first,last,countby)
        shortlist=[]

        for n in range(first,last+countby,countby): 
            if n in llist:
                shortlist.append(n)
    if kwargs["debug"]:
        print("shortlist: ",shortlist)
    return shortlist
    