import os
import sys
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from pyqtgraph.Qt import QtGui, QtCore

from qtrangeslider import QRangeSlider
import scipy.interpolate
# from scipy.interpolate import interp1d

import cv2

from .image_stacks import ImageStacks
from .image_reader import ImageReader
from .uuuuuu import hsv2rgb, gamma_line, get_qhsv_from_czi_hsv, make_hist_data, read_qss_file
from .widgets_utils import BWSpin, GammaSpin
from .movable_points import MovablePoints


reset_button_style = '''
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

'''


class CurvesPlot(pg.PlotWidget):
    class SignalProxy(QObject):
        sigLineChange = pyqtSignal(object)
        sigBoundChange = pyqtSignal()

    def __init__(self, parent=None, background='w'):
        self._sigprox = CurvesPlot.SignalProxy()
        self.sig_line_change = self._sigprox.sigLineChange
        self.sig_spin_max_change = self._sigprox.sigBoundChange

        pg.PlotWidget.__init__(self)
        self.setBackground('w')
        self.plotItem.vb.setMouseEnabled(x=False, y=False)
        self.getPlotItem().hideAxis('bottom')
        self.getPlotItem().hideAxis('left')

        self.scene().sigMouseMoved.connect(self.on_mouse_moved)
        self.scene().sigMouseClicked.connect(self.on_mouse_clicked)

        self.adding_allowed = False
        self.enable_channel = [False, False, False, False]
        self.line_type = 'gamma'
        self.depth_level = 65535
        self.start_point = [np.array([0, 0]) for i in range(4)]
        self.end_point = [np.array([self.depth_level, self.depth_level]) for i in range(4)]
        self.table_input = np.arange(self.depth_level + 1)
        self.hist_data = None
        self.active_index = None

        self.inactive_pen = pg.mkPen(QColor(128, 128, 128, 255), width=3)
        self.inactive_brush = QColor(128, 128, 128, 10)

        self.active_pen = []
        self.active_brush = []

        self.hist_list = []
        self.lut_line = []
        self.lut_points = []
        for i in range(4):
            self.hist_list.append(pg.PlotDataItem())
            self.lut_line.append(pg.PlotCurveItem(fillLevel=None))
            self.lut_points.append(MovablePoints())
            self.lut_points[i].mouseDragged.connect(self.on_mouse_dragged)

        for i in range(4):
            self.addItem(self.hist_list[i])
        for i in range(4):
            self.addItem(self.lut_line[i])
            self.lut_line[i].setVisible(False)
        for i in range(4):
            self.addItem(self.lut_points[i])
            self.lut_points[i].setVisible(False)

    def set_data(self, hist_data, color, depth_level):
        """
        Set data to curve Plot view, only called once there load new data
        :param hist_data: grayscale image data for one scene
        :param color: list of rgb [0, 255] for each channel
        :param depth_level: gray intensity level
        :return: None
        """
        if self.hist_data is not None:
            for i in range(4):
                self.hist_list[i].clear()
                self.lut_line[i].clear()
                self.lut_points[i]. clear()
            self.hist_data = None

        if self.depth_level != depth_level:
            self.start_point = [np.array([0, 0]) for i in range(4)]
            self.end_point = [np.array([depth_level, depth_level]) for i in range(4)]
            self.table_input = np.arange(0, depth_level + 1)
            self.depth_level = depth_level

        self.hist_data = hist_data.copy()

        self.plotItem.vb.setRange(xRange=[0, depth_level], yRange=[0, depth_level])

        for i in range(len(self.hist_data)):
            self.enable_channel[i] = True
            self.active_pen.append(pg.mkPen(QColor(color[i][0], color[i][1], color[i][2], 255), width=3))
            self.active_brush.append((color[i][0], color[i][1], color[i][2], 130))
            self.hist_list[i].setVisible(True)
            self.hist_list[i].setData(self.hist_data[i][0], self.hist_data[i][1],
                                      fillLevel=0, fillBrush=self.active_brush[i], pen=self.active_pen[i])
            self.start_point[i][0] = np.min(self.hist_data[i][0])
            self.end_point[i][0] = np.max(self.hist_data[i][0])

            self.set_original_lut_line(i)

            self.lut_points[i].setData(pos=np.vstack([self.start_point[i], self.end_point[i]]))

    def set_original_lut_line(self, ind):
        line_x = np.array([self.start_point[ind][0], self.end_point[ind][0]])
        line_y = np.array([self.start_point[ind][1], self.end_point[ind][1]])
        self.lut_line[ind].setData(line_x, line_y)
        self.lut_line[ind].setPen(self.active_pen[ind])
        self.lut_line[ind].setVisible(True)

    def reset_plot(self):
        for i in range(len(self.hist_data)):
            self.set_original_lut_line(i)
            self.lut_points[i].setData(pos=np.vstack([self.start_point[i], self.end_point[i]]))

    def set_enable(self, ind, is_enable):
        self.enable_channel[ind] = is_enable
        if is_enable:
            self.hist_list[ind].setPen(self.active_pen[ind])
            self.hist_list[ind].setFillBrush(self.active_brush[ind])
            self.lut_line[ind].setPen(self.active_pen[ind])
        else:
            self.hist_list[ind].setPen(self.inactive_pen)
            self.hist_list[ind].setFillBrush(self.inactive_brush)
            self.lut_line[ind].setPen(self.inactive_pen)
        if np.sum(self.enable_channel) == 1 and self.line_type != 'gamma':
            self.active_index = np.where(self.enable_channel)[0][0]
            self.lut_points[self.active_index].setVisible(True)
        else:
            if self.active_index is not None:
                self.lut_points[self.active_index].setVisible(False)
            self.active_index = None

    def change_hist_color(self, color: tuple, ind: int):
        """
        :param color: (h [0, 1], s [0, 1], v [0, 1])
        :param ind: channel index
        :return: None
        """
        if not self.hist_data:
            return
        da_hsv = get_qhsv_from_czi_hsv(color)
        col = QColor.fromHsv(da_hsv[0], da_hsv[1], da_hsv[2], 255)
        self.active_pen[ind] = pg.mkPen(col, width=3)
        self.active_brush[ind] = QColor.fromHsv(da_hsv[0], da_hsv[1], da_hsv[2], 130)
        self.hist_list[ind].setFillBrush(self.active_brush[ind])
        self.hist_list[ind].setPen(self.active_pen[ind])
        self.lut_line[ind].setPen(self.active_pen[ind])

    def change_line_type(self, line_type):
        self.line_type = line_type
        self.reset_plot()

    def set_lut_line(self, table_output, ind):
        self.lut_line[ind].setData(self.table_input, table_output)

    def set_lut_points(self, point_data, ind):
        self.lut_points[ind].setData(pos=point_data)

    def set_plot(self, points, table):
        # self.pnts = points
        # self.table_output = table
        self.line.setData(self.table_input, table)
        self.points.setData(pos=points)

    def on_mouse_dragged(self, vec):
        if self.line_type == 'gamma' or self.active_index is None:
            return
        ind = vec[1]
        data = self.lut_points[self.active_index].data['pos']
        if ind in [0, len(data)-1]:
            return
        else:
            table_output = self.update_table(data)
            self.lut_line[self.active_index].setData(self.table_input, table_output)
        self.sig_line_change.emit((table_output.astype('int'), self.active_index))
        # self.pnts = data.copy()

    def on_mouse_clicked(self, event):
        if self.line_type == 'gamma' or self.active_index is None:
            return
        pnt = self.plotItem.vb.mapSceneToView(event.scenePos())
        data = self.lut_points[self.active_index].data['pos']
        if self.adding_allowed:
            x = pnt.x()
            y = pnt.y()
            temp = np.vstack([data, np.array([x, y])])
            sort_x = np.argsort(temp[:, 0])
            temp = temp[sort_x, :]
            self.lut_points[self.active_index].setData(pos=temp)
            table_output = self.update_table(temp)
            self.lut_line[self.active_index].setData(self.table_input, table_output)
            self.sig_line_change.emit((table_output.astype('int'), self.active_index))

    def on_mouse_moved(self, point):
        if self.line_type == 'gamma' or self.active_index is None:
            return
        pnts = self.plotItem.vb.mapSceneToView(point)
        data = self.lut_points[self.active_index].data['pos']
        sct = self.lut_points[self.active_index].scatter.pointsAt(pnts)
        if self.lut_line[self.active_index].mouseShape().contains(pnts):
            if len(sct) == 0:
                if data[0, 0] < pnts.x() < data[-1, 0]:
                    self.setCursor(Qt.CrossCursor)
                    self.adding_allowed = True
                else:
                    self.setCursor(Qt.ArrowCursor)
                    self.adding_allowed = False
            else:
                self.setCursor(Qt.OpenHandCursor)
                self.adding_allowed = False
        else:
            self.adding_allowed = False
            if len(sct) == 0:
                self.setCursor(Qt.ArrowCursor)
            else:
                self.setCursor(Qt.OpenHandCursor)

    def update_table(self, data):
        cind = np.logical_and(self.table_input >= data[0, 0], self.table_input <= data[-1, 0])
        temp_output = self.table_input.copy()
        if self.line_type == 'linear':
            line_func = scipy.interpolate.interp1d(data[:, 0], data[:, 1], kind='linear')
            temp_output[cind] = line_func(self.table_input[cind])
        else:
            if len(data) < 4:
                line_func = scipy.interpolate.interp1d(data[:, 0], data[:, 1], kind='linear')
                temp_output[cind] = line_func(self.table_input[cind])
            else:
                tck = scipy.interpolate.splrep(data[:, 0], data[:, 1], s=0)
                temp_output[cind] = scipy.interpolate.splev(self.table_input[cind], tck, der=0)

        temp_output[self.table_input <= data[0, 0]] = 0
        temp_output[self.table_input >= data[-1, 0]] = self.depth_level
        temp_output[temp_output <= 0] = 0
        temp_output[temp_output >= self.depth_level] = self.depth_level
        return temp_output


class CurveWidget(QWidget):
    class SignalProxy(QObject):
        sigTableChanged = pyqtSignal(object)
        sigReSet = pyqtSignal()
        sigLineTypeChanged = pyqtSignal()

    def __init__(self, parent=None):
        self._sigprox = CurveWidget.SignalProxy()
        self.sig_table_changed = self._sigprox.sigTableChanged
        self.sig_reset = self._sigprox.sigReSet
        self.sig_line_type_changed = self._sigprox.sigLineTypeChanged

        QWidget.__init__(self)

        self.gray_max = 65535
        self.gamma = [1, 1, 1, 1]
        self.n_channels = None
        self.table_output = []
        self.original_table = []

        self.current_black_val = 0
        self.current_white_val = self.gray_max
        self.current_width = self.gray_max
        self.vis_hist = True

        self.curve_plot = CurvesPlot()
        self.curve_plot.sig_line_change.connect(self.table_changed)
        # self.curve_plot.sigBoundChange.connect(self.spinbox_bound_changed)
        multi_handle_slider_style = read_qss_file('qss/multi_handle_slider.qss')
        self.multi_handle_slider = QRangeSlider(Qt.Horizontal)
        self.multi_handle_slider.setStyleSheet(multi_handle_slider_style)
        self.multi_handle_slider.setMinimum(0)
        self.multi_handle_slider.setMaximum(65535)
        self.multi_handle_slider.setValue((0, 65535))
        self.multi_handle_slider.setSingleStep(1.)
        self.multi_handle_slider.setBarVisible(False)
        self.multi_handle_slider.sliderMoved.connect(self.slider_changed)

        self.black_spinbox = BWSpin()
        self.black_spinbox.setFixedWidth(60)
        self.black_spinbox.spin_nam.setText('Black:')
        self.black_spinbox.spin_val.setMinimum(0)
        self.black_spinbox.spin_val.setMaximum(65535)
        self.black_spinbox.spin_val.setValue(0)
        self.black_spinbox.spin_val.valueChanged.connect(self.black_spinbox_changed)

        self.white_spinbox = BWSpin()
        self.white_spinbox.setFixedWidth(60)
        self.white_spinbox.spin_nam.setText('White:')
        self.white_spinbox.spin_val.setMinimum(0)
        self.white_spinbox.spin_val.setMaximum(65535)
        self.white_spinbox.spin_val.setValue(65535)
        self.white_spinbox.spin_val.valueChanged.connect(self.white_spinbox_changed)

        self.gamma_spinbox = GammaSpin()
        self.gamma_spinbox.setFixedWidth(60)
        self.gamma_spinbox.spin_nam.setText('Gamma:')
        self.gamma_spinbox.spin_val.setMinimum(0.01)
        self.gamma_spinbox.spin_val.setMaximum(16.00)
        self.gamma_spinbox.spin_val.setSingleStep(0.05)
        self.gamma_spinbox.spin_val.setValue(1.00)
        self.gamma_spinbox.spin_val.valueChanged.connect(self.gamma_spinbox_changed)

        self.reset_btn = QPushButton('Reset')
        self.reset_btn.setStyleSheet(reset_button_style)
        self.reset_btn.setFixedHeight(25)
        self.reset_btn.clicked.connect(self.reset_pressed)

        self.line_type_combo = QComboBox()
        self.line_type_combo.setFixedHeight(22)
        ltypes = ['gamma', 'linear', 'spline']
        self.line_type_combo.addItems(ltypes)
        self.line_type_combo.setCurrentText('gamma')
        self.line_type = 'gamma'
        self.line_type_combo.currentTextChanged.connect(self.line_type_changed)

        top_wrap = QFrame()
        top_layout = QGridLayout(top_wrap)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.addWidget(self.line_type_combo, 0, 0, 1, 1)
        top_layout.addWidget(self.reset_btn, 0, 1, 1, 1)

        bgw_wrap = QFrame()
        bgw_wrap_layout = QHBoxLayout(bgw_wrap)
        bgw_wrap_layout.setContentsMargins(0, 0, 0, 0)
        bgw_wrap_layout.addWidget(self.black_spinbox, alignment=Qt.AlignLeft)
        bgw_wrap_layout.addWidget(self.gamma_spinbox, alignment=Qt.AlignCenter)
        bgw_wrap_layout.addWidget(self.white_spinbox, alignment=Qt.AlignRight)

        slider_wrap = QFrame()
        slider_wrap_layout = QVBoxLayout(slider_wrap)
        slider_wrap_layout.setContentsMargins(0, 0, 0, 0)
        slider_wrap_layout.setSpacing(0)
        slider_wrap_layout.addWidget(self.multi_handle_slider)

        bottom_wrap = QFrame()
        bottom_layout = QVBoxLayout(bottom_wrap)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.addWidget(slider_wrap)
        bottom_layout.addWidget(bgw_wrap)

        widget_layout = QVBoxLayout()
        widget_layout.setContentsMargins(0, 0, 0, 0)
        widget_layout.addWidget(top_wrap)
        widget_layout.addWidget(self.curve_plot)
        widget_layout.addWidget(bottom_wrap)
        self.setLayout(widget_layout)

    def block_signal(self, is_clocked):
        self.multi_handle_slider.blockSignals(is_clocked)
        self.white_spinbox.spin_val.blockSignals(is_clocked)
        self.black_spinbox.spin_val.blockSignals(is_clocked)

    def set_data(self, data, color, depth_level):

        if self.table_output:
            self.table_output = []

        if self.gray_max != depth_level:
            self.gray_max = depth_level
            self.multi_handle_slider.setMaximum(depth_level)
            self.white_spinbox.spin_val.setMaximum(depth_level)

        self.n_channels = data.shape[2]

        hist_data = make_hist_data(data, depth_level)
        self.curve_plot.set_data(hist_data, color, depth_level)

        for i in range(self.n_channels):
            point_data = np.asarray([self.curve_plot.start_point[i], self.curve_plot.end_point[i]])
            table = self.get_table(point_data, i)
            self.table_output.append(table.astype(int))
        self.original_table = self.table_output.copy()

        self.set_original_to_slider()

    def set_original_to_slider(self):
        min_slider_val = np.min(np.asarray(self.curve_plot.start_point)[:self.n_channels, 0])
        max_slider_val = np.max(np.asarray(self.curve_plot.end_point)[:self.n_channels, 0])
        self.block_signal(True)
        self.multi_handle_slider.setValue((min_slider_val, max_slider_val))
        self.black_spinbox.spin_val.setValue(min_slider_val)
        self.white_spinbox.spin_val.setValue(max_slider_val)
        self.block_signal(False)
        self.current_black_val = min_slider_val
        self.current_white_val = max_slider_val
        self.current_width = max_slider_val - min_slider_val

    def slider_changed(self, ev):
        if self.curve_plot.hist_data is None:
            return
        # point_values = self.curve_plot.lut_points.data['pos'].copy()
        # point_values = point_values.astype(int)
        # self.black_spinbox.spin_val.setMaximum(point_values[1, 0] - 1)
        # self.white_spinbox.spin_val.setMinimum(point_values[-2, 0] + 1)
        val1 = int(ev[0])
        val2 = int(ev[1])

        if val1 != self.black_spinbox.spin_val.value():
            # if val1 >= point_values[1, 0]:
            #     val1 = point_values[1, 0] - 1
            #     self.multi_handle_slider.setValue((val1, val2))
            self.black_spinbox.spin_val.setValue(val1)
        if val2 != self.white_spinbox.spin_val.value():
            # if val2 <= point_values[-2, 0]:
            #     val2 = point_values[-2, 0] + 1
            #     self.multi_handle_slider.setValue((val1, val2))
            self.white_spinbox.spin_val.setValue(val2)

    def get_table(self, point_data, ind):
        xval = self.curve_plot.table_input
        if self.curve_plot.line_type == 'gamma':
            lims = (point_data[0, 0], point_data[-1, 0])
            table = gamma_line(xval, lims, self.gamma[ind], self.gray_max)
        else:
            table = self.curve_plot.update_table(point_data)
        return table

    def gamma_spinbox_changed(self):
        if self.line_type != 'gamma':
            return
        x_val = self.curve_plot.table_input
        for i in range(len(self.table_output)):
            if self.curve_plot.enable_channel[i]:
                self.gamma[i] = self.gamma_spinbox.spin_val.value()
                data = self.curve_plot.lut_points[i].data['pos'].copy()
                lims = (data[0, 0], data[-1, 0])
                table = gamma_line(x_val, lims, self.gamma[i], self.gray_max)
                self.table_output[i] = table.astype(int)
                self.curve_plot.set_lut_line(table, i)
                self.sig_table_changed.emit((self.table_output[i], i))

    def black_side_changed(self, diff_factor, ind):
        point_data = self.curve_plot.lut_points[ind].data['pos'].copy()
        da_width = point_data[-1, 0] - point_data[0, 0]
        dists = int(diff_factor * da_width)
        point_data[:-1, 0] = dists + point_data[:-1, 0]

        table = self.get_table(point_data, ind)
        self.table_output[ind] = table.astype(int)

        self.curve_plot.set_lut_points(point_data, ind)
        self.curve_plot.set_lut_line(table, ind)
        # self.white_spinbox.spin_val.setMinimum(point_data[-2, 0] + 1)

    def black_spinbox_changed(self):
        if self.curve_plot.hist_data is None:
            return
        val = self.black_spinbox.spin_val.value()
        val_diff = val - self.current_black_val
        diff_factor = val_diff / self.current_width
        for i in range(len(self.table_output)):
            if self.curve_plot.enable_channel[i]:
                self.black_side_changed(diff_factor, i)
                self.sig_table_changed.emit((self.table_output[i], i))
        self.current_black_val = val
        self.current_width = self.current_white_val - self.current_black_val

    def white_side_changed(self, diff_factor, ind):
        point_data = self.curve_plot.lut_points[ind].data['pos'].copy()
        da_width = point_data[-1, 0] - point_data[0, 0]
        dists = int(diff_factor * da_width)
        point_data[1:, 0] = dists + point_data[1:, 0]

        table = self.get_table(point_data, ind)
        self.table_output[ind] = table.astype(int)

        self.curve_plot.set_lut_points(point_data, ind)
        self.curve_plot.set_lut_line(table, ind)

    def white_spinbox_changed(self):
        if self.curve_plot.hist_data is None:
            return
        val = self.white_spinbox.spin_val.value()
        val_diff = val - self.current_white_val
        diff_factor = val_diff / self.current_width

        for i in range(len(self.table_output)):
            if self.curve_plot.enable_channel[i]:
                self.white_side_changed(diff_factor, i)
                self.sig_table_changed.emit((self.table_output[i], i))
        self.current_white_val = val
        self.current_width = self.current_white_val - self.current_black_val

    def table_changed(self, ev):
        table = ev[0]
        ind = ev[1]
        # curve_scatter = ev[1].astype(int)
        # self.black_spinbox.spin_val.setMaximum(curve_scatter[1, 0] - 1)
        # self.white_spinbox.spin_val.setMinimum(curve_scatter[-2, 0] + 1)
        self.sig_table_changed.emit((table, ind))

    def line_type_changed(self):
        self.line_type = self.line_type_combo.currentText()
        self.curve_plot.change_line_type(self.line_type)
        self.set_original_to_slider()
        if self.line_type != 'gamma':
            self.gamma_spinbox.setVisible(False)
        else:
            self.gamma_spinbox.setVisible(True)
            self.gamma_spinbox.spin_val.blockSignals(True)
            self.gamma_spinbox.spin_val.setValue(1)
            self.gamma_spinbox.spin_val.blockSignals(False)
        self.sig_line_type_changed.emit()

    def reset_pressed(self):
        self.curve_plot.change_line_type('gamma')
        self.set_original_to_slider()
        self.gamma_spinbox.spin_val.blockSignals(True)
        self.gamma_spinbox.spin_val.setValue(1)
        self.gamma_spinbox.setVisible(True)
        self.gamma_spinbox.spin_val.blockSignals(False)
        self.sig_reset.emit()

    def set_enable_induced_slider(self):
        all_start = []
        all_end = []
        for i in range(self.n_channels):
            all_start.append(self.curve_plot.lut_points[i].data['pos'][0, :])
            all_end.append(self.curve_plot.lut_points[i].data['pos'][-1, :])
        selected_start = np.asarray(all_start)[np.ravel(self.curve_plot.enable_channel)[:self.n_channels]]
        selected_end = np.asarray(all_end)[np.ravel(self.curve_plot.enable_channel)[:self.n_channels]]
        min_slider_val = int(np.min(selected_start[:, 0]))
        max_slider_val = int(np.max(selected_end[:, 0]))
        self.current_black_val = min_slider_val
        self.current_white_val = max_slider_val
        self.current_width = max_slider_val - min_slider_val
        self.block_signal(True)
        self.multi_handle_slider.setValue((min_slider_val, max_slider_val))
        self.black_spinbox.spin_val.setValue(min_slider_val)
        self.white_spinbox.spin_val.setValue(max_slider_val)
        self.block_signal(False)
        if np.sum(self.curve_plot.enable_channel) != 1:
            self.gamma_spinbox.spin_val.blockSignals(True)
            self.gamma_spinbox.spin_val.setValue(1)
            self.gamma_spinbox.spin_val.blockSignals(False)
        else:
            g_ind = np.where(self.curve_plot.enable_channel)[0][0]
            self.gamma_spinbox.spin_val.blockSignals(True)
            self.gamma_spinbox.spin_val.setValue(self.gamma[g_ind])
            self.gamma_spinbox.spin_val.blockSignals(False)

    def set_channel_enable(self, ind, is_enable):
        self.curve_plot.set_enable(ind, is_enable)
        self.set_enable_induced_slider()






