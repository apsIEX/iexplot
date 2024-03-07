import os
import cv2 
from PIL import Image, ImageFont,ImageDraw
from matplotlib import font_manager
import numpy as np

def make_video(video_fname,fps,image_filename_list,image_folder_path,**kwargs):
    """
    video_fname = filename with extension, e.g. movie.mp4
    fps = frames per second
    image_filename_list = list of image filenames
    **kwargs:
        txt_list = list of values to add as annotation
        txt_xy = coordinates for annotation
        font_size = 50 is default
        font_name => 'Helvetica Neue' is default
        font_color => 'white' is default
        fourcc => 'MP4V' is default, also used 'XVID'
    """
    kwargs.setdefault('txt_list',None)
    kwargs.setdefault('txt_xy',(25,25))
    kwargs.setdefault('font_size',50)
    kwargs.setdefault('font_name','Helvetica Neue')
    kwargs.setdefault('font_color','white')
    kwargs.setdefault('fourcc','MP4V')

    #font stuff
    if kwargs['txt_list'] != None:
        try:
            font_file = font_manager.findfont(kwargs['font_name'])
            font = ImageFont.truetype(font_file, kwargs['font_size'])
        except:
            print('font_name = '+kwargs['font_name']+' was not found. Pick another font.')
            return

    # setting the frame width, height width from first image and initializing
    frame = cv2.imread(os.path.join(image_folder_path, image_filename_list[0]))
    height, width, layers = frame.shape  
    #fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    fourcc = cv2.VideoWriter_fourcc(*kwargs['fourcc'])
    video = cv2.VideoWriter(video_fname, fourcc, fps, (width, height))     

    #writing the frames
    for i,fname in enumerate(image_filename_list):
        if kwargs['txt_list'] != None:
            frame = Image.open(os.path.join(image_folder_path, fname))
            text = kwargs['txt_list'][i]
            frame_editable = ImageDraw.Draw(frame)
            frame_editable.text(kwargs['txt_xy'],text,font=font,fill=kwargs['font_color'] )
            frame.save('result.jpg')
            video.write(cv2.imread('result.jpg'))
            #video.write(np.array(frame))
        else:
            video.write(cv2.imread(os.path.join(image_folder_path, fname)))

    #cleaning up
    cv2.destroyAllWindows()
    video.release()