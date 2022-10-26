import os
import sys
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from .uuuuuu import hsv2rgb, gamma_line, get_qhsv_from_czi_hsv, make_hist_data, read_qss_file


class BWSpin(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self)
        # wrap_frame = QFrame()
        wrap_layout = QVBoxLayout(self)
        wrap_layout.setContentsMargins(0, 0, 0, 0)
        wrap_layout.setSpacing(0)

        self.spin_nam = QLabel()
        self.spin_nam.setAlignment(Qt.AlignCenter)
        self.spin_val = QSpinBox()

        wrap_layout.addWidget(self.spin_nam)
        wrap_layout.addWidget(self.spin_val)


class GammaSpin(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self)
        # wrap_frame = QFrame()
        wrap_layout = QVBoxLayout(self)
        wrap_layout.setContentsMargins(0, 0, 0, 0)
        wrap_layout.setSpacing(0)

        self.spin_nam = QLabel()
        self.spin_nam.setAlignment(Qt.AlignCenter)
        self.spin_val = QDoubleSpinBox()
        self.spin_val.setDecimals(2)

        wrap_layout.addWidget(self.spin_nam)
        wrap_layout.addWidget(self.spin_val)


class ColorCombo(QComboBox):
    def __init__(self, parent=None):
        QComboBox.__init__(self)
        color_combo_style = read_qss_file('qss/color_combo.qss')
        self.setStyleSheet(color_combo_style)
        self.px = QPixmap(80, 30)
        n_vals = ['Light Blue', 'Blue', 'Green', 'Lime Green', 'Yellow', 'Olive', 'Red', 'Dark Red', 'Violet', 'Purple',
                  'Orange', 'Dark Orange', 'Turquoise', 'Blue Green']
        h_vals = [199, 235, 103, 115, 60, 60, 5, 4, 295, 279, 21, 20, 181, 151]
        s_vals = [60, 100, 70, 57, 67, 55, 85, 88, 77,  84, 81, 82, 51, 46]
        v_vals = [98, 96, 98, 59, 100, 60, 90, 54, 97,  77, 92, 73, 99, 79]
        s_vals = np.ravel(s_vals) * 0.01 * 255
        s_vals = s_vals.astype('uint8')
        v_vals = np.ravel(v_vals) * 0.01 * 255
        v_vals = v_vals.astype('uint8')
        self.hsv_color_list = []
        for i in range(len(h_vals)):
            self.hsv_color_list.append((h_vals[i] / 360., s_vals[i] / 255., v_vals[i] / 255.))
            self.px.fill(QColor.fromHsv(h_vals[i], s_vals[i], v_vals[i]))
            self.addItem(QIcon(self.px), n_vals[i])

        combo_list = QListView(self)
        self.setView(combo_list)


class ChannelSelector(QWidget):
    class SignalProxy(QObject):
        visChannels = pyqtSignal(object, object)
        changeColors = pyqtSignal(object, object)

    def __init__(self, rgb=False, parent=None):
        self._sigprox = ChannelSelector.SignalProxy()
        self.sig_vis_channels = self._sigprox.visChannels
        self.sig_change_color = self._sigprox.changeColors

        QWidget.__init__(self)

        channel_button_style = read_qss_file('qss/channel_selector.qss')
        self.vis = True
        self.setFixedSize(60, 60)
        self.setStyleSheet(channel_button_style)

        # wrap_frame = QFrame()
        wrap_layout = QVBoxLayout(self)
        wrap_layout.setContentsMargins(0, 0, 0, 0)
        wrap_layout.setSpacing(0)

        self.vis_btn = QPushButton()
        self.vis_btn.setFixedSize(60, 30)
        self.vis_btn.setCheckable(True)
        self.vis_btn.clicked.connect(self.change_vis)
        self.color_combo = ColorCombo()
        self.color_combo.setFixedSize(60, 28)
        self.color_combo.currentIndexChanged.connect(self.selection_change)
        self.color_label = QLabel()

        self.color_label.setVisible(False)

        wrap_layout.addWidget(self.vis_btn)
        wrap_layout.addWidget(self.color_combo)
        wrap_layout.addWidget(self.color_label)

    def set_channel_index(self, index):
        self.index = index

    def change_vis(self):
        if self.vis_btn.isChecked():
            self.set_checked(True)
        else:
            self.set_checked(False)
        self.sig_vis_channels.emit(self.vis, self.index)

    def set_checked(self, is_checked):
        if is_checked:
            self.color_label.setVisible(True)
            self.color_combo.setVisible(False)
            self.vis = False
        else:
            self.color_label.setVisible(False)
            self.color_combo.setVisible(True)
            self.vis = True

    def selection_change(self):
        da_index = self.color_combo.currentIndex()
        da_color = self.color_combo.hsv_color_list[da_index]
        self.sig_change_color.emit(da_color, self.index)

    def add_item(self, hsv_color):
        self.color_combo.hsv_color_list.append((hsv_color[0], hsv_color[1], hsv_color[2]))
        q_hsv = get_qhsv_from_czi_hsv(hsv_color)
        self.color_combo.px.fill(QColor.fromHsv(q_hsv[0], q_hsv[1], q_hsv[2]))
        self.color_combo.addItem(QIcon(self.color_combo.px), '')
        self.color_combo.setCurrentIndex(len(self.color_combo.hsv_color_list) - 1)

    def delete_item(self):
        self.color_combo.removeItem(len(self.color_combo.hsv_color_list) - 1)
        self.color_combo.hsv_color_list.pop()

