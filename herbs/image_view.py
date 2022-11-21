import colorsys
import os
import sys

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
from .widgets_utils import ChannelSelector
from .image_curves import CurveWidget
from .uuuuuu import hsv2rgb, gamma_line, color_img, make_color_lut, get_corner_line_from_rect, \
    rotate, rotate_bound, get_tb_size, read_qss_file


class ImagePageController(QWidget):
    class SignalProxy(QObject):
        sigPageChanged = pyqtSignal(object)

    def __init__(self):
        self._sigprox = ImagePageController.SignalProxy()
        self.sig_page_changed = self._sigprox.sigPageChanged

        QWidget.__init__(self)

        # self.setStyleSheet(page_control_style)

        self.max_val = None

        self.page_slider = QSlider(Qt.Horizontal)
        self.page_slider.setMinimum(0)
        self.page_slider.valueChanged.connect(self.slider_value_changed)

        self.page_label = QLabel()
        self.page_label.setFixedSize(50, 20)

        self.page_left_btn = QPushButton()
        self.page_left_btn.setIcon(QIcon("icons/backward.svg"))
        self.page_left_btn.setIconSize(QSize(16, 16))
        self.page_left_btn.clicked.connect(self.left_btn_clicked)

        self.page_right_btn = QPushButton()
        self.page_right_btn.setIcon(QIcon("icons/forward.svg"))
        self.page_right_btn.setIconSize(QSize(16, 16))
        self.page_right_btn.clicked.connect(self.right_btn_clicked)

        page_ctrl_layout = QHBoxLayout()
        page_ctrl_layout.setSpacing(0)
        page_ctrl_layout.setContentsMargins(10, 5, 10, 5)
        page_ctrl_layout.addWidget(self.page_left_btn)
        page_ctrl_layout.addSpacing(10)
        page_ctrl_layout.addWidget(self.page_slider)
        page_ctrl_layout.addSpacing(5)
        page_ctrl_layout.addWidget(self.page_label)
        page_ctrl_layout.addWidget(self.page_right_btn)

        self.setLayout(page_ctrl_layout)

    def set_val(self, val):
        self.page_slider.setValue(val)

    def set_max(self, val):
        self.max_val = val
        self.page_slider.setMaximum(val)

    def slider_value_changed(self):
        val = self.page_slider.value()
        self.page_label.setText(str(val))
        self.sig_page_changed.emit(val)

    def left_btn_clicked(self):
        val = self.page_slider.value() - 1
        if val < 0:
            val = 0
        self.set_val(val)

    def right_btn_clicked(self):
        val = self.page_slider.value() + 1
        if val > self.max_val:
            val = self.max_val
        self.set_val(val)


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
        self.processing_img = None
        self.current_img = None
        self.current_scale = None
        self.img_size = None
        self.tb_size = None
        self.color_lut_list = []
        self.original_lut_list = []
        self.scene_index = 0
        self.max_num_channels = 4
        self.channel_visible = [False, False, False, False]
        self.channel_color = [None, None, None, None]
        self.color_combo_index = [-1, -1, -1, -1]

        self.side_lines = None
        self.corner_points = None
        self.volume_img = None
        self.display_img_index = 0

        # scene control
        sidebar_button_style = read_qss_file('qss/side_bar.qss')
        self.check_scenes = QPushButton('Load ALL Scenes')
        self.check_scenes.setStyleSheet(sidebar_button_style)
        self.check_scenes.setCheckable(True)
        self.scene_slider = QSlider(Qt.Horizontal)
        self.scene_slider.setMinimum(0)
        self.scene_slider.setValue(0)
        self.scene_slider.setTickPosition(QSlider.TicksBelow)
        self.scene_slider.setTickInterval(1)
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
        scale_wrap_layout = QHBoxLayout(self.scale_wrap)
        scale_wrap_layout.addWidget(QLabel('Scale: '))
        scale_wrap_layout.addWidget(self.scale_slider)
        scale_wrap_layout.addWidget(self.scale_label)

        # image stacks
        self.img_stacks = ImageStacks()

        # scene control
        self.page_ctrl = ImagePageController()
        self.page_ctrl.setVisible(False)
        self.page_ctrl.sig_page_changed.connect(self.image_page_changed)

        # curve widget
        self.curve_widget = CurveWidget()
        self.curve_widget.setEnabled(False)
        self.curve_widget.setFixedHeight(280)
        self.curve_widget.sig_table_changed.connect(self.image_curve_changed)
        self.curve_widget.sig_reset.connect(self.image_curve_reset)
        self.curve_widget.sig_line_type_changed.connect(self.image_curve_type_changed)

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
        # self.chn_widget_wrap.setVisible(False)

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
            self.page_ctrl.setVisible(False)
            self.clear_image_stacks()
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
            self.color_lut_list.clear()
            self.original_lut_list.clear()
            self.curve_widget.line_type_combo.setCurrentIndex(0)

        self.image_file = image_file

        if self.image_file.n_pages > 1:
            self.page_ctrl.set_max(self.image_file.n_pages - 1)
            self.page_ctrl.setVisible(True)
            self.volume_img = copy.deepcopy(self.image_file.data['scene 0'])
            init_page_number = int(0.5 * self.image_file.n_pages)
            self.page_ctrl.set_val(init_page_number)
            temp_data = self.volume_img[init_page_number, :, :].copy()
            temp_data = [temp_data]
            self.current_img = np.dstack(temp_data)
        else:
            self.volume_img = None
            self.current_img = copy.deepcopy(self.image_file.data['scene 0'])

        self.current_scale = self.image_file.scale['scene 0']

        if self.image_file.n_scenes != 1:
            self.scene_slider.setMaximum(self.image_file.n_scenes - 1)
            self.scene_label.setText('1/{}'.format(self.image_file.n_scenes))
            self.scene_wrap.setVisible(True)
        else:
            self.scene_wrap.setVisible(False)

        if not self.image_file.is_czi:
            self.scale_wrap.setVisible(False)
        else:
            self.scale_wrap.setVisible(True)

        # set data to curves
        self.set_curve_widgets()  # get reasonable table
        self.set_channel_widgets()  # get initial color_lut_list for each layer

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
            da_lut = make_color_lut(da_hsv_color, self.image_file.level + 1)
            self.original_lut_list.append(da_lut)
            self.color_lut_list.append(da_lut)
            self.chn_widget_list[i].setVisible(True)
            self.chn_widget_list[i].vis_btn.setText(self.image_file.channel_name[i])
            self.chn_widget_list[i].add_item(self.channel_color[i])
            self.channel_visible[i] = True
            self.color_combo_index[i] = self.chn_widget_list[i].color_combo.currentIndex()

    def set_curve_widgets(self):
        self.curve_widget.setEnabled(True)
        img_layers = self.current_img.copy()
        self.curve_widget.set_data(img_layers, self.image_file.rgb_colors, self.image_file.level)

    def channel_color_changed(self, col, ind):
        da_lut = make_color_lut(col, self.curve_widget.gray_max + 1)
        self.original_lut_list[ind] = da_lut.copy()
        self.color_lut_list[ind] = da_lut[self.curve_widget.table_output[ind], :]
        self.img_stacks.image_list[ind].setLevels(levels=(0, self.image_file.level))
        self.img_stacks.image_list[ind].setLookupTable(self.color_lut_list[ind])
        self.channel_color[ind] = col
        self.curve_widget.curve_plot.change_hist_color(col, ind)
        self.color_combo_index[ind] = self.chn_widget_list[ind].color_combo.currentIndex()

    def set_channel_visible(self, vis, ind):
        if np.sum(self.channel_visible) == 1:
            vis_layer_ind = np.where(np.ravel(self.channel_visible))[0][0]
            if vis_layer_ind == ind:
                return
        self.channel_visible[ind] = vis
        self.img_stacks.image_list[ind].setVisible(vis)
        self.curve_widget.set_channel_enable(ind, vis)

    def channel_selector_reset(self):
        for i in range(self.image_file.n_channels):
            self.chn_widget_list[i].vis_btn.setChecked(False)
            self.chn_widget_list[i].vis = True
            self.chn_widget_list[i].set_checked(False)

    def set_data_and_size(self, img_data):
        self.img_stacks.set_data(img_data)
        self.img_size = img_data.shape[:2]
        print('image_view', self.img_size)
        rect = (0, 0, self.img_size[1], self.img_size[0])
        self.corner_points, self.side_lines = get_corner_line_from_rect(rect)
        self.img_stacks.image_dict['tri_pnts'].set_range(self.img_size[1], self.img_size[0])
        self.tb_size = get_tb_size(self.img_size)

    def set_data_to_img_stacks(self):
        self.set_data_and_size(self.current_img)
        self.img_stacks.set_lut(self.color_lut_list, self.curve_widget.gray_max)

    def get_corner_and_lines(self):
        rect = (0, 0, self.img_size[1], self.img_size[0])
        self.corner_points, self.side_lines = get_corner_line_from_rect(rect)
        self.sig_image_changed.emit()

    def image_page_changed(self, page_number):
        self.display_img_index = page_number
        temp_data = self.volume_img[page_number, :, :].copy()
        temp_data = [temp_data]
        self.current_img = np.dstack(temp_data)
        self.img_stacks.set_data(self.current_img)

    def scene_index_changed(self):
        if self.image_file is None:
            return
        scene_index = self.scene_slider.value()
        self.scene_label.setText('{}/{}'.format(scene_index + 1, self.image_file.n_scenes))
        with pg.BusyCursor():
            self.clear_image_stacks()
            if 'scene {}'.format(scene_index) not in list(self.image_file.data.keys()):
                scale = self.scale_slider.value()
                scale_val = scale * 0.01
                self.image_file.read_data(scale_val, scene_index=scene_index)
            self.current_img = copy.deepcopy(self.image_file.data['scene {}'.format(scene_index)])
            self.current_scale = self.image_file.scale['scene {}'.format(scene_index)]

            if self.current_scale != self.scale_slider.value() * 0.01:
                self.scale_slider.setValue(self.current_scale * 100)

            self.img_size = self.current_img.shape[:2]
            for i in range(self.image_file.n_channels):
                self.img_stacks.image_list[i].clear()
            self.img_stacks.image_dict['tri_pnts'].set_range(self.img_size[1], self.img_size[0])

            self.channel_selector_reset()
            self.curve_widget.curve_plot.reset_plot()

            self.img_stacks.set_data(self.current_img)
            self.img_stacks.set_lut(self.original_lut_list, self.image_file.level)
            self.get_corner_and_lines()
            self.set_curve_widgets()
            # reset gamma and channels and black/white slider

    def scale_value_changed(self):
        scale = self.scale_slider.value()
        self.scale_label.setText('{}%'.format(scale))

    def scale_slider_released(self):
        if self.image_file is None:
            return
        if self.image_file.is_czi:
            self.clear_image_stacks()
            scale = self.scale_slider.value()
            scale_val = scale * 0.01
            scene_index = self.scene_slider.value()
            with pg.BusyCursor():
                self.image_file.read_data(scale_val, scene_index)
                self.current_img = copy.deepcopy(self.image_file.data['scene %d' % scene_index])
                self.current_scale = self.image_file.scale['scene {}'.format(scene_index)]

                self.img_size = self.current_img.shape[:2]
                for i in range(self.image_file.n_channels):
                    self.img_stacks.image_list[i].clear()
                self.img_stacks.image_dict['tri_pnts'].set_range(self.img_size[1], self.img_size[0])
                self.set_data_to_img_stacks()
                self.get_corner_and_lines()

    def image_curve_changed(self, ev):
        if self.current_img is None:
            return
        table = ev[0]
        ind = ev[1]
        lut_in = self.original_lut_list[ind].copy()
        self.color_lut_list[ind] = lut_in[table, :]
        self.img_stacks.image_list[ind].setLookupTable(self.color_lut_list[ind])
        # table = table.astype(int)
        # if self.image_file.pixel_type == 'rgb24':
        #     da_img = cv2.LUT(self.current_img.astype('uint8'), table)
        #     self.img_stacks.set_data(da_img)
        # else:
        #     for i in range(self.image_file.n_channels):
        #         if self.channel_visible[i]:
        #             lut_in = self.color_lut_list[i].copy()
        #             self.color_lut_list[i] = lut_in[table, :]
        #             self.img_stacks.image_list[i].setLookupTable(self.color_lut_list[i])

    def image_curve_type_changed(self):
        """
        signal function after change line type
        set to the original 2 points linear type
        """
        if self.image_file is None:
            return
        for i in range(self.image_file.n_channels):
            self.img_stacks.image_list[i].setLookupTable(self.original_lut_list[i])

    def image_curve_reset(self):
        """
        signal function after press button 'Reset'
        """
        for i in range(self.image_file.n_channels):
            self.channel_color[i] = self.image_file.hsv_colors[i]
        for i in range(self.image_file.n_channels):
            self.chn_widget_list[i].color_combo.setCurrentIndex(
                len(self.chn_widget_list[i].color_combo.hsv_color_list) - 1)
            self.curve_widget.curve_plot.change_hist_color(self.channel_color[i], i)
            self.img_stacks.image_list[i].setLookupTable(self.original_lut_list[i])
        self.color_lut_list = self.original_lut_list.copy()

    def get_img_ctrl_data(self):
        lut_points_data = []
        for i in range(self.current_img.shape[2]):
            lut_points_data.append(self.curve_widget.curve_plot.lut_points[i].data['pos'].copy())

        data = {'current_img': self.current_img,
                'processing_img': self.processing_img,
                'current_scene': self.scene_slider.value(),
                'current_scale': self.scale_slider.value(),
                'channel_color': self.channel_color,
                'color_combo_index': self.color_combo_index,
                'original_lut_list': self.original_lut_list,
                'color_lut_list': self.color_lut_list,
                'gamma_vals': self.curve_widget.gamma,
                'table_output': self.curve_widget.table_output,
                'original_table': self.curve_widget.original_table,
                'line_type': self.curve_widget.line_type,
                'hist_data': self.curve_widget.curve_plot.hist_data,
                'lut_points_data': lut_points_data}
        return data

    def load_img_ctrl_data(self, img_ctrl_data):
        self.current_img = img_ctrl_data['current_img']
        self.current_scale = img_ctrl_data['current_scale']
        self.channel_color = img_ctrl_data['channel_color']
        self.color_combo_index = img_ctrl_data['color_combo_index']
        self.processing_img = img_ctrl_data['processing_img']
        # set data
        # self.scene_wrap.setVisible(False)

        self.scene_slider.blockSignals(True)
        self.scene_slider.setValue(img_ctrl_data['current_scene'])
        self.scene_label.setText('{}/{}'.format(img_ctrl_data['current_scene'] + 1, self.image_file.n_scenes))
        self.scene_slider.blockSignals(False)

        self.curve_widget.gamma = img_ctrl_data['gamma_vals']
        self.curve_widget.table_output = img_ctrl_data['table_output']
        self.curve_widget.original_table = img_ctrl_data['original_table']
        self.curve_widget.line_type = img_ctrl_data['line_type']

        self.curve_widget.line_type_combo.blockSignals(True)
        self.curve_widget.line_type_combo.setCurrentText(self.curve_widget.line_type)
        self.curve_widget.line_type_combo.blockSignals(False)

        self.curve_widget.curve_plot.line_type = self.curve_widget.line_type
        self.curve_widget.curve_plot.set_data(img_ctrl_data['hist_data'], self.image_file.rgb_colors,
                                              self.image_file.level)

        for i in range(self.image_file.n_channels):
            self.curve_widget.curve_plot.change_hist_color(self.channel_color[i], i)
            self.curve_widget.curve_plot.set_lut_line(self.curve_widget.table_output[i], i)
            self.curve_widget.curve_plot.set_lut_points(img_ctrl_data['lut_points_data'][i], i)

        for i in range(self.image_file.n_channels):
            self.curve_widget.curve_plot.set_enable(i, True)
        self.curve_widget.set_enable_induced_slider()

        self.original_lut_list = img_ctrl_data['original_lut_list']
        self.color_lut_list = img_ctrl_data['color_lut_list']

        for i in range(self.image_file.n_channels):
            self.chn_widget_list[i].blockSignals(True)
            self.chn_widget_list[i].setVisible(True)
            self.chn_widget_list[i].vis_btn.setChecked(False)
            self.chn_widget_list[i].set_checked(False)
            self.chn_widget_list[i].vis_btn.setText(self.image_file.channel_name[i])
            self.chn_widget_list[i].color_combo.blockSignals(True)
            self.chn_widget_list[i].add_item(self.image_file.hsv_colors[i])
            self.chn_widget_list[i].color_combo.setCurrentIndex(self.color_combo_index[i])
            self.chn_widget_list[i].color_combo.blockSignals(False)
            self.channel_visible[i] = True
            self.chn_widget_list[i].blockSignals(False)

        self.original_lut_list = img_ctrl_data['original_lut_list']
        self.color_lut_list = img_ctrl_data['color_lut_list']

        # self.set_data_and_size(self.processing_img)

    #
    def check_img_process_layer_data(self, layer_dict):
        valid_keys = list(layer_dict.keys())
        check_res = True
        if not np.all(['data', 'level', 'size'] in valid_keys):
            check_res = False
        if not np.all(layer_dict['size'] == self.image_view.current_img.shape[:2]):
            check_res = False
        if layer_dict['level'] != self.image_file.level:
            check_res = False
        return check_res

    def has_loaded_layer_the_same_size(self, layer_dict):
        check_res = True
        if not np.all(layer_dict['data'].shape[:2] == self.image_view.current_img.shape[:2]):
            check_res = False
        return check_res

    def save_img_process_data(self):
        data = {'data': self.processing_img,
                'level': self.image_file.level,
                'size': self.img_size}
        return data

    # clear image stacks
    def clear_image_stacks(self):
        valid_keys = ['img-overlay', 'overlay_contour', 'img-mask', 'circle_follow', 'lasso_path', 'img-virus',
                      'img-contour', 'img-probe', 'img-cells', 'img-blob', 'img-drawing']

        for da_key in valid_keys:
            self.img_stacks.image_dict[da_key].clear()

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

    # def clear_curve_widget(self):




