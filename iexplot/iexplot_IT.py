        
def nData2ra(d):
    """
    converts an nData object to a RegularArray which is used by pyImageTool an returns ra
    d = nData object

    """
    img = d.data
    scales = list(d.scale[key] for key in d.scale.keys())
    units = list(d.unit[key] for key in d.unit.keys())
    #note that the scales are reverse between nData and ra
    ra=RegularDataArray(img,axes=scales.reverse(),dims=units.reverse())
    return ra