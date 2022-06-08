import os
from os.path import dirname, realpath, join
import sys
from sys import argv, exit
from pathlib import Path

import pickle
import csv
import nibabel as nib
import numpy as np
import pandas as pd
import cv2
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from .uuuuuu import make_contour_img, render_volume, render_small_volume
from .atlas_loader import process_atlas_raw_data, AtlasLoader


class AtlasProcessor(QDialog):
    def __init__(self):
        super().__init__()
        self.setStyleSheet('color: black;')
        self.setWindowTitle("Atlas Processor")

        self.folder_path = None
        self.data_local = None
        self.segmentation_local = None
        self.mask_local = None
        self.labinf_path = None
        self.bregma_coord = [0, 0, 0]
        self.lambda_coord = [0, 0, 0]
        self.voxel_size = 0
        self.factor_val = 2

        layout = QGridLayout(self)

        data_label = QLabel('Volume File:')
        self.data_btn = QPushButton('Select File')
        self.data_line = QLineEdit()

        seg_label = QLabel('Segmentation File: ')
        self.seg_btn = QPushButton('Select File')
        self.seg_line = QLineEdit()

        mask_label = QLabel('Mask File (optional): ')
        self.mask_btn = QPushButton('Select File')
        self.mask_line = QLineEdit()

        labinf_label = QLabel('Label Information File:')
        self.labinf_btn = QPushButton('Select File')
        self.labinf_line = QLineEdit()

        valid_input = QIntValidator(0, 99999)

        float_input = QRegExpValidator(QRegExp(r'[0-9].+'))
        # float_input = QDoubleValidator(0.0, 100.0, 6)

        bregma_label = QLabel('Bregma Coordinates (voxel): ')
        self.bregma_input1 = QLineEdit('0')
        self.bregma_input1.setValidator(valid_input)
        self.bregma_input2 = QLineEdit('0')
        self.bregma_input2.setValidator(valid_input)
        self.bregma_input3 = QLineEdit('0')
        self.bregma_input3.setValidator(valid_input)

        lambda_label = QLabel('Lambda Coordinates (voxel): ')
        self.lambda_input1 = QLineEdit('0')
        self.lambda_input1.setValidator(valid_input)
        self.lambda_input2 = QLineEdit('0')
        self.lambda_input2.setValidator(valid_input)
        self.lambda_input3 = QLineEdit('0')
        self.lambda_input3.setValidator(valid_input)

        vox_size_label = QLabel('Voxel Size (um): ')
        self.vox_size_input1 = QLineEdit('0')
        self.vox_size_input1.setValidator(float_input)

        factor_label = QLabel('Factor (voxel): ')
        self.factor_input1 = QLineEdit('2')
        self.factor_input1.setValidator(valid_input)

        selector_vals = ['Left --> Right', 'Right --> Left',
                         'Superior --> Inferior', 'Inferior --> Superior',
                         'Posterior --> Anterior', 'Anterior --> Posterior']

        # x_axis_label = QLabel('x-axis: ')
        # self.x_axis_combo = QComboBox()
        # self.x_axis_combo.addItems(selector_vals)
        #
        # y_axis_label = QLabel('y-axis: ')
        # self.y_axis_combo = QComboBox()
        # self.y_axis_combo.addItems(selector_vals)
        #
        # z_axis_label = QLabel('z-axis: ')
        # self.z_axis_combo = QComboBox()
        # self.z_axis_combo.addItems(selector_vals)

        self.process_btn = QPushButton('Start Process')

        layout.addWidget(data_label, 0, 0, 1, 1)
        layout.addWidget(self.data_btn, 0, 1, 1, 1)
        layout.addWidget(self.data_line, 0, 2, 1, 2)
        layout.addWidget(seg_label, 1, 0, 1, 1)
        layout.addWidget(self.seg_btn, 1, 1, 1, 1)
        layout.addWidget(self.seg_line, 1, 2, 1, 2)
        layout.addWidget(mask_label, 2, 0, 1, 1)
        layout.addWidget(self.mask_btn, 2, 1, 1, 1)
        layout.addWidget(self.mask_line, 2, 2, 1, 2)
        layout.addWidget(labinf_label, 3, 0, 1, 1)
        layout.addWidget(self.labinf_btn, 3, 1, 1, 1)
        layout.addWidget(self.labinf_line, 3, 2, 1, 2)
        layout.addWidget(bregma_label, 4, 0, 1, 1)
        layout.addWidget(self.bregma_input1, 4, 1, 1, 1)
        layout.addWidget(self.bregma_input2, 4, 2, 1, 1)
        layout.addWidget(self.bregma_input3, 4, 3, 1, 1)
        layout.addWidget(lambda_label, 5, 0, 1, 1)
        layout.addWidget(self.lambda_input1, 5, 1, 1, 1)
        layout.addWidget(self.lambda_input2, 5, 2, 1, 1)
        layout.addWidget(self.lambda_input3, 5, 3, 1, 1)
        layout.addWidget(vox_size_label, 6, 0, 1, 1)
        layout.addWidget(self.vox_size_input1, 6, 1, 1, 1)
        layout.addWidget(factor_label, 6, 2, 1, 1)
        layout.addWidget(self.factor_input1, 6, 3, 1, 1)

        # layout.addWidget(x_axis_label, 6, 0, 1, 1)
        # layout.addWidget(self.x_axis_combo, 6, 1, 1, 3)
        # layout.addWidget(y_axis_label, 7, 0, 1, 1)
        # layout.addWidget(self.y_axis_combo, 7, 1, 1, 3)
        # layout.addWidget(z_axis_label, 8, 0, 1, 1)
        # layout.addWidget(self.z_axis_combo, 8, 1, 1, 3)

        layout.addWidget(self.process_btn, 7, 0, 1, 4)

        # connect all buttons
        self.data_btn.clicked.connect(self.get_data_file)
        self.seg_btn.clicked.connect(self.get_seg_file)
        self.mask_btn.clicked.connect(self.get_mask_file)
        self.labinf_btn.clicked.connect(self.get_info_file)
        self.process_btn.clicked.connect(self.process_data)
        self.bregma_input1.textChanged.connect(self.bregma_input1_changed)
        self.bregma_input2.textChanged.connect(self.bregma_input2_changed)
        self.bregma_input3.textChanged.connect(self.bregma_input3_changed)
        self.lambda_input1.textChanged.connect(self.lambda_input1_changed)
        self.lambda_input2.textChanged.connect(self.lambda_input2_changed)
        self.lambda_input3.textChanged.connect(self.lambda_input3_changed)
        self.vox_size_input1.textChanged.connect(self.vox_size_input_changed)
        self.factor_input1.textChanged.connect(self.factor_input_changed)

    def get_folder_path(self, file_path):
        self.folder_path = os.path.dirname(file_path)

    def get_data_file(self):
        if self.folder_path is not None:
            data_path = QFileDialog.getOpenFileName(self, 'Select Atlas Volume File', self.folder_path)
        else:
            data_path = QFileDialog.getOpenFileName(self, 'Select Atlas Volume File')
            self.get_folder_path(data_path[0])
        self.data_local = os.path.basename(data_path[0])
        self.data_line.setText(self.data_local)

    def get_seg_file(self):
        if self.folder_path is not None:
            seg_path = QFileDialog.getOpenFileName(self, 'Select Segmentation File', self.folder_path)
        else:
            seg_path = QFileDialog.getOpenFileName(self, 'Select Segmentation File')
            self.get_folder_path(seg_path[0])
        self.segmentation_local = os.path.basename(seg_path[0])
        self.seg_line.setText(self.segmentation_local)

    def get_mask_file(self):
        if self.folder_path is not None:
            mask_path = QFileDialog.getOpenFileName(self, 'Select Mask File', self.folder_path)
        else:
            mask_path = QFileDialog.getOpenFileName(self, 'Select Mask File')
            self.get_folder_path(mask_path[0])
        self.mask_local = os.path.basename(mask_path[0])
        self.mask_line.setText(self.mask_local)

    def get_info_file(self):
        if self.folder_path is not None:
            self.info_path = QFileDialog.getOpenFileName(self, 'Select Label Information File', self.folder_path)
        else:
            self.info_path = QFileDialog.getOpenFileName(self, 'Select Label Information File')
            self.get_folder_path(self.info_path[0])
        self.labinf_line.setText(os.path.basename(self.info_path[0]))

    def bregma_input1_changed(self, text):
        if text == '':
            return
        self.bregma_coord[0] = int(text)

    def bregma_input2_changed(self, text):
        if text == '':
            return
        self.bregma_coord[1] = int(text)

    def bregma_input3_changed(self, text):
        if text == '':
            return
        self.bregma_coord[2] = int(text)

    def lambda_input1_changed(self, text):
        if text == '':
            return
        self.lambda_coord[0] = int(text)

    def lambda_input2_changed(self, text):
        if text == '':
            return
        self.lambda_coord[1] = int(text)

    def lambda_input3_changed(self, text):
        if text == '':
            return
        self.lambda_coord[2] = int(text)

    def vox_size_input_changed(self, text):
        if text == '':
            return
        self.voxel_size = float(text)

    def factor_input_changed(self, text):
        if text == '':
            return
        self.factor_val = int(text)

    def process_data(self):
        if self.data_local is None or self.segmentation_local is None:
            msg = 'Please give the atlas volume file and label segmentation file.'
            return
        if self.voxel_size == 0 or self.factor_val == 0:
            msg = 'Please give the correct voxel size. Voxel size can not be 0.'
            return

        da_atlas = AtlasLoader(self.folder_path)
        if da_atlas.success:
            atlas_data = da_atlas.atlas_data
            segmentation_data = da_atlas.segmentation_data
            msg = 'Atlas loaded successfully.'
        else:
            atlas_data, atlas_info, segmentation_data, boundary, msg = \
                process_atlas_raw_data(self.folder_path, data_file=self.data_local,
                                       segmentation_file=self.segmentation_local, mask_file=self.mask_local,
                                       bregma_coordinates=self.bregma_coord, lambda_coordinates=self.lambda_coord,
                                       voxel_size=self.voxel_size)

        if msg == 'Atlas loaded successfully.':
            #render_volume(atlas_data, self.folder_path, factor=self.factor_val, level=0.1)
            # render_small_volume(atlas_data, segmentation_data, self.folder_path, factor=self.factor_val, level=0.1)
            self.process_btn.setVisible(False)

            self.close()
        else:
            return msg



