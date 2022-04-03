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

from image_stacks import ImageStacks
from image_curves import CurveWidget, ChannelSelector
from uuuuuu import hsv2rgb, gamma_line, color_img, make_color_lut, get_corner_line_from_rect


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
        # QWidget.__init__(self)
        QObject.__init__(self)

        # define the initials
        self.image_file = None
        self.current_img = None
        self.img_size = None
        self.tb_size = None
        self.adding_allowed = False
        self.line_kind = 'gamma'
        self.channel_tables = []
        self.channel_points = []
        self.color_lut_list = []
        self.scene_index = 0
        self.max_num_channels = 4
        self.channel_visible = [False, False, False, False]
        self.channel_color = [None, None, None, None]

        self.table = None
        self.signal_block = False

        self.side_lines = None
        self.corner_points = None

        self.current_mode = 'gray'

        # make empty space taker, width 300 according to width of sidebar
        space_item = QSpacerItem(300, 10, QSizePolicy.Expanding)

        # scene control
        self.check_scenes = QPushButton('Load ALL Scenes')
        self.check_scenes.setCheckable(True)
        self.scene_slider = QSlider(Qt.Horizontal)
        self.scene_slider.setMinimum(0)
        self.scene_slider.setValue(0)
        self.scene_slider.valueChanged.connect(self.scene_index_changed)
        self.scene_label = QLabel('0/ 0')
        self.scene_wrap = QFrame()
        scene_wrap_layout = QHBoxLayout(self.scene_wrap)
        # scene_wrap_layout.setContentsMargins(0, 0, 0, 0)
        # scene_wrap_layout.setSpacing(0)
        scene_wrap_layout.addWidget(QLabel('Scene: '))
        scene_wrap_layout.addWidget(self.scene_slider)
        scene_wrap_layout.addWidget(self.scene_label, alignment=Qt.AlignRight)
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
        scale_wrap_layout = QHBoxLayout(self.scale_wrap)
        # scale_wrap_layout.setContentsMargins(0, 0, 0, 0)
        # scale_wrap_layout.setSpacing(0)
        scale_wrap_layout.addWidget(QLabel('Scale: '))
        scale_wrap_layout.addWidget(self.scale_slider)
        scale_wrap_layout.addWidget(self.scale_label, alignment=Qt.AlignRight)

        # image stacks
        self.img_stacks = ImageStacks()

        # curve widget
        self.curve_widget = CurveWidget()
        self.curve_widget.setFixedHeight(280)
        self.curve_widget.sig_table_changed.connect(self.image_curve_changed)
        # self.curve_widget.sig_line_changed.connect(self.image_curve_type_changed)
        # self.curve_widget.sig_reset.connect(self.image_curve_reset)
        self.curve_widget.setEnabled(False)

        # channel buttons
        self.chn_widget_wrap = QFrame()
        self.chn_widget_wrap.setStyleSheet('QFrame{border: 1px solid #747a80; border-radius: 5px;}')
        chn_widget_layout = QHBoxLayout(self.chn_widget_wrap)
        self.chn_widget_list = []
        for i in range(self.max_num_channels):
            self.chn_widget_list.append(ChannelSelector())
            self.chn_widget_list[i].set_channel_index(i)
            self.chn_widget_list[i].sig_vis_channels.connect(self.set_channel_visible)
            self.chn_widget_list[i].sig_change_color.connect(self.channel_color_changed)
            chn_widget_layout.addWidget(self.chn_widget_list[i])
            self.chn_widget_list[i].setVisible(False)
        self.chn_widget_wrap.setVisible(False)

        # outer_outer_layout = QHBoxLayout()
        self.outer_frame = QFrame()
        outer_layout = QVBoxLayout(self.outer_frame)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)
        outer_layout.addWidget(self.check_scenes)
        outer_layout.addWidget(self.scale_wrap)
        outer_layout.addWidget(self.scene_wrap)
        outer_layout.addWidget(self.curve_widget)
        outer_layout.addSpacerItem(space_item)
        outer_layout.addWidget(self.chn_widget_wrap)

    def set_data(self, image_file):
        if self.image_file is not None:
            if not self.image_file.is_rgb:
                for i in range(self.image_file.n_channels):
                    self.chn_widget_list[i].delete_item()
                    self.channel_visible[i] = False
                    self.img_stacks.image_list[i].setVisible(False)
            for i in range(self.image_file.n_channels):
                self.channel_color[i] = None
            self.current_mode = 'gray'

        self.image_file = image_file

        scene_ind = self.scene_slider.value()

        self.current_img = copy.deepcopy(self.image_file.data['scene {}'.format(scene_ind)])
        if self.image_file.is_rgb:
            self.current_mode = 'rgb'
            self.current_img = cv2.cvtColor(self.current_img, cv2.COLOR_BGR2RGB)
        self.img_size = self.current_img.shape[:2]
        self.img_stacks.tri_pnts.set_range(self.img_size[1], self.img_size[0])

        scale_factor = np.max(np.ravel(self.img_size) / 80)
        self.tb_size = (int(self.img_size[1] / scale_factor), int(self.img_size[0] / scale_factor))
        print('tb_size', self.tb_size)

        for i in range(self.max_num_channels):
            self.chn_widget_list[i].setVisible(False)

        if self.image_file.n_scenes != 1:
            self.scene_slider.setMaximum(self.image_file.n_scenes-1)
            self.scene_label.setText('0/{}'.format(self.image_file.n_scenes-1))
            self.scene_wrap.setVisible(True)
        else:
            self.scene_wrap.setVisible(False)

        if self.image_file.is_czi:
            self.scale_wrap.setVisible(True)

        # set color and names to channels
        if self.image_file.is_rgb:
            self.chn_widget_wrap.setVisible(False)
        else:
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

        # set data to curves
        self.curve_widget.setEnabled(True)
        self.curve_widget.set_data(self.current_img, self.image_file.rgb_colors, self.image_file.level,
                                   self.image_file.data_type)

        # set data to image stacks
        print(self.current_img.shape)
        print(np.max(self.current_img), np.min(self.current_img))
        self.img_stacks.set_data(self.current_img, self.image_file.is_rgb)
        self.img_stacks.set_lut(self.color_lut_list, self.image_file.is_rgb)
        self.get_corner_and_lines()

    def scene_index_changed(self):
        scene_index = self.scene_slider.value()
        self.scene_label.setText('{}/{}'.format(scene_index, self.image_file.n_scenes-1))
        if self.image_file is None:
            return
        self.current_mode = 'gray'
        with pg.BusyCursor():
            if 'scene {}'.format(scene_index) not in self.image_file.data.keys():
                if self.image_file.is_czi:
                    scale = self.scale_slider.value()
                    scale_val = scale * 0.01
                    self.image_file.read_data(scale_val, scene_index=scene_index)
                else:
                    print('not czi files')
            self.current_img = copy.deepcopy(self.image_file.data['scene {}'.format(scene_index)])
            if self.image_file.is_rgb:
                self.current_mode = 'rgb'
                self.current_img = cv2.cvtColor(self.current_img, cv2.COLOR_BGR2RGB)
            self.img_size = self.current_img.shape[:2]
            self.img_stacks.tri_pnts.set_range(self.img_size[1], self.img_size[0])
            self.img_stacks.set_data(self.current_img, self.image_file.is_rgb)
            self.img_stacks.set_lut(self.color_lut_list, self.image_file.is_rgb)
            self.get_corner_and_lines()



            # for i in range(self.image_file.n_channels):
            #     self.chn_widget_list[i].color_combo.setCurrentIndex(len(self.channel_color)-1)

            # shp = self.current_img.shape[:2]
            # scale_factor = np.max(shp / 80)
            # self.tb_size = np.floor(shp / scale_factor).astype(self.image_file.data_type)

    def get_corner_and_lines(self):
        rect = (0, 0, self.img_size[1], self.img_size[0])
        self.corner_points, self.side_lines = get_corner_line_from_rect(rect)
        self.sig_image_changed.emit()

    def _set_data_to_img_stacks(self):
        self.img_stacks.set_data(self.current_img, self.image_file.is_rgb)
        self.img_stacks.set_lut(self.color_lut_list, self.image_file.is_rgb)

    def scale_value_changed(self):
        scale = self.scale_slider.value()
        self.scale_label.setText('{}%'.format(scale))

    def scale_slider_released(self):
        scale = self.scale_slider.value()
        scale_val = scale * 0.01
        scene_index = self.scene_slider.value()
        if self.image_file is None:
            return
        self.current_mode = 'gray'
        if self.image_file.is_czi:
            with pg.BusyCursor():
                self.image_file.read_data(scale_val, scene_index)
                self.current_img = copy.deepcopy(self.image_file.data['scene %d' % scene_index])
                if self.image_file.is_rgb:
                    self.current_mode = 'rgb'
                    self.current_img = cv2.cvtColor(self.current_img, cv2.COLOR_BGR2RGB)
                self.img_size = self.current_img.shape[:2]
                self.img_stacks.tri_pnts.set_range(self.img_size[1], self.img_size[0])
                self._set_data_to_img_stacks()
                self.get_corner_and_lines()


    def channel_color_changed(self, col, ind):
        print(col)
        da_lut = make_color_lut(col)
        self.img_stacks.image_list[ind].setLookupTable(da_lut)
        self.color_lut_list[ind] = da_lut
        self.channel_color[ind] = col
        self.curve_widget.curve_plot.change_hist_color(col, ind)

    def set_channel_visible(self, vis, ind):
        self.channel_visible[ind] = vis
        if vis:
            self.img_stacks.image_list[ind].setOpts(opacity=1)
        else:
            self.img_stacks.image_list[ind].setOpts(opacity=0)

    def image_curve_changed(self, table):
        if self.image_file is None:
            return
        scene_index = self.scene_slider.value()
        da_img = copy.deepcopy(self.image_file.data['scene %d' % scene_index])
        if self.image_file.is_rgb:
            da_img = cv2.LUT(self.current_img, table.astype("uint8"))
            self.img_stacks.image_list[0].setImage(da_img)
        else:
            for i in range(self.image_file.n_channels):
                if self.channel_visible[i]:
                    lut_in = self.color_lut_list[i].copy()
                    lut_out = lut_in[table.astype("uint16"), :]
                    self.img_stacks.image_list[i].setLookupTable(lut_out)

    def image_curve_type_changed(self):
        """
        signal function after change line type
        set to the original 2 points linear type
        """
        if self.image_file.is_rgb:
            print('curve type changed for rgb image')
        else:
            for i in range(self.image_file.n_channels):
                self.img_stacks.image_list[i].setLookupTable(self.color_lut_list[i])

    def image_curve_reset(self):
        """
        signal function after press button 'Reset'
        """
        original_hsv_list = self.image_file.hsv_colors.copy()
        self.channel_color = original_hsv_list
        for i in range(self.image_file.n_channels):
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
        if self.image_file.is_rgb:
            print('rgb image')
        else:
            for i in range(self.image_file.n_channels):
                self.current_img[:, :, i] = cv2.flip(self.current_img[:, :, i], 0)
            self.img_size = self.current_img.shape[:2]
            self.img_stacks.tri_pnts.set_range(self.img_size[1], self.img_size[0])
        self.img_stacks.set_data(self.current_img)

    #
    def image_horizon_flip(self):
        if self.image_file is None:
            return
        if self.image_file.is_rgb:
            print('rgb image')
        else:
            for i in range(self.image_file.n_channels):
                self.current_img[:, :, i] = cv2.flip(self.current_img[:, :, i], 1)
            self.img_size = self.current_img.shape[:2]
            self.img_stacks.tri_pnts.set_range(self.img_size[1], self.img_size[0])
        self.img_stacks.set_data(self.current_img)

    def image_90_rotate(self):
        if self.image_file is None:
            return
        scene_index = self.scene_slider.value()
        if self.image_file.is_rgb:
            print('rgb image')
        else:
            temp = []
            for i in range(self.image_file.n_channels):
                self.img_stacks.image_list[i].clear()
                temp.append(cv2.rotate(self.current_img[:, :, i], cv2.ROTATE_90_CLOCKWISE))
            self.current_img = np.dstack(temp)
            self.img_size = self.current_img.shape[:2]
            self.img_stacks.tri_pnts.set_range(self.img_size[1], self.img_size[0])
        self.img_stacks.set_data(self.current_img)
        self.get_corner_and_lines()
        self.image_file.data['scene %d' % scene_index] = self.current_img.copy()
        self.tb_size = np.flip(self.tb_size, 0)

    def image_180_rotate(self):
        if self.image_file is None:
            return
        if self.image_file.is_rgb:
            self.current_img = cv2.rotate(self.current_img, cv2.ROTATE_180)
        else:
            temp = []
            for i in range(self.image_file.n_channels):
                self.img_stacks.image_list[i].clear()
                temp.append(cv2.rotate(self.current_img[:, :, i], cv2.ROTATE_180))
            self.current_img = np.dstack(temp)
            self.img_size = self.current_img.shape[:2]
            self.img_stacks.tri_pnts.set_range(self.img_size[1], self.img_size[0])
        self.img_stacks.set_data(self.current_img)

    def image_90_counter_rotate(self):
        if self.image_file is None:
            return
        if self.image_file.is_rgb:
            print('rgb image')
        else:
            temp = []
            for i in range(self.image_file.n_channels):
                self.img_stacks.image_list[i].clear()
                temp.append(cv2.rotate(self.current_img[:, :, i], cv2.ROTATE_90_COUNTERCLOCKWISE))
            self.current_img = np.dstack(temp)
            self.img_size = self.current_img.shape[:2]
            self.img_stacks.tri_pnts.set_range(self.img_size[1], self.img_size[0])
        self.img_stacks.set_data(self.current_img)
        self.get_corner_and_lines()
        self.tb_size = np.flip(self.tb_size, 0)

    # mode change
    def image_mode_changed(self, mode):
        if self.image_file is None or not self.image_file.is_rgb:
            return
        temp = self.current_img.copy()
        if mode == 'gray':
            if self.current_mode != 'rgb':
                return
            da_img = cv2.cvtColor(temp, cv2.COLOR_RGB2GRAY)
        elif mode == 'hsv':
            if self.current_mode != 'rgb':
                return
            da_img = cv2.cvtColor(temp, cv2.COLOR_RGB2HSV)
        else:
            scene_ind = self.scene_slider.value()
            temp = copy.deepcopy(self.image_file.data['scene {}'.format(scene_ind)])
            da_img = cv2.cvtColor(temp, cv2.COLOR_BGR2RGB)
        self.current_img = da_img.copy()
        self.img_stacks.set_data(self.current_img, is_rgb=True)
        self.current_mode = mode

    def hide_original_image(self):
        if self.image_file is None or not self.image_file.is_rgb:
            return
        self.img_stacks.image_list[0].setVisible(False)

    def show_original_image(self):
        if self.image_file is None or not self.image_file.is_rgb:
            return
        self.img_stacks.image_list[0].setVisible(True)


