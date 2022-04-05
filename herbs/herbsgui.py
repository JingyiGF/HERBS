import os
from os.path import dirname, realpath, join
import sys
from sys import argv, exit
from pathlib import Path
import queue
import requests

import pickle
import csv
import nibabel as nib
import tifffile as tiff
from aicspylibczi import CziFile


import numpy as np
import pandas as pd
import math
import scipy
import scipy.io
import scipy.ndimage as ndi
from scipy.ndimage import map_coordinates
from natsort import natsorted, ns

import cv2
opencv_ver = (cv2.__version__).split('.')
from numba import jit
import colorsys


import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtMultimedia import QSound
# from PyQt5 import uic
from PyQt5.uic import loadUiType
import pyqtgraph as pg
pg.setConfigOption('imageAxisOrder', 'row-major')
pg.setConfigOption('useNumba', True)
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph import metaarray

import warnings


from .uuuuuu import *
from .czi_reader import CZIReader

from .atlas_downloader import *
from .atlas_loader import AtlasLoader
from .atlas_view import AtlasView
from .slice_stacks import *

from .image_reader import ImageReader, ImagesReader
from .image_stacks import *
from .image_curves import *
from .image_view import ImageView

from .label_tree import *
from .layers_control import *
from .object_control import *
from .toolbox import ToolBox


herbs_style = '''
QMainWindow {
    background-color: rgb(50, 50, 50);
}

/*---------------------- Slider -----------------------*/
QSlider {
    min-height: 20px;
    max-height: 20px;
    background: transparent;
}

QSlider::groove:horizontal {
    border: 1px solid #999999;
    height: 2px; /* the groove expands to the size of the slider by default. by giving it a height, it has a fixed size */
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B1B1B1, stop:1 #c4c4c4);
    margin: 0px 12px;
}

QSlider::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #8f8f8f);
    border: 1px solid #5c5c5c;
    width: 2px;
    height: 30px;
    margin: -6px -2px; /* handle is placed by default on the contents rect of the groove. Expand outside the groove */
    border-radius: 0px;
}

/*---------------------- LineEdit -----------------------*/
QLineEdit { 
    background-color: transparent;
    color: white;
}

/*---------------------- SpinBox -----------------------*/
QSpinBox {
    padding-right: 0px; /* make room for the arrows */
    border-width: 0;
}

QSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right; /* position at the top right corner */
    width: 15px; 
    border-width: 0px;
}

QSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right; /* position at bottom right corner */
    width: 15px;
    border-width: 0px;
}

QSpinBox::up-button:hover {
    background-color: #282828;
}

QSpinBox::down-button:hover {
    background-color: #282828;
}

QSpinBox::up-button:pressed {
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #282828, stop: 1 #323232);
}

QSpinBox::down-button:pressed {
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #323232, stop: 1 #282828);
}

QSpinBox::up-arrow {
    image: url(icons/up-arrow.svg);
    width: 7px;
    height: 7px;
}

QSpinBox::down-arrow {
    image: url(icons/down-arrow.svg);
    width: 7px;
    height: 7px;
}

/*---------------------- DoubleSpinBox -----------------------*/
QDoubleSpinBox {
    padding-right: 0px; 
    border-width: 0;
}

QDoubleSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right; /* position at the top right corner */
    width: 15px; 
    border: None;
}

QDoubleSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right; /* position at bottom right corner */
    width: 15px;
    border: None;
}

QDoubleSpinBox::up-button:hover {
    background-color: #282828;
}

QDoubleSpinBox::down-button:hover {
    background-color: #282828;
}

QDoubleSpinBox::up-button:pressed {
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #282828, stop: 1 #000000);
}

QDoubleSpinBox::down-button:pressed {
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #000000, stop: 1 #282828);
}

QDoubleSpinBox::up-arrow {
    image: url(icons/up-arrow.svg);
    width: 7px;
    height: 7px;
}

QDoubleSpinBox::down-arrow {
    image: url(icons/down-arrow.svg);
    width: 7px;
    height: 7px;
}
'''


tab_style = '''
/*---------------------- QTabWidget -----------------------*/
QTabWidget{
    background-color: transparent;
    margin-bottom: 0px;

}

QTabWidget::pane {
    background-color: transparent;
    margin-left: 0px;
    padding-left:0px;
    border-top: 1px solid #747a80;
    border-left: 1px solid #747a80;
    border-right: 1px solid #747a80;
    border-bottom: 1px solid #747a80;
    margin-bottom: 0px;
}

QTabWidget::tab-bar {
    bottom: 0;
    border: 1px solid gray;
}

QTabBar::tab {
    background-color: #3c3f41;
    height:30px;
    width: 30px;
    border-bottom: 3px solid #323232;
    margin: 0px;
    padding-top: 5px;
    padding-left: 6px;
}

QTabBar::tab:selected {
    background: #4e5254;
    border-bottom: 3px solid #747a80;
}

QTabBar::tab:hover{
    background: #27292a;
}

QGroupBox {
    background-color: transparent; 
    border: 1px solid; 
    border-radius: 3px; 
    padding-top: 3px; 
    padding-bottom: 3px; 
    margin-top: 0px
}


'''


image_tool_frame_style = '''
QFrame {
    background-color: #535352;
    border-top-color: #2a2a2b;
    border: 2px solid;
    border-radius: 0px;
    padding-top: 0px;
    padding-bottom: 0px; 
    margin-top: 0px;
} 

'''

sidebar_title_label_style = '''
QLabel{
    color: white;
    background: #747a80;
    width: 300px;
    height: 20px;
    padding-bottom: 5px;
    padding-left: 5px;
    padding-top: 2px;
}

'''

ic_bnt_style = '''

QPushButton {
    border : None; 
    background: transparent;
    margin: 0px;
    padding-top: 0px;
    border-radius: 0px;
    min-width: 32px;
    min-height: 30px;
}
QPushButton:checked {
    background-color: #383838; 
    border: 1px solid #636363; 
}

QPushButton:pressed {
    background-color: #383838; 
    border: 1px solid #636363; 
}

QPushButton:hover {
    background-color: #383838; 
    border: 1px solid #636363; 
}

'''

toolbar_style = '''
QToolBar::separator { 
    color: white;
    background-color: gray;
    width: 1px;
    height: 10px;
    border: 5px solid rgb(50, 50, 50);
}


QToolBar {
    color: rgb(255, 255, 255);
    background-color: rgb(50, 50, 50);
    border: None;
    selection-color: rgb(50, 50, 50);
    selection-background-color: #27292a;
    spacing: 0px;
}

QToolButton {
    border-top: 2px solid rgb(50, 50, 50);
    border-bottom: 2px solid rgb(50, 50, 50);
}


QToolButton::hover {
    background-color: #27292a;
    border-top: 2px solid #27292a;
    border-bottom: 2px solid #27292a;
}

QToolButton::checked {
    border-bottom: 2px solid gray;
}

QPushButton {
    background-color: rgb(50, 50, 50);
    border: 0px solid gray;
    width: 32px;
    height: 32px;
    margin: 0px;
    padding: 0px;
}

QPushButton::hover {
    background-color: #27292a;
}

QLabel {
    color: #d6d6d6;
    background-color: rgb(50, 50, 50);
}

QLineEdit { 
    border: 1px solid gray;
}



QSlider::groove:horizontal {
    border: 1px solid #999999;
    height: 2px; 
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B1B1B1, stop:1 #c4c4c4);
    margin: 2px 0;
}

QSlider::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #8f8f8f);
    border: 1px solid #5c5c5c;
    width: 18px;
    margin: -2px 0; /* handle is placed by default on the contents rect of the groove. Expand outside the groove */
    border-radius: 3px;
}

'''

script_dir = dirname(realpath(__file__))
FORM_Main, _ = loadUiType((join(dirname(__file__), "main_window.ui")))


class HERBS(QMainWindow, FORM_Main):
    def __init__(self, parent=FORM_Main):
        super(HERBS, self).__init__()
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.setWindowTitle("HERBS - Histological E-data Registration in Rat Brain Space")

        self.num_windows = 1

        self.np_onside = None
        self.atlas_rect = None
        self.histo_rect = None
        self.small_atlas_rect = None
        self.small_histo_rect = None

        self.atlas_folder = None

        self.small_mesh_list = {}
        self.lasso_pnts = []
        self.lasso_is_closure = False
        self.eraser_is_on = False

        self.atlas_corner_points = None
        self.atlas_side_lines = None
        self.atlas_tri_data = []
        self.atlas_tri_inside_data = []
        self.atlas_tri_onside_data = []

        self.histo_corner_points = None
        self.histo_side_lines = None
        self.histo_tri_data = []
        self.histo_tri_inside_data = []
        self.histo_tri_onside_data = []

        self.working_img_mask_data = None
        self.working_atlas_mask = None

        self.working_blob_data = []

        self.working_img_drawing_data = []
        self.working_img_cell_data = []
        self.working_img_cell_size = []
        self.working_img_probe_data = []
        self.working_img_virus_data = None
        self.working_img_contour_data = None
        self.cell_count = 0

        self.working_atlas_probe = []
        self.working_atlas_cell = []
        self.working_atlas_virus = []
        self.working_atlas_drawing = []
        self.working_atlas_contour = []

        self.working_atlas_text = []
        self.working_img_text = []

        self.a2h_transferred = False
        self.h2a_transferred = False
        self.project_method = 'pre plan'
        self.register_method = 0

        self.is_projected = False
        self.project_matrix = None
        self.action_after_projection = {}

        self.registered_probe_count = 1
        self.registered_prob_list = []


        self.register_cell_list = []
        self.registered_probe_pnts_list = []
        self.registered_probe_lines_list = []
        self.registered_virus_dict = {}
        self.registered_boundary_dict = {}

        self.probe_data_dicts = []
        self.prob_list = []
        self.probe_lines_3d_list = []
        self.probe_lines_2d_list = []

        self.previous_checked_label = []
        self.atlas_display = 'coronal'
        self.show_child_mesh = False
        self.warning_status = False

        self.current_checked_tool = None

        self.atlas_adjusted_corner_points = None
        self.atlas_adjusted_side_lines = None
        self.atlas_adjusted_tri_onside_data = None

        self.histo_adjusted_corner_points = None
        self.histo_adjusted_side_lines = None
        self.histo_adjusted_tri_onside_data = None

        self.is_pencil_allowed = False
        self.pencil_size = 3
        self.pencil_color = (128, 128, 128, 1)

        self.tip_length = 175
        self.channel_size = 20
        self.channel_number_in_banks = (384, 384, 192)

        self.image_mode = None
        self.process_img = None

        # ---------------------
        self.tool_box = ToolBox()
        self.toolbar_wrap_action_dict = {}

        self.statusLabel = QLabel()
        self.statusLabel.setFixedHeight(30)
        self.statusbar.addWidget(self.statusLabel)
        self.statusbar.showMessage('Ready')

        # ---------------------------- load controls, views, panels
        self.layer_ctrl = LayersControl()
        self.layer_ctrl.sig_opacity_changed.connect(self.layers_opacity_changed)
        self.layer_ctrl.sig_visible_changed.connect(self.layers_visible_changed)

        self.object_ctrl = ObjectControl()
        self.object_ctrl.add_object_btn.clicked.connect(self.make_object_pieces)
        self.object_ctrl.merge_probe_btn.clicked.connect(self.merge_probes)
        self.object_ctrl.line_width_slider.valueChanged.connect(self.obj_line_width_changed)
        # self.object_ctrl.merge_virus_btn.clicked.connect(self.merge_virus)
        # self.object_ctrl.merge_bnd_btn.clicked.connect(self.merge_bnds)

        self.image_view = ImageView()
        self.image_view.sig_image_changed.connect(self.update_histo_tri_onside_data)
        self.image_view.img_stacks.sig_mouse_clicked.connect(self.img_stacks_clicked)
        self.image_view.img_stacks.sig_mouse_hovered.connect(self.img_stacks_hovered)
        self.image_view.img_stacks.tri_pnts.mouseDragged.connect(self.hist_window_tri_pnts_moving)
        self.image_view.img_stacks.tri_pnts.mouseClicked.connect(self.hist_window_tri_pnts_clicked)
        self.image_view.img_stacks.lasso_path.sigPointsClicked.connect(self.lasso_points_clicked)
        self.image_view.img_stacks.sig_key_pressed.connect(self.img_stacks_key_pressed)
        self.image_view.img_stacks.drawing_pnts.sigClicked.connect(self.img_drawing_pnts_clicked)
        # self.image_view.img_stacks.drawing_img.setLookupTable(lut=self.tool_box.base_lut)

        self.atlas_view = AtlasView()
        self.atlas_view.show_boundary_btn.clicked.connect(self.vis_atlas_boundary)
        self.atlas_view.section_rabnt1.toggled.connect(self.display_changed)
        self.atlas_view.section_rabnt2.toggled.connect(self.display_changed)
        self.atlas_view.section_rabnt3.toggled.connect(self.display_changed)
        self.atlas_view.label_tree.labels_changed.connect(self.sig_label_changed)
        # hovered
        self.atlas_view.cimg.sig_mouse_hovered.connect(self.coronal_slice_stacks_hovered)
        self.atlas_view.simg.sig_mouse_hovered.connect(self.sagital_slice_stacks_hovered)
        self.atlas_view.himg.sig_mouse_hovered.connect(self.horizontal_slice_stacks_hovered)
        # clicked
        self.atlas_view.cimg.sig_mouse_clicked.connect(self.atlas_stacks_clicked)
        # drawing clicked
        self.atlas_view.cimg.drawing_pnts.sigClicked.connect(self.atlas_drawing_pnts_clicked)
        self.atlas_view.simg.drawing_pnts.sigClicked.connect(self.atlas_drawing_pnts_clicked)
        self.atlas_view.himg.drawing_pnts.sigClicked.connect(self.atlas_drawing_pnts_clicked)
        # triangle points moving and clicked
        self.atlas_view.cimg.tri_pnts.mouseDragged.connect(self.atlas_window_tri_pnts_moving)
        self.atlas_view.cimg.tri_pnts.mouseClicked.connect(self.atlas_window_tri_pnts_clicked)

        # --------------------------------------------------------
        #                 connect all menu actions
        # --------------------------------------------------------
        # file menu related
        self.actionSingle_Image.triggered.connect(self.load_image)
        # atlas menu related
        self.actionDownload.triggered.connect(self.download_waxholm_rat_atlas)

        self.actionCoronal_Window.triggered.connect(self.show_only_coronal_window)
        self.actionSagital_Window.triggered.connect(self.show_only_sagital_window)
        self.actionHorizontal_Window.triggered.connect(self.show_only_horizontal_window)
        self.action3D_Window.triggered.connect(self.show_only_3d_window)
        self.actionImage_Window.triggered.connect(self.show_only_image_window)
        self.action2_Windows.triggered.connect(self.show_2_windows)
        self.action4_Windows.triggered.connect(self.show_4_windows)

        # image menu related
        self.actionGray_Mode.triggered.connect(lambda: self.image_view.image_mode_changed('gray'))
        self.actionHSV_Mode.triggered.connect(lambda: self.image_view.image_mode_changed('hsv'))
        self.actionRGB_Mode.triggered.connect(lambda: self.image_view.image_mode_changed('rgb'))
        self.actionFlip_Horizontal.triggered.connect(self.image_view.image_horizon_flip)
        self.actionFlip_Vertical.triggered.connect(self.image_view.image_vertical_flip)
        self.action180.triggered.connect(self.image_view.image_180_rotate)
        self.action90_Clockwise.triggered.connect(self.image_view.image_90_rotate)
        self.action90_Counter_Clockwise.triggered.connect(self.image_view.image_90_counter_rotate)
        self.actionCopy_Current_Image.triggered.connect(self.make_copy_of_current_image)
        self.actionHide_Original_Image.triggered.connect(self.image_view.hide_original_image)
        self.actionShow_Original_Image.triggered.connect(self.image_view.show_original_image)



        self.init_tool_bar()
        self.init_side_bar()
        # --------------------------------------------------------
        # --------------------------------------------------------
        #
        #                 windows setting up
        #
        # --------------------------------------------------------
        # --------------------------------------------------------
        # ------------------ coronal
        coronal_layout = QGridLayout(self.coronalframe)
        coronal_layout.setSpacing(0)
        coronal_layout.setContentsMargins(0, 0, 0, 0)
        coronal_layout.addWidget(self.atlas_view.cimg, 0, 0, 1, 1)
        coronal_layout.addWidget(self.atlas_view.clut, 0, 1, 1, 1)
        coronal_layout.addWidget(self.atlas_view.cpage_ctrl, 1, 0, 1, 2)

        # ------------------ sagital / image sagital
        self.sagital_layout = QGridLayout(self.sagitalframe)
        self.sagital_layout.setSpacing(0)
        self.sagital_layout.setContentsMargins(0, 0, 0, 0)
        self.sagital_layout.addWidget(self.atlas_view.simg, 0, 0, 1, 1)
        self.sagital_layout.addWidget(self.atlas_view.slut, 0, 1, 1, 1)
        self.sagital_layout.addWidget(self.atlas_view.spage_ctrl, 1, 0, 1, 2)

        # ------------------ horizontal
        horizontal_layout = QGridLayout(self.horizontalframe)
        horizontal_layout.setSpacing(0)
        horizontal_layout.setContentsMargins(0, 0, 0, 0)
        horizontal_layout.addWidget(self.atlas_view.himg, 0, 0, 1, 1)
        horizontal_layout.addWidget(self.atlas_view.hlut, 0, 1, 1, 1)
        horizontal_layout.addWidget(self.atlas_view.hpage_ctrl, 1, 0, 1, 2)

        # ------------------ sagital copy / atlas sagital
        self.sagital_copy_layout = QGridLayout(self.sagitalcopyframe)
        self.sagital_copy_layout.setSpacing(0)
        self.sagital_copy_layout.setContentsMargins(0, 0, 0, 0)

        # ------------------ image
        self.image_view_layout = QGridLayout(self.histview)
        self.image_view_layout.setSpacing(0)
        self.image_view_layout.setContentsMargins(0, 0, 0, 0)
        self.image_view_layout.addWidget(self.image_view.img_stacks, 0, 0, 1, 1)

        # -------------------- 3D view
        self.view3d.opts['distance'] = 200  # distance of camera from center
        self.view3d.opts['elevation'] = 50  # camera's angle of elevation in degrees
        self.view3d.opts['azimuth'] = 45    # camera's azimuthal angle in degrees
        self.view3d.opts['fov'] = 60        # horizontal field of view in degrees
        # self.view3d.setBackgroundColor(pg.mkColor(50, 50, 50))
        self.view3d.addItem(self.atlas_view.axis)
        self.view3d.addItem(self.atlas_view.grid)
        self.view3d.addItem(self.atlas_view.mesh)
        self.view3d.addItem(self.atlas_view.ap_plate_mesh)
        self.view3d.addItem(self.atlas_view.dv_plate_mesh)
        self.view3d.addItem(self.atlas_view.ml_plate_mesh)

        # -------------------- initial window
        self.coronalframe.show()
        self.sagitalframe.hide()
        self.horizontalframe.hide()
        self.sagitalcopyframe.hide()
        self.view3d.hide()
        self.histview.hide()

        self.sidebar.setCurrentIndex(0)
        tab1_shortcut = QShortcut(QKeySequence('Ctrl+1'), self)
        tab1_shortcut.activated.connect(lambda: self.sidebar_tab_state(0))
        tab2_shortcut = QShortcut(QKeySequence('Ctrl+2'), self)
        tab2_shortcut.activated.connect(lambda: self.sidebar_tab_state(1))
        tab3_shortcut = QShortcut(QKeySequence('Ctrl+3'), self)
        tab3_shortcut.activated.connect(lambda: self.sidebar_tab_state(2))
        tab4_shortcut = QShortcut(QKeySequence('Ctrl+4'), self)
        tab4_shortcut.activated.connect(lambda: self.sidebar_tab_state(3))
        tab5_shortcut = QShortcut(QKeySequence('Ctrl+5'), self)
        tab5_shortcut.activated.connect(lambda: self.sidebar_tab_state(4))

    def sidebar_tab_state(self, tab_num):
        self.sidebar.setCurrentIndex(tab_num)

    # ------------------------------------------------------------------
    #
    #                      Window Control
    #
    # ------------------------------------------------------------------

    def show_only_coronal_window(self):
        if self.atlas_view.atlas_data is None:
            return
        if self.num_windows == 4:
            self.sagital_copy_layout.removeWidget(self.atlas_view.simg)
            self.sagital_copy_layout.removeWidget(self.atlas_view.slut)
            self.sagital_copy_layout.removeWidget(self.atlas_view.spage_ctrl)
            self.sagital_layout.addWidget(self.atlas_view.simg, 0, 0, 1, 1)
            self.sagital_layout.addWidget(self.atlas_view.slut, 0, 1, 1, 1)
            self.sagital_layout.addWidget(self.atlas_view.spage_ctrl, 1, 0, 1, 2)
        self.num_windows = 1
        self.atlas_view.radio_group.setVisible(True)
        self.coronalframe.setVisible(True)
        self.sagitalframe.setVisible(False)
        self.horizontalframe.setVisible(False)
        self.sagitalcopyframe.setVisible(False)
        self.view3d.setVisible(False)
        self.histview.setVisible(False)

    def show_only_sagital_window(self):
        if self.atlas_view.atlas_data is None:
            return
        if self.num_windows == 4:
            self.sagital_copy_layout.removeWidget(self.atlas_view.simg)
            self.sagital_copy_layout.removeWidget(self.atlas_view.slut)
            self.sagital_copy_layout.removeWidget(self.atlas_view.spage_ctrl)
            self.sagital_layout.addWidget(self.atlas_view.simg, 0, 0, 1, 1)
            self.sagital_layout.addWidget(self.atlas_view.slut, 0, 1, 1, 1)
            self.sagital_layout.addWidget(self.atlas_view.spage_ctrl, 1, 0, 1, 2)
        self.num_windows = 1
        self.atlas_view.radio_group.setVisible(True)
        self.coronalframe.setVisible(False)
        self.sagitalframe.setVisible(True)
        self.horizontalframe.setVisible(False)
        self.sagitalcopyframe.setVisible(False)
        self.view3d.setVisible(False)
        self.histview.setVisible(False)

    def show_only_horizontal_window(self):
        if self.atlas_view.atlas_data is None:
            return
        if self.num_windows == 4:
            self.sagital_copy_layout.removeWidget(self.atlas_view.simg)
            self.sagital_copy_layout.removeWidget(self.atlas_view.slut)
            self.sagital_copy_layout.removeWidget(self.atlas_view.spage_ctrl)
            self.sagital_layout.addWidget(self.atlas_view.simg, 0, 0, 1, 1)
            self.sagital_layout.addWidget(self.atlas_view.slut, 0, 1, 1, 1)
            self.sagital_layout.addWidget(self.atlas_view.spage_ctrl, 1, 0, 1, 2)
        self.num_windows = 1
        self.atlas_view.radio_group.setVisible(True)
        self.coronalframe.setVisible(False)
        self.sagitalframe.setVisible(False)
        self.horizontalframe.setVisible(True)
        self.sagitalcopyframe.setVisible(False)
        self.view3d.setVisible(False)
        self.histview.setVisible(False)

    def show_only_image_window(self):
        self.atlas_view.radio_group.setVisible(True)
        self.coronalframe.setVisible(False)
        self.sagitalframe.setVisible(False)
        self.horizontalframe.setVisible(False)
        self.sagitalcopyframe.setVisible(False)
        self.view3d.setVisible(False)
        self.histview.setVisible(True)

    def show_only_3d_window(self):
        if self.atlas_view.atlas_data is None:
            return
        if self.num_windows == 4:
            self.sagital_copy_layout.removeWidget(self.atlas_view.simg)
            self.sagital_copy_layout.removeWidget(self.atlas_view.slut)
            self.sagital_copy_layout.removeWidget(self.atlas_view.spage_ctrl)
            self.sagital_layout.addWidget(self.atlas_view.simg, 0, 0, 1, 1)
            self.sagital_layout.addWidget(self.atlas_view.slut, 0, 1, 1, 1)
            self.sagital_layout.addWidget(self.atlas_view.spage_ctrl, 1, 0, 1, 2)
        self.num_windows = 1
        self.atlas_view.radio_group.setVisible(True)
        self.coronalframe.setVisible(False)
        self.sagitalframe.setVisible(False)
        self.horizontalframe.setVisible(False)
        self.sagitalcopyframe.setVisible(False)
        self.view3d.setVisible(True)
        self.histview.setVisible(False)

    def show_2_windows(self):
        if self.atlas_view.atlas_data is None:
            return
        if self.num_windows == 4:
            self.sagital_copy_layout.removeWidget(self.atlas_view.simg)
            self.sagital_copy_layout.removeWidget(self.atlas_view.slut)
            self.sagital_copy_layout.removeWidget(self.atlas_view.spage_ctrl)
            self.sagital_layout.addWidget(self.atlas_view.simg, 0, 0, 1, 1)
            self.sagital_layout.addWidget(self.atlas_view.slut, 0, 1, 1, 1)
            self.sagital_layout.addWidget(self.atlas_view.spage_ctrl, 1, 0, 1, 2)
        self.num_windows = 2
        self.atlas_view.radio_group.setVisible(True)
        if self.atlas_display == 'coronal':
            self.coronalframe.setVisible(True)
            self.sagitalframe.setVisible(False)
            self.horizontalframe.setVisible(False)
        elif self.atlas_display == 'sagital':
            self.coronalframe.setVisible(False)
            self.sagitalframe.setVisible(True)
            self.horizontalframe.setVisible(False)
        else:
            self.coronalframe.setVisible(False)
            self.sagitalframe.setVisible(False)
            self.horizontalframe.setVisible(True)

        self.sagitalcopyframe.setVisible(False)
        self.view3d.setVisible(False)
        self.histview.setVisible(True)

    def show_3_windows(self):
        if self.atlas_view.atlas_data is None:
            return
        if self.num_windows == 4:
            self.sagital_copy_layout.removeWidget(self.atlas_view.simg)
            self.sagital_copy_layout.removeWidget(self.atlas_view.slut)
            self.sagital_copy_layout.removeWidget(self.atlas_view.spage_ctrl)
            self.sagital_layout.addWidget(self.atlas_view.simg, 0, 0, 1, 1)
            self.sagital_layout.addWidget(self.atlas_view.slut, 0, 1, 1, 1)
            self.sagital_layout.addWidget(self.atlas_view.spage_ctrl, 1, 0, 1, 2)
        self.num_windows = 3
        self.atlas_view.radio_group.setVisible(True)
        if self.atlas_display == 'coronal':
            self.coronalframe.setVisible(True)
            self.sagitalframe.setVisible(False)
            self.horizontalframe.setVisible(False)
        elif self.atlas_display == 'sagital':
            self.coronalframe.setVisible(False)
            self.sagitalframe.setVisible(True)
            self.horizontalframe.setVisible(False)
        else:
            self.coronalframe.setVisible(False)
            self.sagitalframe.setVisible(False)
            self.horizontalframe.setVisible(True)

        self.sagitalcopyframe.setVisible(False)
        self.view3d.setVisible(True)
        self.histview.setVisible(True)

    def show_4_windows(self):
        if self.atlas_view.atlas_data is None:
            return
        if self.num_windows != 4:
            self.sagital_layout.removeWidget(self.atlas_view.simg)
            self.sagital_layout.removeWidget(self.atlas_view.slut)
            self.sagital_layout.removeWidget(self.atlas_view.spage_ctrl)
            self.sagital_copy_layout.addWidget(self.atlas_view.simg, 0, 0, 1, 1)
            self.sagital_copy_layout.addWidget(self.atlas_view.slut, 0, 1, 1, 1)
            self.sagital_copy_layout.addWidget(self.atlas_view.spage_ctrl, 1, 0, 1, 2)
        self.num_windows = 4
        self.atlas_view.radio_group.setVisible(False)
        self.coronalframe.setVisible(True)
        self.sagitalframe.setVisible(False)
        self.horizontalframe.setVisible(True)
        self.sagitalcopyframe.setVisible(True)
        self.view3d.setVisible(True)
        self.histview.setVisible(False)

    #
    # def clear_layout(self, layout):
    #     while layout.count() > 0:
    #         item = layout.takeAt(0)
    #         if not item:
    #             continue
    #         w = item.widget()
    #         if w:
    #             w.deleteLater()
    #

    # ------------------------------------------------------------------
    #
    #                      atlas panel related
    #
    # ------------------------------------------------------------------
    def display_changed(self):
        rbtn = self.sender()
        if rbtn.isChecked():
            if rbtn.text() == "Coronal":
                self.coronalframe.setVisible(True)
                self.sagitalframe.setVisible(False)
                self.horizontalframe.setVisible(False)
                self.atlas_display = 'coronal'
            elif rbtn.text() == "Sagital":
                self.coronalframe.setVisible(False)
                self.sagitalframe.setVisible(True)
                self.horizontalframe.setVisible(False)
                self.atlas_display = 'sagital'
            else:
                self.coronalframe.setVisible(False)
                self.sagitalframe.setVisible(False)
                self.horizontalframe.setVisible(True)
                self.atlas_display = 'horizontal'
        if self.atlas_view.atlas_data is None or self.atlas_view.atlas_label is None:
            return
        self.atlas_view.working_cut_changed(self.atlas_display)
        self.reset_corners_atlas()
        self.working_atlas_mask = np.ones(self.atlas_view.slice_size).astype('uint8')

    def reset_corners_atlas(self):
        self.atlas_rect = (0, 0, self.atlas_view.slice_size[1], self.atlas_view.slice_size[0])
        self.atlas_tri_inside_data = []  # renew tri_inside data to empty
        for da_item in self.working_atlas_text:
            self.atlas_view.working_atlas.vb.removeItem(da_item)
        self.working_atlas_text = []
        self.atlas_corner_points = self.atlas_view.corner_points.copy()
        self.atlas_side_lines = self.atlas_view.side_lines.copy()
        self.atlas_tri_onside_data = num_side_pnt_changed(self.np_onside, self.atlas_corner_points, self.atlas_side_lines)
        self.atlas_tri_data = self.atlas_tri_onside_data + self.atlas_tri_inside_data
        self.atlas_view.working_atlas.tri_pnts.setData(pos=np.asarray(self.atlas_tri_data))
        if self.tool_box.triang_vis_btn.isChecked():
            self.update_atlas_tri_lines()
        self.small_atlas_rect = None
        self.small_histo_rect = None

    def reset_corners_hist(self):
        self.histo_rect = (0, 0, self.image_view.img_size[1], self.image_view.img_size[0])
        self.histo_tri_inside_data = []  # renew tri_inside data to empty
        for da_item in self.working_img_text:
            self.image_view.img_stacks.vb.removeItem(da_item)
        self.working_img_text = []
        self.histo_corner_points = self.image_view.corner_points.copy()
        self.histo_side_lines = self.image_view.side_lines.copy()
        self.histo_tri_onside_data = num_side_pnt_changed(self.np_onside, self.histo_corner_points, self.histo_side_lines)

        self.histo_tri_data = self.histo_tri_onside_data + self.histo_tri_inside_data
        self.image_view.img_stacks.tri_pnts.setData(pos=np.asarray(self.histo_tri_data))
        if self.tool_box.triang_vis_btn.isChecked():
            self.update_histo_tri_lines()
        self.small_atlas_rect = None
        self.small_histo_rect = None

    def vis_atlas_boundary(self):
        if self.atlas_view.atlas_data is None:
            return
        if self.atlas_view.show_boundary_btn.isChecked():
            self.atlas_view.cimg.boundary.setVisible(True)
            self.atlas_view.simg.boundary.setVisible(True)
            self.atlas_view.himg.boundary.setVisible(True)
        else:
            self.atlas_view.cimg.boundary.setVisible(False)
            self.atlas_view.simg.boundary.setVisible(False)
            self.atlas_view.himg.boundary.setVisible(False)


    # ------------------------------------------------------------------
    #
    #                  Menu Bar ---- File ----- related
    #
    # ------------------------------------------------------------------
    def file_save(self):
        file_name = QtGui.QFileDialog.getSaveFileName(self, 'Save File')
        if file_name != '':
            file = open(file_name, 'w')
            text = self.textEdit.toPlainText()
            file.write(text)
            file.close()

    # ------------------------------------------------------------------
    #
    #                  Menu Bar ---- Edit ----- related
    #
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    #
    #                  Menu Bar ---- Image ----- related
    #
    # ------------------------------------------------------------------
    def make_copy_of_current_image(self):
        if self.image_view.image_file is None or not self.image_view.image_file.is_rgb:
            return
        self.process_img = self.image_view.current_img.copy()
        self.image_view.img_stacks.processing_image.setImage(self.process_img)
        res = cv2.resize(self.process_img, self.image_view.tb_size, interpolation=cv2.INTER_AREA)
        self.master_layers(res, layer_type='img-copy')

    # ------------------------------------------------------------------
    #
    #                  Menu Bar ---- Atlas ----- related
    #
    # ------------------------------------------------------------------
    def download_waxholm_rat_atlas(self):
        download_waxholm_rat_window = AtlasDownloader()
        download_waxholm_rat_window.exec()


    # ------------------------------------------------------------------
    #
    #                      ToolBar layout and connections
    #
    # -----------------------------------------------------------------
    def init_tool_bar(self):
        self.toolbar.setStyleSheet(toolbar_style)
        # -------------- ToolBar layout and functions -------------- #
        self.tool_box.add_atlas.triggered.connect(lambda: self.load_atlas('WHS'))
        self.tool_box.add_image_stack.triggered.connect(self.load_image)
        #     add_cell_act = QAction(QIcon('icons/neuron.png'), 'upload recorded cell activities', self)
        self.tool_box.vis2.triggered.connect(self.show_2_windows)
        self.tool_box.vis3.triggered.connect(self.show_3_windows)
        self.tool_box.vis4.triggered.connect(self.show_4_windows)
        self.tool_box.toh_btn.triggered.connect(self.transfer_to_hist_clicked)
        self.tool_box.toa_btn.triggered.connect(self.transfer_to_atlas_clicked)
        self.tool_box.check_btn.triggered.connect(self.transform_accept)

        self.tool_box.checkable_btn_dict['moving_btn'].triggered.connect(self.moving_btn_clicked)
        self.tool_box.checkable_btn_dict['rotation_btn'].triggered.connect(self.rotation_btn_clicked)
        self.tool_box.checkable_btn_dict['lasso_btn'].triggered.connect(self.lasso_btn_clicked)
        self.tool_box.checkable_btn_dict['magic_wand_btn'].triggered.connect(self.magic_wand_btn_clicked)
        self.tool_box.checkable_btn_dict['pencil_btn'].triggered.connect(self.pencil_btn_clicked)
        self.tool_box.checkable_btn_dict['eraser_btn'].triggered.connect(self.eraser_btn_clicked)
        self.tool_box.checkable_btn_dict['probe_btn'].triggered.connect(self.probe_btn_clicked)
        self.tool_box.checkable_btn_dict['triang_btn'].triggered.connect(self.triang_btn_clicked)
        self.tool_box.checkable_btn_dict['loc_btn'].triggered.connect(self.loc_btn_clicked)
        # magic_wand related
        self.tool_box.magic_color_btn.sigColorChanged.connect(self.change_magic_wand_color)
        self.tool_box.magic_wand_virus_register.clicked.connect(self.get_virus_img)
        self.tool_box.magic_wand_bnd_register.clicked.connect(self.get_contour_img)
        # triangle related
        self.tool_box.bound_pnts_num.textEdited.connect(self.number_of_side_points_changed)
        self.tool_box.triang_vis_btn.clicked.connect(self.vis_tri_lines_btn_clicked)
        self.tool_box.triang_match_bnd.clicked.connect(self.matching_tri_bnd)
        # cell related
        self.tool_box.cell_radar_btn.clicked.connect(self.cell_detect_btn_clicked)
        self.tool_box.cell_selector_btn.clicked.connect(self.cell_select_btn_clicked)
        self.tool_box.cell_aim_btn.clicked.connect(self.cell_aim_btn_clicked)
        # moving related
        self.tool_box.left_button.clicked.connect(self.moving_left_btn_clicked)
        self.tool_box.right_button.clicked.connect(self.moving_right_btn_clicked)
        self.tool_box.up_button.clicked.connect(self.moving_up_btn_clicked)
        self.tool_box.down_button.clicked.connect(self.moving_down_btn_clicked)
        # rotation related
        # pencil related
        self.tool_box.pencil_color_btn.sigColorChanged.connect(self.change_pencil_color)
        self.tool_box.pencil_size_valt.textChanged.connect(self.change_pencil_size)
        # probe_related
        self.tool_box.probe_type1.toggled.connect(lambda: self.probe_type_changed(0))
        self.tool_box.probe_type2.toggled.connect(lambda: self.probe_type_changed(1))
        self.tool_box.probe_type3.toggled.connect(lambda: self.probe_type_changed(2))

        self.toolbar.addAction(self.tool_box.add_atlas)
        self.toolbar.addAction(self.tool_box.add_image_stack)
        #     self.toolBar.addAction(add_cell_act)
        self.toolbar.addAction(self.tool_box.vis2)
        self.toolbar.addAction(self.tool_box.vis3)
        self.toolbar.addAction(self.tool_box.vis4)
        self.toolbar.addSeparator()
        self.toolbox_btn_keys = list(self.tool_box.checkable_btn_dict.keys())
        for da_key in self.toolbox_btn_keys:
            self.toolbar.addAction(self.tool_box.checkable_btn_dict[da_key])
        # self.toolbar.addAction(self.tool_box.boundary_btn)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.tool_box.toa_btn)
        self.toolbar.addAction(self.tool_box.check_btn)
        self.toolbar.addAction(self.tool_box.toh_btn)
        self.toolbar.addWidget(self.tool_box.sep_label)

        moving_action = self.toolbar.addWidget(self.tool_box.moving_wrap)
        rotation_action = self.toolbar.addWidget(self.tool_box.rotation_wrap)
        magic_wand_action = self.toolbar.addWidget(self.tool_box.magic_wand_wrap)
        pencil_action = self.toolbar.addWidget(self.tool_box.pencil_wrap)
        eraser_action = self.toolbar.addWidget(self.tool_box.eraser_wrap)
        lasso_action = self.toolbar.addWidget(self.tool_box.lasso_wrap)
        probe_action = self.toolbar.addWidget(self.tool_box.probe_wrap)
        triang_action = self.toolbar.addWidget(self.tool_box.triang_wrap)
        loc_action = self.toolbar.addWidget(self.tool_box.cell_count_wrap)

        self.toolbar_wrap_action_dict['moving_act'] = moving_action
        self.toolbar_wrap_action_dict['rotation_act'] = rotation_action
        self.toolbar_wrap_action_dict['pencil_act'] = pencil_action
        self.toolbar_wrap_action_dict['eraser_act'] = eraser_action
        self.toolbar_wrap_action_dict['lasso_act'] = lasso_action
        self.toolbar_wrap_action_dict['magic_wand_act'] = magic_wand_action
        self.toolbar_wrap_action_dict['probe_act'] = probe_action
        self.toolbar_wrap_action_dict['triang_act'] = triang_action
        self.toolbar_wrap_action_dict['loc_act'] = loc_action

        self.toolbar_wrap_action_keys = list(self.toolbar_wrap_action_dict.keys())
        for da_key in self.toolbar_wrap_action_keys:
            self.toolbar_wrap_action_dict[da_key].setVisible(False)

        self.np_onside = int(self.tool_box.bound_pnts_num.text())

    # ------------------------------------------------------------------
    #              ToolBar checkable btn clicked
    # ------------------------------------------------------------------
    def moving_btn_clicked(self):
        if self.eraser_is_on:
            self.remove_eraser_symbol()
            self.eraser_is_on = False
        self.inactive_lasso()
        self.set_toolbox_btns_unchecked('moving')

    def lasso_btn_clicked(self):
        if self.eraser_is_on:
            self.remove_eraser_symbol()
        self.set_toolbox_btns_unchecked('lasso')

    def magic_wand_btn_clicked(self):
        if self.eraser_is_on:
            self.remove_eraser_symbol()
            self.eraser_is_on = False
        self.inactive_lasso()
        self.set_toolbox_btns_unchecked('magic_wand')

    def pencil_btn_clicked(self):
        if self.eraser_is_on:
            self.remove_eraser_symbol()
            self.eraser_is_on = False
        self.inactive_lasso()
        self.set_toolbox_btns_unchecked('pencil')

    def eraser_btn_clicked(self):
        self.inactive_lasso()
        self.set_toolbox_btns_unchecked('eraser')

    def rotation_btn_clicked(self):
        if self.eraser_is_on:
            self.remove_eraser_symbol()
            self.eraser_is_on = False
        self.inactive_lasso()
        self.set_toolbox_btns_unchecked('rotation')

    def triang_btn_clicked(self):
        if self.eraser_is_on:
            self.remove_eraser_symbol()
            self.eraser_is_on = False
        self.inactive_lasso()
        self.set_toolbox_btns_unchecked('triang')
        self.show_triangle_points('triang')

    def probe_btn_clicked(self):
        if self.eraser_is_on:
            self.remove_eraser_symbol()
            self.eraser_is_on = False
        self.inactive_lasso()
        self.set_toolbox_btns_unchecked('probe')

    def loc_btn_clicked(self):
        if self.eraser_is_on:
            self.remove_eraser_symbol()
            self.eraser_is_on = False
        self.inactive_lasso()
        self.set_toolbox_btns_unchecked('loc')

    def set_toolbox_btns_unchecked(self, current_btn):
        if self.tool_box.checkable_btn_dict['{}_btn'.format(current_btn)].isChecked():
            self.current_checked_tool = current_btn
            for da_key in self.toolbox_btn_keys:
                if current_btn in da_key:
                    continue
                else:
                    self.tool_box.checkable_btn_dict[da_key].setChecked(False)
            for da_key in self.toolbar_wrap_action_keys:
                if current_btn in da_key:
                    self.toolbar_wrap_action_dict[da_key].setVisible(True)
                else:
                    self.toolbar_wrap_action_dict[da_key].setVisible(False)
        else:
            self.current_checked_tool = None
            self.toolbar_wrap_action_dict['{}_act'.format(current_btn)].setVisible(False)



    def remove_eraser_symbol(self):
        self.image_view.img_stacks.circle_follow.clear()
        self.image_view.img_stacks.circle_follow.updateItems()

    # ------------------------------------------------------------------
    #
    #                      SideBar layout and connections
    #
    # ------------------------------------------------------------------
    def init_side_bar(self):
        self.sidebar.setStyleSheet(tab_style)
        self.sidebar.setIconSize(QSize(24, 24))
        self.sidebar.setTabIcon(0, QIcon('icons/sidebar/atlascontrol.svg'))
        # self.sidebar.setIconSize(QtCore.QSize(24, 24))
        self.sidebar.setTabIcon(1, QIcon('icons/sidebar/treeview.svg'))
        # self.sidebar.setIconSize(QtCore.QSize(24, 24))
        self.sidebar.setTabIcon(2, QIcon('icons/sidebar/tool.svg'))
        # self.sidebar.setIconSize(QtCore.QSize(24, 24))
        self.sidebar.setTabIcon(3, QIcon('icons/sidebar/layers.svg'))
        # self.sidebar.setIconSize(QtCore.QSize(24, 24))
        self.sidebar.setTabIcon(4, QIcon('icons/sidebar/object.svg'))

        # ---------------------------- atlas control panel
        atlas_panel_layout = QVBoxLayout(self.atlascontrolpanel)
        atlas_panel_layout.setContentsMargins(0, 0, 0, 0)
        atlas_panel_layout.setAlignment(Qt.AlignTop)
        atlas_control_label = QLabel('Atlasing Controller')
        atlas_control_label.setStyleSheet(sidebar_title_label_style)

        atlas_panel_layout.addWidget(atlas_control_label)
        atlas_panel_layout.addWidget(self.atlas_view.sidebar_wrap)

        # ---------------------------- Label Panel
        label_panel_layout = QVBoxLayout(self.treeviewpanel)
        label_panel_layout.setContentsMargins(0, 0, 0, 0)
        label_panel_layout.setAlignment(Qt.AlignTop)
        label_control_label = QLabel('Segmentation View Controller')
        label_control_label.setStyleSheet(sidebar_title_label_style)

        label_panel_layout.addWidget(label_control_label)

        label_container = QFrame()
        label_container_layout = QVBoxLayout(label_container)
        label_container_layout.setContentsMargins(0, 0, 0, 0)
        label_container_layout.setSpacing(5)
        label_container_layout.setAlignment(Qt.AlignTop)
        show_3d_button = QPushButton()
        show_3d_button.setStyleSheet(
            'margin-left: 5px; margin-right:5px; margin-bottom:10px; padding-top:3px; height: 20px;')
        show_3d_button.setCheckable(True)
        show_3d_button.setText('Show in 3D view')
        show_3d_button.clicked.connect(self.show_small_area_in_3d)

        composition_label = QLabel('Composition: ')
        self.composition_combo = QComboBox()
        self.composition_combo.addItems(['opaque', 'translucent', 'additive'])
        self.composition_combo.currentIndexChanged.connect(self.composition_3d_changed)

        label_container_layout.addWidget(show_3d_button)
        label_container_layout.addWidget(self.composition_combo)
        label_container_layout.addWidget(self.atlas_view.label_tree)
        label_panel_layout.addWidget(label_container)

        # ---------------------------- layer panel
        layer_panel_layout = QVBoxLayout(self.layerpanel)
        layer_panel_layout.setContentsMargins(0, 0, 0, 0)
        layer_panel_layout.setSpacing(0)
        layer_panel_layout.setAlignment(Qt.AlignTop)
        layer_control_label = QLabel('Layer View Controller')
        layer_control_label.setStyleSheet(sidebar_title_label_style)

        layer_btm_ctrl = QFrame()
        layer_btm_ctrl.setStyleSheet('background-color:rgb(65, 65, 65);')
        layer_btm_ctrl.setFixedHeight(24)
        layer_btm_layout = QHBoxLayout(layer_btm_ctrl)
        layer_btm_layout.setContentsMargins(0, 0, 0, 0)
        layer_btm_layout.setSpacing(5)
        layer_btm_layout.setAlignment(Qt.AlignRight)
        # layer_btm_layout.addWidget(self.lcontrols.vis_ai_layer_btn)
        # layer_btm_layout.addWidget(self.lcontrols.vis_hi_layer_btn)
        layer_btm_layout.addWidget(self.layer_ctrl.add_layer_btn)
        layer_btm_layout.addWidget(self.layer_ctrl.delete_layer_btn)

        layer_panel_layout.addWidget(layer_control_label)
        layer_panel_layout.addWidget(self.layer_ctrl)
        layer_panel_layout.addWidget(layer_btm_ctrl)
        # self.layerpanel.setEnabled(False)

        # ---------------------------- image panel
        image_panel_layout = QVBoxLayout(self.imagecontrolpanel)
        image_panel_layout.setContentsMargins(0, 0, 0, 0)
        image_panel_layout.setSpacing(0)
        image_panel_layout.setAlignment(Qt.AlignTop)
        image_control_label = QLabel('Image View Controller')
        image_control_label.setStyleSheet(sidebar_title_label_style)

        image_panel_layout.addWidget(image_control_label)

        space_item = QSpacerItem(300, 10, QSizePolicy.Expanding)

        image_container = QFrame()
        image_container_layout = QVBoxLayout(image_container)
        image_container_layout.setSpacing(5)
        image_container_layout.setAlignment(Qt.AlignTop)
        image_container_layout.addWidget(self.image_view.outer_frame)
        # image_container_layout.addSpacerItem(space_item)
        # image_container_layout.addWidget(self.image_view.chn_widget_wrap)

        image_panel_layout.addWidget(image_container)
        image_panel_layout.insertStretch(-1, 1)

        # ---------------------------- object panel
        object_panel_layout = QVBoxLayout(self.probecontrolpanel)
        object_panel_layout.setContentsMargins(0, 0, 0, 0)
        object_panel_layout.setSpacing(0)
        object_panel_layout.setAlignment(Qt.AlignTop)
        object_control_label = QLabel('Object View Controller')
        object_control_label.setStyleSheet(sidebar_title_label_style)

        object_btm_ctrl = QFrame()
        object_btm_ctrl.setStyleSheet('background-color:rgb(65, 65, 65);')
        object_btm_ctrl.setFixedHeight(24)
        object_btm_layout = QHBoxLayout(object_btm_ctrl)
        object_btm_layout.setContentsMargins(0, 0, 0, 0)
        object_btm_layout.setSpacing(5)
        object_btm_layout.setAlignment(Qt.AlignRight)

        object_btm_layout.addWidget(self.object_ctrl.merge_probe_btn)
        object_btm_layout.addWidget(self.object_ctrl.merge_virus_btn)
        object_btm_layout.addWidget(self.object_ctrl.merge_cell_btn)
        object_btm_layout.addWidget(self.object_ctrl.merge_drawing_btn)
        object_btm_layout.addWidget(self.object_ctrl.merge_contour_btn)
        object_btm_layout.addWidget(self.object_ctrl.add_object_btn)
        object_btm_layout.addWidget(self.object_ctrl.delete_object_btn)

        object_panel_layout.addWidget(object_control_label)
        object_panel_layout.addWidget(self.object_ctrl.outer_frame)
        object_panel_layout.addWidget(object_btm_ctrl)

    # ------------------------------------------------------------------
    #
    #               ToolBar lasso btn related
    #
    # ------------------------------------------------------------------
    def inactive_lasso(self):
        # if self.lasso_is_closure:
        self.lasso_pnts = []
        self.image_view.img_stacks.lasso_path.clear()
        self.image_view.img_stacks.lasso_path.updateItems()
        self.image_view.img_stacks.lasso_path.setPen(pg.mkPen(color='r', width=3, style=Qt.DashLine))
        self.lasso_is_closure = False

    def lasso_points_clicked(self, points, ev):
        if len(self.lasso_pnts) == 0:
            return
        clicked_ind = ev[0].index()
        if clicked_ind == 0 and len(self.lasso_pnts) >= 3:
            self.lasso_pnts.append(self.lasso_pnts[0])
            self.image_view.img_stacks.lasso_path.setData(np.asarray(self.lasso_pnts))
            self.lasso_is_closure = True
            self.image_view.img_stacks.lasso_path.setPen(pg.mkPen(color='r', width=3, style=Qt.SolidLine))
        else:
            self.inactive_lasso()

    # ------------------------------------------------------------------
    #
    #               ToolBar rotation btn related
    #
    # ------------------------------------------------------------------
    def rotate_clockwise_btn_clicked(self):
        print('moving left')

    # ------------------------------------------------------------------
    #
    #               ToolBar probe btn related
    #
    # ------------------------------------------------------------------
    def probe_type_changed(self, type):
        if type == 0:
            self.tip_length = 175
            self.channel_size = 20
            self.channel_number_in_banks = (384, 384, 192)
        elif type == 1:
            self.tip_length = 175
            self.channel_size = 15
            self.channel_number_in_banks = (384, 384, 192)
        else:
            self.tip_length = 0
            self.channel_size = None
            self.channel_number_in_banks = None

    # ------------------------------------------------------------------
    #
    #               ToolBar moving btn related
    #
    # ------------------------------------------------------------------
    def check_layers(self, link):
        if 'image' in link:
            da_stacks = self.image_view.img_stacks
        elif 'atlas' in link:
            da_stacks = self.atlas_view.working_atlas
        else:
            return
        if 'overlay' in link:
            da_img_widget = da_stacks.overlay_img
            da_pnt_widget = None
        elif 'drawing' in link:
            # da_img_widget = da_stacks.drawing_img
            da_pnt_widget = da_stacks.drawing_pnts
        elif 'virus' in link:
            da_img_widget = da_stacks.virus_img
            da_pnt_widget = da_stacks.virus_pnts
        elif 'probe' in link:
            da_img_widget = da_stacks.probe_img
            da_pnt_widget = da_stacks.probe_pnts
        elif 'cell' in link:
            da_img_widget = da_stacks.cell_img
            da_pnt_widget = da_stacks.cell_pnts
        elif 'overlay_contour' in link:
            da_img_widget = da_stacks.overlay_contour
            da_pnt_widget = None
        else:
            da_img_widget = None
            da_pnt_widget = None
        return da_img_widget, da_pnt_widget

    def moving_layers(self, tx, ty):
        shift_mat = np.float32([[1, 0, tx], [0, 1, ty]])
        n_working_layer = len(self.layer_ctrl.current_layer_ind)
        for i in range(n_working_layer):
            da_ind = self.layer_ctrl.current_layer_ind[i]
            da_link = self.layer_ctrl.layer_link[i]
            da_img_widget, da_pnt_widget = self.check_layers(da_link)
            if da_img_widget is not None:
                da_img = da_img_widget.image.copy()
                dst = cv2.warpAffine(da_img, shift_mat, da_img.shape[:2])
                da_img_widget.setImage(dst)
            if da_pnt_widget is not None:
                da_data = da_img_widget.data['pos'].copy()
                print(da_data)
                da_data[:, 0] = da_data[:, 0] + tx
                da_data[:, 1] = da_data[:, 1] + ty
                da_img_widget.setData(pos=da_data)

    def moving_left_btn_clicked(self):
        if not self.layer_ctrl.current_layer_ind:
            return
        self.moving_layers(-self.tool_box.moving_px, 0)

    def moving_right_btn_clicked(self):
        if not self.layer_ctrl.current_layer_ind:
            return
        self.moving_layers(self.tool_box.moving_px, 0)

    def moving_up_btn_clicked(self):
        if not self.layer_ctrl.current_layer_ind:
            return
        self.moving_layers(0, -self.tool_box.moving_px)

    def moving_down_btn_clicked(self):
        if not self.layer_ctrl.current_layer_ind:
            return
        self.moving_layers(0, self.tool_box.moving_px)

    # ------------------------------------------------------------------
    #
    #               ToolBar pencil btn related
    #
    # ------------------------------------------------------------------
    def change_pencil_color(self, ev):
        pencil_color = ev.color()
        self.pencil_color = np.ravel(pencil_color.getRgb())
        lut = self.tool_box.base_lut.copy()
        lut[1] = self.pencil_color
        # self.image_view.img_stacks.drawing_img.setLookupTable(lut=lut)
        self.atlas_view.cimg.drawing_img.setLookupTable(lut=lut)
        # self.atlas_view.simg.drawing_img.setLookupTable(lut=lut)
        # self.atlas_view.himg.drawing_img.setLookupTable(lut=lut)
        self.image_view.img_stacks.drawing_pnts.setPen(pg.mkPen(color=self.pencil_color, width=self.pencil_size))
        self.atlas_view.cimg.drawing_pnts.setPen(pg.mkPen(color=self.pencil_color, width=self.pencil_size))
        self.atlas_view.simg.drawing_pnts.setPen(pg.mkPen(color=self.pencil_color, width=self.pencil_size))
        self.atlas_view.himg.drawing_pnts.setPen(pg.mkPen(color=self.pencil_color, width=self.pencil_size))

    def change_pencil_size(self):
        val = int(self.tool_box.pencil_size_valt.text())
        self.pencil_size = val
        self.tool_box.pencil_size_slider.setValue(val)
        self.image_view.img_stacks.drawing_pnts.setPen(pg.mkPen(color=self.pencil_color, width=self.pencil_size))
        self.atlas_view.cimg.drawing_pnts.setPen(pg.mkPen(color=self.pencil_color, width=self.pencil_size))
        self.atlas_view.simg.drawing_pnts.setPen(pg.mkPen(color=self.pencil_color, width=self.pencil_size))
        self.atlas_view.himg.drawing_pnts.setPen(pg.mkPen(color=self.pencil_color, width=self.pencil_size))

    # ------------------------------------------------------------------
    #
    #               ToolBar loc btn related
    #
    # ------------------------------------------------------------------
    def cell_select_btn_clicked(self):
        if self.tool_box.cell_aim_btn.isChecked():
            self.tool_box.cell_aim_btn.setChecked(False)

    def cell_aim_btn_clicked(self):
        if self.tool_box.cell_selector_btn.isChecked():
            self.tool_box.cell_selector_btn.setChecked(False)

    def cell_detect_btn_clicked(self):
        if self.working_blob_data is None:
            return
        temp = self.image_view.current_img.copy()
        if self.image_view.current_mode == 'hsv':
            return
        if self.image_view.current_mode == 'rgb':
            temp = cv2.cvtColor(temp, cv2.COLOR_RGB2GRAY)

        locs = np.asarray(self.working_blob_data).astype(int)
        da_colors = temp[locs[:, 1], locs[:, 0]]

        da_width = np.max(locs[:, 0]) - np.min(locs[:, 0]) + 1
        da_height = np.max(locs[:, 1]) - np.min(locs[:, 1]) + 1
        small_img = np.zeros((da_height, da_width), 'uint8')
        small_locs = locs - np.array([np.min(locs[:, 0]), np.min(locs[:, 1])])
        small_img[small_locs[:, 1], small_locs[:, 0]] = 1
        ct, ht = cv2.findContours(small_img, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
        cnt = ct[0]
        da_moment = cv2.moments(cnt)
        center_x = int(da_moment["m10"] / da_moment["m00"])
        center_y = int(da_moment["m01"] / da_moment["m00"])

        da_area = cv2.contourArea(cnt)
        da_perimeter = cv2.arcLength(cnt, True)

        da_circularity = 4 * np.pi * da_area / (da_perimeter ** 2)

        params = cv2.SimpleBlobDetector_Params()
        # Change thresholds
        params.minThreshold = np.min(da_colors)
        params.maxThreshold = np.max(da_colors)
        params.filterByArea = True
        params.minArea = da_area - 1
        params.maxArea = da_area + 1
        params.filterByCircularity = True
        params.minCircularity = da_circularity
        params.filterByConvexity = True
        params.minConvexity = 0.87
        params.filterByInertia = True
        params.minInertiaRatio = 0.01

        if int(opencv_ver[0]) < 3:
            detector = cv2.SimpleBlobDetector(params)
        else:
            detector = cv2.SimpleBlobDetector_create(params)

        keypoints = detector.detect(temp)

        n_keypoints = len(keypoints)
        for i in range(n_keypoints):
            x = keypoints[i].pt[0]
            y = keypoints[i].pt[1]
            size = keypoints[i].size
            self.working_img_cell_data.append([x, y])
            self.working_img_cell_size.append(size)
        self.cell_count = self.cell_count + n_keypoints
        self.tool_box.cell_count_val.setText(str(self.cell_count))

        self.image_view.img_stacks.cell_pnts.setData(pos=np.asarray(self.working_img_cell_data))
        self.working_blob_data = []
        self.image_view.img_stacks.blob_pnts.clear()

    # ------------------------------------------------------------------
    #
    #               ToolBar magic wand btn related
    #
    # ------------------------------------------------------------------
    def change_magic_wand_color(self, ev):
        if self.image_view.image_file is None:
            return
        wand_color = ev.color()
        wand_color = np.ravel(wand_color.getRgb())
        print(wand_color)
        lut = self.tool_box.base_lut.copy()
        lut[1] = wand_color
        self.image_view.img_stacks.mask_img.setLookupTable(lut)
        self.image_view.img_stacks.contour_img.setLookupTable(lut)

    def get_virus_img(self):
        if self.working_img_mask_data is None:
            return
        self.working_img_virus_data = self.working_img_mask_data.copy()
        self.image_view.img_stacks.virus_img.setImage(self.working_img_virus_data)
        res = cv2.resize(self.working_img_virus_data, self.image_view.tb_size, interpolation=cv2.INTER_AREA)
        self.master_layers(res, layer_type='img-virus')
        self.working_img_mask_data = None
        self.image_view.img_stacks.mask_img.clear()
        layer_ind = [ind for ind in range(self.layer_ctrl.layer_count) if
                     self.layer_ctrl.layer_link[ind] == 'img-mask']
        self.layer_ctrl.delete_layer(layer_ind)

    def get_contour_img(self):
        if self.working_img_mask_data is not None:
            temp = self.working_img_mask_data.astype('uint8')
            contour_img = np.zeros(temp.shape, 'uint8')
            ct, hc = cv2.findContours(image=temp, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
            for j in range(len(ct)):
                da_contour = ct[j].copy()
                da_shp = da_contour.shape
                da_contour = np.reshape(da_contour, (da_shp[0], da_shp[2]))
                contour_img[da_contour[:, 1], da_contour[:, 0]] = 1
            self.working_img_contour_data = contour_img.copy()
            # self.working_img_contour_data = cv2.Canny(self.working_img_mask_data.astype('uint8'), 100, 200)
            self.image_view.img_stacks.contour_img.setImage(self.working_img_contour_data)
            wand_color = self.tool_box.magic_color_btn.color()
            wand_color = np.ravel(wand_color.getRgb())
            print(wand_color)
            lut = self.tool_box.base_lut.copy()
            lut[1] = wand_color
            self.image_view.img_stacks.contour_img.setLookupTable(lut)

            res = cv2.resize(self.working_img_contour_data, self.image_view.tb_size, interpolation=cv2.INTER_AREA)
            self.master_layers(res, layer_type='img-contour')
            self.working_img_mask_data = None
            self.image_view.img_stacks.mask_img.clear()
            layer_ind = [ind for ind in range(self.layer_ctrl.layer_count) if
                         self.layer_ctrl.layer_link[ind] == 'img-mask']
            self.layer_ctrl.delete_layer(layer_ind)

    # ------------------------------------------------------------------
    #
    #               ToolBar triangle btn related
    #
    # ------------------------------------------------------------------
    def show_triangle_points(self, current_btn):
        if self.tool_box.checkable_btn_dict['{}_btn'.format(current_btn)].isChecked():
            if self.atlas_tri_data:
                if not self.atlas_view.working_atlas.tri_pnts.isVisible():
                    self.atlas_view.working_atlas.tri_pnts.setVisible(True)
                if self.atlas_tri_inside_data and not self.working_atlas_text[0].isVisible():
                    for i in range(len(self.working_atlas_text)):
                        self.working_atlas_text[i].setVisible(True)
            if self.histo_tri_data:
                if not self.image_view.img_stacks.tri_pnts.isVisible():
                    self.image_view.img_stacks.tri_pnts.setVisible(True)
                if self.histo_tri_inside_data and not self.working_img_text[0].isVisible():
                    for i in range(len(self.working_img_text)):
                        self.working_img_text[i].setVisible(True)
        else:
            if self.atlas_tri_data:
                if self.atlas_view.working_atlas.tri_pnts.isVisible():
                    self.atlas_view.working_atlas.tri_pnts.setVisible(False)
                if self.atlas_tri_inside_data and self.working_atlas_text[0].isVisible():
                    for i in range(len(self.working_atlas_text)):
                        self.working_atlas_text[i].setVisible(False)
            if self.histo_tri_data:
                if self.image_view.img_stacks.tri_pnts.isVisible():
                    self.image_view.img_stacks.tri_pnts.setVisible(False)
                if self.histo_tri_inside_data and self.working_img_text[0].isVisible():
                    for i in range(len(self.working_img_text)):
                        self.working_img_text[i].setVisible(False)

    def number_of_side_points_changed(self):
        self.np_onside = int(self.tool_box.bound_pnts_num.text())
        if self.atlas_view.atlas_data is not None:
            self.atlas_tri_onside_data = num_side_pnt_changed(self.np_onside, self.atlas_corner_points,
                                                              self.atlas_side_lines)
            self.atlas_tri_data = self.atlas_tri_onside_data + self.atlas_tri_inside_data
            self.atlas_view.working_atlas.tri_pnts.setData(pos=np.asarray(self.atlas_tri_data))
            if self.tool_box.triang_vis_btn.isChecked():
                self.update_atlas_tri_lines()
        if self.image_view.image_file is not None:
            self.histo_tri_onside_data = num_side_pnt_changed(self.np_onside, self.histo_corner_points,
                                                              self.histo_side_lines)
            self.histo_tri_data = self.histo_tri_onside_data + self.histo_tri_inside_data
            self.image_view.img_stacks.tri_pnts.setData(pos=np.asarray(self.histo_tri_data))
            if self.tool_box.triang_vis_btn.isChecked():
                self.update_histo_tri_lines()

    def remove_histo_tri_lines(self):
        if self.image_view.img_stacks.tri_lines_list:
            for da_item in self.image_view.img_stacks.tri_lines_list:
                self.image_view.img_stacks.vb.removeItem(da_item)
            self.image_view.img_stacks.tri_lines_list = []

    def update_histo_tri_lines(self):
        self.remove_histo_tri_lines()
        histo_tri_lines = get_tri_lines(self.histo_rect, self.histo_tri_data)
        for el in histo_tri_lines:
            pt1 = [el[0], el[1]]
            pt2 = [el[2], el[3]]
            self.image_view.img_stacks.tri_lines_list.append(pg.PlotDataItem(pen=self.tool_box.tri_line_style))
            self.image_view.img_stacks.tri_lines_list[-1].setData(np.asarray([pt1, pt2]))
            self.image_view.img_stacks.vb.addItem(self.image_view.img_stacks.tri_lines_list[-1])

    def remove_atlas_tri_lines(self):
        if self.atlas_view.working_atlas.tri_lines_list:
            for da_item in self.atlas_view.working_atlas.tri_lines_list:
                self.atlas_view.working_atlas.vb.removeItem(da_item)
            self.atlas_view.working_atlas.tri_lines_list = []

    def update_atlas_tri_lines(self):
        self.remove_atlas_tri_lines()
        atlas_tri_lines = get_tri_lines(self.atlas_rect, self.atlas_tri_data)
        for el in atlas_tri_lines:
            pt1 = [el[0], el[1]]
            pt2 = [el[2], el[3]]
            self.atlas_view.working_atlas.tri_lines_list.append(pg.PlotDataItem(pen=self.tool_box.tri_line_style))
            self.atlas_view.working_atlas.tri_lines_list[-1].setData(np.asarray([pt1, pt2]))
            self.atlas_view.working_atlas.vb.addItem(self.atlas_view.working_atlas.tri_lines_list[-1])

    def vis_tri_lines_btn_clicked(self):
        if self.tool_box.triang_vis_btn.isChecked():
            if self.atlas_tri_data:
                self.update_atlas_tri_lines()
            if self.histo_tri_data:
                self.update_histo_tri_lines()
        else:
            if self.atlas_tri_data:
                self.remove_atlas_tri_lines()
            if self.histo_tri_data:
                self.remove_histo_tri_lines()

    def matching_tri_bnd(self):
        if self.image_view.image_file is None:
            return
        if self.atlas_view.atlas_data is None:
            return
        if self.atlas_view.atlas_label is None:
            return
        if not self.histo_tri_inside_data:
            return
        print('matching bnd')
        slice_size = self.atlas_view.slice_size
        image_size = self.image_view.img_size

        histo_pnts = np.asarray(self.histo_tri_inside_data)
        rect_img = cv2.boundingRect(histo_pnts.astype(np.float32))

        if not self.atlas_tri_inside_data:
            label_img = self.atlas_view.working_atlas.label_img.image.copy()
            none_zero_label = np.where(label_img != 0)
            if len(none_zero_label) == 0:
                return
            atlas_pnts = np.vstack([none_zero_label[1], none_zero_label[0]]).T
        else:
            atlas_pnts = np.asarray(self.atlas_tri_inside_data)
        rect_atlas = cv2.boundingRect(atlas_pnts.astype(np.float32))

        self.small_atlas_rect = rect_atlas
        self.small_histo_rect = rect_img

        self.atlas_corner_points, self.atlas_side_lines, self.histo_corner_points, self.histo_side_lines = \
            match_sides_points(rect_atlas, slice_size, rect_img, image_size)

        self.atlas_tri_onside_data = num_side_pnt_changed(self.np_onside, self.atlas_corner_points, self.atlas_side_lines)
        self.atlas_tri_data = self.atlas_tri_onside_data + self.atlas_tri_inside_data
        self.atlas_view.working_atlas.tri_pnts.setData(pos=np.asarray(self.atlas_tri_data))

        self.histo_tri_onside_data = num_side_pnt_changed(self.np_onside, self.histo_corner_points, self.histo_side_lines)
        self.histo_tri_data = self.histo_tri_onside_data + self.histo_tri_inside_data
        self.image_view.img_stacks.tri_pnts.setData(pos=np.asarray(self.histo_tri_data))
        if self.tool_box.triang_vis_btn.isChecked():
            self.update_histo_tri_lines()
            self.update_atlas_tri_lines()

    # ------------------------------------------------------------------
    #
    #               ToolBar transform btn clicked
    #
    # ------------------------------------------------------------------
    def transfer_to_hist_clicked(self):
        if self.image_view.image_file is None:
            return
        if self.atlas_view.atlas_data is None:
            return
        if self.atlas_view.atlas_label is None:
            return
        print('transfer to hist')
        if not self.a2h_transferred:
            label_img = self.atlas_view.working_atlas.label_img.image.copy()
            lut = self.atlas_view.label_tree.current_lut.copy()
            da_label_img = make_label_rgb_img(label_img, lut)

            img_wrap = np.zeros((self.image_view.img_size[0], self.image_view.img_size[1], 3), np.float32)

            if self.histo_tri_inside_data and self.atlas_tri_inside_data:
                print('match triangles to hist')
                a_temp = len(self.histo_tri_data)
                b_temp = len(self.atlas_tri_data)
                if a_temp != b_temp:
                    print('number of points are not mathcing.')
                    return
                input_img = da_label_img.copy()

                # rect = (0, 0, self.image_view.img_size[1], self.image_view.img_size[0])

                subdiv = cv2.Subdiv2D(self.histo_rect)
                for p in self.histo_tri_data:
                    subdiv.insert(p)

                tri_vet_inds = get_vertex_ind_in_triangle(subdiv)
                for i in range(len(tri_vet_inds)):
                    da_inds = tri_vet_inds[i]
                    t1 = [self.atlas_tri_data[da_inds[0]], self.atlas_tri_data[da_inds[1]], self.atlas_tri_data[da_inds[2]]]
                    t2 = [self.histo_tri_data[da_inds[0]], self.histo_tri_data[da_inds[1]], self.histo_tri_data[da_inds[2]]]
                    t1 = np.reshape(t1, (3, 2))
                    t2 = np.reshape(t2, (3, 2))
                    warp_triangle(input_img, img_wrap, t1, t2, True)
                self.project_method = 'match to hist'
                self.register_method = 2
            else:
                if self.small_atlas_rect is not None:
                    atlas_rect = self.small_atlas_rect
                    histo_rect = self.small_histo_rect
                    self.project_method = 'match to hist'
                    self.register_method = 2
                else:
                    atlas_rect = self.atlas_rect
                    histo_rect = self.histo_rect
                    self.project_method = 'match to atlas'
                    self.register_method = 1
                src_xrange = (atlas_rect[0], atlas_rect[0] + atlas_rect[2])
                src_yrange = (atlas_rect[1], atlas_rect[1] + atlas_rect[3])
                src_img = da_label_img[src_yrange[0]:src_yrange[1], src_xrange[0]:src_xrange[1], :].copy()

                da_dim = (histo_rect[2], histo_rect[3])
                resized_des = cv2.resize(src_img, da_dim, interpolation=cv2.INTER_LINEAR)

                des_xrange = (histo_rect[0], histo_rect[0] + histo_rect[2])
                des_yrange = (histo_rect[1], histo_rect[1] + histo_rect[3])
                img_wrap[des_yrange[0]:des_yrange[1], des_xrange[0]:des_xrange[1]] = resized_des

            self.image_view.img_stacks.overlay_img.setImage(img_wrap)
            res = cv2.resize(img_wrap, self.image_view.tb_size, interpolation=cv2.INTER_AREA)
            self.master_layers(res, layer_type='image-overlay')
            self.a2h_transferred = True
            self.tool_box.toh_btn.setIcon(self.tool_box.toh_btn_on_icon)
            self.tool_box.toa_btn.setEnabled(False)
        else:
            self.image_view.img_stacks.overlay_img.clear()
            layer_ind = [ind for ind in range(self.layer_ctrl.layer_count) if
                         self.layer_ctrl.layer_link[ind] == 'image-overlay']
            self.layer_ctrl.delete_layer(layer_ind)
            self.a2h_transferred = False
            self.tool_box.toh_btn.setIcon(self.tool_box.toh_btn_off_icon)
            self.project_method = 'pre plan'
            self.register_method = 0
            self.tool_box.toa_btn.setEnabled(True)

    #
    def transfer_to_atlas_clicked(self):
        if self.image_view.image_file is None:
            return
        if self.atlas_view.atlas_data is None:
            return
        if self.atlas_view.atlas_label is None:
            return
        print('to A clicked')
        if not self.h2a_transferred:
            if self.image_view.image_file.is_rgb:
                self.input_img = self.image_view.current_img.copy()
            else:
                czi_img = self.image_view.current_img.copy()
                channel_hsv = self.image_view.image_file.hsv_colors
                img_temp = merge_channels_into_single_img(czi_img, channel_hsv)
                input_img = cv2.normalize(img_temp, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
                self.input_img = input_img.astype('uint8')

            input_img = self.input_img.copy()
            img_wrap = np.zeros((self.atlas_view.slice_size[0], self.atlas_view.slice_size[1], 3), np.float32)

            if self.histo_tri_inside_data and self.atlas_tri_inside_data:
                print('match triangles to atlas')
                a_temp = len(self.histo_tri_data)
                b_temp = len(self.atlas_tri_data)
                if a_temp != b_temp:
                    print('number of points are not matching.')
                    return

                subdiv = cv2.Subdiv2D(self.atlas_rect)
                for p in self.atlas_tri_data:
                    subdiv.insert(p)

                tri_vet_inds = get_vertex_ind_in_triangle(subdiv)

                for i in range(len(tri_vet_inds)):
                    da_inds = tri_vet_inds[i]
                    t2 = [self.atlas_tri_data[da_inds[0]], self.atlas_tri_data[da_inds[1]],
                          self.atlas_tri_data[da_inds[2]]]
                    t1 = [self.histo_tri_data[da_inds[0]], self.histo_tri_data[da_inds[1]],
                          self.histo_tri_data[da_inds[2]]]
                    t1 = np.reshape(t1, (3, 2))
                    t2 = np.reshape(t2, (3, 2))
                    warp_triangle(input_img, img_wrap, t1, t2, True)
            else:
                if self.small_atlas_rect is not None:
                    atlas_rect = self.small_atlas_rect
                    histo_rect = self.small_histo_rect
                else:
                    atlas_rect = self.atlas_rect
                    histo_rect = self.histo_rect
                src_xrange = (histo_rect[0], histo_rect[0] + histo_rect[2])
                src_yrange = (histo_rect[1], histo_rect[1] + histo_rect[3])
                src_img = input_img[src_yrange[0]:src_yrange[1], src_xrange[0]:src_xrange[1], :].copy()

                da_dim = (atlas_rect[2], atlas_rect[3])
                resized_des = cv2.resize(src_img, da_dim, interpolation=cv2.INTER_LINEAR)

                des_xrange = (atlas_rect[0], atlas_rect[0] + atlas_rect[2])
                des_yrange = (atlas_rect[1], atlas_rect[1] + atlas_rect[3])
                img_wrap[des_yrange[0]:des_yrange[1], des_xrange[0]:des_xrange[1]] = resized_des

            self.atlas_view.working_atlas.overlay_img.setImage(img_wrap)
            res = cv2.resize(img_wrap, self.atlas_view.slice_tb_size, interpolation=cv2.INTER_AREA)
            self.master_layers(res, layer_type='atlas-overlay')
            self.h2a_transferred = True
            self.tool_box.toa_btn.setIcon(self.tool_box.toa_btn_on_icon)
            self.project_method = 'match to atlas'
            self.register_method = 0
            self.tool_box.toh_btn.setEnabled(False)
        else:
            self.atlas_view.working_atlas.overlay_img.clear()
            layer_ind = [ind for ind in range(self.layer_ctrl.layer_count) if self.layer_ctrl.layer_link[ind] == 'atlas-overlay']
            self.layer_ctrl.delete_layer(layer_ind)
            self.h2a_transferred = False
            self.tool_box.toa_btn.setIcon(self.tool_box.toa_btn_off_icon)
            self.project_method = 'pre plan'
            self.register_method = 0
            self.tool_box.toh_btn.setEnabled(True)

    #
    #    Accept
    #
    def transfer_pnt(self, pnt, tri_vet_inds):
        res_pnts = np.zeros((len(pnt), 2))
        res_pnts[:] = np.nan
        loc = get_pnts_triangle_ind(tri_vet_inds, self.histo_tri_data, self.image_view.img_size, pnt)
        loc = np.ravel(loc)
        if np.any(np.isnan(loc)):
            print('check transform')
        for i in range(len(tri_vet_inds)):
            da_inds = tri_vet_inds[i]
            t2 = [self.atlas_tri_data[da_inds[0]], self.atlas_tri_data[da_inds[1]],
                  self.atlas_tri_data[da_inds[2]]]
            t1 = [self.histo_tri_data[da_inds[0]], self.histo_tri_data[da_inds[1]],
                  self.histo_tri_data[da_inds[2]]]
            t1 = np.reshape(t1, (3, 2))
            t2 = np.reshape(t2, (3, 2))
            inds = np.where(loc == i)
            if len(inds) > 0:
                pnts_inside = pnt[inds[0]]
                res = warp_points(pnts_inside, t1, t2)
                res_pnts[inds[0]] = res
        res_pnts = res_pnts[~np.isnan(res_pnts[:, 0])]
        return res_pnts

    def transfer_vox_to_pnt(self, img_data, tri_vet_inds):
        temp_pnts = np.where(img_data != 0)
        data = np.stack([temp_pnts[1], temp_pnts[0]], axis=1) + 0.5
        res_pnts = self.transfer_pnt(data, tri_vet_inds)
        return res_pnts

    def transform_accept(self):
        subdiv = cv2.Subdiv2D(self.atlas_rect)
        for p in self.atlas_tri_data:
            subdiv.insert(p)

        tri_vet_inds = get_vertex_ind_in_triangle(subdiv)

        if self.working_img_virus_data is not None:
            input_virus_img = self.working_img_virus_data.copy()
            res_pnts = self.transfer_vox_to_pnt(input_virus_img, tri_vet_inds)
            self.working_atlas_virus = res_pnts
            self.atlas_view.working_atlas.virus_pnts.setData(pos=np.asarray(self.working_atlas_virus))

        if self.working_img_contour_data is not None:
            input_contour_img = self.working_img_contour_data.copy()
            res_pnts = self.transfer_vox_to_pnt(input_contour_img, tri_vet_inds)
            self.working_atlas_contour = res_pnts
            self.atlas_view.working_atlas.contour_pnts.setData(pos=np.asarray(self.working_atlas_contour))

        if self.working_img_cell_data:
            res_pnts = self.transfer_pnt(np.asarray(self.working_img_cell_data), tri_vet_inds)
            self.working_atlas_cell = res_pnts
            self.atlas_view.working_atlas.cell_pnts.setData(pos=np.asarray(self.working_atlas_cell))

        if self.working_img_probe_data:
            res_pnts = self.transfer_pnt(np.asarray(self.working_img_probe_data), tri_vet_inds)
            self.working_atlas_probe = res_pnts
            self.atlas_view.working_atlas.probe_pnts.setData(pos=np.asarray(self.working_atlas_probe))
            if not self.atlas_view.working_atlas.probe_pnts.isVisible():
                self.atlas_view.working_atlas.probe_pnts.setVisible(True)

        if self.working_img_drawing_data:
            res_pnts = self.transfer_pnt(np.asarray(self.working_img_drawing_data), tri_vet_inds)
            self.working_atlas_drawing = res_pnts
            self.atlas_view.working_atlas.drawing_pnts.setData(pos=np.asarray(self.working_atlas_drawing))


    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    #
    #                      Image Processing
    #
    # ------------------------------------------------------------------
    def update_histo_tri_onside_data(self):
        print('image_changed')
        self.reset_corners_hist()
        self.working_img_mask_data = np.zeros(self.image_view.img_size).astype('uint8')
        self.process_img = None
        self.image_view.img_stacks.processing_image.clear()

    def make_pencil_path(self, loc, img):
        x = int(loc[1] - 0.5 * self.pencil_size)
        y = int(loc[0] - 0.5 * self.pencil_size)
        xr = (x, x + self.pencil_size)
        yr = (y, y + self.pencil_size)
        img[xr[0]:xr[1], yr[0]:yr[1]] = 1
        return img

    def img_stacks_clicked(self, pos):
        x = pos[0]
        y = pos[1]
        print('image', (x, y))
        if self.image_view.image_file is None:
            return
        # ------------------------- pencil
        if self.tool_box.checkable_btn_dict['pencil_btn'].isChecked():
            self.working_img_drawing_data.append([x, y])
            self.image_view.img_stacks.drawing_pnts.setData(np.asarray(self.working_img_drawing_data))
            if len(self.working_img_drawing_data) < 2:
                img = np.zeros(self.image_view.img_size).astype('uint8')
            else:
                img = self.image_view.img_stacks.drawing_img.image.copy()
            loc = np.ravel(self.working_img_drawing_data[-1]).astype(int)
            img = self.make_pencil_path(loc, img)
            # self.image_view.img_stacks.drawing_img.setImage(img, autoLevels=False)
            if self.is_pencil_allowed:
                self.is_pencil_allowed = False
            else:
                self.is_pencil_allowed = True
        # ------------------------- eraser
        elif self.tool_box.checkable_btn_dict['eraser_btn'].isChecked():
            r = self.tool_box.eraser_size_slider.value()
            mask_img = np.zeros(self.image_view.img_size, dtype=np.uint8)
            cv2.circle(mask_img, center=(int(x), int(y)), radius=r, color=255, thickness=-1)
            mask_img = 255 - mask_img
            if not self.layer_ctrl.layer_index or len(self.layer_ctrl.current_layer_ind) > 1:
                print('check')
                return
            else:
                da_ind = np.where(np.ravel(self.layer_ctrl.layer_index) == self.layer_ctrl.current_layer_ind[0])[0]
                da_link = self.layer_ctrl.layer_link[da_ind[0]]
                if da_link == 'img-mask':
                    temp = self.working_img_mask_data.astype(np.uint8)
                    dst = cv2.bitwise_and(temp, temp, mask=mask_img)
                    res = cv2.resize(dst, self.image_view.tb_size, interpolation=cv2.INTER_AREA)
                    self.image_view.img_stacks.mask_img.setImage(dst)
                    self.working_img_mask_data = dst
                if da_link == 'img-copy':
                    print('do something')
                else:
                    return
                self.layer_ctrl.layer_list[da_ind[0]].set_thumbnail_data(res)
        # ------------------------- magic wand -- virus
        elif self.tool_box.checkable_btn_dict['magic_wand_btn'].isChecked():
            tol_val = float(self.tool_box.magic_tol_val.text())
            white_img = np.ones(self.image_view.img_size).astype('uint8')
            if self.image_view.image_file.is_rgb:
                src_img = self.image_view.current_img.copy()
                da_color = src_img[int(y), int(x)]
                lower_val, upper_val = get_bound_color(da_color, tol_val, self.image_view.image_file.level,
                                                       self.image_view.current_mode)
                if self.image_view.current_mode != 'gray':
                    mask_img = cv2.inRange(src_img, tuple(lower_val), tuple(upper_val))
                else:
                    mask_img = white_img.copy()
                    ret, thresh = cv2.threshold(src_img, lower_val, upper_val, cv2.THRESH_BINARY)
                    mask_img = cv2.bitwise_and(mask_img, mask_img, mask=thresh.astype(np.uint8))
            else:
                mask_img = white_img.copy()
                for i in range(self.image_view.image_file.n_channels):
                    if not self.image_view.channel_visible[i]:
                        continue
                    temp = self.image_view.current_img[:, :, i]
                    selected_color = temp[int(y), int(x)]
                    lower_range = selected_color - tol_val
                    upper_range = selected_color + tol_val
                    ret, thresh = cv2.threshold(temp, lower_range, upper_range, cv2.THRESH_BINARY)
                    mask_img = cv2.bitwise_and(mask_img, mask_img, mask=thresh.astype(np.uint8))
            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier:
                self.working_img_mask_data = cv2.bitwise_or(self.working_img_mask_data, mask_img, mask=white_img)
            else:
                self.working_img_mask_data = mask_img.copy()

            ksize = int(self.tool_box.magic_wand_ksize.text())
            kernel_shape = self.tool_box.magic_wand_kernel.currentText()
            if ksize != 0 and kernel_shape != "Kernel":
                if kernel_shape == "Rectangular":
                    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (ksize, ksize))
                elif kernel_shape == "Elliptical":
                    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ksize, ksize))
                else:
                    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (ksize, ksize))
                temp = self.working_img_mask_data.copy()
                open_img = cv2.morphologyEx(temp, cv2.MORPH_OPEN, kernel)
                close_img = cv2.morphologyEx(open_img, cv2.MORPH_CLOSE, kernel)
                self.working_img_mask_data = close_img.copy()
            self.image_view.img_stacks.mask_img.setImage(self.working_img_mask_data)
            res = cv2.resize(self.working_img_mask_data, self.image_view.tb_size, interpolation=cv2.INTER_AREA)
            self.master_layers(res, layer_type='img-mask')

        # ------------------------- lasso
        elif self.tool_box.checkable_btn_dict['lasso_btn'].isChecked():
            if self.lasso_is_closure:
                self.inactive_lasso()
                return
            new_pnt = np.array([x, y])
            if len(self.lasso_pnts) > 1:
                dists = np.sum((np.asarray(self.lasso_pnts[0]) - new_pnt) ** 2)
            else:
                dists = 1e5
            if dists < 5:
                self.lasso_pnts.append(self.lasso_pnts[0])
                self.image_view.img_stacks.lasso_pnts.setPen(pg.mkPen(color='r', width=3, style=Qt.SolidLine))
                self.lasso_is_closure = True
            else:
                self.lasso_pnts.append([x, y])
            drawing_pnts = np.asarray(self.lasso_pnts)
            self.image_view.img_stacks.lasso_path.setData(drawing_pnts)
        # ------------------------- triang -- triangulation pnts
        elif self.tool_box.checkable_btn_dict['triang_btn'].isChecked():
            if self.a2h_transferred or self.h2a_transferred:
                return
            self.histo_tri_inside_data.append([int(x), int(y)])
            self.histo_tri_data = self.histo_tri_onside_data + self.histo_tri_inside_data
            self.image_view.img_stacks.tri_pnts.setData(pos=np.asarray(self.histo_tri_data))
            self.working_img_text.append(pg.TextItem(str(len(self.histo_tri_data) - (self.np_onside - 1) * 4)))
            self.image_view.img_stacks.vb.addItem(self.working_img_text[-1])
            self.working_img_text[-1].setPos(x, y)
            if self.tool_box.triang_vis_btn.isChecked():
                self.update_histo_tri_lines()
        # ------------------------- loc -- cell
        elif self.tool_box.checkable_btn_dict['loc_btn'].isChecked():
            if self.tool_box.cell_selector_btn.isChecked():
                self.working_img_cell_data.append([x, y])
                self.working_img_cell_size.append(1)
                self.image_view.img_stacks.cell_pnts.setData(pos=np.asarray(self.working_img_cell_data))
                self.cell_count += 1
                self.tool_box.cell_count_val.setText(str(self.cell_count))
                locs = np.asarray(self.working_img_cell_data).astype(int)
                temp = np.zeros(self.image_view.img_size[:2], 'uint8')
                temp[locs[:, 1], locs[:, 0]] = 1
                res = cv2.resize(temp, self.image_view.tb_size, interpolation=cv2.INTER_AREA)
                self.master_layers(res, layer_type='img-cells')
            if self.tool_box.cell_aim_btn.isChecked():
                self.working_blob_data.append([x, y])
                self.image_view.img_stacks.blob_pnts.setData(pos=np.asarray(self.working_blob_data))

        # ------------------------- probe
        elif self.tool_box.checkable_btn_dict['probe_btn'].isChecked():
            self.working_img_probe_data.append([x, y])
            self.image_view.img_stacks.probe_pnts.setData(pos=np.asarray(self.working_img_probe_data))
            mask = np.zeros(self.image_view.img_size, dtype="uint8")
            locs = np.asarray(self.working_img_probe_data).astype(int)
            mask[locs[:, 1], locs[:, 0]] = 255
            res = cv2.resize(mask.T, self.image_view.tb_size, interpolation=cv2.INTER_AREA)
            self.master_layers(res, layer_type='img-probes')
        else:
            return

    def img_stacks_hovered(self, event):
        if event.isExit():
            return
        try:
            pos = (event.pos())
        except (IndexError, AttributeError):
            return
        y = pos.y()
        x = pos.x()
        if self.tool_box.checkable_btn_dict['eraser_btn'].isChecked():
            self.eraser_is_on = True
            r = self.tool_box.eraser_size_slider.value()
            shp = self.image_view.current_img.shape
            if x - r > 0 and x + r < shp[1] and y - r > 0 and y + r < shp[0]:
                data = self.tool_box.circle.copy()
                data[:, 0] = data[:, 0] + x
                data[:, 1] = data[:, 1] + y
                self.image_view.img_stacks.circle_follow.setData(data)
        if self.tool_box.checkable_btn_dict['pencil_btn'].isChecked():
            if self.is_pencil_allowed:
                self.working_img_drawing_data.append([x, y])
                self.image_view.img_stacks.drawing_pnts.setData(np.asarray(self.working_img_drawing_data))
                img = self.image_view.img_stacks.drawing_img.image.copy()
                loc = np.ravel(self.working_img_drawing_data[-1]).astype(int)
                img = self.make_pencil_path(loc, img)
                self.image_view.img_stacks.drawing_img.setImage(img, autoLevels=False)
        self.statusbar.showMessage('Histological image coordinates: {}, {}'.format(x, y))

    def img_stacks_key_pressed(self, action):
        print(action)
        if not self.layer_ctrl.current_layer_ind or len(self.layer_ctrl.current_layer_ind) > 1:
            return
        da_ind = np.where(np.ravel(self.layer_ctrl.layer_index) == self.layer_ctrl.current_layer_ind[0])[0]
        da_link = self.layer_ctrl.layer_link[da_ind[0]]

        if action == 'delete':
            if self.lasso_is_closure:
                mask = np.zeros(self.image_view.img_size, dtype=np.uint8)
                pts = np.int32(self.lasso_pnts)
                cv2.fillPoly(mask, pts=[pts], color=255)
                mask = 255 - mask
                if da_link == 'img-virus':
                    dst = cv2.bitwise_and(self.working_img_virus_data, self.working_img_virus_data, mask=mask)
                    self.image_view.img_stacks.virus_img.setImage(dst)
                    self.working_img_virus_data = dst
                    res = cv2.resize(self.working_img_virus_data, self.image_view.tb_size, interpolation=cv2.INTER_AREA)
                elif da_link == 'img-contour':
                    dst = cv2.bitwise_and(self.working_img_contour_data, self.working_img_contour_data, mask=mask)
                    self.image_view.img_stacks.contour_img.setImage(dst)
                    self.working_img_contour_data = dst
                    res = cv2.resize(self.working_img_contour_data, self.image_view.tb_size, interpolation=cv2.INTER_AREA)
                elif da_link == 'img-mask':
                    dst = cv2.bitwise_and(self.working_img_mask_data, self.working_img_mask_data, mask=mask)
                    self.image_view.img_stacks.mask_img.setImage(dst)
                    self.working_img_mask_data = dst
                    res = cv2.resize(self.working_img_mask_data, self.image_view.tb_size, interpolation=cv2.INTER_AREA)
                elif da_link == 'img-copy':
                    print('do something')
                else:
                    return
                self.layer_ctrl.layer_list[da_ind[0]].set_thumbnail_data(res)
            else:
                if self.working_img_mask_data is None or da_link != 'img-copy':
                    return
                mask = self.working_img_mask_data.copy()
                temp_img = self.image_view.img_stacks.processing_image.image.copy()
                new_img = np.zeros((self.image_view.img_size[0], self.image_view.img_size[1], 4), 'uint8')
                new_img[:, :, :3] = temp_img
                new_img[:, :, 3] = mask
                self.image_view.img_stacks.processing_image.setImage(new_img)

    def hist_window_tri_pnts_moving(self, ev_obj):
        ev = ev_obj[0]
        ind = ev_obj[1]
        da_num = (self.np_onside - 1) * 4
        if ind < da_num:
            return
        if self.a2h_transferred:
            old_pnts = self.histo_tri_data.copy()
            new_pnts = self.histo_tri_data.copy()
            da_new_pnt = self.image_view.img_stacks.tri_pnts.data['pos'][ind].copy()
            new_pnts[ind] = [int(da_new_pnt[0]), int(da_new_pnt[1])]

            img_overlay = self.image_view.img_stacks.overlay_img.image.copy()
            img_wrap = img_overlay.copy()

            img_size = img_wrap.shape[:2]
            rect = (0, 0, img_size[1], img_size[0])

            subdiv = cv2.Subdiv2D(rect)
            for p in new_pnts:
                subdiv.insert(p)

            tri_vet_inds = get_vertex_ind_in_triangle(subdiv)
            for i in range(len(tri_vet_inds)):
                da_inds = tri_vet_inds[i]
                # if ind not in da_inds:
                #     continue
                t1 = [old_pnts[da_inds[0]], old_pnts[da_inds[1]], old_pnts[da_inds[2]]]
                t2 = [new_pnts[da_inds[0]], new_pnts[da_inds[1]], new_pnts[da_inds[2]]]
                t1 = np.reshape(t1, (3, 2))
                t2 = np.reshape(t2, (3, 2))
                warp_triangle(img_overlay, img_wrap,  t1, t2, True)
            self.image_view.img_stacks.overlay_img.setImage(img_wrap)
            self.histo_tri_data = new_pnts
        else:
            da_new_pnt = self.image_view.img_stacks.tri_pnts.data['pos'][ind].copy()
            self.histo_tri_data[ind] = [int(da_new_pnt[0]), int(da_new_pnt[1])]
        self.histo_tri_inside_data[ind - da_num] = [int(da_new_pnt[0]), int(da_new_pnt[1])]
        self.working_img_text[ind - da_num].setPos(da_new_pnt[0], da_new_pnt[1])
        if self.tool_box.triang_vis_btn.isChecked():
            self.update_histo_tri_lines()

    def img_probe_pnts_clicked(self, points, ev):
        if not self.tool_box.checkable_btn_dict['eraser_btn'].isChecked() or not self.working_img_probe_data:
            return
        clicked_ind = ev[0].index()
        del self.working_img_probe_data[clicked_ind]
        self.image_view.img_stacks.probe_pnts.setData(np.asarray(self.working_img_probe_data))

    def img_drawing_pnts_clicked(self, points, ev):
        if not self.tool_box.checkable_btn_dict['eraser_btn'].isChecked() or not self.working_img_drawing_data:
            return
        clicked_ind = ev[0].index()
        del self.working_img_pnts[clicked_ind]
        self.image_view.img_stacks.drawing_pnts.setData(np.asarray(self.working_img_drawing_data))

    def img_manual_cell_pnts_clicked(self, points, ev):
        if not self.tool_box.checkable_btn_dict['eraser_btn'].isChecked() or not self.working_img_man:
            return

    def hist_window_tri_pnts_clicked(self, ev):
        if not self.tool_box.checkable_btn_dict['eraser_btn'].isChecked() or not self.histo_tri_data:
            return
        if self.a2h_transferred or self.h2a_transferred:
            return
        self.inactive_lasso()
        clicked_ind = ev[1]
        num = (self.np_onside - 1) * 4
        if clicked_ind < num:
            return
        self.image_view.img_stacks.vb.removeItem(self.working_img_text[-1])
        del self.working_img_text[-1]
        del self.histo_tri_data[clicked_ind]
        del self.histo_tri_inside_data[clicked_ind - num]
        self.image_view.img_stacks.tri_pnts.setData(pos=np.asarray(self.histo_tri_data))
        for i in range(len(self.working_img_text)):
            pnt_id = i + num
            self.working_img_text[i].setPos(self.histo_tri_data[pnt_id][0], self.histo_tri_data[pnt_id][1])
        if self.tool_box.triang_vis_btn.isChecked():
            self.update_histo_tri_lines()

    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    #
    #                       Atlas control
    #
    # ------------------------------------------------------------------
    def coronal_slice_stacks_hovered(self, pos):
        y = pos.y()
        x = pos.x()

        c_id = self.atlas_view.current_coronal_index
        s_id = self.atlas_view.current_sagital_index
        h_id = self.atlas_view.current_horizontal_index

        o_rot = np.array([h_id, s_id, c_id])
        da_pnt = np.array([y, x, c_id])

        if self.atlas_view.coronal_rotated:
            da_pnt = o_rot + np.dot(self.atlas_view.c_rotm, (da_pnt - o_rot))

        da_label = self.atlas_view.cimg.label_img.image.copy()
        da_id = da_label[int(y), int(x)]

        coords = np.round((da_pnt - np.ravel(self.atlas_view.Bregma)) * self.atlas_view.vxsize_um, 2)
        pstr = 'Atlas voxel:({}, {}, {}), ML:{}um, AP:{}um, DV:{}um) : {} '.format(
            int(da_pnt[1]), int(da_pnt[2]), int(self.atlas_view.atlas_size[0] - da_pnt[0]), coords[1], coords[2], coords[0],
            self.atlas_view.label_tree.describe(da_id))
        self.statusbar.showMessage(pstr)

    def sagital_slice_stacks_hovered(self, pos):
        y = pos.y()
        x = pos.x()

        c_id = self.atlas_view.current_coronal_index
        s_id = self.atlas_view.current_sagital_index
        h_id = self.atlas_view.current_horizontal_index

        o_rot = np.array([h_id, s_id, c_id])
        da_pnt = np.array([y, s_id, x])

        if self.atlas_view.sagital_rotated:
            da_pnt = o_rot + np.dot(self.atlas_view.s_rotm, (da_pnt - o_rot))

        da_label = self.atlas_view.simg.label_img.image.copy()
        da_id = da_label[int(y), int(x)]

        coords = np.round((da_pnt - np.ravel(self.atlas_view.Bregma)) * self.atlas_view.vxsize_um, 2)
        pstr = 'Atlas voxel:({}, {}, {}), ML:{}um, AP:{}um, DV:{}um) : {} '.format(
            int(da_pnt[1]), int(da_pnt[2]), int(self.atlas_view.atlas_size[0] - da_pnt[0]), coords[1], coords[2], coords[0],
            self.atlas_view.label_tree.describe(da_id))
        self.statusbar.showMessage(pstr)

    def horizontal_slice_stacks_hovered(self, pos):
        y = pos.y()
        x = pos.x()

        c_id = self.atlas_view.current_coronal_index
        s_id = self.atlas_view.current_sagital_index
        h_id = self.atlas_view.current_horizontal_index

        o_rot = np.array([h_id, s_id, c_id])
        da_pnt = np.array([h_id, y, x])

        if self.atlas_view.horizontal_rotated:
            da_pnt = o_rot + np.dot(self.atlas_view.h_rotm, (da_pnt - o_rot))

        da_label = self.atlas_view.himg.label_img.image.copy()
        da_id = da_label[int(y), int(x)]

        coords = np.round((da_pnt - np.ravel(self.atlas_view.Bregma)) * self.atlas_view.vxsize_um, 2)
        pstr = 'Atlas voxel:({}, {}, {}), ML:{}um, AP:{}um, DV:{}um) : {} '.format(
            int(da_pnt[1]), int(da_pnt[2]), int(self.atlas_view.atlas_size[0] - da_pnt[0]), coords[1], coords[2], coords[0],
            self.atlas_view.label_tree.describe(da_id))
        self.statusbar.showMessage(pstr)

    def atlas_stacks_clicked(self, pos):
        # print('atlas clicked')
        x = pos[0]
        y = pos[1]
        if self.atlas_view.atlas_data is None:
            return
        if self.num_windows == 4:
            return
        if self.tool_box.checkable_btn_dict['triang_btn'].isChecked():
            self.inactive_lasso()
            if self.a2h_transferred or self.h2a_transferred:
                return
            self.atlas_tri_inside_data.append([int(x), int(y)])
            self.atlas_tri_data = self.atlas_tri_onside_data + self.atlas_tri_inside_data
            self.atlas_view.working_atlas.tri_pnts.setData(pos=np.asarray(self.atlas_tri_data))
            self.working_atlas_text.append(pg.TextItem(str(len(self.atlas_tri_inside_data))))
            self.atlas_view.working_atlas.vb.addItem(self.working_atlas_text[-1])
            self.working_atlas_text[-1].setPos(x, y)
            if self.tool_box.triang_vis_btn.isChecked():
                self.update_atlas_tri_lines()
        if self.tool_box.checkable_btn_dict['probe_btn'].isChecked():
            self.inactive_lasso()
            self.working_atlas_probe.append([x, y])
            self.atlas_view.working_atlas.probe_pnts.setData(pos=np.asarray(self.working_atlas_probe))
            if not self.atlas_view.working_atlas.probe_pnts.isVisible():
                self.atlas_view.working_atlas.probe_pnts.setVisible(True)
        # ------------------------- magic wand -- mask
        if self.tool_box.checkable_btn_dict['magic_wand_btn'].isChecked():
            self.inactive_lasso()
            if not self.h2a_transferred:
                return
            white_img = np.ones(self.atlas_view.slice_size).astype('uint8')
            tol_val = int(self.tool_box.magic_tol_val.text())
            src_img = self.atlas_view.working_atlas.overlay_img.image.copy()
            da_color = src_img[int(y), int(x)]
            lower_val, upper_val = get_bound_color(da_color, tol_val, self.image_view.image_file.level, 'rgb')
            mask_img = cv2.inRange(src_img, lower_val, upper_val)

            # des_img = cv2.bitwise_and(des_img, des_img, mask=self.working_atlas_mask)

            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier:
                self.working_atlas_mask = cv2.bitwise_or(self.working_atlas_mask, mask_img, mask=white_img)
            else:
                self.working_atlas_mask = mask_img * 255

            ksize = int(self.tool_box.magic_wand_ksize.text())
            kernel_shape = self.tool_box.magic_wand_kernel.currentText()
            if ksize != 0 and kernel_shape != "Kernel":
                if kernel_shape == "Rectangular":
                    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (ksize, ksize))
                elif kernel_shape == "Elliptical":
                    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ksize, ksize))
                else:
                    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (ksize, ksize))
                temp = self.working_atlas_mask.copy()
                open_img = cv2.morphologyEx(temp, cv2.MORPH_OPEN, kernel)
                close_img = cv2.morphologyEx(open_img, cv2.MORPH_CLOSE, kernel)
                self.working_atlas_mask = 255 - close_img

            self.atlas_view.working_atlas.mask_img.setImage(self.working_atlas_mask)
            res = cv2.resize(self.working_atlas_mask, self.image_view.tb_size, interpolation=cv2.INTER_AREA)
            self.master_layers(res, layer_type='atlas-mask')

    #
    def atlas_window_tri_pnts_moving(self, ev_obj):
        ev = ev_obj[0]
        ind = ev_obj[1]
        da_num = (self.np_onside - 1) * 4
        if ind < da_num:
            return
        if self.h2a_transferred:
            old_pnts = self.atlas_tri_data.copy()
            new_pnts = self.atlas_tri_data.copy()
            da_new_pnt = self.atlas_view.working_atlas.tri_pnts.data['pos'][ind].copy()
            new_pnts[ind] = [int(da_new_pnt[0]), int(da_new_pnt[1])]

            input_img = self.input_img.copy()

            img_wrap = np.zeros((self.atlas_view.slice_size[0], self.atlas_view.slice_size[1], 3), np.float32)

            subdiv = cv2.Subdiv2D(self.atlas_rect)
            for p in self.atlas_tri_data:
                subdiv.insert(p)

            tri_vet_inds = get_vertex_ind_in_triangle(subdiv)
            for i in range(len(tri_vet_inds)):
                da_inds = tri_vet_inds[i]
                t2 = [self.atlas_tri_data[da_inds[0]], self.atlas_tri_data[da_inds[1]],
                      self.atlas_tri_data[da_inds[2]]]
                t1 = [self.histo_tri_data[da_inds[0]], self.histo_tri_data[da_inds[1]],
                      self.histo_tri_data[da_inds[2]]]
                t1 = np.reshape(t1, (3, 2))
                t2 = np.reshape(t2, (3, 2))
                warp_triangle(input_img, img_wrap, t1, t2, True)

            #

            # # img_overlay = self.atlas_view.working_atlas.overlay_img.image.copy()
            # img_wrap = img_overlay.copy()
            #
            # img_size = img_wrap.shape[:2]
            # rect = (0, 0, img_size[1], img_size[0])
            #
            # subdiv = cv2.Subdiv2D(rect)
            # for p in new_pnts:
            #     subdiv.insert(p)
            #
            # tri_vet_inds = get_vertex_ind_in_triangle(subdiv)
            # for i in range(len(tri_vet_inds)):
            #     da_inds = tri_vet_inds[i]
            #     if ind not in da_inds:
            #         continue
            #     t1 = [old_pnts[da_inds[0]], old_pnts[da_inds[1]], old_pnts[da_inds[2]]]
            #     t2 = [new_pnts[da_inds[0]], new_pnts[da_inds[1]], new_pnts[da_inds[2]]]
            #     t1 = np.reshape(t1, (3, 2))
            #     t2 = np.reshape(t2, (3, 2))
            #     warp_triangle(img_overlay, img_wrap,  t1, t2, True)
            self.atlas_view.working_atlas.overlay_img.setImage(img_wrap)
            self.atlas_tri_data = new_pnts
        else:
            da_new_pnt = self.atlas_view.working_atlas.tri_pnts.data['pos'][ind].copy()
            self.atlas_tri_data[ind] = [int(da_new_pnt[0]), int(da_new_pnt[1])]
        self.atlas_tri_inside_data[ind - da_num] = [int(da_new_pnt[0]), int(da_new_pnt[1])]
        self.working_atlas_text[ind - da_num].setPos(da_new_pnt[0], da_new_pnt[1])
        if self.tool_box.triang_vis_btn.isChecked():
            self.update_atlas_tri_lines()

    def atlas_window_tri_pnts_clicked(self, ev):
        print('atlas tri pnts clicked')
        if not self.tool_box.checkable_btn_dict['eraser_btn'].isChecked() or not self.atlas_tri_data:
            return
        if self.a2h_transferred or self.h2a_transferred:
            return
        self.inactive_lasso()
        clicked_ind = ev[1]
        num = (self.np_onside - 1) * 4
        if clicked_ind < num:
            return
        print(self.atlas_tri_data)
        self.atlas_view.working_atlas.vb.removeItem(self.working_atlas_text[-1])
        del self.working_atlas_text[-1]
        del self.atlas_tri_inside_data[clicked_ind - num]
        self.atlas_tri_data = self.atlas_tri_onside_data + self.atlas_tri_inside_data
        self.atlas_view.working_atlas.tri_pnts.setData(pos=np.asarray(self.atlas_tri_data))
        for i in range(len(self.working_atlas_text)):
            pnt_id = i + num
            self.working_atlas_text[i].setPos(self.atlas_tri_data[pnt_id][0], self.atlas_tri_data[pnt_id][1])
        if self.tool_box.triang_vis_btn.isChecked():
            self.update_atlas_tri_lines()




    # ------------------------------------------------------------------
    #
    #                       Atlas 3D control
    #
    # ------------------------------------------------------------------
    def show_small_area_in_3d(self):
        if self.show_child_mesh:
            self.show_child_mesh = False
        else:
            self.show_child_mesh = True

    def composition_3d_changed(self):
        if self.atlas_view.atlas_data is None:
            return
        all_keys = list(self.small_mesh_list.keys())
        for da_key in all_keys:
            self.small_mesh_list[da_key].setGLOptions(self.composition_combo.currentText())

    def sig_label_changed(self):
        if self.atlas_view.atlas_data is None or self.atlas_view.atlas_label is None:
            return
        lut = self.atlas_view.label_tree.lookup_table()

        self.atlas_view.cimg.label_img.setLookupTable(lut=lut)
        self.atlas_view.simg.label_img.setLookupTable(lut=lut)
        self.atlas_view.himg.label_img.setLookupTable(lut=lut)

        if len(self.small_mesh_list) == 0:
            return
        valid_id = list(self.small_mesh_list.keys())
        current_checked_label = list(self.atlas_view.label_tree.checked)
        n_current_label = len(current_checked_label)
        n_previous_label = len(self.previous_checked_label)
        if self.show_child_mesh:
            if n_current_label > n_previous_label:
                label_to_show = [id for id in current_checked_label if id not in self.previous_checked_label]
                label_to_show = list(np.ravel(label_to_show).astype(str))
                for id in label_to_show:
                    if id in valid_id:
                        self.small_mesh_list[id].setVisible(True)
            else:
                label_to_hide = [id for id in self.previous_checked_label if id not in current_checked_label]
                label_to_hide = list(np.ravel(label_to_hide).astype(str))
                for id in label_to_hide:
                    if id in valid_id:
                        self.small_mesh_list[id].setVisible(False)
        self.previous_checked_label = current_checked_label

        check_id = list(self.atlas_view.label_tree.checked)

        if self.show_child_mesh:
            if len(check_id) != 0:
                for id in check_id:
                    if id in valid_id:
                        if not self.small_mesh_list[id].visible():
                            self.small_mesh_list[id].setVisible(True)
            else:
                for id in valid_id:
                    if self.small_mesh_list[id].visible():
                        self.small_mesh_list[id].setVisible(False)
        #
        # # lut = self.label_tree.lookup_table()
        # lut = self.acontrols.atlas_view.label_tree.lookup_table()
        # check_id = list(self.acontrols.atlas_view.label_tree.checked)
        # check_id = np.ravel(check_id).astype(str)
        # if len(self.working_mesh) != 0:
        #     print(len(self.working_mesh))
        #     print(self.working_mesh[0])
        #     for i in range(len(self.working_mesh)):
        #         self.view3d.removeItem(self.working_mesh[i])
        #     self.working_mesh = {}
        # print(check_id)
        # valid_id = list(self.small_mesh_list.keys())
        # # valid_id = np.ravel(valid_id).astype(int)
        # print(valid_id)
        # if len(check_id) != 0:
        #     valid_mesh_count = 0
        #     for id in check_id:
        #         if id in valid_id:
        #             col_to_set = np.ravel(lut[int(id)]) / 255
        #             self.small_mesh_list[id].setColor((col_to_set[0], col_to_set[1], col_to_set[2], 0.3))
        #             self.working_mesh[valid_mesh_count] = self.small_mesh_list[id]
        #             self.view3d.addItem(self.working_mesh[valid_mesh_count])
        #             valid_mesh_count += 1





    def atlas_drawing_pnts_clicked(self, points, ev):
        if not self.tool_box.eraser_btn.isChecked() or not self.working_atlas_pnts:
            return
        clicked_ind = ev[0].index()
        del self.working_atlas_drawing[clicked_ind]
        self.atlas_view.working_atlas.drawing_pnts.setData(pos=np.asarray(self.working_atlas_drawing))




    #
    # def image_rotation_changed(self):
    #     val = self.acontrols.hist_img_view.image_rt_slider.value()
    #     page_number = self.acontrols.hist_img_view.page_slider.value()
    #     da_image_data = rotate(self.image_data[page_number], val, preserve_range=True)
    #     if self.hist_overlay:
    #         if self.atlas_display == 'coronal':
    #             self.overlay_img1.setImage(da_image_data)
    #     else:
    #         self.image_data[page_number] = da_image_data
    #         self.acontrols.hist_img_view.img1.setImage(self.image_data[page_number])
    #
    # def image_opacity_changed(self):
    #     val = self.acontrols.hist_img_view.image_op_slider.value()
    #     if self.atlas_display == 'coronal':
    #         self.overlay_img1.3
    #

    # ------------------------------------------------------------------
    #
    #                      layers control
    #
    # ------------------------------------------------------------------
    def master_layers(self, res, layer_type):
        if not self.layer_ctrl.layer_link or layer_type not in self.layer_ctrl.layer_link:
            self.layer_ctrl.add_layer(layer_type)
            self.layer_ctrl.layer_list[-1].set_thumbnail_data(res)
        else:
            print(self.layer_ctrl.layer_link)
            print(layer_type)
            da_ind = np.where(np.ravel(self.layer_ctrl.layer_link) == layer_type)[0]
            self.layer_ctrl.layer_list[da_ind[0]].set_thumbnail_data(res)

    def layers_opacity_changed(self, val):
        if not self.layer_ctrl.current_layer_ind or len(self.layer_ctrl.current_layer_ind) > 1:
            return
        da_ind = np.where(np.ravel(self.layer_ctrl.layer_index) == self.layer_ctrl.current_layer_ind[0])[0]
        if len(da_ind) == 0:
            return
        da_link = self.layer_ctrl.layer_list[da_ind[0]].get_link()
        if 'img' in da_link:
            respond_widget = self.image_view.img_stacks
        elif 'atlas' in da_link:
            respond_widget = self.atlas_view.working_atlas
        else:
            return
        if 'virus' in da_link:
            respond_widget.virus_img.setOpts(opacity=val * 0.01)
        elif 'boundary' in da_link:
            respond_widget.boundary.setOpts(opacity=val * 0.01)
        elif 'mask' in da_link:
            respond_widget.mask_img.setOpts(opacity=val * 0.01)
        elif 'overlay' in da_link:
            respond_widget.overlay_img.setOpts(opacity=val * 0.01)
        elif 'cells' in da_link:
            respond_widget.cell_pnts.setPen((0, 0, 255, int(val * 255 * 0.01)))
        elif 'probes' in da_link:
            respond_widget.probe_pnts.setPen((0, 255, 0, int(val * 255 * 0.01)))
        elif 'lines' in da_link:
            respond_widget.lines.setPen((0, 255, 0, int(val * 255 * 0.01)))
        else:
            return


    def layers_visible_changed(self, event):
        da_link = event[1]
        vis = event[2]
        if vis:
            val = self.layer_ctrl.layer_opacity_slider.value() * 0.01
        else:
            val = 0
        if 'img' in da_link:
            respond_widget = self.image_view.img_stacks
        elif 'atlas' in da_link:
            respond_widget = self.atlas_view.working_atlas
        else:
            return
        if 'virus' in da_link:
            respond_widget.virus_img.setOpts(opacity=val)
        elif 'contour' in da_link:
            respond_widget.contour_img.setOpts(opacity=val)
        elif 'mask' in da_link:
            respond_widget.mask_img.setOpts(opacity=val)
        elif 'overlay' in da_link:
            respond_widget.overlay_img.setOpts(opacity=val)
        elif 'cells' in da_link:
            respond_widget.cell_pnts.setPen((0, 0, 255, int(val * 255)))
        elif 'probes' in da_link:
            respond_widget.probe_pnts.setPen((0, 255, 0, int(val * 255)))
        elif 'drawing' in da_link:
            respond_widget.drawing_pnts.setPen((0, 255, 0, int(val * 255)))
        else:
            return

    #
    # ------------------------------------------------------------------
    #
    #              objects (probe, virus, ....) control
    #
    # ------------------------------------------------------------------
    def get_coronal_3d(self, points2):
        da_y = np.ones(len(points2)) * self.atlas_view.current_coronal_index
        points3 = np.vstack([points2[:, 0], da_y, self.atlas_view.atlas_size[0] - points2[:, 1]]).T
        points3 = points3 - self.atlas_view.bregma3d
        shift_dist = self.atlas_view.current_coronal_index - self.atlas_view.bregma3d[1]
        points3 = points3 + np.array([0, shift_dist, 0])
        if self.atlas_view.coronal_rotated:
            rotm = self.atlas_view.c_rotm_3d
            origin = self.atlas_view.origin3d
            print(origin)
            points3 = np.dot(rotm, (points3 - origin).T).T + origin
            print('p3', points3)
        return points3

    def get_sagital_3d(self, points2):
        da_x = np.ones(len(points2)) * self.atlas_view.current_sagital_index
        points3 = np.vstack([da_x, points2[:, 0], self.atlas_view.atlas_size[0] - points2[:, 1]]).T
        points3 = points3 - self.atlas_view.bregma3d
        shift_dist = self.atlas_view.current_sagital_index - self.atlas_view.bregma3d[0]
        points3 = points3 + np.array([shift_dist, 0, 0])
        if self.atlas_view.sagital_rotated:
            rotm = self.atlas_view.s_rotm_3d
            origin = self.atlas_view.origin3d
            points3 = np.dot(rotm, (points3 - origin).T).T + origin
        return points3

    def get_horizontal_3d(self, points2):
        da_z = np.ones(len(points2)) * self.atlas_view.current_horizontal_index
        points3 = np.vstack([points2[:, 1], points2[:, 0], self.atlas_view.atlas_size[0] - da_z]).T
        points3 = points3 - self.atlas_view.bregma3d
        shift_dist = self.atlas_view.current_sagital_index - self.atlas_view.bregma3d[2]
        points3 = points3 + np.array([0, 0, shift_dist])
        if self.atlas_view.horizontal_rotated:
            rotm = self.atlas_view.h_rotm_3d
            origin = self.atlas_view.origin3d
            points3 = np.dot(rotm, (points3 - origin).T).T + origin
        return points3

    def get_3d_pnts(self, processing_data):
        if self.register_method == 0:
            if self.atlas_display == 'coronal':
                data = self.get_coronal_3d(processing_data)
            elif self.atlas_display == 'sagital':
                data = self.get_sagital_3d(processing_data)
            else:
                data = self.get_horizontal_3d(processing_data)
        elif self.register_method == 1:
            print('need to be considered later')
            data = None
        else:
            data = processing_data   # ??????????
        return data

    def make_probe_piece(self):
        if self.a2h_transferred:
            data_tobe_registered = self.working_img_probe_data
        else:
            data_tobe_registered = self.working_atlas_probe
        if not data_tobe_registered:
            return
        processing_data = np.asarray(data_tobe_registered)
        data = self.get_3d_pnts(processing_data)
        self.object_ctrl.add_object_piece(object_name='probe - piece', object_data=data)
        self.working_atlas_probe = []
        # self.atlas_view.working_atlas.probe_pnts.setPointsVisible(False)
        # self.atlas_view.working_atlas.probe_pnts.clear()

    def make_virus_piece(self):
        if self.a2h_transferred:
            if self.working_img_virus_data is None:
                return
            inds = np.where(self.working_img_virus_data != 0)
            processing_pnt = np.vstack([inds[0], inds[1]]).T
        else:
            if not self.working_atlas_virus:
                return
            processing_pnt = self.working_atlas_virus.copy()

        data = self.get_3d_pnts(processing_pnt)
        self.object_ctrl.add_object_piece(object_name='virus - piece', object_data=data)
        self.working_atlas_virus = []
        # self.atlas_view.working_atlas.probe_pnts.setPointsVisible(False)
        # self.atlas_view.working_atlas.probe_pnts.clear()

    def make_contour_piece(self):
        if self.a2h_transferred:
            if self.working_img_contour_data is None:
                return
            inds = np.where(self.working_img_contour_data != 0)
            processing_pnt = np.vstack([inds[0], inds[1]]).T
        else:
            if not self.working_atlas_contour:
                return
            processing_pnt = self.working_atlas_contour.copy()

        data = self.get_3d_pnts(processing_pnt)
        self.object_ctrl.add_object_piece(object_name='contour - piece', object_data=data)
        self.working_atlas_contour = []

    def make_cell_piece(self):
        if self.a2h_transferred:
            data_tobe_registered = self.working_img_cell_data
        else:
            data_tobe_registered = self.working_atlas_cell
        if not data_tobe_registered:
            return
        processing_data = np.asarray(data_tobe_registered)
        data = self.get_3d_pnts(processing_data)
        self.object_ctrl.add_object_piece(object_name='cell - piece', object_data=data)
        self.working_atlas_cell = []

    def make_drawing_piece(self):
        if self.a2h_transferred:
            data_tobe_registered = self.working_img_drawing_data
        else:
            data_tobe_registered = self.working_atlas_drawing
        if not data_tobe_registered:
            return
        processing_data = np.asarray(data_tobe_registered)
        data = self.get_3d_pnts(processing_data)
        self.object_ctrl.add_object_piece(object_name='drawing - piece', object_data=data)
        self.working_atlas_drawing = []

    def make_object_pieces(self):
        self.make_probe_piece()
        self.make_virus_piece()
        self.make_cell_piece()
        self.make_drawing_piece()
        self.make_contour_piece()

    def merge_probes(self):
        # check none type, should not run when there is none type
        data = self.object_ctrl.merge_probe_pieces()
        print(data)
        label_data = np.transpose(self.atlas_view.atlas_label, (1, 2, 0))[:, :, ::-1]

        for i in range(len(data)):
            self.object_ctrl.add_merged_object('merged probe', object_data=[])
            info_dict = calculate_probe_info(data[i], label_data, self.atlas_view.label_info, self.atlas_view.vxsize_um,
                                             self.tip_length, self.channel_size, self.atlas_view.bregma3d)

            info_dict['probe_color'] = self.object_ctrl.obj_list[-1].color.name()
            self.registered_prob_list.append(info_dict)
            self.object_ctrl.obj_list[-1].sig_clicked.connect(self.probe_info_on_click)
            self.object_ctrl.obj_list[-1].sig_object_color_changed.connect(self.obj_color_changed)

            self.add_3d_probe_lines(info_dict)

    #
    def add_3d_probe_lines(self, data_dict):
        sp = data_dict['new_sp']
        ep = data_dict['new_ep']
        print(sp, ep)
        pos = np.stack([sp, ep], axis=0)
        print(pos)
        probe_line = gl.GLLinePlotItem(pos=pos, color=data_dict['probe_color'], width=3, mode='line_strip')
        probe_line.setGLOptions('opaque')
        self.probe_lines_3d_list.append(probe_line)
        self.view3d.addItem(self.probe_lines_3d_list[-1])

    #
    def probe_info_on_click(self, ev):
        print(ev)
        index = ev[0]
        num = ev[-1]
        print(('obj clicked', index))
        self.object_ctrl.set_active_layer_to_current(index)

        da_data = self.registered_prob_list[num]
        self.probe_window = ProbeInfoWindow(num + 1, da_data)
        self.probe_window.exec()

    def obj_color_changed(self, ev):
        id = ev[0]
        color = ev[1]
        object_name = ev[2]
        group_id = ev[3]
        self.probe_lines_3d_list[group_id].setData(color=color)
        # self.probe_lines_2d[group_id].setPen(color)
        self.registered_prob_list[group_id]['probe_color'] = color.name()

    def obj_line_width_changed(self):
        val = self.object_ctrl.line_width_slider.value()
        for i in range(len(self.probe_lines_3d)):
            self.probe_lines_3d[i].setData(width=val)

    # ------------------------------------------------------------------
    #
    #                       Atlas Loader
    #
    # ------------------------------------------------------------------
    def load_atlas(self, atlas_name):
        atlas_folder = str(QFileDialog.getExistingDirectory(self, "Select Atlas Folder"))

        if atlas_folder != '':
            self.statusbar.showMessage('Loading Atlas...')
            self.atlas_folder = atlas_folder
            with pg.BusyCursor():
                da_atlas = AtlasLoader(atlas_folder, atlas_name=atlas_name,
                                       data_file='WHS_SD_rat_T2star_v1.01.nii.gz',
                                       segmentation_file='WHS_SD_rat_atlas_v4.nii.gz',
                                       mask_file='WHS_SD_rat_brainmask_v1.01.nii.gz',
                                       bregma_coordinates=(246, 653, 440),
                                       lambda_coordinates=(244, 442, 464))
                if da_atlas.atlas_data is None or da_atlas.segmentation_data is None:
                    self.statusbar.showMessage('Something went wrong with atlas, please check your atlas data.')
                    return

                atlas_data = np.transpose(da_atlas.atlas_data, [2, 0, 1])[::-1, :, :]
                segmentation_data = np.transpose(da_atlas.segmentation_data, [2, 0, 1])[::-1, :, :]

                s_boundary = np.transpose(da_atlas.boundary['s_contour'], [2, 0, 1])[::-1, :, :]
                c_boundary = np.transpose(da_atlas.boundary['c_contour'], [2, 0, 1])[::-1, :, :]
                h_boundary = np.transpose(da_atlas.boundary['h_contour'], [2, 0, 1])[::-1, :, :]

                boundary = {'s_contour': s_boundary, 'c_contour': c_boundary, 'h_contour': h_boundary}

                self.atlas_view.set_data(atlas_data, segmentation_data, da_atlas.atlas_info,
                                         da_atlas.label_info, boundary)
                self.atlas_view.working_cut_changed(self.atlas_display)
                self.reset_corners_atlas()

            self.statusbar.showMessage('Atlas Loaded.')

            pre_made_meshdata_path = os.path.join(atlas_folder, '{}_atlas_meshdata.pkl'.format(atlas_name))

            if os.path.exists(pre_made_meshdata_path):
                infile = open(pre_made_meshdata_path, 'rb')
                self.meshdata = pickle.load(infile)
                infile.close()

            else:
                self.statusbar.showMessage('Brain mesh is not found! Mesh is constructing in 3D view....')
                with pg.BusyCursor():
                    self.meshdata = render_volume(da_atlas.atlas_data, self.atlas_folder,
                                                  atlas_name, factor=2, level=0.01)

            self.atlas_view.mesh.setMeshData(meshdata=self.meshdata)
            self.mesh_origin = np.ravel(da_atlas.atlas_info[3]['Bregma'])
            self.atlas_view.mesh.translate(-self.mesh_origin[0], -self.mesh_origin[1], -self.mesh_origin[2])

            self.statusbar.showMessage('Brain mesh is Loaded.')

            # volume_data_3d = np.zeros((da_atlas.segmentation_data.shape + (4,)), dtype=np.ubyte)
            # volume_data_3d[:, :, :, 0] = da_atlas.atlas_data * 255 / np.max(da_atlas.atlas_data)
            # volume_data_3d[:, :, :, 1] = volume_data_3d[:, :, :, 0]
            # volume_data_3d[:, :, :, 2] = volume_data_3d[:, :, :, 0]
            # vis_inds = np.where(da_atlas.atlas_data != 0)
            # volume_data_3d[vis_inds[0], vis_inds[1], vis_inds[2], 3] = 128
            #
            # v = gl.GLVolumeItem(volume_data_3d, sliceDensity=1, smooth=False, glOptions='translucent')
            # v.translate(-self.mesh_origin[0], -self.mesh_origin[1], -self.mesh_origin[2])
            # self.view3d.addItem(v)

            # return

            pre_made_small_meshdata_path = os.path.join(atlas_folder, 'WHS_atlas_small_meshdata.pkl')
            if os.path.exists(pre_made_small_meshdata_path):
                infile = open(pre_made_small_meshdata_path, 'rb')
                self.small_meshdata_list = pickle.load(infile)
                infile.close()
            else:
                self.statusbar.showMessage('Brain region mesh is not found! Rendering in 3D view....')
                with pg.BusyCursor():
                    self.small_meshdata_list = render_small_volume(da_atlas.atlas_data, da_atlas.segmentation_data,
                                                                   self.atlas_folder, atlas_name, factor=2, level=0.01)

            for id in np.unique(da_atlas.segmentation_data):
                id = int(id)
                if id == 0:
                    continue
                if id in self.atlas_view.label_info['index']:
                    color_to_set = self.atlas_view.label_info['color'][(self.atlas_view.label_info['index'] == id)][0] / 255
                    mesh = gl.GLMeshItem(meshdata=self.small_meshdata_list[str(id)], smooth=True,
                                         color=(color_to_set[0], color_to_set[1], color_to_set[2], 0.8), shader='balloon')
                    mesh.setGLOptions('opaque')
                    mesh.translate(-self.mesh_origin[0], -self.mesh_origin[1], -self.mesh_origin[2])
                    # mesh.setVisible(False)
                    self.small_mesh_list[str(id)] = mesh
                    self.small_mesh_list[str(id)].setVisible(False)

            mesh_keys = list(self.small_mesh_list.keys())
            for i in range(len(self.small_mesh_list)):
                self.view3d.addItem(self.small_mesh_list[mesh_keys[i]])

            self.sidebar.setCurrentIndex(0)

            self.statusbar.showMessage('Brain region mesh is Loaded.')

        self.statusbar.showMessage('Atlas loaded successfully.')


    # ------------------------------------------------------------------
    #
    #                       Image Loader
    #
    # ------------------------------------------------------------------
    def load_image(self):

        # path = "/Users/jingyig/Work/Kavli/PyCode/herrbs/test.jpeg"
        # image = cv2.imread(path)
        # window_name = 'image'
        # cv2.imshow(window_name, image)
        # cv2.waitKey(0)
        if self.image_view.image_file is not None:
            print('need to clean everything')

        # image_file = CZIReader("/Users/jingyig/Work/Kavli/Data/HERBS_DATA/grethe/13234_BDADAB_s4_g005.czi")
        # image_file.read_data(0.1, scene_index=0)
        # self.image_view.set_data(image_file)
        # self.reset_corners_hist()
        # if self.atlas_view.atlas_data is None:
        #     self.show_only_image_window()
        # else:
        #     self.show_2_windows()
        #
        # self.image_view.img_stacks.mask_img.setLookupTable(self.tool_box.base_lut)
        # self.image_view.img_stacks.virus_img.setLookupTable(self.tool_box.base_lut)
        # self.image_view.img_stacks.contour_img.setLookupTable(self.tool_box.base_lut)


        # self.hist_lut.setImageItem(self.image_view.current_color_img)

        filter = "CZI (*.czi);;JPEG (*.jpg;*.jpeg);;PNG (*.png);;TIFF (*.tif)"
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.ExistingFiles)
        image_file_path = dlg.getOpenFileName(self, "Select Histological Image File", str(Path.home()), filter)

        self.image_file_type = image_file_path[0][-4:].lower()
        if image_file_path[0] != '':
            self.statusbar.showMessage('Image file loading ...')
            with pg.BusyCursor():
                with warnings.catch_warnings():
                    warnings.filterwarnings("error")
                    if self.image_file_type == '.czi':
                        image_file = CZIReader(image_file_path[0])
                        scale = self.image_view.scale_slider.value()
                        scale = 0.01 if scale == 0 else scale * 0.01
                        if self.image_view.check_scenes.isChecked():
                            image_file.read_data(scale, scene_index=None)
                        else:
                            image_file.read_data(scale, scene_index=0)
                    else:
                        image_file = ImageReader(image_file_path[0])
                self.image_view.set_data(image_file)
                self.reset_corners_hist()
            self.layerpanel.setEnabled(True)
            self.statusbar.showMessage('Image file loaded.')
            # change sidebar focus
            self.sidebar.setCurrentIndex(2)
            if self.atlas_view.atlas_data is None:
                self.show_only_image_window()
            else:
                self.show_2_windows()

            self.image_view.img_stacks.mask_img.setLookupTable(self.tool_box.base_lut)
            self.image_view.img_stacks.virus_img.setLookupTable(self.tool_box.base_lut)
            self.image_view.img_stacks.contour_img.setLookupTable(self.tool_box.base_lut)
        else:
            return

    # load multiple images
    def load_images(self):
        images_folder = str(QFileDialog.getExistingDirectory(self, "Select Images Folder"))
        print(images_folder)
        # histology_images_folder = '/Users/jingyig/Work/Kavli/PyCode/vitlab/racer/image/Jacopo 26504 S2 Sld1 NeuN DiI/'
        if images_folder != '':
            image_files_list = os.listdir(images_folder)
            image_files_list = natsorted(image_files_list)
            self.statusbar.showMessage('Image files loading ...')
            with pg.BusyCursor():
                with warnings.catch_warnings():
                    warnings.filterwarnings("error")
                    image_file = ImagesReader(images_folder, image_files_list)
                    self.image_view.set_data(image_file)

            self.sidebar.setCurrentIndex(3)
            self.statusbar.showMessage('Image files loaded.')
        else:
            return


def main():
    app = QApplication(argv)
    app.setStyleSheet(herbs_style)
    # if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    #     app.instance().exec_()
    window = HERBS()
    window.show()

    exit(app.exec_())
    # app.exec_()







