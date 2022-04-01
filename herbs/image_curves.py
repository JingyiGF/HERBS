import os
import sys
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from pyqtgraph.Qt import QtGui, QtCore

from qtrangeslider import QRangeSlider
from scipy.interpolate import interp1d

import cv2

from image_stacks import ImageStacks
from image_reader import ImageReader
from uuuuuu import hsv2rgb, gamma_line, get_qhsv_from_czi_hsv, make_hist_data
from widgets_utils import BWSpin, GammaSpin, ColorCombo, ChannelSelector
from movable_points import MovablePoints


multi_handle_slider_style = """
QSlider::groove:horizontal {
    border: 1px solid #999999;
    height: 8px; /* the groove expands to the size of the slider by default. by giving it a height, it has a fixed size */
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 black, stop:1 white);
    margin: 2px 0;
}

QSlider::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #8f8f8f);
    border: 1px solid #5c5c5c;
    width: 18px;
    margin: -2px 0; /* handle is placed by default on the contents rect of the groove. Expand outside the groove */
    border-radius: 3px;
}

"""

chn_widget_warp_frame_style = '''
QFrame {
    border: 1px solid #747a80; 
    border-radius: 5px;
}
'''


class CurvesPlot(pg.PlotWidget):
    sigLineChange = pyqtSignal(object)
    sigBoundChange = pyqtSignal()

    def __init__(self, parent=None, background='w'):
        pg.PlotWidget.__init__(self)
        self.setBackground('w')

        self.plotItem.vb.setMouseEnabled(x=False, y=False)
        self.getPlotItem().hideAxis('bottom')
        self.getPlotItem().hideAxis('left')

        self.scene().sigMouseMoved.connect(self.on_mouse_moved)
        self.scene().sigMouseClicked.connect(self.add_points)

        self.pnts = None
        self.dtype = 'uint16'
        self.line_type = 'gamma'
        self.gray_max = 65535
        self.start_point = np.array([0, 0])
        self.end_point = np.array([self.gray_max, self.gray_max])
        self.line_x = np.arange(0, self.gray_max + 1)
        self.line_y = np.arange(self.gray_max + 1)
        self.hist_data = []

        self.hist_list = []
        for i in range(4):
            self.hist_list.append(pg.PlotDataItem())
        self.line = pg.PlotCurveItem(fillLevel=None, pen='k')
        self.points = MovablePoints()
        self.points.mouseDragged.connect(self.on_mouse_dragged)

        for i in range(4):
            self.addItem(self.hist_list[i])
        self.addItem(self.line)
        self.addItem(self.points)

    def set_data(self, image_data, color, gray_max):
        """
        Set data to curve Plot view, only called once there load new data
        :param image_data: grayscale image data for one scene
        :param color: list of rgb [0, 255] for each channel
        :param gray_max: gray intensity level
        :return: None
        """
        if self.pnts is not None:
            for i in range(4):
                self.removeItem(self.hist_list[i])
                self.hist_list[i] = pg.PlotDataItem()
                self.addItem(self.hist_list[i])

        self.plotItem.vb.setRange(xRange=[0, gray_max], yRange=[0, gray_max])

        self.hist_data = make_hist_data(image_data, gray_max)
        for i in range(len(self.hist_data)):
            self.hist_list[i].setData(self.hist_data[i][0], self.hist_data[i][1],
                                      fillLevel=0,
                                      fillBrush=(color[i][0], color[i][1], color[i][2], 130),
                                      pen=pg.mkPen(QColor(color[i][0], color[i][1], color[i][2], 255), width=3))

        if self.gray_max != gray_max:
            self.start_point = np.array([0, 0])
            self.end_point = np.array([gray_max, gray_max])
            self.line_x = np.arange(0, gray_max + 1)
            self.line_y = np.arange(gray_max + 1)
            self.gray_max = gray_max

        self.pnts = np.vstack([self.start_point, self.end_point])
        self.line.setData(self.pnts[:, 0], self.pnts[:, 1])
        self.points.setData(pos=self.pnts)


    def set_plot(self, points, table):
        self.pnts = points
        self.table = table
        self.line.setData(self.line_x, self.table)
        self.points.setData(pos=self.pnts)

    def change_hist_color(self, color: tuple, ind: int):
        """
        :param color: (h [0, 1], s [0, 1], v [0, 1])
        :param ind: channel index
        :return: None
        """
        if not self.hist_data:
            return
        self.hist_list[ind].setFillLevel(0)
        da_hsv = get_qhsv_from_czi_hsv(color)
        self.hist_list[ind].setBrush(QColor.fromHsv(da_hsv[0], da_hsv[1], da_hsv[2], 130))
        self.hist_list[ind].setPen(pg.mkPen(QColor.fromHsv(da_hsv[0], da_hsv[1], da_hsv[2], 255), width=3))

    def set_line_type(self, line_type):
        self.line_type = line_type
        self.pnts = np.vstack([self.start_point, self.end_point])
        self.points.setData(pos=self.pnts)
        self.line.setData(self.pnts[:, 0], self.pnts[:, 1])

    def reset(self):
        self.set_line_type('gamma')
        self.line_type = 'gamma'
        self.pnts = np.vstack([self.start_point, self.end_point])
        self.points.setData(pos=self.pnts)
        self.line.setData(self.pnts[:, 0], self.pnts[:, 1])

    # def on_mouse_clicked(self, pos):
    #     if self.line.mouseShape().contains(pos):
    #         data = np.vstack([self.pnts, np.array([pos.x(), pos.y()])])
    #         sort_x = np.argsort(data[:, 0])
    #         data = data[sort_x, :]
    #         self.points.setData(pos=data)

    def on_mouse_dragged(self, vec):
        if self.line_type == 'gamma':
            return
        ev = vec[0]
        ind = vec[1]
        pos = ev.pos()
        data = self.points.data['pos']
        npts = len(data)
        cind = np.logical_and(self.line_x >= self.pnts[0, 0], self.line_x <= self.pnts[-1, 0])
        if ind in [0, len(data)-1]:
            return
        else:
            table = self.update_table(data)
            self.line.setData(self.line_x, self.table)
            self.table.astype(self.dtype)
        self.sigLineChange.emit(self.table)
        self.sigBoundChange.emit()

    def add_points(self, event):
        # print(event.scenePos())
        if self.line_type == 'gamma':
            return
        pnt = self.plotItem.vb.mapSceneToView(event.scenePos())
        if self.adding_allowed:
            x = pnt.x()
            y = pnt.y()
            if x <= self.pnts[0, 0] or x >= self.pnts[-1, 0]:
                return
            self.pnts = np.vstack([self.pnts, np.array([x, y])])
            sort_x = np.argsort(self.pnts[:, 0])
            self.pnts = self.pnts[sort_x, :]
            print(self.pnts)
            self.points.setData(pos=self.pnts)
            table = self.update_table(self.pnts)
            self.line.setData(self.line_x, table)
            table = table.astype(self.dtype)
            self.sigLineChange.emit(table)
            self.sigBoundChange.emit()

    def update_table(self, data):
        cind = np.logical_and(self.line_x >= data[0, 0], self.line_x <= data[-1, 0])

        if self.line_type == 'linear':
            line_func = interp1d(data[:, 0], data[:, 1], kind='linear')
        else:
            slope_vec = (data[1:, 1] - data[0, 1]) / (data[1:, 0] - data[0, 0])
            if np.all(abs(np.diff(slope_vec)) < 0.1):
                line_func = interp1d(data[:, 0], data[:, 1], kind='linear')
            else:
                line_func = interp1d(data[:, 0], data[:, 1], kind='cubic')
        temp_line = self.line_y.copy()
        temp_line[cind] = line_func(self.line_x[cind])
        temp_line[self.line_x <= data[0, 0]] = 0
        temp_line[self.line_x >= data[-1, 0]] = self.line_y.max()
        temp_line[temp_line <= 0] = 0
        temp_line[temp_line >= self.gray_max] = self.gray_max
        return temp_line

    def on_mouse_moved(self, point):
        if self.line_type == 'gamma':
            return
        pnts = self.plotItem.vb.mapSceneToView(point)
        sct = self.points.scatter.pointsAt(pnts)
        # print(len(sct))
        if self.line.mouseShape().contains(pnts):
            if len(sct) == 0:
                self.setCursor(Qt.CrossCursor)
                self.adding_allowed = True
            else:
                self.setCursor(Qt.OpenHandCursor)
                self.adding_allowed = False
        else:
            self.adding_allowed = False
            if len(sct) == 0:
                self.setCursor(Qt.ArrowCursor)
            else:
                self.setCursor(Qt.OpenHandCursor)


class CurveWidget(QWidget):
    class SignalProxy(QObject):
        sigTableChanged = pyqtSignal(object)

    def __init__(self, parent=None):
        self._sigprox = CurveWidget.SignalProxy()
        self.sig_table_changed = self._sigprox.sigTableChanged

        QWidget.__init__(self)

        self.gray_max = 65535
        self.gamma = 1
        # self.prev_handle_pos = (0., 32767., 65535.)

        self.curve_plot = CurvesPlot()
        self.curve_plot.sigLineChange.connect(self.table_changed)
        self.curve_plot.sigBoundChange.connect(self.spinbox_bound_changed)

        self.multi_handle_slider = QRangeSlider(Qt.Horizontal)
        self.multi_handle_slider.setStyleSheet(multi_handle_slider_style)
        self.multi_handle_slider.setMinimum(0)
        self.multi_handle_slider.setMaximum(65535)
        self.multi_handle_slider.setValue((0, 65535))
        self.multi_handle_slider.setSingleStep(1.)
        self.multi_handle_slider.setBarVisible(False)
        self.multi_handle_slider.sliderMoved.connect(self.slider_changed)

        self.black_spinbox = BWSpin()
        self.black_spinbox.spin_nam.setText('Black:')
        self.black_spinbox.spin_val.setMinimum(0)
        self.black_spinbox.spin_val.setMaximum(65535)
        self.black_spinbox.spin_val.setValue(0)
        self.black_spinbox.spin_val.valueChanged.connect(self.black_spinbox_changed)

        self.white_spinbox = BWSpin()
        self.white_spinbox.spin_nam.setText('White:')
        self.white_spinbox.spin_val.setMinimum(0)
        self.white_spinbox.spin_val.setMaximum(65535)
        self.white_spinbox.spin_val.setValue(65535)
        self.white_spinbox.spin_val.valueChanged.connect(self.white_spinbox_changed)

        self.gamma_spinbox = GammaSpin()
        self.gamma_spinbox.spin_nam.setText('Gamma:')
        self.gamma_spinbox.spin_val.setMinimum(0.01)
        self.gamma_spinbox.spin_val.setMaximum(16.00)
        self.gamma_spinbox.spin_val.setSingleStep(0.05)
        self.gamma_spinbox.spin_val.setValue(1.00)
        self.gamma_spinbox.spin_val.valueChanged.connect(self.gamma_spinbox_changed)

        self.reset_btn = QPushButton('Reset')
        self.reset_btn.clicked.connect(self.reset_pressed)

        self.line_type_combo = QComboBox()
        ltypes = ['gamma', 'linear', 'spline']
        self.line_type_combo.addItems(ltypes)
        self.line_type_combo.setCurrentText('gamma')
        self.line_type = 'gamma'
        self.line_type_combo.currentTextChanged.connect(self.line_type_changed)

        top_wrap = QFrame()
        top_layout = QHBoxLayout(top_wrap)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.addWidget(self.line_type_combo)
        top_layout.addWidget(self.reset_btn)

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

    def set_data(self, data, color, gray_max, data_type):
        if self.gray_max != gray_max:
            self.multi_handle_slider.setMaximum(gray_max)
            self.multi_handle_slider.setValue((0, gray_max))
            # self.prev_handle_pos = (0., 127., 255.)
            self.white_spinbox.spin_val.setMaximum(gray_max)
            self.white_spinbox.spin_val.setValue(gray_max)
        self.gray_max = gray_max
        self.dtype = data_type
        self.curve_plot.set_data(data, color, self.gray_max)

    def slider_changed(self, ev):
        if self.curve_plot.pnts is None:
            return

        point_values = self.curve_plot.points.data['pos'].copy()
        val1 = int(ev[0])
        val2 = int(ev[1])
        if val1 != self.black_spinbox.spin_val.value():
            if val1 >= point_values[1, 0]:
                self.multi_handle_slider.setValue((val2 - 1, val2))
                return
            print('black')
            self.black_spinbox.spin_val.setValue(val1)
            self.white_spinbox.spin_val.setMinimum(val1 + 1)

        if val2 != self.white_spinbox.spin_val.value():
            if val2 <= point_values[-2, 0]:
                self.multi_handle_slider.setValue((val1, val1 + 1))
                return
            print('white')
            self.white_spinbox.spin_val.setValue(val2)
            self.black_spinbox.spin_val.setMaximum(val2 - 1)

    # def slider_end_point_change_mid_point(self, ev):
    #     da_pnt = np.exp(self.gamma * np.log(0.5)) * (ev[-1] - ev[0]) + ev[0]
    #     if round(da_pnt) != ev[1]:
    #         self.multi_handle_slider.setValue((ev[0], da_pnt, ev[-1]))
    #     return da_pnt

    def spinbox_bound_changed(self):
        points = self.curve_plot.points.data['pos']
        max_val = points[1, 0]
        min_val = points[-2, 0]
        if max_val != self.black_spinbox.spin_val.maximum():
            self.black_spinbox.spin_val.setMaximum(max_val)




        print(points)

    def gamma_spinbox_changed(self):
        if self.line_type != 'gamma':
            return
        vals = self.multi_handle_slider.value()
        self.gamma = self.gamma_spinbox.spin_val.value()
        self.table = gamma_line(self.curve_plot.line_x, (vals[0], vals[1]), self.gamma, dtype=self.dtype)
        self.curve_plot.set_plot(self.curve_plot.pnts, self.table)
        self.sig_table_changed.emit(self.table)

    def black_spinbox_changed(self):
        if self.curve_plot.pnts is None:
            return
        point_values = self.curve_plot.pnts.copy()
        inter_xval = self.curve_plot.line_x.copy()
        val = self.black_spinbox.spin_val.value()
        line_type = self.line_type_combo.currentText()
        slider_vals = self.multi_handle_slider.value()
        # if val >= self.curve_plot.pnts[1, 0]:
        #     val = self.curve_plot.pnts[1, 0] - 1
        #     self.black_spinbox.spin_val.setValue(int(val))
        point_values[0, 0] = val
        if line_type == 'gamma':
            table = gamma_line(inter_xval, (val, slider_vals[1]), self.gamma, dtype=self.dtype)
        else:
            table = self.curve_plot.table.copy()
            self.multi_handle_slider.setValue((val, slider_vals[1]))
            slope_vec = (point_values[1:, 1] - point_values[0, 1]) / (point_values[1:, 0] - point_values[0, 0])
            if np.all(abs(np.diff(slope_vec)) < 0.1):
                line_func = interp1d(point_values[:, 0], point_values[:, 1], kind='linear')
            else:
                line_func = interp1d(point_values[:, 0], point_values[:, 1], kind=line_type)

            table[np.logical_and(inter_xval >= val, inter_xval <= slider_vals[1])] = line_func(
                inter_xval[np.logical_and(inter_xval >= val, inter_xval <= slider_vals[1])])
            table[inter_xval <= val] = 0
            table[inter_xval >= slider_vals[1]] = self.gray_max
            table[table <= 0] = 0
            table[table >= self.gray_max] = self.gray_max
            table = table.astype(self.dtype)
        self.table = table.copy()
        self.curve_plot.set_plot(point_values, self.table)
        self.sig_table_changed.emit(self.table)

    def white_spinbox_changed(self):
        if self.curve_plot.pnts is None:
            return
        point_values = self.curve_plot.pnts.copy()
        inter_xval = self.curve_plot.line_x
        val = self.white_spinbox.spin_val.value()
        slider_vals = self.multi_handle_slider.value()
        # if val <= self.curve_plot.pnts[-2, 0]:
        #     val = self.curve_plot.pnts[-2, 0] + 1
        #     self.white_spinbox.spin_val.setValue(int(val))
        point_values[-1, 0] = val
        if self.line_type == 'gamma':
            table = gamma_line(inter_xval, (slider_vals[0], val), self.gamma, dtype=self.dtype)
        else:
            table = self.curve_plot.table
            self.multi_handle_slider.setValue((slider_vals[0], val))
            slope_vec = (point_values[1:, 1] - point_values[0, 1]) / (point_values[1:, 0] - point_values[0, 0])
            if np.all(abs(np.diff(slope_vec)) < 0.1):
                line_func = interp1d(point_values[:, 0], point_values[:, 1], kind='linear')
            else:
                line_func = interp1d(point_values[:, 0], point_values[:, 1], kind=self.line_type)

            table[np.logical_and(inter_xval >= slider_vals[0], inter_xval <= val)] = line_func(
                inter_xval[np.logical_and(inter_xval >= slider_vals[0], inter_xval <= val)])
            table[inter_xval <= slider_vals[0]] = 0
            table[inter_xval >= val] = self.gray_max
            table[table <= 0] = 0
            table[table >= self.gray_max] = self.gray_max
            table = table.astype(self.dtype)
        self.table = table.copy()
        self.curve_plot.set_plot(point_values, self.table)
        self.sig_table_changed.emit(self.table)

    def line_type_changed(self):
        self.line_type = self.line_type_combo.currentText()
        self.curve_plot.set_line_type(self.line_type)
        self.black_spinbox.spin_val.setValue(0)
        self.white_spinbox.spin_val.setValue(self.gray_max)
        if self.line_type_combo.currentText() != 'gamma':
            self.multi_handle_slider.setValue((0, self.gray_max))
            self.gamma_spinbox.setVisible(False)
        else:
            self.multi_handle_slider.setValue((0, int(0.5 * self.gray_max), self.gray_max))
            self.gamma_spinbox.setVisible(True)
            self.gamma_spinbox.spin_val.setValue(1)
        # self.sig_line_changed.emit()

    def reset_pressed(self):
        self.curve_plot.set_line_type(self.line_type_combo.currentText())
        self.black_spinbox.spin_val.setValue(0)
        self.white_spinbox.spin_val.setValue(self.gray_max)
        self.gamma_spinbox.spin_val.setValue(1)
        if self.line_type_combo.currentText() != 'gamma':
            self.multi_handle_slider.setValue((0, self.gray_max))
        else:
            self.multi_handle_slider.setValue((0, int(0.5 * self.gray_max), self.gray_max))
        # self.sig_reset.emit()

    def table_changed(self, table):
        print(table)
        self.table = table
        self.sig_table_changed.emit(self.table)
