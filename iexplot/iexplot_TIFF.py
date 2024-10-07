import matplotlib.pyplot as plt
import numpy as np
import tifffile

from iexplot.utilities import _shortlist, make_num_list 
from iexplot.plotting import plot_1D, plot_2D, plot_3D
from iexplot.pynData.pynData import nstack



def tiff_metadata():
    """
    """
    with tifffile.TiffFile('/net/s29data/export/data_29idb/2024_2/20240718/TIFF/TIFF_4740.TIFF') as tif:
        for page in tif.pages:
            print(page)
            for tag in page.tags:
                tag_name, tag_value = tag.name, tag.value
                print('\t', tag_name, ': ', tag_value)

    def read_tiff():
        tiff_file = f'/home/beams/29IDUSER/Documents/User_Folders/Wootton/2024/TIFF/TIFF_{tiff_num:04d}.TIFF'
        ts = get_tiff_ts(tiff_file)
        img = tifffile.imread(f'/net/s29data/export/data_29idb/2024_2/20240718/TIFF/TIFF_4712.TIFF')

class PLOT_TIFF:
    """
    adds tiff plotting functions to the IEXnData class
    """

    def __init__():
        pass
