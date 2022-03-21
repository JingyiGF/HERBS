import os
import sys
import numpy as np
from random import randint
from PyQt5.QtWidgets import *
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph.functions as fn
from PyQt5.QtGui import QIcon, QPixmap, QColor, QFont
from PyQt5.QtCore import Qt, QSize
from herrbs.wtiles import *

btm_style = '''

QPushButton {
    border : None; 
    background: transparent;
    margin: 0px;
    padding-top: 0px;
    border-radius: 0px;
    min-width: 24px;
    min-height: 24px;
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

class VirusInfoWindow(QWidget):
    def __init__(self, num, probe_color, theta, phi, r, label_name, label_ano, values, channels, colors):
        super().__init__()



class ProbeInfoWindow(QWidget):
    def __init__(self, num, probe_color, theta, phi, r, label_name, label_ano, values, channels, colors):
        super().__init__()

        layout = QGridLayout()
        self.label = QLabel("Probe % d Info Window " % num)
        self.label.setStyleSheet('QLabel {background-color: ' + probe_color + ';}')
        self.label.setFont(QFont('Arial', 20))

        ang_label = QLabel()
        ang_pixmap = QPixmap('icons/angle_icon.png')
        ang_label.setPixmap(ang_pixmap)

        theta_label = QLabel('\u03f4 : ')
        theta_label.setAlignment(Qt.AlignCenter)
        phi_label = QLabel('\u03d5 : ')
        phi_label.setAlignment(Qt.AlignCenter)
        r_label = QLabel('r')
        r_label.setAlignment(Qt.AlignCenter)

        alpha_value = QLabel('{} degree'.format(str(theta)))
        phi_value = QLabel('{} degree'.format(str(phi)))
        r = QLabel('{} um'.format(str(r)))

        da_group = QGroupBox()
        glayt = QGridLayout(da_group)
        glayt.addWidget(theta_label, 0, 0, 1, 1)
        glayt.addWidget(phi_label, 1, 0, 1, 1)
        glayt.addWidget(r_label, 2, 0, 1, 1)
        glayt.addWidget(alpha_value, 0, 1, 1, 1)
        glayt.addWidget(phi_value, 1, 1, 1, 1)
        glayt.addWidget(r, 2, 1, 1, 1)

        print(colors)

        sec_group = QGroupBox()
        slayout = QGridLayout(sec_group)
        lb1 = QLabel('Brain Region')
        # lb1.setAlignment(Qt.AlignCenter)
        lb2 = QLabel('Acronym')
        # lb2.setAlignment(Qt.AlignCenter)
        lb3 = QLabel('Channels')
        # lb3.setAlignment(Qt.AlignCenter)
        lb4 = QLabel('Color')
        # lb4.setAlignment(Qt.AlignCenter)
        slayout.addWidget(lb1, 0, 0, 1, 1)
        slayout.addWidget(lb2, 0, 1, 1, 1)
        slayout.addWidget(lb3, 0, 2, 1, 1)
        slayout.addWidget(lb4, 0, 3, 1, 1)

        channels = np.ravel(channels).astype(str)

        for i in range(len(label_name)):
            slayout.addWidget(QLabel(label_name[i]), i + 1, 0, 1, 1)
            slayout.addWidget(QLabel(label_ano[i]), i + 1, 1, 1, 1)
            slayout.addWidget(QLabel(channels[i]), i + 1, 2, 1, 1)
            clb = QLabel()
            da_color = QColor(colors[i][0], colors[i][1], colors[i][2], 255).name()
            # print(da_color)
            clb.setStyleSheet('QLabel {background-color: ' + da_color + '; width: 20px; height: 20px}')
            slayout.addWidget(clb, i + 1, 3, 1, 1)
            # full_data.append([label_name[i], label_ano[i], values[i], channels[i]])

        # full_data = []
        # full_data.append(['label_name', 'label_ano', 'values', 'channels'])
        # for i in range(len(label_name)):
        #     full_data.append([label_name[i], label_ano[i], values[i], channels[i]])
        #
        #
        # table = QTableView()
        # model = TableModel(full_data)
        # table.setModel(model)

        self.data = list(np.cumsum(values))
        self.data = self.data[::-1]
        # self.label = label[::-1]
        self.colors = colors[::-1]

        self.plot_frame = QFrame()
        self.plot_frame.setMaximumWidth(300)
        self.plot_frame.setMinimumWidth(300)
        view_layout = QGridLayout(self.plot_frame)
        view_layout.setSpacing(0)
        view_layout.setContentsMargins(0, 0, 0, 0)

        self.w = pg.GraphicsLayoutWidget()
        self.view = self.w.addViewBox()
        self.view.setAspectLocked()
        self.view.invertY(False)

        # create bar chart
        for i in range(len(self.data)):
            bg = pg.BarGraphItem(x=[1], height=self.data[i], width=0.6,
                                 brush=QColor(self.colors[i][0], self.colors[i][1], self.colors[i][2], 255))
            self.view.addItem(bg)

        view_layout.addWidget(self.w, 0, 0, 1, 1)

        layout.addWidget(self.label, 0, 0, 1, 4)
        layout.addWidget(ang_label, 1, 0, 1, 1)

        layout.addWidget(da_group, 1, 1, 1, 1)

        layout.addWidget(QLabel(), 1, 2, 1, 1)
        layout.addWidget(QLabel(), 1, 3, 1, 1)

        layout.addWidget(self.plot_frame, 3, 0, 1, 1)
        layout.addWidget(sec_group, 3, 1, 1, 3)
        self.setLayout(layout)



class SingleObject(QWidget):
    sig_clicked = pyqtSignal(object)
    sig_name_changed = pyqtSignal(object)

    def __init__(self, parent=None, index=0, object_name='probes', object_icon=None, group_index=0):
        QWidget.__init__(self, parent=parent)

        self.uncheck_style = 'background-color:rgb(83, 83, 83);'
        self.check_style = 'background-color:rgb(107, 107, 107);'

        self.setStyleSheet('border: 1px solid rgb(71, 71, 71)')
        self.id = index
        self.object_name = object_name
        self.active = True
        self.group_id = group_index

        self.tbnail = QPushButton()
        self.tbnail.setIcon(object_icon)
        self.tbnail.setIconSize(QSize(20, 20))

        self.text_btn = QDoubleButton()
        self.text_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
        self.text_btn.setStyleSheet('border:None; text-align:left; padding-left:5px; color:rgb(240, 240, 240);')
        self.text_btn.clicked.connect(self.on_click)
        self.text_btn.doubleClicked.connect(self.on_doubleclick)

        self.l_line_edit = LineEditEntered()
        self.l_line_edit.setStyleSheet('border:None; color:white; padding-left:5px; background-color:rgb(83, 83, 83);')
        # self.l_line_edit.setText(self.text_btn.text())
        self.l_line_edit.setFixedWidth(100)
        self.l_line_edit.sig_return_pressed.connect(self.enter_pressed)

        self.empty_btn = QPushButton()
        self.empty_btn.setStyleSheet('border:None;')
        self.empty_btn.setFixedWidth(100)
        self.empty_btn.clicked.connect(self.on_click)

        self.inner_frame = QFrameClickable()
        self.inner_frame.setStyleSheet('background-color:rgb(83, 83, 83);')
        self.inner_layout = QGridLayout(self.inner_frame)
        self.inner_layout.setContentsMargins(10, 0, 0, 0)
        self.inner_layout.setSpacing(5)
        self.inner_layout.addWidget(self.tbnail, 0, 0, 1, 1)
        self.inner_layout.addWidget(self.text_btn, 0, 1, 1, 1)
        self.inner_layout.addWidget(self.l_line_edit, 0, 1, 1, 1)
        self.inner_layout.addWidget(self.empty_btn, 0, 2, 1, 1)
        self.inner_frame.clicked.connect(self.on_click)

        self.outer_layout = QHBoxLayout()
        self.outer_layout.setContentsMargins(0, 0, 0, 0)
        self.outer_layout.setSpacing(0)
        self.outer_layout.setAlignment(Qt.AlignLeft)
        self.outer_layout.addWidget(self.inner_frame)

        self.l_line_edit.hide()

        self.setLayout(self.outer_layout)
        self.setFixedHeight(40)
        # self.show()

    @pyqtSlot()
    def on_click(self):
        print("Click")
        # self.inner_frame.setStyleSheet('background-color:rgb(107, 107, 107); ')
        self.set_checked(True)
        self.sig_clicked.emit((self.id, self.object_name, self.group_id))


    @pyqtSlot()
    def on_doubleclick(self):
        print("Doubleclick")
        # self.inner_frame.setStyleSheet('background-color:rgb(107, 107, 107); ')
        self.l_line_edit.setText(self.text_btn.text())
        self.l_line_edit.setVisible(True)
        self.text_btn.setVisible(False)
        self.l_line_edit.setFocus(True)
        self.set_checked(True)
        self.sig_clicked.emit((self.id, self.object_name, self.group_id))

    @pyqtSlot()
    def enter_pressed(self):
        print('return')
        self.l_line_edit.setVisible(False)
        self.text_btn.setText(self.l_line_edit.text())
        self.object_name = self.l_line_edit.text()
        self.text_btn.setVisible(True)
        self.sig_name_changed.emit((self.id, self.object_name, self.group_id))

    def is_checked(self):
        return self.active

    def set_checked(self, check):
        self.active = check
        if self.inner_frame.isEnabled():
            if not self.active:
                self.inner_frame.setStyleSheet(self.uncheck_style)
            else:
                self.inner_frame.setStyleSheet(self.check_style)
        else:
            pass


class RegisteredObject(QWidget):
    sig_object_color_changed = pyqtSignal(object)
    eye_clicked = pyqtSignal(object)
    sig_clicked = pyqtSignal(object)

    def __init__(self, parent=None, index=0, object_name='probes', object_icon=None, group_index=0):
        QWidget.__init__(self, parent=parent)

        self.uncheck_style = 'background-color:rgb(83, 83, 83);'
        self.check_style = 'background-color:rgb(107, 107, 107);'
        self.color = QColor(randint(0, 255), randint(0, 255), randint(0, 255), 255)
        self.icon_back = 'border:1px solid black; background-color: {}'.format(self.color.name())

        self.setStyleSheet('border: 1px solid rgb(71, 71, 71)')
        self.id = index
        self.object_name = object_name
        self.active = True
        self.vis = True
        self.group_id = group_index


        self.eye_button = QToolButton()
        self.eye_button.setStyleSheet('border:None;')
        self.eye_button.setCheckable(True)
        eye_icon = QIcon()
        eye_icon.addPixmap(QPixmap("icons/layers/eye_on.png"), QIcon.Normal, QIcon.Off)
        eye_icon.addPixmap(QPixmap("icons/layers/eye_off.png"), QIcon.Normal, QIcon.On)
        self.eye_button.setIcon(eye_icon)
        self.eye_button.clicked.connect(self.eye_on_click)

        left_frame = QFrame()
        left_frame.setStyleSheet('background-color:rgb(83, 83, 83); border-right: 1px solid rgb(71, 71, 71)')
        left_layout = QHBoxLayout(left_frame)
        left_layout.addWidget(self.eye_button)

        self.tbnail = QPushButton()
        self.tbnail.setStyleSheet(self.icon_back)
        self.tbnail.setIcon(object_icon)
        self.tbnail.setIconSize(QSize(20, 20))
        self.tbnail.clicked.connect(self.change_object_color)

        self.text_btn = QPushButton(self.object_name)
        self.text_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
        self.text_btn.setStyleSheet('border:None; text-align:left; padding-left:5px; color:rgb(240, 240, 240);')
        self.text_btn.clicked.connect(self.on_click)

        self.inner_frame = QFrameClickable()
        self.inner_frame.setStyleSheet('background-color:rgb(83, 83, 83);')
        self.inner_layout = QGridLayout(self.inner_frame)
        self.inner_layout.setContentsMargins(10, 0, 0, 0)
        self.inner_layout.setSpacing(5)
        self.inner_layout.addWidget(self.tbnail, 0, 0, 1, 1)
        self.inner_layout.addWidget(self.text_btn, 0, 1, 1, 1)
        # self.inner_frame.clicked.connect(self.frame_on_click)

        self.outer_layout = QHBoxLayout()
        self.outer_layout.setContentsMargins(0, 0, 0, 0)
        self.outer_layout.setSpacing(0)
        self.outer_layout.setAlignment(Qt.AlignLeft)
        self.outer_layout.addWidget(left_frame)
        self.outer_layout.addWidget(self.inner_frame)

        self.setLayout(self.outer_layout)
        self.setFixedHeight(40)
        # self.show()

    def change_object_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color = QColor(color)
            self.icon_back = 'border:1px solid black; background-color: {}'.format(color.name())
            self.tbnail.setStyleSheet(self.icon_back)
            self.sig_object_color_changed.emit((self.id, self.color, self.object_name, self.group_id))

    def eye_on_click(self):
        if self.vis:
            self.vis = False
        else:
            self.vis = True
        self.set_checked(self.vis)
        self.eye_clicked.emit((self.id, self.object_name, self.vis, self.group_id))
        if self.inner_frame.isEnabled():
            self.tbnail.setEnabled(False)
            self.text_btn.setEnabled(False)
        else:
            self.tbnail.setEnabled(True)
            self.text_btn.setEnabled(True)

    @pyqtSlot()
    def on_click(self):
        print("Click")
        # self.inner_frame.setStyleSheet('background-color:rgb(107, 107, 107); ')
        self.set_checked(True)
        self.sig_clicked.emit((self.id, self.object_name, self.group_id))

    # @pyqtSlot()
    # def frame_on_click(self):
    #     print("Frame Click")
    #     # self.inner_frame.setStyleSheet('background-color:rgb(107, 107, 107); ')
    #     self.set_checked(True)
    #     self.sig_clicked.emit((self.id, self.object_name, self.group_id))

    def is_checked(self):
        return self.active

    def set_checked(self, check):
        self.active = check
        if self.inner_frame.isEnabled():
            if not self.active:
                self.inner_frame.setStyleSheet(self.uncheck_style)
            else:
                self.inner_frame.setStyleSheet(self.check_style)
        else:
            pass


    

class ObjectControl(QObject):

    class SignalProxy(QObject):
        sigOpacityChanged = pyqtSignal(object)
        sigVisChanged = pyqtSignal(object)

    def __init__(self, parent=None):

        self._sigprox = ObjectControl.SignalProxy()
        self.sig_opacity_changed = self._sigprox.sigOpacityChanged
        self.sig_visible_changed = self._sigprox.sigVisChanged

        QObject.__init__(self)

        self.current_obj_ind = None
        self.obj_count = 0
        self.probe_piece_count = 0
        self.cell_piece_count = 0
        self.line_piece_count = 0
        self.virus_piece_count = 0
        self.boundary_piece_count = 0

        self.obj_list = []
        self.obj_index = []
        self.obj_name = []
        self.obj_data = []

        self.probe_icon = QIcon('icons/sidebar/probe.svg')
        self.virus_icon = QIcon('icons/sidebar/virus.svg')
        self.line_icon = QIcon('icons/sidebar/line.svg')
        self.cell_icon = QIcon('icons/sidebar/cell.svg')
        self.bnd_icon = QIcon('icons/sidebar/bnd.svg')

        combo_label = QLabel('Composition:')
        self.obj_blend_combo = QComboBox()
        self.obj_blend_combo.setEditable(False)
        combo_value = ['Multiply', 'Overlay', 'SourceOver']
        self.obj_blend_combo.addItems(combo_value)
        self.obj_blend_combo.setCurrentText('Multiply')

        obj_opacity_label = QLabel('Opacity:')
        self.obj_opacity_slider = QSlider(Qt.Horizontal)
        self.obj_opacity_slider.setMaximum(100)
        self.obj_opacity_slider.setMinimum(0)
        self.obj_opacity_slider.setValue(100)
        self.obj_opacity_slider.valueChanged.connect(self.change_opacity_label_value)
        self.obj_opacity_val_label = QLabel('100%')

        point_size_label = QLabel('Point Size: ')
        self.point_size_slider = QSlider(QtCore.Qt.Horizontal)
        self.point_size_slider.setValue(2)
        self.point_size_slider.setMinimum(1)
        self.point_size_slider.setMaximum(100)
        # self.atlas_op_slider.valueChanged.connect(self.sig_rescale_slider)

        line_width_label = QLabel('Line Width: ')
        self.line_width_slider = QSlider(QtCore.Qt.Horizontal)
        self.line_width_slider.setValue(2)
        self.line_width_slider.setMinimum(1)
        self.line_width_slider.setMaximum(100)

        self.top_frame = QFrame()
        top_layout = QGridLayout(self.top_frame)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(5)
        top_layout.addWidget(combo_label, 0, 0, 1, 1)
        top_layout.addWidget(self.obj_blend_combo, 0, 1, 1, 3)
        top_layout.addWidget(obj_opacity_label, 1, 0, 1, 1)
        top_layout.addWidget(self.obj_opacity_slider, 1, 1, 1, 2)
        top_layout.addWidget(self.obj_opacity_val_label, 1, 3, 1, 1)
        top_layout.addWidget(point_size_label, 2, 0, 1, 1)
        top_layout.addWidget(self.point_size_slider, 2, 1, 1, 2)
        # top_layout.addWidget(self.obj_opacity_val_label, 1, 3, 1, 1)
        top_layout.addWidget(line_width_label, 3, 0, 1, 1)
        top_layout.addWidget(self.line_width_slider, 3, 1, 1, 2)

        self.layer_frame = QFrame()
        self.layer_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layer_layout = QBoxLayout(QBoxLayout.BottomToTop, self.layer_frame)
        self.layer_layout.setAlignment(Qt.AlignBottom)
        self.layer_layout.setContentsMargins(0, 0, 0, 0)
        self.layer_layout.setSpacing(5)

        self.layer_scroll = QScrollArea()
        self.layer_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layer_scroll.setWidget(self.layer_frame)
        self.layer_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.layer_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.layer_scroll.setWidgetResizable(True)

        self.outer_frame = QFrame()
        self.outer_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        outer_layout = QVBoxLayout(self.outer_frame)
        outer_layout.setSpacing(0)
        # outer_layout.setAlignment(Qt.AlignTop)
        outer_layout.addWidget(self.top_frame)
        outer_layout.addWidget(self.layer_scroll)

        # bottom buttons
        self.merge_probe_btn = QPushButton()
        self.merge_probe_btn.setFixedSize(24, 24)
        self.merge_probe_btn.setStyleSheet(btm_style)
        self.merge_probe_btn.setIcon(QIcon('icons/sidebar/probe.svg'))
        self.merge_probe_btn.setIconSize(QSize(20, 20))

        self.merge_line_btn = QPushButton()
        self.merge_line_btn.setFixedSize(24, 24)
        self.merge_line_btn.setStyleSheet(btm_style)
        self.merge_line_btn.setIcon(QIcon('icons/sidebar/line.svg'))
        self.merge_line_btn.setIconSize(QSize(20, 20))

        self.merge_cell_btn = QPushButton()
        self.merge_cell_btn.setFixedSize(24, 24)
        self.merge_cell_btn.setStyleSheet(btm_style)
        self.merge_cell_btn.setIcon(QIcon('icons/sidebar/cell.svg'))
        self.merge_cell_btn.setIconSize(QSize(20, 20))

        self.merge_virus_btn = QPushButton()
        self.merge_virus_btn.setFixedSize(24, 24)
        self.merge_virus_btn.setStyleSheet(btm_style)
        self.merge_virus_btn.setIcon(QIcon('icons/sidebar/virus.svg'))
        self.merge_virus_btn.setIconSize(QSize(20, 20))

        self.merge_bnd_btn = QPushButton()
        self.merge_bnd_btn.setFixedSize(24, 24)
        self.merge_bnd_btn.setStyleSheet(btm_style)
        self.merge_bnd_btn.setIcon(QIcon('icons/sidebar/merge.svg'))
        self.merge_bnd_btn.setIconSize(QSize(20, 20))


        self.add_object_btn = QPushButton()
        self.add_object_btn.setFixedSize(24, 24)
        self.add_object_btn.setStyleSheet(btm_style)
        self.add_object_btn.setIcon(QIcon('icons/layers/add.png'))
        self.add_object_btn.setIconSize(QSize(20, 20))

        self.delete_object_btn = QPushButton()
        self.delete_object_btn.setFixedSize(24, 24)
        self.delete_object_btn.setStyleSheet(btm_style)
        self.delete_object_btn.setIcon(QIcon('icons/layers/trash.png'))
        self.delete_object_btn.setIconSize(QSize(20, 20))
        self.delete_object_btn.clicked.connect(self.delete_object)

    def change_opacity_label_value(self):
        da_val = self.layer_opacity_slider.value()
        self.layer_opacity_val_label.setText('{} %'.format(da_val))
        self.sig_opacity_changed.emit(da_val)

    def add_object_piece(self, object_name, object_icon, object_data=None):
        if 'probe' in object_name:
            group_index = self.probe_piece_count
        elif 'virus' in object_name:
            group_index = self.virus_piece_count
        elif 'cell' in object_name:
            group_index = self.cell_piece_count
        elif 'line' in object_name:
            group_index = self.line_piece_count
        else:
            group_index = self.boundary_piece_count
        new_layer = SingleObject(index=self.obj_count, object_name=object_name, object_icon=object_icon, group_index=group_index)
        new_layer.text_btn.setText("{} {}".format(object_name, group_index + 1))
        new_layer.set_checked(True)
        new_layer.sig_clicked.connect(self.obj_clicked)
        new_layer.sig_name_changed.connect(self.obj_piece_name_changed)
        self.obj_data.append(object_data)
        self.obj_list.append(new_layer)
        self.obj_index.append(self.obj_count)
        self.obj_name.append("{} {}".format(object_name, group_index + 1))

        if self.current_obj_ind is None:
            self.current_obj_ind = self.obj_count
        else:
            ind2unactive = np.where(np.asarray(self.obj_index) == self.current_obj_ind)[0][0]
            self.obj_list[ind2unactive].set_checked(False)
            self.current_obj_ind = self.obj_count
        self.layer_layout.addWidget(self.obj_list[-1])
        self.obj_count += 1
        if 'probe' in object_name:
            self.probe_piece_count += 1
        elif 'virus' in object_name:
            self.virus_piece_count += 1
        elif 'cell' in object_name:
            self.cell_piece_count += 1
        elif 'line' in object_name:
            self.line_piece_count += 1
        else:
            self.boundary_piece_count += 1

    def obj_piece_name_changed(self, ev):
        id = ev[0]
        name = ev[1]
        cind = np.where(np.ravel(self.obj_index) == id)[0][0]
        self.obj_name[cind] = name
        print(self.obj_name)

    def delete_object(self):
        if self.current_obj_ind is None:
            return
        ind2del = np.where(np.asarray(self.obj_index) == self.current_obj_ind)[0][0]
        self.layer_layout.removeWidget(self.obj_list[ind2del])
        self.obj_list[ind2del].deleteLater()
        del self.obj_list[ind2del]
        del self.obj_index[ind2del]
        del self.obj_name[ind2del]
        del self.obj_data[ind2del]
        self.obj_list[-1].set_checked(True)
        self.current_obj_ind = self.obj_index[-1]
        print(self.current_obj_ind)
        print(self.obj_index)

    def obj_clicked(self, ev):
        index = ev[0]
        print(('obj clicked', index))
        if self.current_obj_ind != index:
            id2unactive = np.where(np.ravel(self.obj_index) == self.current_obj_ind)[0][0]
            self.obj_list[id2unactive].set_checked(False)
            id2active = np.where(np.ravel(self.obj_index) == index)[0][0]
            self.obj_list[id2active].set_checked(True)
            self.current_obj_ind = index
        print(self.current_obj_ind)


    # # draw 3d
    # pos = (np.array([sp, new_ep, ep]) - np.array([256, 512, 256])) / 4.
    # # pos_color = da_probe.cbutton.color(mode='byte')
    #
    # pos_color = da_probe.color
    # pos_color = [pos_color[0], pos_color[1], pos_color[2], 1]
    # da_color = np.array(pos_color) * 255
    # da_color = da_color.astype(int)
    # da_dict['prob_color'] = QColor(da_color[0], da_color[1], da_color[2], 255).name()
    #
    # # pos_color = np.array([da_color, da_color, [0, 0, 0, 1]])
    # probe_line_3d = gl.GLLinePlotItem(pos=pos, color=pos_color, width=3, mode='line_strip')
    # probe_line_3d.setGLOptions('opaque')
    # self.probe3d_lines.append(probe_line_3d)
    #
    # # pos_tip = (np.array([new_ep, ep]) - np.array([256, 512, 256])) / 4.
    # # probe_line_tip = gl.GLLinePlotItem(pos=pos_tip, color=(0, 0, 0, 1), width=1, mode='line_strip')
    # # probe_line_tip.setGLOptions('opaque')
    # self.view3d.addItem(self.probe3d_lines[-1])
    # # self.view3d.addItem(probe_line_tip)
    #
    # self.probe_data_dicts.append(da_dict)


    def merge_cells(self):
        print('merge_cells')

    def merge_virus(self):
        print('merge_cells')

    def merge_lines(self):
        print('merge_lines')

    def merge_boundaries(self):
        print('merge bnd')