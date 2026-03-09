import sys,os

#The sys._MEIPASS is variable that has the path to a temp folder where data folder is created. 
#Every time you execute the application a temp folder is created
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    IMAGES_PATH = os.path.join(sys._MEIPASS,'data','img') #type: ignore
else:
    IMAGES_PATH = os.path.join('data','img')
    
ICON_PATH = os.path.join(IMAGES_PATH,'icon.ico')
EDIT_IMG_PATH = os.path.join(IMAGES_PATH,'edit.png')
REFRESH_IMG_PATH = os.path.join(IMAGES_PATH,'refresh.png')
ROTATE_R_IMG_PATH = os.path.join(IMAGES_PATH,'rotate_left.png')
ROTATE_L_IMG_PATH = os.path.join(IMAGES_PATH,'rotate_right.png')
TRASH_IMG_PATH = os.path.join(IMAGES_PATH,'trash.png')