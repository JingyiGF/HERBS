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

from .atlas_downloader import AtlasDownloader
from .atlas_processor import AtlasProcessor
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
from .styles import Styles


herbs_style = '''
QMainWindow {
    background-color: rgb(50, 50, 50);
    color: white;
    font-size: 12px;
}

/*---------------------- QComboBox -----------------------*/
QComboBox {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    selection-background-color: transparent;
    color: white;
    background-color: #656565;
    border: None;
    border-radius: 5px;
    padding: 0px 0px 0px 5px;
    margin: 0px;
}


QComboBox:item {
    background: #656565;
    color: white;
    height: 20px;
    margin: 0px;
    padding: 3px;
}

QComboBox:item:selected
{
    border: 3px solid #656565;
    background: #232323;
    margin: 0px;
    color: white;
    padding: 3px;
}


QComboBox:editable {
    background: #656565;
    margin: 0px;
}

QComboBox:!editable, QComboBox::drop-down:editable {
     background: #656565;
}

QComboBox:!editable:on, QComboBox::drop-down:editable:on {
    background: #656565;
    margin: 0px;
    padding: 0px;
}

QComboBox:on { /* shift the text when the popup opens */
    margin: 0px;
    padding: 0px;
    color: white;
    background-color: transparent;
    selection-background-color: transparent;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-top: None;
    border-bottom: None;
    border-left-width: 1px;
    border-left-color: transparent;
    border-left-style: solid; /* just a single line */
    border-top-right-radius: 3px; /* same radius as the QComboBox */
    border-bottom-right-radius: 3px;
    margin: 0px;
}

QComboBox::down-arrow {
    image: url(icons/tdown.svg);
    width: 13px;
    height: 14px;
    padding-right: 3px;
}

QComboBox::down-arrow:on { /* shift the arrow when popup is open */
    top: 1px;
    left: 1px;
}



/*---------------------- Slider -----------------------*/
QSlider {
    min-height: 20px;
    max-height: 20px;
    background: transparent;
    border: None;
}

QSlider::groove:horizontal {
    border: None;
    height: 2px; /* the groove expands to the size of the slider by default. by giving it a height, it has a fixed size */
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B1B1B1, stop:1 #c4c4c4);
    margin: 2px 0px;
}

QSlider::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #8f8f8f);
    border: 1px solid #5c5c5c;
    width: 10px;
    height: 30px;
    margin: -4px -2px; /* handle is placed by default on the contents rect of the groove. Expand outside the groove */
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
    border: 1px solid #242424;
    background: transparent;
}

QSpinBox::up-button {
    background: transparent;
    subcontrol-origin: border;
    subcontrol-position: top right; /* position at the top right corner */
    width: 15px; 
    border-width: 0px;
}

QSpinBox::down-button {
    background: transparent;
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
    border: 1px solid #242424;
    background: transparent;
    
}

QDoubleSpinBox::up-button {
    background: transparent;
    subcontrol-origin: border;
    subcontrol-position: top right; /* position at the top right corner */
    width: 15px; 
    border: None;
}

QDoubleSpinBox::down-button {
    background: transparent;
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



/*---------------------- QSplitter -----------------------*/
QSplitter::handle {
    image: url(icons/dot.svg);
}

QSplitter::handle:horizontal {
    width: 5px;
}

QSplitter::handle:vertical {
    height: 5px;
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

QRadioButton {
    color: white;
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

        self.styles = Styles()

        self.np_onside = None
        self.atlas_rect = None
        self.histo_rect = None
        self.small_atlas_rect = None
        self.small_histo_rect = None

        self.atlas_folder = None
        self.current_img_path = None

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
        self.working_img_probe_data = []
        self.working_img_virus_data = None
        self.working_img_contour_data = None

        self.working_atlas_probe = []
        self.working_atlas_virus = []
        self.working_atlas_drawing = []
        self.working_atlas_contour = []

        self.working_img_cell_data = []
        self.working_atlas_cell = []
        self.cell_count = [0 for i in range(5)]
        self.cell_size = []
        self.cell_symbol = []
        self.cell_layer_index = []

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
        self.registered_cell_count = 1
        self.registered_cell_list = []
        self.registered_virus_count = 1
        self.registered_virus_list = []
        self.registered_contour_count = 1
        self.registered_contour_list = []
        self.registered_drawing_count = 1
        self.registered_drawing_list = []

        self.probe_lines_2d_list = []

        self.probe_lines_3d_list = []
        self.virus_points_3d_list = []
        self.cell_points_3d_list = []
        self.contour_points_3d_list = []
        self.drawing_lines_3d_list = []

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
        self.drawing_img = None
        self.cell_img = None

        self.processing_img = None
        self.overlay_img = None

        self.triangle_color = QColor(128, 128, 128, 255)



        # ---------------------
        self.tool_box = ToolBox()
        self.toolbar_wrap_action_dict = {}
        self.cell_base_symbol = ['+', '+', 'x', 't', 's']

        # ---------------------------- load controls, views, panels
        self.layer_ctrl = LayersControl()
        self.layer_ctrl.sig_opacity_changed.connect(self.layers_opacity_changed)
        self.layer_ctrl.sig_visible_changed.connect(self.layers_visible_changed)

        self.object_ctrl = ObjectControl()
        self.object_ctrl.sig_delete_object.connect(self.object_deleted)
        self.object_ctrl.add_object_btn.clicked.connect(self.make_object_pieces)
        self.object_ctrl.merge_probe_btn.clicked.connect(self.merge_probes)
        self.object_ctrl.merge_virus_btn.clicked.connect(self.merge_virus)
        self.object_ctrl.merge_cell_btn.clicked.connect(self.merge_cells)
        self.object_ctrl.merge_contour_btn.clicked.connect(self.merge_contour)
        self.object_ctrl.merge_drawing_btn.clicked.connect(self.merge_drawings)
        self.object_ctrl.line_width_slider.valueChanged.connect(self.obj_line_width_changed)


        self.image_view = ImageView()
        self.image_view.sig_image_changed.connect(self.update_histo_tri_onside_data)
        self.image_view.img_stacks.sig_mouse_clicked.connect(self.img_stacks_clicked)
        self.image_view.img_stacks.sig_mouse_hovered.connect(self.img_stacks_hovered)
        self.image_view.img_stacks.sig_key_pressed.connect(self.img_stacks_key_pressed)
        self.image_view.img_stacks.tri_pnts.mouseDragged.connect(self.hist_window_tri_pnts_moving)
        self.image_view.img_stacks.tri_pnts.mouseClicked.connect(self.hist_window_tri_pnts_clicked)
        self.image_view.img_stacks.lasso_path.sigPointsClicked.connect(self.lasso_points_clicked)
        self.image_view.img_stacks.cell_pnts.sigClicked.connect(self.img_cell_pnts_clicked)
        self.image_view.img_stacks.probe_pnts.sigClicked.connect(self.img_probe_pnts_clicked)
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
        self.atlas_view.simg.sig_mouse_clicked.connect(self.atlas_stacks_clicked)
        self.atlas_view.himg.sig_mouse_clicked.connect(self.atlas_stacks_clicked)
        # triangle points moving and clicked
        self.atlas_view.cimg.tri_pnts.mouseDragged.connect(self.atlas_window_tri_pnts_moving)
        self.atlas_view.cimg.tri_pnts.mouseClicked.connect(self.atlas_window_tri_pnts_clicked)
        self.atlas_view.himg.tri_pnts.mouseDragged.connect(self.atlas_window_tri_pnts_moving)
        self.atlas_view.himg.tri_pnts.mouseClicked.connect(self.atlas_window_tri_pnts_clicked)
        self.atlas_view.simg.tri_pnts.mouseDragged.connect(self.atlas_window_tri_pnts_moving)
        self.atlas_view.simg.tri_pnts.mouseClicked.connect(self.atlas_window_tri_pnts_clicked)
        # probe clicked
        self.atlas_view.cimg.probe_pnts.sigClicked.connect(self.atlas_probe_pnts_clicked)
        self.atlas_view.simg.probe_pnts.sigClicked.connect(self.atlas_probe_pnts_clicked)
        self.atlas_view.himg.probe_pnts.sigClicked.connect(self.atlas_probe_pnts_clicked)
        # contour clicked
        self.atlas_view.cimg.contour_pnts.sigClicked.connect(self.atlas_contour_pnts_clicked)
        self.atlas_view.simg.contour_pnts.sigClicked.connect(self.atlas_contour_pnts_clicked)
        self.atlas_view.himg.contour_pnts.sigClicked.connect(self.atlas_contour_pnts_clicked)


        # --------------------------------------------------------
        #                 connect all menu actions
        # --------------------------------------------------------
        # file menu related
        self.actionSingle_Image.triggered.connect(self.load_image)
        self.actionProcessed_Image.triggered.connect(lambda: self.save_image('Processed'))
        self.actionOverlay_Image.triggered.connect(lambda: self.save_image('Overlay'))

        self.actionCurrent.triggered.connect(self.save_current_object)
        # atlas menu related
        self.actionDownload.triggered.connect(self.download_waxholm_rat_atlas)
        self.actionAtlas_Processor.triggered.connect(self.process_raw_atlas_data)

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
        self.actionProcess_Image.triggered.connect(self.turn_current_to_process)
        self.actionReset_Image.triggered.connect(self.reset_current_image)

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

        self.statusbar.showMessage('Ready')

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
        if self.tool_box.checkable_btn_dict['triang_btn'].isChecked():
            self.atlas_view.working_atlas.tri_pnts.setVisible(True)
        else:
            self.atlas_view.working_atlas.tri_pnts.setVisible(False)
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
        if self.tool_box.checkable_btn_dict['triang_btn'].isChecked():
            self.image_view.img_stacks.tri_pnts.setVisible(True)
        else:
            self.image_view.img_stacks.tri_pnts.setVisible(False)
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
    def turn_current_to_process(self):
        if self.image_view.image_file is None or not self.image_view.image_file.is_rgb:
            return
        self.processing_img = self.image_view.current_img.copy()
        # self.image_view.img_stacks.image_list[0].setImage(self.processing_img)
        res = cv2.resize(self.processing_img[:, :, :3], self.image_view.tb_size, interpolation=cv2.INTER_AREA)
        self.master_layers(res, layer_type='Image')

    def reset_current_image(self):
        if self.image_view.image_file is None or not self.image_view.image_file.is_rgb:
            return
        self.image_view.img_stacks.image_list[0].setImage(self.image_view.current_img)
        self.processing_img = None
        print('delete img-copy layer')

    # ------------------------------------------------------------------
    #
    #                  Menu Bar ---- Atlas ----- related
    #
    # ------------------------------------------------------------------
    def download_waxholm_rat_atlas(self):
        download_waxholm_rat_window = AtlasDownloader()
        download_waxholm_rat_window.exec()

    def process_raw_atlas_data(self):
        process_atlas_window = AtlasProcessor()
        process_atlas_window.exec()

    # ------------------------------------------------------------------
    #
    #                      ToolBar layout and connections
    #
    # -----------------------------------------------------------------
    def init_tool_bar(self):
        self.toolbar.setStyleSheet(toolbar_style)
        # -------------- ToolBar layout and functions -------------- #
        self.tool_box.add_atlas.triggered.connect(self.load_atlas)
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
        self.tool_box.triang_color_btn.sigColorChanged.connect(self.change_triangle_color)
        self.tool_box.bound_pnts_num.textEdited.connect(self.number_of_side_points_changed)
        self.tool_box.triang_vis_btn.clicked.connect(self.vis_tri_lines_btn_clicked)
        self.tool_box.triang_match_bnd.clicked.connect(self.matching_tri_bnd)
        # cell related
        self.tool_box.cell_color_btn.sigColorChanged.connect(self.change_cell_color)
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
        self.tool_box.probe_color_btn.sigColorChanged.connect(self.probe_color_changed)
        self.tool_box.probe_type1.toggled.connect(lambda: self.probe_type_changed(0))
        self.tool_box.probe_type2.toggled.connect(lambda: self.probe_type_changed(1))
        self.tool_box.probe_type3.toggled.connect(lambda: self.probe_type_changed(2))
        # eraser_related
        self.tool_box.eraser_color_btn.sigColorChanged.connect(self.probe_color_changed)

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
        self.inactive_lasso()
        self.set_toolbox_btns_unchecked('moving')
        self.vis_eraser_symbol(False)

    def lasso_btn_clicked(self):
        self.set_toolbox_btns_unchecked('lasso')
        self.vis_eraser_symbol(False)

    def magic_wand_btn_clicked(self):
        self.inactive_lasso()
        self.set_toolbox_btns_unchecked('magic_wand')
        self.vis_eraser_symbol(False)

    def pencil_btn_clicked(self):
        self.inactive_lasso()
        self.set_toolbox_btns_unchecked('pencil')
        self.vis_eraser_symbol(False)

    def eraser_btn_clicked(self):
        self.inactive_lasso()
        self.set_toolbox_btns_unchecked('eraser')
        if self.tool_box.checkable_btn_dict['eraser_btn'].isChecked():
            self.vis_eraser_symbol(True)
        else:
            self.vis_eraser_symbol(False)

    def rotation_btn_clicked(self):
        self.inactive_lasso()
        self.set_toolbox_btns_unchecked('rotation')
        self.vis_eraser_symbol(False)

    def triang_btn_clicked(self):
        self.inactive_lasso()
        self.set_toolbox_btns_unchecked('triang')
        self.show_triangle_points('triang')
        self.vis_eraser_symbol(False)

    def probe_btn_clicked(self):
        self.inactive_lasso()
        self.set_toolbox_btns_unchecked('probe')
        self.vis_eraser_symbol(False)

    def loc_btn_clicked(self):
        self.inactive_lasso()
        self.set_toolbox_btns_unchecked('loc')
        self.vis_eraser_symbol(False)

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

    def vis_eraser_symbol(self, vis):
        self.image_view.img_stacks.circle_follow.setVisible(vis)

    # ------------------------------------------------------------------
    #
    #                      SideBar layout and connections
    #
    # ------------------------------------------------------------------
    def init_side_bar(self):
        self.sidebar.setStyleSheet(self.styles.tab_style)
        self.sidebar.setIconSize(QSize(24, 24))
        self.sidebar.setTabIcon(0, QIcon('icons/sidebar/atlascontrol.svg'))
        self.sidebar.setTabIcon(1, QIcon('icons/sidebar/treeview.svg'))
        self.sidebar.setTabIcon(2, QIcon('icons/sidebar/tool.svg'))
        self.sidebar.setTabIcon(3, QIcon('icons/sidebar/layers.svg'))
        self.sidebar.setTabIcon(4, QIcon('icons/sidebar/object.svg'))

        # ---------------------------- atlas control panel
        atlas_panel_layout = QVBoxLayout(self.atlascontrolpanel)
        atlas_panel_layout.setContentsMargins(0, 0, 0, 0)
        atlas_panel_layout.setAlignment(Qt.AlignTop)
        atlas_control_label = QLabel('Atlasing Controller')
        atlas_control_label.setStyleSheet(self.styles.sidebar_title_label_style)

        atlas_panel_layout.addWidget(atlas_control_label)
        atlas_panel_layout.addWidget(self.atlas_view.sidebar_wrap)

        # ---------------------------- Label Panel
        label_panel_layout = QVBoxLayout(self.treeviewpanel)
        label_panel_layout.setContentsMargins(0, 0, 0, 0)
        label_panel_layout.setAlignment(Qt.AlignTop)
        label_control_label = QLabel('Segmentation View Controller')
        label_control_label.setStyleSheet(self.styles.sidebar_title_label_style)

        label_tree_container = QFrame()
        label_container_layout = QVBoxLayout(label_tree_container)
        # label_container_layout.setContentsMargins(0, 0, 0, 0)
        label_container_layout.setSpacing(0)
        label_container_layout.setAlignment(Qt.AlignTop)
        show_3d_button = QPushButton()
        show_3d_button.setStyleSheet('margin: 0px;')
        show_3d_button.setCheckable(True)
        show_3d_button.setText('Show in 3D view')
        show_3d_button.clicked.connect(self.show_small_area_in_3d)

        composition_label = QLabel('Composition: ')
        self.composition_combo = QComboBox()
        self.composition_combo.setFixedHeight(22)
        self.composition_combo.addItems(['opaque', 'translucent', 'additive'])
        self.composition_combo.currentIndexChanged.connect(self.composition_3d_changed)

        label_container_layout.addWidget(show_3d_button)
        label_container_layout.addSpacing(10)
        label_container_layout.addWidget(self.composition_combo)
        label_container_layout.addSpacing(10)
        label_container_layout.addWidget(self.atlas_view.label_tree)

        label_panel_layout.addWidget(label_control_label)
        label_panel_layout.addWidget(label_tree_container)

        # ---------------------------- image panel
        image_panel_layout = QVBoxLayout(self.imagecontrolpanel)
        image_panel_layout.setContentsMargins(0, 0, 0, 0)
        image_panel_layout.setSpacing(0)
        image_panel_layout.setAlignment(Qt.AlignTop)
        image_control_label = QLabel('Image View Controller')
        image_control_label.setStyleSheet(self.styles.sidebar_title_label_style)

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

        # ---------------------------- layer panel
        layer_panel_layout = QVBoxLayout(self.layerpanel)
        layer_panel_layout.setContentsMargins(0, 0, 0, 0)
        layer_panel_layout.setSpacing(0)
        layer_panel_layout.setAlignment(Qt.AlignTop)
        layer_control_label = QLabel('Layer View Controller')
        layer_control_label.setStyleSheet(self.styles.sidebar_title_label_style)

        layer_btm_ctrl = QFrame()
        layer_btm_ctrl.setStyleSheet('background-color:rgb(65, 65, 65);')
        layer_btm_ctrl.setFixedHeight(24)
        layer_btm_layout = QHBoxLayout(layer_btm_ctrl)
        layer_btm_layout.setContentsMargins(0, 0, 0, 0)
        layer_btm_layout.setSpacing(5)
        layer_btm_layout.setAlignment(Qt.AlignRight)
        layer_btm_layout.addWidget(self.layer_ctrl.add_layer_btn)
        layer_btm_layout.addWidget(self.layer_ctrl.delete_layer_btn)

        layer_panel_layout.addWidget(layer_control_label)
        layer_panel_layout.addWidget(self.layer_ctrl)
        layer_panel_layout.addWidget(layer_btm_ctrl)
        # self.layerpanel.setEnabled(False)

        # ---------------------------- object panel
        object_panel_layout = QVBoxLayout(self.probecontrolpanel)
        object_panel_layout.setContentsMargins(0, 0, 0, 0)
        object_panel_layout.setSpacing(0)
        object_panel_layout.setAlignment(Qt.AlignTop)
        object_control_label = QLabel('Object View Controller')
        object_control_label.setStyleSheet(self.styles.sidebar_title_label_style)

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

    def probe_color_changed(self, ev):
        probe_color = ev.color()
        self.image_view.img_stacks.probe_pnts.setPen(pg.mkPen(color=probe_color))
        self.atlas_view.working_atlas.probe_pnts.setPen(pg.mkPen(color=probe_color))

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
        n_working_layer = len(self.layer_ctrl.current_layer_id)
        for i in range(n_working_layer):
            da_ind = self.layer_ctrl.current_layer_id[i]
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
        if not self.layer_ctrl.current_layer_id:
            return
        self.moving_layers(-self.tool_box.moving_px, 0)

    def moving_right_btn_clicked(self):
        if not self.layer_ctrl.current_layer_id:
            return
        self.moving_layers(self.tool_box.moving_px, 0)

    def moving_up_btn_clicked(self):
        if not self.layer_ctrl.current_layer_id:
            return
        self.moving_layers(0, -self.tool_box.moving_px)

    def moving_down_btn_clicked(self):
        if not self.layer_ctrl.current_layer_id:
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
    #               ToolBar eraser btn related
    #
    # ------------------------------------------------------------------
    def change_eraser_color(self, ev):
        eraser_color = ev.color()
        self.image_view.img_stacks.circle_follow.setPen(pg.mkPen(color=eraser_color))
        self.atlas_view.working_atlas.circle_follow.setPen(pg.mkPen(color=eraser_color))

    # ------------------------------------------------------------------
    #
    #               ToolBar loc btn related
    #
    # ------------------------------------------------------------------
    def change_cell_color(self, ev):
        cell_color = ev.color()
        self.image_view.img_stacks.cell_pnts.setPen(color=cell_color)
        self.image_view.img_stacks.cell_pnts.setBrush(color=cell_color)

    def cell_select_btn_clicked(self):
        if self.tool_box.cell_aim_btn.isChecked():
            self.tool_box.cell_aim_btn.setChecked(False)

    def cell_aim_btn_clicked(self):
        if self.tool_box.cell_selector_btn.isChecked():
            self.tool_box.cell_selector_btn.setChecked(False)

    def cell_detect_btn_clicked(self):
        if self.working_blob_data is None:
            return
        if self.image_view.current_mode == 'hsv':
            return

        locs = np.asarray(self.working_blob_data).astype(int)
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
        params.filterByArea = True
        params.minArea = da_area - 1
        params.maxArea = da_area + 1
        params.filterByCircularity = True
        params.minCircularity = da_circularity
        params.filterByConvexity = True
        params.minConvexity = 0.87
        params.filterByInertia = True
        params.minInertiaRatio = 0.01

        temp = self.image_view.current_img.copy()
        if self.image_view.image_file.is_rgb:
            if self.image_view.current_mode == 'rgb':
                temp = cv2.cvtColor(temp, cv2.COLOR_RGB2GRAY)
                layer_ind = 0
        else:
            da_layer = [ind for ind in range(4) if self.image_view.channel_visible[ind]]
            n_layers = len(da_layer)
            if n_layers == 0:
                return
            if n_layers > 1:
                return
            temp = temp[:, :, da_layer[0]]
            layer_ind = da_layer[0] + 1

        da_colors = temp[locs[:, 1], locs[:, 0]]
        params.minThreshold = np.min(da_colors)
        params.maxThreshold = np.max(da_colors)

        if int(opencv_ver[0]) < 3:
            detector = cv2.SimpleBlobDetector(params)
        else:
            detector = cv2.SimpleBlobDetector_create(params)

        keypoints = detector.detect(temp)
        n_keypoints = len(keypoints)
        if n_keypoints == 0:
            return

        for i in range(n_keypoints):
            x = keypoints[i].pt[0]
            y = keypoints[i].pt[1]
            size = keypoints[i].size
            self.working_img_cell_data.append([x, y])
            self.cell_layer_index.append(layer_ind)
            self.cell_symbol.append(self.cell_base_symbol[layer_ind])
            self.cell_size.append(size)
        self.cell_count[layer_ind] = self.cell_count[layer_ind] + n_keypoints
        self.tool_box.cell_count_val_list[layer_ind].setText(str(self.cell_count[layer_ind]))

        self.image_view.img_stacks.cell_pnts.setData(pos=np.asarray(self.working_img_cell_data), symbol=self.cell_symbol)

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

        layer_ind = np.where(np.ravel(self.layer_ctrl.layer_link) == 'img-mask')[0][0]
        self.layer_ctrl.delete_layer(layer_ind)

    def get_contour_img(self):
        if self.working_img_mask_data is None:
            return
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
        layer_ind = np.where(np.ravel(self.layer_ctrl.layer_link) == 'img-mask')[0][0]
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

    # change color for triangle points and text
    def change_triangle_color(self, ev):
        self.triangle_color = ev.color()
        # triang_color = np.ravel(triang_color.getRgb())
        self.image_view.img_stacks.tri_pnts.scatter.setPen(color=self.triangle_color)
        self.image_view.img_stacks.tri_pnts.scatter.setBrush(color=self.triangle_color)
        if self.working_img_text:
            for i in range(len(self.working_img_text)):
                self.working_img_text[i].setColor(self.triangle_color)
        self.atlas_view.cimg.tri_pnts.scatter.setPen(color=self.triangle_color)
        self.atlas_view.simg.tri_pnts.scatter.setPen(color=self.triangle_color)
        self.atlas_view.himg.tri_pnts.scatter.setPen(color=self.triangle_color)
        self.atlas_view.cimg.tri_pnts.scatter.setBrush(color=self.triangle_color)
        self.atlas_view.simg.tri_pnts.scatter.setBrush(color=self.triangle_color)
        self.atlas_view.himg.tri_pnts.scatter.setBrush(color=self.triangle_color)
        if self.working_atlas_text:
            for i in range(len(self.working_atlas_text)):
                self.working_atlas_text[i].setColor(self.triangle_color)

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

            self.overlay_img = img_wrap
            self.image_view.img_stacks.overlay_img.setImage(img_wrap)
            res = cv2.resize(img_wrap, self.image_view.tb_size, interpolation=cv2.INTER_AREA)
            self.master_layers(res, layer_type='image-overlay')
            self.a2h_transferred = True
            self.tool_box.toh_btn.setIcon(self.tool_box.toh_btn_on_icon)
            self.tool_box.toa_btn.setEnabled(False)
        else:
            self.overlay_img = None
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
        if self.image_view.image_file is None or self.atlas_view.atlas_data is None:
            return
        if self.atlas_view.atlas_label is None:
            return
        print('to A clicked')
        if not self.h2a_transferred:
            if self.image_view.image_file.is_rgb:
                if self.processing_img is not None:
                    self.input_img = self.processing_img.copy()
                else:
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

            self.overlay_img = img_wrap
            self.atlas_view.working_atlas.overlay_img.setImage(img_wrap)
            res = cv2.resize(img_wrap, self.atlas_view.slice_tb_size, interpolation=cv2.INTER_AREA)
            self.master_layers(res, layer_type='atlas-overlay')
            self.h2a_transferred = True
            self.tool_box.toa_btn.setIcon(self.tool_box.toa_btn_on_icon)
            self.project_method = 'match to atlas'
            self.register_method = 0
            self.tool_box.toh_btn.setEnabled(False)
        else:
            self.overlay_img = None
            self.atlas_view.working_atlas.overlay_img.clear()
            layer_ind = np.where(np.ravel(self.layer_ctrl.layer_link) == 'atlas-overlay')[0][0]
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
            self.working_atlas_virus = res_pnts.tolist()
            self.atlas_view.working_atlas.virus_pnts.setData(pos=np.asarray(self.working_atlas_virus))

        if self.working_img_contour_data is not None:
            input_contour_img = self.working_img_contour_data.copy()
            res_pnts = self.transfer_vox_to_pnt(input_contour_img, tri_vet_inds)
            self.working_atlas_contour = res_pnts.tolist()
            self.atlas_view.working_atlas.contour_pnts.setData(pos=np.asarray(self.working_atlas_contour))

        if self.working_img_probe_data:
            res_pnts = self.transfer_pnt(np.asarray(self.working_img_probe_data), tri_vet_inds)
            self.working_atlas_probe = res_pnts.tolist()
            self.atlas_view.working_atlas.probe_pnts.setData(pos=np.asarray(self.working_atlas_probe))
            if not self.atlas_view.working_atlas.probe_pnts.isVisible():
                self.atlas_view.working_atlas.probe_pnts.setVisible(True)

        if self.working_img_drawing_data:
            res_pnts = self.transfer_pnt(np.asarray(self.working_img_drawing_data), tri_vet_inds)
            self.working_atlas_drawing = res_pnts.tolist()
            self.atlas_view.working_atlas.drawing_pnts.setData(pos=np.asarray(self.working_atlas_drawing))

        if self.working_img_cell_data:
            res_pnts = self.transfer_pnt(np.asarray(self.working_img_cell_data), tri_vet_inds)
            self.working_atlas_cell = res_pnts.tolist()
            self.atlas_view.working_atlas.cell_pnts.setData(pos=np.asarray(self.working_atlas_cell),
                                                            symbol=self.cell_symbol)

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
        if self.processing_img is not None:
            self.processing_img = None
            print('delete img-copy layer')
        self.drawing_img = np.zeros(self.image_view.img_size).astype('uint8')
        self.cell_img = np.zeros(self.image_view.img_size).astype('uint8')

    def img_stacks_clicked(self, pos):
        x = pos[0]
        y = pos[1]
        print('image', (x, y))
        if self.image_view.image_file is None:
            return
        # ------------------------- pencil
        if self.tool_box.checkable_btn_dict['pencil_btn'].isChecked():

            if len(self.working_img_drawing_data) > 1:
                start_pnt = np.ravel(self.working_img_drawing_data[-1]).astype(int)
                end_pnt = np.ravel([x, y]).astype(int)
                cv2.line(self.drawing_img, start_pnt, end_pnt, 255, 2)
            self.working_img_drawing_data.append([x, y])
            self.image_view.img_stacks.drawing_pnts.setData(np.asarray(self.working_img_drawing_data))
            if self.is_pencil_allowed:
                self.is_pencil_allowed = False
            else:
                self.is_pencil_allowed = True
            res = cv2.resize(self.drawing_img, self.image_view.tb_size, interpolation=cv2.INTER_AREA)
            self.master_layers(res, layer_type='img-drawing')
        # ------------------------- eraser
        elif self.tool_box.checkable_btn_dict['eraser_btn'].isChecked():
            r = self.tool_box.eraser_size_slider.value()
            mask_img = np.zeros(self.image_view.img_size, dtype=np.uint8)
            cv2.circle(mask_img, center=(int(x), int(y)), radius=r, color=255, thickness=-1)
            mask_img = 255 - mask_img
            if not self.layer_ctrl.layer_id or len(self.layer_ctrl.current_layer_id) > 1:
                print('check')
                return
            else:
                da_ind = np.where(np.ravel(self.layer_ctrl.layer_id) == self.layer_ctrl.current_layer_id[0])[0]
                da_link = self.layer_ctrl.layer_link[da_ind[0]]
                if da_link == 'img-mask':
                    temp = self.working_img_mask_data.astype(np.uint8)
                    dst = cv2.bitwise_and(temp, temp, mask=mask_img)
                    res = cv2.resize(dst, self.image_view.tb_size, interpolation=cv2.INTER_AREA)
                    self.image_view.img_stacks.mask_img.setImage(dst)
                    self.working_img_mask_data = dst
                elif da_link == 'img-contour':
                    temp = self.working_img_contour_data.astype(np.uint8)
                    dst = cv2.bitwise_and(temp, temp, mask=mask_img)
                    res = cv2.resize(dst, self.image_view.tb_size, interpolation=cv2.INTER_AREA)
                    self.image_view.img_stacks.contour_img.setImage(dst)
                    self.working_img_contour_data = dst
                elif da_link == 'img-virus':
                    temp = self.working_img_virus_data.astype(np.uint8)
                    dst = cv2.bitwise_and(temp, temp, mask=mask_img)
                    res = cv2.resize(dst, self.image_view.tb_size, interpolation=cv2.INTER_AREA)
                    self.image_view.img_stacks.virus_img.setImage(dst)
                    self.working_img_virus_data = dst
                elif da_link == 'Image':
                    temp = self.processing_img.copy()
                    dst = cv2.bitwise_and(temp, temp, mask=mask_img)
                    res = cv2.resize(dst, self.image_view.tb_size, interpolation=cv2.INTER_AREA)
                    self.image_view.img_stacks.image_list[0].setImage(dst)
                    self.processing_img = dst
                else:
                    return
                self.layer_ctrl.layer_list[da_ind[0]].set_thumbnail_data(res)
        # ------------------------- magic wand -- virus
        elif self.tool_box.checkable_btn_dict['magic_wand_btn'].isChecked():
            tol_val = float(self.tool_box.magic_tol_val.text())
            white_img = np.ones(self.image_view.img_size).astype('uint8')
            if self.image_view.image_file.is_rgb:
                if self.processing_img is None:
                    src_img = self.image_view.current_img.copy()
                else:
                    src_img = self.processing_img.copy()
                da_color = src_img[int(y), int(x)]
                lower_val, upper_val = get_bound_color(da_color, tol_val, self.image_view.image_file.level,
                                                       self.image_view.current_mode)
                if self.image_view.current_mode != 'gray':
                    mask_img = cv2.inRange(src_img[:, :, :3], tuple(lower_val), tuple(upper_val))
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
                    print(selected_color)
                    lower_val, upper_val = get_bound_color(selected_color, tol_val, self.image_view.image_file.level,
                                                           'gray')
                    ret, thresh = cv2.threshold(temp, lower_val, upper_val, cv2.THRESH_BINARY)
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
            self.working_img_text[-1].setColor(self.triangle_color)
            self.image_view.img_stacks.vb.addItem(self.working_img_text[-1])
            self.working_img_text[-1].setPos(x, y)
            if self.tool_box.triang_vis_btn.isChecked():
                self.update_histo_tri_lines()
        # ------------------------- loc -- cell
        elif self.tool_box.checkable_btn_dict['loc_btn'].isChecked():
            if self.tool_box.cell_selector_btn.isChecked():
                if self.image_view.image_file.is_rgb:
                    layer_ind = 0
                else:
                    # only one layer is allowed to work on
                    da_layer = [ind for ind in range(4) if self.image_view.channel_visible[ind]]
                    n_layers = len(da_layer)
                    if n_layers == 0:
                        return
                    if n_layers > 1:
                        return
                    layer_ind = da_layer[0] + 1

                self.working_img_cell_data.append([x, y])
                self.cell_size.append(1)
                self.cell_symbol.append(self.cell_base_symbol[layer_ind])
                self.cell_layer_index.append(layer_ind)
                self.cell_count[layer_ind] += 1
                self.tool_box.cell_count_val_list[layer_ind].setText(str(self.cell_count[layer_ind]))

                self.image_view.img_stacks.cell_pnts.setData(pos=np.asarray(self.working_img_cell_data),
                                                             symbol=self.cell_symbol)

                self.cell_img[int(y), int(x)] = 255
                res = cv2.resize(self.cell_img, self.image_view.tb_size, interpolation=cv2.INTER_AREA)
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
            res = cv2.resize(mask, self.image_view.tb_size, interpolation=cv2.INTER_AREA)
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
            r = self.tool_box.eraser_size_slider.value()
            shp = self.image_view.current_img.shape
            if x - r > 0 and x + r < shp[1] and y - r > 0 and y + r < shp[0]:
                if not self.image_view.img_stacks.circle_follow.isVisible():
                    self.vis_eraser_symbol(True)
                data = self.tool_box.circle.copy()
                data[:, 0] = data[:, 0] + x
                data[:, 1] = data[:, 1] + y
                self.image_view.img_stacks.circle_follow.setData(data)
            else:
                if self.image_view.img_stacks.circle_follow.isVisible():
                    self.vis_eraser_symbol(False)
        if self.tool_box.checkable_btn_dict['pencil_btn'].isChecked():
            if self.is_pencil_allowed:
                start_pnt = np.ravel(self.working_img_drawing_data[-1]).astype(int)
                end_pnt = np.ravel([x, y]).astype(int)
                cv2.line(self.drawing_img, start_pnt, end_pnt, 255, 2)
                if abs(self.working_img_drawing_data[-1][0] - x) > 1 or abs(self.working_img_drawing_data[-1][1] - y) > 1:
                    self.working_img_drawing_data.append([x, y])
                    self.image_view.img_stacks.drawing_pnts.setData(np.asarray(self.working_img_drawing_data))

        self.statusbar.showMessage('Histological image coordinates: {}, {}'.format(round(x, 3), round(y, 3)))

    def img_stacks_key_pressed(self, action):
        print(action)
        if not self.layer_ctrl.current_layer_id or len(self.layer_ctrl.current_layer_id) > 1:
            return
        da_ind = np.where(np.ravel(self.layer_ctrl.layer_id) == self.layer_ctrl.current_layer_id[0])[0]
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
                elif da_link == 'Image':
                    dst = cv2.bitwise_and(self.processing_img, self.processing_img, mask=mask)
                    self.image_view.img_stacks.image_list[0].setImage(dst)
                    self.processing_img = dst
                    res = cv2.resize(dst, self.image_view.tb_size, interpolation=cv2.INTER_AREA)
                else:
                    return
            else:
                if self.working_img_mask_data is None or da_link != 'Image':
                    return
                mask = self.working_img_mask_data.copy()
                mask = 255 - mask
                temp = self.processing_img.copy()
                dst = cv2.bitwise_and(temp, temp, mask=mask)
                self.image_view.img_stacks.image_list[0].setImage(dst)
                self.processing_img = dst
                res = cv2.resize(dst, self.image_view.tb_size, interpolation=cv2.INTER_AREA)

            self.layer_ctrl.layer_list[da_ind[0]].set_thumbnail_data(res)

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

    def img_cell_pnts_clicked(self, points, ev):
        if not self.tool_box.checkable_btn_dict['eraser_btn'].isChecked() or not self.working_img_cell_data:
            return
        clicked_ind = ev[0].index()
        layer_ind = self.cell_layer_index[clicked_ind]
        self.cell_count[layer_ind] -= 1
        self.tool_box.cell_count_val_list[layer_ind].setText(str(self.cell_count[layer_ind]))
        del self.working_img_cell_data[clicked_ind]
        del self.cell_symbol[clicked_ind]
        del self.cell_size[clicked_ind]
        del self.cell_layer_index[clicked_ind]
        self.image_view.img_stacks.cell_pnts.setData(pos=np.asarray(self.working_img_cell_data),
                                                     symbol=self.cell_symbol)

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
            int(da_pnt[1]), int(da_pnt[2]), int(da_pnt[0]), coords[1], coords[2], coords[0],
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
            int(da_pnt[1]), int(da_pnt[2]), int(da_pnt[0]), coords[1], coords[2], coords[0],
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
            int(da_pnt[1]), int(da_pnt[2]), int(da_pnt[0]), coords[1], coords[2], coords[0],
            self.atlas_view.label_tree.describe(da_id))
        self.statusbar.showMessage(pstr)

    def atlas_stacks_clicked(self, pos):
        # print('atlas clicked')
        x = pos[0]
        y = pos[1]
        if self.atlas_view.atlas_data is None or self.num_windows == 4:
            return
        if self.tool_box.checkable_btn_dict['triang_btn'].isChecked():
            self.inactive_lasso()
            if self.a2h_transferred or self.h2a_transferred:
                return
            self.atlas_tri_inside_data.append([int(x), int(y)])
            self.atlas_tri_data = self.atlas_tri_onside_data + self.atlas_tri_inside_data
            self.atlas_view.working_atlas.tri_pnts.setData(pos=np.asarray(self.atlas_tri_data))
            self.working_atlas_text.append(pg.TextItem(str(len(self.atlas_tri_inside_data))))
            self.working_atlas_text[-1].setColor(self.triangle_color)
            self.working_atlas_text[-1].setPos(x, y)
            self.atlas_view.working_atlas.vb.addItem(self.working_atlas_text[-1])
            if self.tool_box.triang_vis_btn.isChecked():
                self.update_atlas_tri_lines()
        elif self.tool_box.checkable_btn_dict['probe_btn'].isChecked():
            self.inactive_lasso()
            self.working_atlas_probe.append([x, y])
            self.atlas_view.working_atlas.probe_pnts.setData(pos=np.asarray(self.working_atlas_probe))
            if not self.atlas_view.working_atlas.probe_pnts.isVisible():
                self.atlas_view.working_atlas.probe_pnts.setVisible(True)
        # ------------------------- magic wand -- mask
        elif self.tool_box.checkable_btn_dict['magic_wand_btn'].isChecked():
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
        else:
            return

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

    def atlas_probe_pnts_clicked(self, points, ev):
        if self.num_windows == 4:
            return
        if not self.tool_box.checkable_btn_dict['eraser_btn'].isChecked() or not self.working_atlas_probe:
            return
        clicked_ind = ev[0].index()
        del self.working_atlas_probe[clicked_ind]
        self.atlas_view.working_atlas.probe_pnts.setData(pos=np.asarray(self.working_atlas_probe))

    def atlas_contour_pnts_clicked(self, points, ev):
        print('test contour points')
        if self.num_windows == 4:
            return
        if not self.tool_box.checkable_btn_dict['eraser_btn'].isChecked() or not self.working_atlas_contour:
            return
        clicked_ind = ev[0].index()
        del self.working_atlas_contour[clicked_ind]
        self.atlas_view.working_atlas.contour_pnts.setData(pos=np.asarray(self.working_atlas_contour))




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
            da_ind = np.where(np.ravel(self.layer_ctrl.layer_link) == layer_type)[0]
            self.layer_ctrl.layer_list[da_ind[0]].set_thumbnail_data(res)

    def layers_opacity_changed(self, ev):
        da_link = ev[0]
        val = ev[1]
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
        if data_tobe_registered:
            processing_data = np.asarray(data_tobe_registered)
            data = self.get_3d_pnts(processing_data)
            self.object_ctrl.add_object(object_type='probe - piece', object_data=data)
            self.working_atlas_probe = []

    def make_virus_piece(self):
        if self.h2a_transferred:
            if not self.working_atlas_virus:
                return
            processing_pnt = np.asarray(self.working_atlas_virus)
        else:
            if self.working_img_virus_data is None:
                return
            inds = np.where(self.working_img_virus_data != 0)
            processing_pnt = np.vstack([inds[0], inds[1]]).T

        data = self.get_3d_pnts(processing_pnt)
        self.object_ctrl.add_object(object_type='virus - piece', object_data=data)
        self.working_atlas_virus = []

    def make_contour_piece(self):
        if self.h2a_transferred:
            if not self.working_atlas_contour:
                return
            processing_pnt = np.asarray(self.working_atlas_contour)
        else:
            if self.working_img_contour_data is None:
                return
            inds = np.where(self.working_img_contour_data != 0)
            processing_pnt = np.vstack([inds[0], inds[1]]).T

        data = self.get_3d_pnts(processing_pnt)
        self.object_ctrl.add_object(object_type='contour - piece', object_data=data)
        self.working_atlas_contour = []

    def make_drawing_piece(self):
        if self.a2h_transferred:
            data_tobe_registered = self.working_img_drawing_data
        else:
            data_tobe_registered = self.working_atlas_drawing
        if not data_tobe_registered:
            return
        processing_data = np.asarray(data_tobe_registered)
        data = self.get_3d_pnts(processing_data)
        self.object_ctrl.add_object(object_type='drawing - piece', object_data=data)
        self.working_atlas_drawing = []

    def make_cell_piece(self):
        if self.a2h_transferred:
            data_tobe_registered = self.working_img_cell_data
        else:
            data_tobe_registered = self.working_atlas_cell
        if not data_tobe_registered:
            return
        processing_data = np.asarray(data_tobe_registered)
        data = self.get_3d_pnts(processing_data)
        print(data)
        for i in range(5):
            if i == 0:
                object_type = 'cell - piece'
            else:
                object_type = 'cell {} - piece'.format(i)
            if self.cell_count[i] != 0:
                piece_data = data[np.where(np.ravel(self.cell_layer_index) == i)[0], :]
                print(piece_data)
                self.object_ctrl.add_object(object_type=object_type, object_data=piece_data)
        self.working_atlas_cell = []

    def make_object_pieces(self):
        self.make_probe_piece()
        self.make_virus_piece()
        self.make_cell_piece()
        self.make_drawing_piece()
        self.make_contour_piece()

    # probe related functions
    def merge_probes(self):
        if self.object_ctrl.probe_piece_count == 0:
            return
        data = self.object_ctrl.merge_object_pieces('probe')
        print(data)
        label_data = np.transpose(self.atlas_view.atlas_label, (1, 2, 0))[:, :, ::-1]

        for i in range(len(data)):
            self.object_ctrl.add_object('merged probe', object_data=[])
            info_dict = calculate_probe_info(data[i], label_data, self.atlas_view.label_info, self.atlas_view.vxsize_um,
                                             self.tip_length, self.channel_size, self.atlas_view.bregma3d)

            info_dict['vis_color'] = self.object_ctrl.obj_list[-1].color
            self.registered_prob_list.append(info_dict)
            self.object_ctrl.obj_list[-1].eye_clicked.connect(self.obj_vis_changed)
            self.object_ctrl.obj_list[-1].sig_clicked.connect(self.probe_info_on_click)
            self.object_ctrl.obj_list[-1].sig_object_color_changed.connect(self.obj_color_changed)

            self.add_3d_probe_lines(info_dict)

    def add_3d_probe_lines(self, data_dict):
        pos = np.stack([data_dict['new_sp'], data_dict['new_ep']], axis=0)
        vis_color = get_object_vis_color(data_dict['vis_color'])
        probe_line = gl.GLLinePlotItem(pos=pos, color=vis_color, width=3, mode='line_strip')
        probe_line.setGLOptions('opaque')
        self.probe_lines_3d_list.append(probe_line)
        self.view3d.addItem(self.probe_lines_3d_list[-1])

    def probe_info_on_click(self, ev):
        print(ev)
        index = ev[0]
        num = ev[-1]
        print(('obj clicked', index))
        self.object_ctrl.set_active_layer_to_current(index)

        da_data = self.registered_prob_list[num]
        self.probe_window = ProbeInfoWindow(num + 1, da_data)
        self.probe_window.exec()

    # virus related functions
    def merge_virus(self):
        if self.object_ctrl.virus_piece_count == 0:
            return
        data = self.object_ctrl.merge_object_pieces('virus')
        print(data)
        label_data = np.transpose(self.atlas_view.atlas_label, (1, 2, 0))[:, :, ::-1]

        for i in range(len(data)):
            self.object_ctrl.add_object('merged virus', object_data=[])
            info_dict = calculate_virus_info(data[i], label_data, self.atlas_view.label_info, self.atlas_view.bregma3d)

            info_dict['vis_color'] = self.object_ctrl.obj_list[-1].color
            self.registered_virus_list.append(info_dict)
            self.object_ctrl.obj_list[-1].eye_clicked.connect(self.obj_vis_changed)
            self.object_ctrl.obj_list[-1].sig_clicked.connect(self.virus_info_on_click)
            self.object_ctrl.obj_list[-1].sig_object_color_changed.connect(self.obj_color_changed)

            virus_points = create_plot_points_in_3d(info_dict)
            self.virus_points_3d_list.append(virus_points)
            self.view3d.addItem(self.virus_points_3d_list[-1])

    def virus_info_on_click(self, ev):
        print(ev)
        index = ev[0]
        num = ev[-1]
        print(('obj clicked', index))
        self.object_ctrl.set_active_layer_to_current(index)

        da_data = self.registered_virus_list[num]
        self.virus_window = VirusInfoWindow(num + 1, da_data)
        self.virus_window.exec()

    # cell related functions
    def merge_cells(self):
        if self.object_ctrl.cell_piece_count == 0:
            return
        data = self.object_ctrl.merge_object_pieces('cell')
        print(data)
        label_data = np.transpose(self.atlas_view.atlas_label, (1, 2, 0))[:, :, ::-1]

        for i in range(len(data)):
            self.object_ctrl.add_object('merged cell', object_data=[])
            info_dict = calculate_cells_info(data[i], label_data, self.atlas_view.label_info,
                                             self.atlas_view.bregma3d)

            info_dict['vis_color'] = self.object_ctrl.obj_list[-1].color
            self.registered_cell_list.append(info_dict)
            self.object_ctrl.obj_list[-1].sig_clicked.connect(self.cell_info_on_click)
            self.object_ctrl.obj_list[-1].sig_object_color_changed.connect(self.obj_color_changed)
            self.object_ctrl.obj_list[-1].eye_clicked.connect(self.obj_vis_changed)

            cell_points = create_plot_points_in_3d(info_dict)
            self.cell_points_3d_list.append(cell_points)
            self.view3d.addItem(self.cell_points_3d_list[-1])

    def cell_info_on_click(self, ev):
        print(ev)
        index = ev[0]
        num = ev[-1]
        print(('obj clicked', index))
        self.object_ctrl.set_active_layer_to_current(index)

        da_data = self.registered_cell_list[num]
        self.cell_window = CellsInfoWindow(num + 1, da_data)
        self.cell_window.exec()

    # drawing related functions
    def merge_drawings(self):
        if self.object_ctrl.drawing_piece_count == 0:
            return
        data = self.object_ctrl.merge_object_pieces('drawing')
        # label_data = np.transpose(self.atlas_view.atlas_label, (1, 2, 0))[:, :, ::-1]

        for i in range(len(data)):
            self.object_ctrl.add_object('merged drawing', object_data=[])
            info_dict = {'object_type': 'drawing', 'data': data[i], 'vis_color': self.object_ctrl.obj_list[-1].color}
            self.registered_drawing_list.append(info_dict)
            self.object_ctrl.obj_list[-1].sig_object_color_changed.connect(self.obj_color_changed)
            self.object_ctrl.obj_list[-1].eye_clicked.connect(self.obj_vis_changed)

            self.add_3d_drawing_lines(info_dict)

    def add_3d_drawing_lines(self, data_dict):
        pos = np.asarray(data_dict['data'])
        vis_color = get_object_vis_color(data_dict['vis_color'])
        drawing_line = gl.GLLinePlotItem(pos=pos, color=vis_color, width=3, mode='line_strip')
        drawing_line.setGLOptions('opaque')
        self.drawing_lines_3d_list.append(drawing_line)
        self.view3d.addItem(self.drawing_lines_3d_list[-1])

    # contour related functions
    def merge_contour(self):
        if self.object_ctrl.contour_piece_count == 0:
            return
        data = self.object_ctrl.merge_object_pieces('contour')
        print(data)

        for i in range(len(data)):
            info_dict = {'object_type': 'contour', 'data': data[i], 'vis_color': self.object_ctrl.obj_list[-1].color}
            self.object_ctrl.add_object('merged contour', object_data=info_dict)

            # self.registered_contour_list.append(info_dict)
            self.object_ctrl.obj_list[-1].sig_object_color_changed.connect(self.obj_color_changed)
            self.object_ctrl.obj_list[-1].eye_clicked.connect(self.obj_vis_changed)

            contour_points = create_plot_points_in_3d(info_dict)
            self.contour_points_3d_list.append(contour_points)
            self.view3d.addItem(self.contour_points_3d_list[-1])


    # def add_3d_contour_pnts(self, data_dict):
    #     pos = np.asarray(data_dict['data'])
    #     vis_color = get_object_vis_color(data_dict['vis_color'])
    #     contour_line = gl.GLLinePlotItem(pos=pos, color=vis_color, width=3, mode='line_strip')
    #     contour_line.setGLOptions('opaque')
    #     self.contour_lines_3d_list.append(contour_line)
    #     self.view3d.addItem(self.contour_lines_3d_list[-1])

    def obj_color_changed(self, ev):
        id = ev[0]
        color = ev[1]
        object_type = ev[2]
        group_id = ev[3]
        if 'probe' in object_type:
            self.probe_lines_3d_list[group_id].setData(color=color)
            self.registered_prob_list[group_id]['vis_color'] = color.name()
        elif 'virus' in object_type:
            self.virus_points_3d_list[group_id].setData(color=color)
            self.registered_virus_list[group_id]['vis_color'] = color.name()
        elif 'contour' in object_type:
            self.contour_points_3d_list[group_id].setData(color=color)
            self.registered_contour_list[group_id]['vis_color'] = color.name()
        elif 'drawing' in object_type:
            self.drawing_lines_3d_list[group_id].setData(color=color)
            self.registered_drawing_list[group_id]['vis_color'] = color.name()
        else:
            self.cell_points_3d_list[group_id].setData(color=color)
            self.registered_cell_list[group_id]['vis_color'] = color.name()
        # self.probe_lines_2d[group_id].setPen(color)

    def obj_vis_changed(self, ev):
        id = ev[0]
        object_type = ev[1]
        vis = ev[2]
        group_id = ev[3]
        if 'probe' in object_type:
            self.probe_lines_3d_list[group_id].setVisible(vis)
        elif 'virus' in object_type:
            self.virus_points_3d_list[group_id].setVisible(vis)
        elif 'contour' in object_type:
            self.contour_points_3d_list[group_id].setVisible(vis)
        elif 'drawing' in object_type:
            self.drawing_lines_3d_list[group_id].setVisible(vis)
        else:
            self.cell_points_3d_list[group_id].setVisible(vis)
        # self.probe_lines_2d[group_id].setPen(color)

    def object_deleted(self):
        current_type = self.object_ctrl.obj_type[self.object_ctrl.current_obj_index]
        if 'merged' not in current_type:
            return
        group_id = self.object_ctrl.obj_group_id[self.object_ctrl.current_obj_index]
        if 'probe' in current_type:
            del self.registered_prob_list[group_id]

        elif 'cell' in current_type:
            del self.registered_cell_list[group_id]


    def obj_line_width_changed(self):
        val = self.object_ctrl.line_width_slider.value()
        for i in range(len(self.probe_lines_3d)):
            self.probe_lines_3d[i].setData(width=val)

    # ------------------------------------------------------------------
    #
    #                       Atlas Loader
    #
    # ------------------------------------------------------------------
    def load_atlas(self):
        self.statusbar.showMessage('Select folder to load Brain Atlas...')

        if os.path.exists('data/atlas_path.txt'):
            with open('data/atlas_path.txt') as f:
                lines = f.readlines()
            atlas_folder = lines[0]
        if os.path.exists(atlas_folder):
            self.statusbar.showMessage('Loading Brain Atlas...')
        else:
            atlas_folder = str(QFileDialog.getExistingDirectory(self, "Select Atlas Folder"))
            with open('data/atlas_path.txt', 'w') as f:
                f.write(atlas_folder)

        if atlas_folder != '':
            self.atlas_folder = atlas_folder

            with pg.BusyCursor():
                da_atlas = AtlasLoader(atlas_folder)

            if not da_atlas.success:
                self.statusbar.showMessage(da_atlas.msg)
                return
            else:
                self.statusbar.showMessage('Atlas loaded successfully.')

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

            self.statusbar.showMessage('Successfully set atlas data to view. Checking rendering for 3D visualisation...')

            # load mesh data
            pre_made_meshdata_path = os.path.join(atlas_folder, 'atlas_meshdata.pkl')
            pre_made_small_meshdata_path = os.path.join(atlas_folder, 'atlas_small_meshdata.pkl')

            if not os.path.exists(pre_made_meshdata_path) or not os.path.exists(pre_made_small_meshdata_path):
                self.statusbar.showMessage(
                    'Brain mesh is not found! Please pre-process the atlas.')

            try:
                infile = open(pre_made_meshdata_path, 'rb')
                self.meshdata = pickle.load(infile)
                infile.close()
            except ValueError:
                self.statusbar.showMessage('Please re-process mesh for the whole brain.')
                return

            self.atlas_view.mesh.setMeshData(meshdata=self.meshdata)
            self.mesh_origin = np.ravel(da_atlas.atlas_info[3]['Bregma'])
            self.atlas_view.mesh.translate(-self.mesh_origin[0], -self.mesh_origin[1], -self.mesh_origin[2])

            self.statusbar.showMessage('Brain mesh is Loaded.')

            return

            try:
                infile = open(pre_made_small_meshdata_path, 'rb')
                self.small_meshdata_list = pickle.load(infile)
                infile.close()
            except ValueError:
                self.statusbar.showMessage('Please re-process meshes for each brain region.')
                return

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

            self.statusbar.showMessage('Brain region mesh is Loaded.  Atlas loaded successfully.')
        else:
            if self.atlas_view.atlas_data is not None:
                self.statusbar.showMessage('No new atlas is selected.')
            else:
                self.statusbar.showMessage('No atlas is selected.')

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

    # ------------------------------------------------------------------
    #
    #                       Image Loader
    #
    # ------------------------------------------------------------------
    def load_image(self):
        if self.image_view.image_file is not None:
            print('need to clean everything outside of image_view')

        self.statusbar.showMessage('Choose Image file to load ...')
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

        filter = "CZI (*.czi);;JPEG (*.jpg;*.jpeg);;PNG (*.png);;TIFF (*.tif);;BMP (*.bmp)"
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.ExistingFiles)
        image_file_path = dlg.getOpenFileName(self, "Select Histological Image File", str(Path.home()), filter)

        image_file_type = image_file_path[0][-4:].lower()
        if image_file_path[0] != '':
            self.current_img_path = image_file_path[0]
            self.current_img_name = os.path.basename(os.path.realpath(image_file_path[0]))
            with pg.BusyCursor():
                with warnings.catch_warnings():
                    warnings.filterwarnings("error")
                    if image_file_type == '.czi':
                        image_file = CZIReader(image_file_path[0])
                        scale = self.image_view.scale_slider.value()
                        scale = 0.01 if scale == 0 else scale * 0.01
                        if self.image_view.check_scenes.isChecked():
                            image_file.read_data(scale, scene_index=None)
                        else:
                            image_file.read_data(scale, scene_index=0)
                        if image_file.is_rgb:
                            self.tool_box.cell_count_label_list[-1].setVisible(True)
                            self.tool_box.cell_count_val_list[-1].setVisible(True)
                        else:
                            for i in range(image_file.n_channels):
                                self.tool_box.cell_count_label_list[i+1].setVisible(True)
                                self.tool_box.cell_count_val_list[i+1].setVisible(True)
                    else:
                        image_file = ImageReader(image_file_path[0])
                        self.tool_box.cell_count_label_list[0].setVisible(True)
                        self.tool_box.cell_count_val_list[0].setVisible(True)
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

            self.drawing_img = np.zeros(self.image_view.img_size, 'uint8')
            self.cell_img = np.zeros(self.image_view.img_size, 'uint8')

            self.image_view.img_stacks.mask_img.setLookupTable(self.tool_box.base_lut)
            self.image_view.img_stacks.virus_img.setLookupTable(self.tool_box.base_lut)
            self.image_view.img_stacks.contour_img.setLookupTable(self.tool_box.base_lut)
        else:
            if self.image_view.image_file is None:
                self.statusbar.showMessage('No image file is selected.')
            else:
                self.statusbar.showMessage('No new image file is selected.')
            return

    # load multiple images
    def load_images(self):
        self.statusbar.showMessage('Selecte folder to load multiple images, files can not be .czi format ...')
        images_folder = str(QFileDialog.getExistingDirectory(self, "Select Images Folder"))
        if images_folder != '':
            # image_files_list = os.listdir(images_folder)
            # image_files_list = natsorted(image_files_list)

            with pg.BusyCursor():
                with warnings.catch_warnings():
                    warnings.filterwarnings("error")
                    image_file = ImagesReader(images_folder)
                    self.image_view.set_data(image_file)

            self.sidebar.setCurrentIndex(3)
            self.statusbar.showMessage('Image files loaded.')
        else:
            return

    # ------------------------------------------------------------------
    #
    #                       Saving Files
    #
    # ------------------------------------------------------------------
    def save_image(self, image_type):
        if image_type == 'Processed':
            da_img = self.processing_img
            da_img = cv2.cvtColor(da_img, cv2.COLOR_RGB2BGR)
        elif image_type == 'Overlay':
            da_img = self.overlay_img
        else:
            da_img = self.working_img_mask_data
        if da_img is None:
            return
        self.statusbar.showMessage('Save {} Image ...'.format(image_type))
        path = QFileDialog.getSaveFileName(self, "Save Image", self.current_img_path, "JPEG (*.jpg)")
        if path[0] != '':
            cv2.imwrite(path[0], da_img)
            self.statusbar.showMessage('{} Image is saved successfully ...'.format(image_type))
        else:
            self.statusbar.showMessage('No file name is given to save.')

    def save_triangulation_points(self):
        print('save triang pnts')

    def save_probe_object(self):
        if not self.registered_prob_list:
            return

    def save_virus_object(self):
        print('1')

    def save_cell_object(self):
        print('1')

    def save_drawing_object(self):
        print('1')

    def save_contour_object(self):
        print('1')

    def save_objects(self):
        print('1')

    def save_current_object(self):
        if self.object_ctrl.current_obj_index is None:
            self.statusbar.showMessage('No object is created ...')
            return
        file_name = QFileDialog.getSaveFileName(self, 'Save Current Object File', self.current_img_path, "JPEG (*.jpg)")
        if file_name[0] != '':
            current_obj_type = self.object_ctrl.obj_type[self.object_ctrl.current_obj_index]
            if 'merged' not in current_obj_type:
                self.statusbar.showMessage('Only merged object can be saved ...')
                return
            group_id = self.object_ctrl.obj_group_id[self.object_ctrl.current_obj_index]
            if 'probe' in current_obj_type:
                da_data = self.registered_prob_list[group_id]
            elif 'viurs' in current_obj_type:
                da_data = self.registered_virus_list[group_id]
            elif 'cell' in current_obj_type:
                da_data = self.registered_cell_list[group_id]
            elif 'contour' in current_obj_type:
                da_data = self.registered_contour_list[group_id]
            else:
                da_data = self.registered_drawing_list[group_id]
            with open(file_name[0], 'wb') as handle:
                pickle.dump(da_data, handle, protocol=pickle.HIGHEST_PROTOCOL)
            self.statusbar.showMessage('Current merged object is saved successfully.')

    def save_project(self):
        if self.overlay_img is None:
            self.statusbar.showMessage('Project can be saved after overlay image is created.')
            return
        self.statusbar.showMessage('Saving Project ...')

        file_name = QFileDialog.getSaveFileName(self, 'Save Project')
        if file_name != '':
            project_data = {'atlas_display': self.atlas_display,
                            'slice_index': 1,
                            'image_path': 1,
                            'scene_index': 1,
                            'scale_val': 1,
                            'img_triang_pnt': 1,
                            'atlas_triang_pnt': 1,
                            'processed_img': self.processing_img,
                            'overlay_img': self.overlay_img,
                            'layers': 1,
                            'objects': 1}

            with open(file_name[0], 'wb') as handle:
                pickle.dump(project_data, handle, protocol=pickle.HIGHEST_PROTOCOL)
            self.statusbar.showMessage('Project saved successfully.')


    # ------------------------------------------------------------------
    #
    #                       Load Files
    #
    # ------------------------------------------------------------------
    def load_project(self):
        print('1')

    # load triangulation points
    def load_triangulation_points(self):
        filter = "Pickle File (*.pkl)"
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.ExistingFiles)
        pnt_path = dlg.getOpenFileName(self, "Load Triangulation Points", str(Path.home()), filter)

        if pnt_path[0] != '':
            infile = open(pnt_path[0], 'rb')
            pnt_dict = pickle.load(infile)
            infile.close()

    # load object
    def load_object(self):
        filter = "Pickle File (*.pkl)"
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.ExistingFiles)
        object_file_path = dlg.getOpenFileName(self, "Load Object File", str(Path.home()), filter)

        if object_file_path[0] != '':
            infile = open(object_file_path[0], 'rb')
            object_dict = pickle.load(infile)
            infile.close()






def main():
    app = QApplication(argv)
    app.setStyleSheet(herbs_style)
    # if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    #     app.instance().exec_()
    window = HERBS()
    window.show()
    exit(app.exec_())








