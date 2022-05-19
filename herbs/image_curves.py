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
from .uuuuuu import hsv2rgb, gamma_line, get_qhsv_from_czi_hsv, make_hist_data
from .widgets_utils import BWSpin, GammaSpin, ColorCombo, ChannelSelector
from .movable_points import MovablePoints
from .styles import Styles


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

spinbox_style = '''
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
        self.pnts = None
        self.line_type = 'gamma'
        self.depth_level = 65535
        self.start_point = np.array([0, 0])
        self.end_point = np.array([self.depth_level, self.depth_level])
        self.table_input = np.arange(self.depth_level + 1)
        self.table_output = np.arange(self.depth_level + 1)
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

    def set_data(self, image_data, color, depth_level):
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

        self.plotItem.vb.setRange(xRange=[0, depth_level], yRange=[0, depth_level])

        self.hist_data = make_hist_data(image_data, depth_level)
        for i in range(len(self.hist_data)):
            self.hist_list[i].setData(self.hist_data[i][0], self.hist_data[i][1],
                                      fillLevel=0,
                                      fillBrush=(color[i][0], color[i][1], color[i][2], 130),
                                      pen=pg.mkPen(QColor(color[i][0], color[i][1], color[i][2], 255), width=3))
        if self.depth_level != depth_level:
            self.start_point = np.array([0, 0])
            self.end_point = np.array([depth_level, depth_level])
            self.table_input = np.arange(0, depth_level + 1)
            self.table_output = np.arange(depth_level + 1)
            self.depth_level = depth_level

        self.pnts = np.vstack([self.start_point, self.end_point])
        self.line.setData(self.pnts[:, 0], self.pnts[:, 1])
        self.points.setData(pos=self.pnts)

    def set_plot(self, points, table):
        self.pnts = points
        self.table_output = table
        self.line.setData(self.table_input, self.table_output)
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

    def on_mouse_dragged(self, vec):
        if self.line_type == 'gamma':
            return
        ind = vec[1]
        data = self.points.data['pos']
        if ind in [0, len(data)-1]:
            return
        else:
            self.table_output = self.update_table(data)
            self.line.setData(self.table_input, self.table_output)
        self.sig_line_change.emit((self.table_output.astype('int'), data))
        # self.pnts = data.copy()

    def on_mouse_clicked(self, event):
        if self.line_type == 'gamma':
            return
        pnt = self.plotItem.vb.mapSceneToView(event.scenePos())
        data = self.points.data['pos']
        if self.adding_allowed:
            x = pnt.x()
            y = pnt.y()
            if x <= data[0, 0] or x >= data[-1, 0]:
                return
            self.pnts = np.vstack([data, np.array([x, y])])
            sort_x = np.argsort(self.pnts[:, 0])
            self.pnts = self.pnts[sort_x, :]
            self.table_output = self.update_table(self.pnts)
            self.points.setData(pos=self.pnts)
            print(self.pnts)
            self.line.setData(self.table_input, self.table_output)
            self.sig_line_change.emit((self.table_output.astype('int'), self.pnts))

    def on_mouse_moved(self, point):
        if self.line_type == 'gamma':
            return
        pnts = self.plotItem.vb.mapSceneToView(point)
        sct = self.points.scatter.pointsAt(pnts)
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

    def clear(self):
        self.points.clear()
        for i in range(4):
            self.hist_list[i].clear()


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
        self.gamma = 1
        self.table_output = np.arange(self.gray_max)

        self.curve_plot = CurvesPlot()
        self.curve_plot.sig_line_change.connect(self.table_changed)
        # self.curve_plot.sigBoundChange.connect(self.spinbox_bound_changed)

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

    def set_data(self, data, color, depth_level):
        self.curve_plot.set_data(data, color, depth_level)
        if self.gray_max != depth_level:
            self.gray_max = depth_level
            self.multi_handle_slider.setMaximum(depth_level)
            self.multi_handle_slider.setValue((0, depth_level))
            self.white_spinbox.spin_val.setMaximum(depth_level)
            self.white_spinbox.spin_val.setValue(depth_level)

    def slider_changed(self, ev):
        if self.curve_plot.pnts is None:
            return
        point_values = self.curve_plot.points.data['pos'].copy()
        point_values = point_values.astype(int)
        self.black_spinbox.spin_val.setMaximum(point_values[1, 0] - 1)
        self.white_spinbox.spin_val.setMinimum(point_values[-2, 0] + 1)
        val1 = int(ev[0])
        val2 = int(ev[1])

        if val1 != self.black_spinbox.spin_val.value():
            if val1 >= point_values[1, 0]:
                val1 = point_values[1, 0] - 1
                self.multi_handle_slider.setValue((val1, val2))
            self.black_spinbox.spin_val.setValue(val1)
        if val2 != self.white_spinbox.spin_val.value():
            if val2 <= point_values[-2, 0]:
                val2 = point_values[-2, 0] + 1
                self.multi_handle_slider.setValue((val1, val2))
            self.white_spinbox.spin_val.setValue(val2)

    def gamma_spinbox_changed(self):
        if self.line_type != 'gamma':
            return
        data = self.curve_plot.points.data['pos'].copy()
        self.gamma = self.gamma_spinbox.spin_val.value()
        lims = (data[0, 0], data[-1, 0])
        self.table_output = gamma_line(self.curve_plot.table_input, lims, self.gamma, self.gray_max)
        self.curve_plot.set_plot(data, self.table_output)
        self.sig_table_changed.emit(self.table_output.astype(int))

    def black_spinbox_changed(self):
        if self.curve_plot.pnts is None:
            return
        val = self.black_spinbox.spin_val.value()
        line_type = self.line_type_combo.currentText()
        slider_vals = self.multi_handle_slider.value()
        self.multi_handle_slider.setValue((val, slider_vals[1]))
        point_values = self.curve_plot.pnts.copy()
        point_values[0, 0] = val

        xval = self.curve_plot.table_input
        if line_type == 'gamma':
            table = gamma_line(xval, (val, slider_vals[1]), self.gamma, self.gray_max)
        else:
            table = self.curve_plot.update_table(point_values)
        self.table_output = table.copy()
        self.curve_plot.set_plot(point_values, self.table_output)
        self.sig_table_changed.emit(self.table_output.astype(int))

    def white_spinbox_changed(self):
        if self.curve_plot.pnts is None:
            return
        val = self.white_spinbox.spin_val.value()
        line_type = self.line_type_combo.currentText()
        slider_vals = self.multi_handle_slider.value()
        self.multi_handle_slider.setValue((slider_vals[0], val))
        point_values = self.curve_plot.pnts.copy()
        point_values[-1, 0] = val

        xval = self.curve_plot.table_input
        if line_type == 'gamma':
            table = gamma_line(xval, (slider_vals[0], val), self.gamma, self.gray_max)
        else:
            table = self.curve_plot.update_table(point_values)
        self.table_output = table.copy()
        self.curve_plot.set_plot(point_values, self.table_output)
        self.sig_table_changed.emit(self.table_output.astype(int))

    def table_changed(self, ev):
        table = ev[0]
        curve_scatter = ev[1].astype(int)
        self.black_spinbox.spin_val.setMaximum(curve_scatter[1, 0] - 1)
        self.white_spinbox.spin_val.setMinimum(curve_scatter[-2, 0] + 1)
        self.sig_table_changed.emit(table)

    def line_type_changed(self):
        self.line_type = self.line_type_combo.currentText()
        self.curve_plot.set_line_type(self.line_type)
        self.black_spinbox.spin_val.setValue(0)
        self.white_spinbox.spin_val.setValue(self.gray_max)
        self.multi_handle_slider.setValue((0, self.gray_max))
        if self.line_type_combo.currentText() != 'gamma':
            self.gamma_spinbox.setVisible(False)
        else:
            self.gamma_spinbox.setVisible(True)
            self.gamma_spinbox.spin_val.setValue(1)
        self.sig_line_type_changed.emit()

    def reset_pressed(self):
        self.curve_plot.set_line_type(self.line_type_combo.currentText())
        self.black_spinbox.spin_val.setValue(0)
        self.white_spinbox.spin_val.setValue(self.gray_max)
        self.gamma_spinbox.spin_val.setValue(1)
        self.multi_handle_slider.setValue((0, self.gray_max))
        self.sig_reset.emit()
