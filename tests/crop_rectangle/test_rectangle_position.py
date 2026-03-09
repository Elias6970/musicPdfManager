from backend.app.crop_rectangle import CropRectangle
from frontend_pyqt.interactive_previewer.movable_rectangle import MovableRectangle
from PyQt6.QtCore import QRectF, QSize
import pytest, fitz
import numpy as np


def test_get_corners_rectangle_no_rotation():
    rect_x0 = 20.0
    rect_x1 = 420.0
    rect_y0 = 30.0
    rect_y1 = 530.0
    rectf = QRectF(rect_x0,
                   rect_y0,
                   rect_x1-rect_x0,
                   rect_y1-rect_y0)
    

    cr =CropRectangle(rectf,0)
    calculated_rect_corners = cr.get_rectangle_corners()

    rect_corners = np.array([[rect_x0,rect_y0],
                             [rect_x0,rect_y1],
                             [rect_x1,rect_y0],
                             [rect_x1,rect_y1]],dtype="float32")


    np.testing.assert_allclose(np.sort(calculated_rect_corners,axis=0),np.sort(rect_corners,axis=0))
    

def test_get_corners_rectangle_180_degrees_rotation():
    rect_x0 = 20.0
    rect_x1 = 420.0
    rect_y0 = 30.0
    rect_y1 = 530.0
    rectf = QRectF(rect_x0,
                   rect_y0,
                   rect_x1-rect_x0,
                   rect_y1-rect_y0)

    cr =CropRectangle(rectf,180)
    calculated_rect_corners = cr.get_rectangle_corners()

    rect_corners = np.array([[rect_x0,rect_y0],
                             [rect_x0,rect_y1],
                             [rect_x1,rect_y0],
                             [rect_x1,rect_y1]],dtype="float32")


    np.testing.assert_allclose(np.sort(calculated_rect_corners,axis=0),np.sort(rect_corners,axis=0))
    

    
    