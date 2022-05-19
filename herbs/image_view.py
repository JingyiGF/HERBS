import colorsys
import os
import sys

import PyQt5.QtGui
import cv2
import copy
import pyqtgraph.functions as fn
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from pyqtgraph.Qt import QtGui, QtCore
import scipy.ndimage as ndi

from .image_stacks import ImageStacks
from .image_curves import CurveWidget, ChannelSelector
from .uuuuuu import hsv2rgb, gamma_line, color_img, make_color_lut, get_corner_line_from_rect, \
    rotate, rotate_bound, get_tb_size


sidebar_button_style = '''
QPushButton{
    background: #656565;
    border-radius: 5px;
    color: white;
    border-style: outset;
    border-bottom: 1px solid rgb(30, 30, 30);
    height: 24px;
    margin: 0px;
}

QPushButton:hover{
    background-color: #323232;
    border: 1px solid #656565;
}

QPushButton:checked{
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #17bb00, stop: 1 #0e6900);
    border-bottom: 1px solid rgb(30, 30, 30);
    border-top: None;
    border-left: None;
    border-right: None;  
}
'''


class ImageView(QObject):
    """
    A collection of user interface elements bound together:
        for histological images usage.

    When set data into this object, the full image file is needed.
    * the maximum channel number is 4, matching ZenBlue.
    * scene_wrap, scale_wrap, img_stacks, curve_widget, chn_widget_wrap
    * if image file is rgb, chn_widget_wrap will not show
    * curve change for rgb ---> hsv on brightness channel
    * curve change for not rgb ----> on the channel which is visible


    """
    class SignalProxy(QObject):
        imageChanged = pyqtSignal()  # id

    def __init__(self):
        self._sigprox = ImageView.SignalProxy()
        self.sig_image_changed = self._sigprox.imageChanged

        QObject.__init__(self)

        # define the initials
        self.image_file = None
        self.current_img = None
        self.current_scale = None
        self.img_size = None
        self.tb_size = None
        self.color_lut_list = []
        self.scene_index = 0
        self.max_num_channels = 4
        self.channel_visible = [False, False, False, False]
        self.channel_color = [None, None, None, None]

        self.side_lines = None
        self.corner_points = None

        self.current_mode = 'rgb'

        # scene control
        self.check_scenes = QPushButton('Load ALL Scenes')
        self.check_scenes.setStyleSheet(sidebar_button_style)
        self.check_scenes.setCheckable(True)
        self.scene_slider = QSlider(Qt.Horizontal)
        self.scene_slider.setMinimum(0)
        self.scene_slider.setValue(0)
        self.scene_slider.valueChanged.connect(self.scene_index_changed)
        self.scene_label = QLabel('0/ 0')
        self.scene_wrap = QFrame()
        # self.scene_wrap.setFixedWidth(290)
        scene_wrap_layout = QHBoxLayout(self.scene_wrap)
        # scene_wrap_layout.setContentsMargins(0, 0, 0, 0)
        # scene_wrap_layout.setSpacing(5)
        scene_wrap_layout.addWidget(QLabel('Scene: '))
        scene_wrap_layout.addWidget(self.scene_slider)
        scene_wrap_layout.addWidget(self.scene_label)
        # self.scene_wrap.setVisible(False)

        # scale control
        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setMinimum(1)
        self.scale_slider.setMaximum(100)
        self.scale_slider.setValue(10)
        self.scale_slider.setSingleStep(10)
        self.scale_slider.setTickInterval(10)
        self.scale_slider.valueChanged.connect(self.scale_value_changed)
        self.scale_slider.sliderReleased.connect(self.scale_slider_released)
        self.scale_label = QLabel('{}%'.format(10))
        self.scale_wrap = QFrame()
        # self.scale_wrap.setFixedWidth(290)
        scale_wrap_layout = QHBoxLayout(self.scale_wrap)
        # scale_wrap_layout.setContentsMargins(0, 0, 0, 0)
        # scale_wrap_layout.setSpacing(5)
        scale_wrap_layout.addWidget(QLabel('Scale: '))
        scale_wrap_layout.addWidget(self.scale_slider)
        scale_wrap_layout.addWidget(self.scale_label)

        # image stacks
        self.img_stacks = ImageStacks()

        # curve widget
        self.curve_widget = CurveWidget()
        self.curve_widget.setEnabled(False)
        self.curve_widget.setFixedHeight(280)
        self.curve_widget.sig_table_changed.connect(self.image_curve_changed)
        self.curve_widget.sig_reset.connect(self.image_curve_reset)
        self.curve_widget.sig_line_type_changed.connect(self.image_curve_type_changed)

        # channel buttons
        self.chn_widget_wrap = QFrame()
        # self.chn_widget_wrap.setFixedWidth(280)
        self.chn_widget_wrap.setStyleSheet('QFrame{border: 1px solid #747a80; border-radius: 5px;}')
        chn_widget_layout = QHBoxLayout(self.chn_widget_wrap)
        # chn_widget_layout.setContentsMargins(0, 0, 0, 0)
        # chn_widget_layout.setSpacing(5)
        self.chn_widget_list = []
        for i in range(self.max_num_channels):
            self.chn_widget_list.append(ChannelSelector())
            self.chn_widget_list[i].set_channel_index(i)
            self.chn_widget_list[i].sig_vis_channels.connect(self.set_channel_visible)
            self.chn_widget_list[i].sig_change_color.connect(self.channel_color_changed)
            chn_widget_layout.addWidget(self.chn_widget_list[i])
            self.chn_widget_list[i].setVisible(False)
        self.chn_widget_wrap.setVisible(False)

        self.outer_frame = QFrame()
        outer_layout = QVBoxLayout(self.outer_frame)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)
        outer_layout.addWidget(self.check_scenes)
        outer_layout.addWidget(self.scale_wrap)
        outer_layout.addWidget(self.scene_wrap)
        outer_layout.addWidget(self.curve_widget)
        outer_layout.addSpacing(10)
        outer_layout.addWidget(self.chn_widget_wrap)

    def set_data(self, image_file):
        if self.image_file is not None:
            self.clear_image_stacks()
            self.chn_widget_wrap.setVisible(False)
            self.curve_widget.reset_pressed()
            self.curve_widget.setEnabled(False)
            for i in range(self.image_file.n_channels):
                self.chn_widget_list[i].delete_item()
            for i in range(self.max_num_channels):
                self.channel_color[i] = None
                self.channel_visible[i] = False
                self.img_stacks.image_list[i].clear()
                self.chn_widget_list[i].setVisible(False)
            self.image_file = None

        scene_ind = self.scene_slider.value()

        self.image_file = image_file
        self.current_img = copy.deepcopy(self.image_file.data['scene {}'.format(scene_ind)])
        self.current_scale = self.image_file.scale['scene {}'.format(scene_ind)]



        if self.image_file.n_scenes != 1:
            self.scene_slider.setMaximum(self.image_file.n_scenes-1)
            self.scene_label.setText('0/{}'.format(self.image_file.n_scenes-1))
            self.scene_wrap.setVisible(True)
        else:
            self.scene_wrap.setVisible(False)

        # set data to curves
        self.update_curves()

        self.set_channel_widgets()
        # set data to image stacks
        self.set_data_to_img_stacks()
        self.get_corner_and_lines()

    def set_channel_widgets(self):
        # set color and names to channels
        self.chn_widget_wrap.setVisible(True)
        for i in range(self.image_file.n_channels):
            # get color look-up-table
            self.channel_color[i] = copy.deepcopy(self.image_file.hsv_colors[i])
            da_hsv_color = self.channel_color[i]
            da_lut = make_color_lut(da_hsv_color)
            self.color_lut_list.append(da_lut)

            self.chn_widget_list[i].setVisible(True)
            self.chn_widget_list[i].vis_btn.setText(self.image_file.channel_name[i])
            self.chn_widget_list[i].add_item(self.channel_color[i])
            self.channel_visible[i] = True

    def set_data_and_size(self, img_data):
        self.img_stacks.set_data(img_data)
        self.img_size = img_data.shape[:2]
        self.img_stacks.image_dict['tri_pnts'].set_range(self.img_size[1], self.img_size[0])
        self.tb_size = get_tb_size(self.img_size)

    def set_data_to_img_stacks(self):
        self.set_data_and_size(self.current_img)
        self.img_stacks.set_lut(self.color_lut_list, self.image_file.level)

    def get_corner_and_lines(self):
        rect = (0, 0, self.img_size[1], self.img_size[0])
        self.corner_points, self.side_lines = get_corner_line_from_rect(rect)
        self.sig_image_changed.emit()

    def update_curves(self):
        self.curve_widget.setEnabled(True)
        img_layers = self.current_img.copy()
        self.curve_widget.set_data(img_layers, self.image_file.rgb_colors, self.image_file.level)

    def scene_index_changed(self):
        scene_index = self.scene_slider.value()
        self.scene_label.setText('{}/{}'.format(scene_index, self.image_file.n_scenes-1))
        if self.image_file is None:
            return
        with pg.BusyCursor():
            if 'scene {}'.format(scene_index) not in self.image_file.data.keys():
                if self.image_file.is_czi:
                    scale = self.scale_slider.value()
                    scale_val = scale * 0.01
                    self.image_file.read_data(scale_val, scene_index=scene_index)
                else:
                    print('not czi files')
            self.current_img = copy.deepcopy(self.image_file.data['scene {}'.format(scene_index)])
            self.current_scale = self.image_file.scale['scene {}'.format(scene_index)]

            self.img_size = self.current_img.shape[:2]
            self.clear_image_stacks()
            self.img_stacks.image_dict['tri_pnts'].set_range(self.img_size[1], self.img_size[0])
            self.img_stacks.set_data(self.current_img)
            self.img_stacks.set_lut(self.color_lut_list, self.image_file.level)
            self.get_corner_and_lines()
            self.update_curves()
            # reset gamma and channels and black/white slider

    def scale_value_changed(self):
        scale = self.scale_slider.value()
        self.scale_label.setText('{}%'.format(scale))

    def scale_slider_released(self):
        scale = self.scale_slider.value()
        scale_val = scale * 0.01
        scene_index = self.scene_slider.value()
        if self.image_file is None:
            return
        if self.image_file.is_czi:
            with pg.BusyCursor():
                self.image_file.read_data(scale_val, scene_index)
                self.current_img = copy.deepcopy(self.image_file.data['scene %d' % scene_index])
                self.current_scale = self.image_file.scale['scene {}'.format(scene_index)]

                self.img_size = self.current_img.shape[:2]
                self.clear_image_stacks()
                self.img_stacks.image_dict['tri_pnts'].set_range(self.img_size[1], self.img_size[0])
                self.set_data_to_img_stacks()
                self.get_corner_and_lines()

    def channel_color_changed(self, col, ind):
        da_lut = make_color_lut(col)
        self.img_stacks.image_list[ind].setLookupTable(da_lut)
        self.color_lut_list[ind] = da_lut
        self.channel_color[ind] = col
        self.curve_widget.curve_plot.change_hist_color(col, ind)

    def set_channel_visible(self, vis, ind):
        self.channel_visible[ind] = vis
        self.img_stacks.image_list[ind].setVisible(vis)

    def image_curve_changed(self, table):
        if self.image_file is None:
            return
        table = table.astype(int)
        print(np.max(table))
        if self.image_file.pixel_type == 'rgb24':
            da_img = cv2.LUT(self.current_img.astype('uint8'), table)
            self.img_stacks.set_data(da_img)
        else:
            for i in range(self.image_file.n_channels):
                if self.channel_visible[i]:
                    lut_in = self.color_lut_list[i].copy()
                    lut_out = lut_in[table, :]
                    self.img_stacks.image_list[i].setLookupTable(lut_out)

    def image_curve_type_changed(self):
        """
        signal function after change line type
        set to the original 2 points linear type
        """
        if self.image_file is None:
            return
        for i in range(self.image_file.n_channels):
            self.img_stacks.image_list[i].setLookupTable(self.color_lut_list[i])

    def image_curve_reset(self):
        """
        signal function after press button 'Reset'
        """
        original_hsv_list = self.image_file.hsv_colors.copy()
        for i in range(self.image_file.n_channels):
            self.channel_color[i] = original_hsv_list[i]
            self.chn_widget_list[i].color_combo.setCurrentIndex(
                len(self.chn_widget_list[i].color_combo.hsv_color_list) - 1)
            self.curve_widget.curve_plot.change_hist_color(self.channel_color[i], i)
            da_lut = make_color_lut(self.channel_color[i])
            self.color_lut_list[i] = da_lut
            self.img_stacks.image_list[i].setLookupTable(da_lut)

    # image rotation
    def image_vertical_flip(self):
        if self.image_file is None:
            return
        # if self.image_file.is_rgb:
        #     self.current_img = cv2.flip(self.current_img, 0)
        # else:
        for i in range(self.image_file.n_channels):
            self.current_img[:, :, i] = cv2.flip(self.current_img[:, :, i], 0)
        self.clear_image_stacks()
        self.img_size = self.current_img.shape[:2]
        self.img_stacks.image_dict['tri_pnts'].set_range(self.img_size[1], self.img_size[0])
        self.img_stacks.set_data(self.current_img)

    def image_horizon_flip(self):
        if self.image_file is None:
            return
        # if self.image_file.is_rgb:
        #     self.current_img = cv2.flip(self.current_img, 1)
        # else:
        for i in range(self.image_file.n_channels):
            self.current_img[:, :, i] = cv2.flip(self.current_img[:, :, i], 1)
        self.clear_image_stacks()
        self.img_stacks.set_data(self.current_img)
        self.img_size = self.current_img.shape[:2]
        self.img_stacks.image_dict['tri_pnts'].set_range(self.img_size[1], self.img_size[0])

    def image_90_rotate(self):
        if self.image_file is None:
            return
        # if self.image_file.is_rgb:
        #     self.current_img = cv2.rotate(self.current_img, cv2.ROTATE_90_CLOCKWISE)
        # else:
        # scene_index = self.scene_slider.value()
        temp = []
        for i in range(self.image_file.n_channels):
            self.img_stacks.image_list[i].clear()
            temp.append(cv2.rotate(self.current_img[:, :, i], cv2.ROTATE_90_CLOCKWISE))
        self.current_img = np.dstack(temp)
        self.clear_image_stacks()
        self.img_stacks.set_data(self.current_img)
        self.img_size = self.current_img.shape[:2]
        self.img_stacks.image_dict['tri_pnts'].set_range(self.img_size[1], self.img_size[0])
        self.get_corner_and_lines()
        # self.image_file.data['scene %d' % scene_index] = self.current_img.copy()
        self.tb_size = np.flip(self.tb_size, 0)

    def image_180_rotate(self):
        if self.image_file is None:
            return
        # if self.image_file.is_rgb:
        #     self.current_img = cv2.rotate(self.current_img, cv2.ROTATE_180)
        # else:
        temp = []
        for i in range(self.image_file.n_channels):
            self.img_stacks.image_list[i].clear()
            temp.append(cv2.rotate(self.current_img[:, :, i], cv2.ROTATE_180))
        self.current_img = np.dstack(temp)
        self.clear_image_stacks()
        self.img_stacks.set_data(self.current_img)
        self.img_size = self.current_img.shape[:2]
        self.img_stacks.image_dict['tri_pnts'].set_range(self.img_size[1], self.img_size[0])

    def image_90_counter_rotate(self):
        if self.image_file is None:
            return
        # if self.image_file.is_rgb:
        #     self.current_img = cv2.rotate(self.current_img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        # else:
        temp = []
        for i in range(self.image_file.n_channels):
            self.img_stacks.image_list[i].clear()
            temp.append(cv2.rotate(self.current_img[:, :, i], cv2.ROTATE_90_COUNTERCLOCKWISE))
        self.current_img = np.dstack(temp)
        self.clear_image_stacks()
        self.img_stacks.set_data(self.current_img)
        self.img_size = self.current_img.shape[:2]
        self.img_stacks.image_dict['tri_pnts'].set_range(self.img_size[1], self.img_size[0])
        self.get_corner_and_lines()
        self.tb_size = np.flip(self.tb_size, 0)

    def image_1_rotate(self, rotate_direction):
        if self.image_file is None:
            return
        if rotate_direction == 'clockwise':
            rotation_angle = - 1
        else:
            rotation_angle = 1
        temp = []
        for i in range(self.image_file.n_channels):
            temp.append(rotate(self.current_img[:, :, i], rotation_angle))
        self.current_img = np.dstack(temp)
        self.clear_image_stacks()
        self.img_stacks.set_data(self.current_img)
        self.img_size = self.current_img.shape[:2]
        self.img_stacks.image_dict['tri_pnts'].set_range(self.img_size[1], self.img_size[0])
        self.get_corner_and_lines()

    # mode change
    def image_mode_changed(self, mode):
        if self.image_file is None:
            return
        if not self.image_file.is_rgb:
            return
        temp = self.current_img.copy()
        scene_ind = self.scene_slider.value()
        if mode == 'gray':
            if self.current_mode != 'rgb':
                temp = copy.deepcopy(self.image_file.data['scene {}'.format(scene_ind)])
                temp = cv2.cvtColor(temp, cv2.COLOR_BGR2RGBA)
            da_img = cv2.cvtColor(temp, cv2.COLOR_RGBA2GRAY)
        elif mode == 'hsv':
            if self.current_mode != 'rgb':
                temp = copy.deepcopy(self.image_file.data['scene {}'.format(scene_ind)])
                temp = cv2.cvtColor(temp, cv2.COLOR_BGR2RGBA)
            da_temp = cv2.cvtColor(temp, cv2.COLOR_RGBA2RGB)
            da_img = cv2.cvtColor(da_temp, cv2.COLOR_RGB2HSV)
        else:
            scene_ind = self.scene_slider.value()
            temp = copy.deepcopy(self.image_file.data['scene {}'.format(scene_ind)])
            da_img = cv2.cvtColor(temp, cv2.COLOR_BGR2RGBA)
        # self.current_img = da_img.copy()
        # self.img_stacks.set_data(self.current_img, is_rgb=True)
        # self.current_mode = mode

    def get_image_control_data(self):
        data = {'current_img': self.current_img,
                'color_lut_list': self.color_lut_list,
                'scene_index': self.scene_index,
                'scale_val': self.scale_slider.value(),
                'channel_visible': self.channel_visible,
                'channel_color': self.channel_color,
                'side_lines': self.side_lines,
                'corner_points': self.corner_points,
                'current_mode': self.current_mode}
        return data

    def clear_image_stacks(self):
        for i in range(self.image_file.n_channels):
            self.img_stacks.image_list[i].clear()

        valid_keys = ['img-overlay', 'overlay_contour', 'img-mask', 'circle_follow', 'lasso_path', 'img-virus',
                      'img-contour', 'img-probe', 'img-cells', 'img-blob', 'img-drawing', 'img-slice']

        for da_key in valid_keys:
            self.img_stacks.image_dict[da_key].clear()

    # def clear_curve_widget(self):




