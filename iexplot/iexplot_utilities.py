from numpy import inf

def _make_num_list(*nums):
    """
    Making a shortlist based on *num
    *num =>
        nums: for a single scan
        first,last: for all numbers between and including first and last; last can be inf
        first,last,countby: to load a subset
        [num1,num2]: to load a subset does not need to be consecutive  
    """

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
        print("nums: ",nums)
        print("llist",llist)
    llist.sort()
    #dealing with inf
    last = llist[-1]
    if inf in nums:
        numslist = list(nums)
        numslist[numslist.index(inf)] = last
        nums = tuple(numslist)
    #creating number list
    num_list = _make_num_list(*nums)
    shortlist = []
    for n in num_list: 
        if n in llist:
            shortlist.append(n)
    if kwargs["debug"]:
        print("shortlist: ",shortlist)
    return shortlist
    