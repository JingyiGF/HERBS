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
from .wtiles import *
from .styles import Styles

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


eye_button_style = '''
    border-left: None;
    border-right: 1px solid gray;
    border-top: None;
    border-bottom: None;
    border-radius: 0px;
    background: transparent;
'''

text_btn_style = '''
QPushButton {
    background: transparent;
    border: None;
    border-radius:0px;
    text-align:left; 
    padding-left: 5px; 
    padding-right: 0px;
    padding-top: 0px;
    padding-bottom: 0px;
    color:rgb(240, 240, 240);
    margin: 0px;
    height: 40px;
    width: 220px;
}


QPushButton:disabled {
    color: rgb(190, 190, 190);
}
'''


line_edit_style = '''
QLineEdit {
    background: transparent;
    border: 1px solid green;
    border-radius:0px;
    text-align:left; 
    color: white; 
    padding-left: 5px;    
    margin: 0px;
    height: 40px;
    width: 220px; 
}
'''


class CellsInfoWindow(QDialog):
    def __init__(self, group_id, data):
        super().__init__()

        self.setWindowTitle("Cell Information Window")

        layout = QVBoxLayout()
        self.label = QLabel("Cell % d " % group_id)
        label_style = 'QLabel {background-color: ' + QColor(data['vis_color']).name() + '; font-size: 20px}'
        self.label.setStyleSheet(label_style)

        sec_group = QGroupBox('Total Count: {}'.format(len(data['data'])))
        slayout = QGridLayout(sec_group)
        lb1 = QLabel('Brain Region')
        lb2 = QLabel('Acronym')
        lb3 = QLabel('Color')
        lb4 = QLabel('Count')
        slayout.addWidget(lb1, 0, 0, 1, 1)
        slayout.addWidget(lb2, 0, 1, 1, 1)
        slayout.addWidget(lb3, 0, 2, 1, 1)
        slayout.addWidget(lb4, 0, 3, 1, 1)

        for i in range(len(data['label_name'])):
            slayout.addWidget(QLabel(data['label_name'][i]), i + 1, 0, 1, 1)
            slayout.addWidget(QLabel(data['label_acronym'][i]), i + 1, 1, 1, 1)
            clb = QLabel()
            da_color = QColor(data['label_color'][i][0], data['label_color'][i][1], data['label_color'][i][2],
                              255).name()
            clb.setStyleSheet('QLabel {background-color: ' + da_color + '; width: 20px; height: 20px}')
            slayout.addWidget(clb, i + 1, 2, 1, 1)
            slayout.addWidget(QLabel(str(data['region_count'][i])), i + 1, 3, 1, 1)

        # ok button, used to close window
        ok_btn = QDialogButtonBox(QDialogButtonBox.Ok)
        ok_btn.accepted.connect(self.accept)

        # add widget to layout
        layout.addWidget(self.label)
        layout.addWidget(sec_group)
        layout.addWidget(ok_btn)
        self.setLayout(layout)

    def accept(self) -> None:
        self.close()

    def set_probe_color(self, color):
        self.label.setStyleSheet('QLabel {background-color: ' + color + ';}')


class VirusInfoWindow(QDialog):
    def __init__(self, group_id, data):
        super().__init__()

        self.setWindowTitle("Virus Information Window")

        layout = QVBoxLayout()
        self.label = QLabel("Virus % d " % group_id)
        label_style = 'QLabel {background-color: ' + QColor(data['vis_color']).name() + '; font-size: 20px}'
        self.label.setStyleSheet(label_style)

        sec_group = QGroupBox()
        slayout = QGridLayout(sec_group)
        lb1 = QLabel('Brain Region')
        lb2 = QLabel('Acronym')
        lb3 = QLabel('Color')
        slayout.addWidget(lb1, 0, 0, 1, 1)
        slayout.addWidget(lb2, 0, 1, 1, 1)
        slayout.addWidget(lb3, 0, 2, 1, 1)

        for i in range(len(data['label_name'])):
            slayout.addWidget(QLabel(data['label_name'][i]), i + 1, 0, 1, 1)
            slayout.addWidget(QLabel(data['label_acronym'][i]), i + 1, 1, 1, 1)
            clb = QLabel()
            da_color = QColor(data['label_color'][i][0], data['label_color'][i][1], data['label_color'][i][2],
                              255).name()
            clb.setStyleSheet('QLabel {background-color: ' + da_color + '; width: 20px; height: 20px}')
            slayout.addWidget(clb, i + 1, 2, 1, 1)

        # ok button, used to close window
        ok_btn = QDialogButtonBox(QDialogButtonBox.Ok)
        ok_btn.accepted.connect(self.accept)

        # add widget to layout
        layout.addWidget(self.label)
        layout.addWidget(sec_group)
        layout.addWidget(ok_btn)
        self.setLayout(layout)

    def accept(self) -> None:
        self.close()

    def set_probe_color(self, color):
        self.label.setStyleSheet('QLabel {background-color: ' + color + ';}')


class ProbeInfoWindow(QDialog):
    def __init__(self, name, data):
        super().__init__()

        self.setWindowTitle("Probe Information Window")

        layout = QGridLayout()
        self.label = QLabel(name)
        # self.label = QLabel("Probe % d " % group_id)
        color = QColor(data['vis_color'][0], data['vis_color'][1], data['vis_color'][2], data['vis_color'][3])
        label_style = 'QLabel {background-color: ' + color.name() + '; font-size: 20px}'
        self.label.setStyleSheet(label_style)

        ang_label = QLabel()
        ang_pixmap = QPixmap('icons/angle_illustration.png')
        ang_label.setPixmap(ang_pixmap)

        theta_label = QLabel('\u03f4 : ')
        theta_label.setAlignment(Qt.AlignCenter)
        phi_label = QLabel('\u03d5 : ')
        phi_label.setAlignment(Qt.AlignCenter)
        r_label = QLabel('r : ')
        r_label.setAlignment(Qt.AlignCenter)
        coords_label = QLabel('Enter coordinates : ')
        coords_label.setAlignment(Qt.AlignCenter)
        voxels_label = QLabel('Enter voxels : ')
        voxels_label.setAlignment(Qt.AlignCenter)


        alpha_value = QLabel('{} \u00B0'.format(data['theta']))
        phi_value = QLabel('{} \u00B0'.format(data['phi']))
        total_length = QLabel('{} \u03BCm'.format(data['probe_length']))
        cval = np.round(data['coords'], 2)
        enter_coords = QLabel('ML: {}\u03BCm,  AP: {}\u03BCm,  DV: {}\u03BCm'.format(cval[0], cval[1], cval[2]))
        sval = data['new_sp'].astype(int)
        enter_vox = QLabel('({} {} {})'.format(sval[0], sval[1], sval[2]))

        angle_length_group = QGroupBox()
        anglen_layout = QGridLayout(angle_length_group)
        anglen_layout.addWidget(theta_label, 0, 0, 1, 1)
        anglen_layout.addWidget(phi_label, 1, 0, 1, 1)
        anglen_layout.addWidget(r_label, 2, 0, 1, 1)
        anglen_layout.addWidget(coords_label, 3, 0, 1, 1)
        anglen_layout.addWidget(voxels_label, 4, 0, 1, 1)
        anglen_layout.addWidget(alpha_value, 0, 1, 1, 1)
        anglen_layout.addWidget(phi_value, 1, 1, 1, 1)
        anglen_layout.addWidget(total_length, 2, 1, 1, 1)
        anglen_layout.addWidget(enter_coords, 3, 1, 1, 1)
        anglen_layout.addWidget(enter_vox, 4, 1, 1, 1)

        sec_group = QGroupBox()
        slayout = QGridLayout(sec_group)
        lb1 = QLabel('Brain Region')
        lb2 = QLabel('Acronym')
        lb3 = QLabel('Channels')
        lb4 = QLabel('Color')
        slayout.addWidget(lb1, 0, 0, 1, 1)
        slayout.addWidget(lb2, 0, 1, 1, 1)
        slayout.addWidget(lb3, 0, 2, 1, 1)
        slayout.addWidget(lb4, 0, 3, 1, 1)

        channels = np.ravel(data['region_channels'].astype(int)).astype(str)

        for i in range(len(data['label_name'])):
            slayout.addWidget(QLabel(data['label_name'][i]), i + 1, 0, 1, 1)
            slayout.addWidget(QLabel(data['label_acronym'][i]), i + 1, 1, 1, 1)
            slayout.addWidget(QLabel(channels[i]), i + 1, 2, 1, 1)
            clb = QLabel()
            da_color = QColor(data['label_color'][i][0], data['label_color'][i][1], data['label_color'][i][2], 255).name()
            clb.setStyleSheet('QLabel {background-color: ' + da_color + '; width: 20px; height: 20px}')
            slayout.addWidget(clb, i + 1, 3, 1, 1)

        self.data = np.cumsum(data['block_count'])
        self.data = self.data / self.data[-1] * 2
        self.data = self.data[::-1]
        # self.label = label[::-1]
        self.colors = data['chn_lines_color'][::-1]

        plot_frame = QFrame()
        plot_frame.setMaximumWidth(300)
        plot_frame.setMinimumWidth(300)
        view_layout = QGridLayout(plot_frame)
        view_layout.setSpacing(0)
        view_layout.setContentsMargins(0, 0, 0, 0)

        w = pg.GraphicsLayoutWidget()
        view = w.addViewBox()
        view.setAspectLocked()
        view.invertY(True)

        # draw tips
        top_value = self.data[0]
        da_tip_loc = np.array([[0.7, top_value], [1, top_value + 0.7], [1.3, top_value]])
        tips = pg.PlotDataItem(da_tip_loc, connect='all', fillLevel=0, fillBrush=pg.mkBrush(color=(128, 128, 128)))
        view.addItem(tips)

        # create bar chart
        self.bg_list = []
        for i in range(len(self.data)):
            bg = pg.BarGraphItem(x=[1], height=self.data[i], width=0.6,
                                 brush=QColor(self.colors[i][0], self.colors[i][1], self.colors[i][2], 255))
            self.bg_list.append(bg)
            view.addItem(self.bg_list[i])

        view_layout.addWidget(w, 0, 0, 1, 1)

        # ok button, used to close window
        ok_btn = QDialogButtonBox(QDialogButtonBox.Ok)
        ok_btn.accepted.connect(self.accept)

        # add widget to layout
        layout.addWidget(self.label, 0, 0, 1, 4)
        layout.addWidget(ang_label, 1, 0, 1, 1)

        layout.addWidget(angle_length_group, 1, 1, 1, 3)

        layout.addWidget(QLabel(), 1, 2, 1, 1)
        layout.addWidget(QLabel(), 1, 3, 1, 1)

        layout.addWidget(plot_frame, 3, 0, 1, 1)
        layout.addWidget(sec_group, 3, 1, 1, 3)
        layout.addWidget(ok_btn, 4, 0, 1, 4)
        self.setLayout(layout)

    def accept(self) -> None:
        self.close()

    def set_probe_color(self, color):
        self.label.setStyleSheet('QLabel {background-color: ' + color + ';}')


class SinglePiece(QWidget):
    sig_clicked = pyqtSignal(object)
    sig_name_changed = pyqtSignal(object)

    def __init__(self, parent=None, index=0, object_type='probes', object_icon=None, group_index=0):
        QWidget.__init__(self, parent=parent)

        self.inactive_style = 'QFrame{background-color:rgb(83, 83, 83); border: 1px solid rgb(128, 128, 128);}'
        self.active_style = 'QFrame{background-color:rgb(107, 107, 107); border: 1px solid rgb(128, 128, 128);}'

        self.id = index
        self.object_name = object_type
        self.object_type = object_type
        self.active = True
        self.group_id = group_index

        self.tbnail = QPushButton()
        self.tbnail.setFixedSize(QSize(40, 40))
        self.tbnail.setStyleSheet(eye_button_style)
        self.tbnail.setIcon(object_icon)
        self.tbnail.setIconSize(QSize(20, 20))
        self.tbnail.clicked.connect(self.on_click)

        self.text_btn = QDoubleButton()
        self.text_btn.setStyleSheet(text_btn_style)
        self.text_btn.setFixedSize(QSize(240, 40))
        self.text_btn.left_clicked.connect(self.on_click)
        self.text_btn.double_clicked.connect(self.on_doubleclick)

        self.l_line_edit = QLineEdit()
        self.l_line_edit.setStyleSheet(line_edit_style)
        self.l_line_edit.setFixedWidth(240)
        self.l_line_edit.editingFinished.connect(self.enter_pressed)
        self.l_line_edit.setVisible(False)

        self.inner_frame = QFrame()
        self.inner_frame.setStyleSheet(self.active_style)
        self.inner_layout = QHBoxLayout(self.inner_frame)
        self.inner_layout.setContentsMargins(0, 0, 0, 0)
        self.inner_layout.setSpacing(0)
        self.inner_layout.setAlignment(Qt.AlignVCenter)
        self.inner_layout.addWidget(self.tbnail)
        self.inner_layout.addSpacing(5)
        self.inner_layout.addWidget(self.text_btn)
        self.inner_layout.addWidget(self.l_line_edit)
        self.inner_layout.addStretch()

        outer_layout = QHBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)
        outer_layout.setAlignment(Qt.AlignVCenter)
        outer_layout.addWidget(self.inner_frame)

        self.setLayout(outer_layout)
        self.setFixedHeight(40)
        # self.show()

    @pyqtSlot()
    def on_click(self):
        print("Click")
        self.set_checked(True)
        self.sig_clicked.emit(self.id)

    @pyqtSlot()
    def on_doubleclick(self):
        self.l_line_edit.setText(self.text_btn.text())
        self.l_line_edit.setVisible(True)
        self.text_btn.setVisible(False)
        self.l_line_edit.setFocus(True)
        self.set_checked(True)
        self.sig_clicked.emit(self.id)

    @pyqtSlot()
    def enter_pressed(self):
        print('return')
        da_text = self.l_line_edit.text()
        if '-' not in da_text or 'piece' not in da_text:
            return
        self.l_line_edit.setVisible(False)
        self.text_btn.setText(self.l_line_edit.text())
        self.object_name = self.l_line_edit.text()
        self.text_btn.setVisible(True)
        self.sig_name_changed.emit((self.id, self.object_name, self.group_id))

    def is_checked(self):
        return self.active

    def set_checked(self, check):
        self.active = check
        if not self.active:
            self.inner_frame.setStyleSheet(self.inactive_style)
        else:
            self.inner_frame.setStyleSheet(self.active_style)


class RegisteredObject(QWidget):
    sig_object_color_changed = pyqtSignal(object)
    eye_clicked = pyqtSignal(object)
    sig_clicked = pyqtSignal(object)

    def __init__(self, parent=None, index=0, object_type='merged probes', object_icon=None, group_index=0):
        QWidget.__init__(self, parent=parent)

        self.inactive_style = 'QFrame{background-color:rgb(83, 83, 83); border: 1px solid rgb(128, 128, 128);}'
        self.active_style = 'QFrame{background-color:rgb(107, 107, 107); border: 1px solid rgb(128, 128, 128);}'

        self.color = QColor(randint(0, 255), randint(0, 255), randint(0, 255), 255)
        self.icon_back = 'border:1px solid black; background-color: {}'.format(self.color.name())

        self.id = index
        self.object_type = object_type
        self.object_name = object_type
        self.active = True
        self.vis = True
        self.group_id = group_index

        self.eye_button = QPushButton()
        self.eye_button.setFixedSize(QSize(40, 40))
        self.eye_button.setStyleSheet(eye_button_style)
        self.eye_button.setCheckable(True)
        eye_icon = QIcon()
        eye_icon.addPixmap(QPixmap("icons/layers/eye_on.png"), QIcon.Normal, QIcon.Off)
        eye_icon.addPixmap(QPixmap("icons/layers/eye_off.png"), QIcon.Normal, QIcon.On)
        self.eye_button.setIcon(eye_icon)
        self.eye_button.setIconSize(QSize(20, 20))
        self.eye_button.clicked.connect(self.eye_on_click)

        self.tbnail = QPushButton()
        self.tbnail.setStyleSheet(self.icon_back)
        self.tbnail.setIcon(object_icon)
        self.tbnail.setIconSize(QSize(20, 20))
        self.tbnail.clicked.connect(self.change_object_color)

        self.text_btn = QPushButton(self.object_name)
        self.text_btn.setStyleSheet(text_btn_style)
        self.text_btn.setFixedHeight(40)
        # self.text_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
        self.text_btn.clicked.connect(self.on_click)

        self.inner_frame = QFrame()
        self.inner_frame.setStyleSheet(self.active_style)
        self.inner_layout = QHBoxLayout(self.inner_frame)
        self.inner_layout.setContentsMargins(0, 0, 0, 0)
        self.inner_layout.setSpacing(0)
        self.inner_layout.setAlignment(Qt.AlignVCenter)
        self.inner_layout.addWidget(self.eye_button)
        self.inner_layout.addSpacing(5)
        self.inner_layout.addWidget(self.tbnail)
        self.inner_layout.addSpacing(5)
        self.inner_layout.addWidget(self.text_btn)
        self.inner_layout.addStretch()

        outer_layout = QHBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)
        outer_layout.setAlignment(Qt.AlignVCenter)
        outer_layout.addWidget(self.inner_frame)

        self.setLayout(outer_layout)
        self.setFixedHeight(40)

    def set_icon_style(self, color):
        self.color = color
        self.icon_back = 'border:1px solid black; background-color: {}'.format(color.name())
        self.tbnail.setStyleSheet(self.icon_back)

    def change_object_color(self):
        self.sig_object_color_changed.emit(self.id)

    def eye_on_click(self):
        if self.eye_button.isChecked():
            self.vis = False
        else:
            self.vis = True
        self.set_checked(True)
        self.tbnail.setEnabled(self.vis)
        self.text_btn.setEnabled(self.vis)
        self.eye_clicked.emit((self.id, self.vis))

    def set_checked(self, check):
        self.active = check
        if not self.active:
            self.inner_frame.setStyleSheet(self.inactive_style)
        else:
            self.inner_frame.setStyleSheet(self.active_style)

    def on_click(self):
        print("Click")
        self.set_checked(True)
        self.sig_clicked.emit(self.id)

    def is_checked(self):
        return self.active


class ObjectControl(QObject):
    """
    only pieces' name can be changed, the merged can not, so far
    """

    class SignalProxy(QObject):
        sigOpacityChanged = pyqtSignal(object)
        sigVisChanged = pyqtSignal(object)
        sigDeleteObject = pyqtSignal(object)
        sigColorChanged = pyqtSignal(object)
        sigSizeChanged = pyqtSignal(object)
        sigBlendModeChanged = pyqtSignal(object)

    def __init__(self, parent=None):

        self._sigprox = ObjectControl.SignalProxy()
        self.sig_opacity_changed = self._sigprox.sigOpacityChanged
        self.sig_visible_changed = self._sigprox.sigVisChanged
        self.sig_delete_object = self._sigprox.sigDeleteObject
        self.sig_color_changed = self._sigprox.sigColorChanged
        self.sig_size_changed = self._sigprox.sigSizeChanged
        self.sig_blend_mode_changed = self._sigprox.sigBlendModeChanged

        QObject.__init__(self)

        self.default_size_val = 2
        self.default_opacity_val = 100

        self.current_obj_index = None

        self.obj_count = 0

        self.probe_piece_count = 0
        self.cell_piece_count = 0
        self.drawing_piece_count = 0
        self.virus_piece_count = 0
        self.contour_piece_count = 0

        self.reg_probe_count = 0
        self.reg_cell_count = 0
        self.reg_drawing_count = 0
        self.reg_virus_count = 0
        self.reg_contour_count = 0

        self.obj_list = []  # widgets
        self.obj_id = []  # identity
        self.obj_name = []  # names, initially the same as type, can be changed freely ???
        self.obj_type = []  # type
        self.obj_data = []  # data
        self.obj_group_id = []  # group identity
        self.obj_size = []  # size
        self.obj_opacity = []
        self.obj_comp_mode = []

        self.probe_icon = QIcon('icons/sidebar/probe.svg')
        self.virus_icon = QIcon('icons/sidebar/virus.svg')
        self.drawing_icon = QIcon('icons/toolbar/pencil.svg')
        self.cell_icon = QIcon('icons/toolbar/location.svg')
        self.contour_icon = QIcon('icons/sidebar/contour.svg')

        combo_label = QLabel('Composition:')
        combo_label.setFixedWidth(80)
        self.obj_blend_combo = QComboBox()
        self.obj_blend_combo.setEditable(False)
        combo_value = ['opaque', 'translucent', 'additive']
        self.obj_blend_combo.addItems(combo_value)
        self.obj_blend_combo.setCurrentText('opaque')
        self.obj_blend_combo.currentTextChanged.connect(self.blend_mode_changed)
        combo_wrap = QFrame()
        combo_wrap_layout = QHBoxLayout(combo_wrap)
        combo_wrap_layout.setContentsMargins(0, 0, 0, 0)
        combo_wrap_layout.setSpacing(5)
        combo_wrap_layout.addWidget(combo_label)
        combo_wrap_layout.addWidget(self.obj_blend_combo)

        obj_opacity_label = QLabel('Opacity:')
        obj_opacity_label.setFixedWidth(80)
        self.obj_opacity_slider = QSlider(Qt.Horizontal)
        self.obj_opacity_slider.setMaximum(100)
        self.obj_opacity_slider.setMinimum(0)
        self.obj_opacity_slider.setValue(100)
        self.obj_opacity_slider.valueChanged.connect(self.change_opacity_label_value)
        self.obj_opacity_slider.sliderMoved.connect(self.send_opacity_changed_signal)
        self.obj_opacity_val_label = QLabel('100%')
        self.obj_opacity_val_label.setFixedWidth(40)
        opacity_wrap = QFrame()
        opacity_wrap_layout = QHBoxLayout(opacity_wrap)
        opacity_wrap_layout.setContentsMargins(0, 0, 0, 0)
        opacity_wrap_layout.setSpacing(5)
        opacity_wrap_layout.addWidget(obj_opacity_label)
        opacity_wrap_layout.addWidget(self.obj_opacity_slider)
        opacity_wrap_layout.addWidget(self.obj_opacity_val_label)

        obj_size_label = QLabel('Size/Width: ')
        obj_size_label.setFixedWidth(80)
        self.obj_size_slider = QSlider(QtCore.Qt.Horizontal)
        self.obj_size_slider.setValue(2)
        self.obj_size_slider.setMinimum(1)
        self.obj_size_slider.setMaximum(10)
        self.obj_size_slider.valueChanged.connect(self.change_size_label_value)
        self.obj_size_slider.sliderMoved.connect(self.send_size_changed_signal)
        self.obj_size_val_label = QLabel('2')
        self.obj_size_val_label.setAlignment(Qt.AlignCenter)
        self.obj_size_val_label.setFixedWidth(40)
        size_wrap = QFrame()
        size_wrap_layout = QHBoxLayout(size_wrap)
        size_wrap_layout.setContentsMargins(0, 0, 0, 0)
        size_wrap_layout.setSpacing(5)
        size_wrap_layout.addWidget(obj_size_label)
        size_wrap_layout.addWidget(self.obj_size_slider)
        size_wrap_layout.addWidget(self.obj_size_val_label)

        top_frame = QFrame()
        top_layout = QVBoxLayout(top_frame)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(0)
        top_layout.addWidget(combo_wrap)
        top_layout.addSpacing(10)
        top_layout.addWidget(opacity_wrap)
        top_layout.addSpacing(10)
        top_layout.addWidget(size_wrap)
        top_layout.addSpacing(10)

        self.layer_frame = QFrame()
        self.layer_frame.setStyleSheet('background: transparent; border: 0px;')
        self.layer_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layer_layout = QBoxLayout(QBoxLayout.BottomToTop, self.layer_frame)
        self.layer_layout.setAlignment(Qt.AlignBottom)
        self.layer_layout.setContentsMargins(0, 0, 0, 0)
        self.layer_layout.setSpacing(5)

        self.layer_scroll = QScrollArea()
        self.layer_scroll.setStyleSheet('background: transparent; border: 0px;')
        self.layer_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layer_scroll.setWidget(self.layer_frame)
        self.layer_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.layer_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.layer_scroll.setWidgetResizable(True)

        mid_frame = QFrame()
        mid_frame.setStyleSheet('background: transparent; border: 1px solid rgb(128, 128, 128);')
        mid_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        mid_layout = QGridLayout(mid_frame)
        mid_layout.setContentsMargins(0, 0, 0, 0)
        mid_layout.setSpacing(0)
        mid_layout.setAlignment(Qt.AlignBottom)
        mid_layout.addWidget(self.layer_scroll, 0, 0, 1, 1)

        self.outer_frame = QFrame()
        self.outer_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        outer_layout = QVBoxLayout(self.outer_frame)
        outer_layout.setSpacing(0)
        outer_layout.addWidget(top_frame)
        outer_layout.addWidget(mid_frame)

        # bottom buttons
        self.merge_probe_btn = QPushButton()
        self.merge_probe_btn.setFixedSize(24, 24)
        self.merge_probe_btn.setStyleSheet(btm_style)
        self.merge_probe_btn.setIcon(QIcon('icons/sidebar/probe.svg'))
        self.merge_probe_btn.setIconSize(QSize(20, 20))

        self.merge_drawing_btn = QPushButton()
        self.merge_drawing_btn.setFixedSize(24, 24)
        self.merge_drawing_btn.setStyleSheet(btm_style)
        self.merge_drawing_btn.setIcon(QIcon('icons/toolbar/pencil.svg'))
        self.merge_drawing_btn.setIconSize(QSize(20, 20))

        self.merge_cell_btn = QPushButton()
        self.merge_cell_btn.setFixedSize(24, 24)
        self.merge_cell_btn.setStyleSheet(btm_style)
        self.merge_cell_btn.setIcon(QIcon('icons/toolbar/location.svg'))
        self.merge_cell_btn.setIconSize(QSize(20, 20))

        self.merge_virus_btn = QPushButton()
        self.merge_virus_btn.setFixedSize(24, 24)
        self.merge_virus_btn.setStyleSheet(btm_style)
        self.merge_virus_btn.setIcon(QIcon('icons/sidebar/virus.svg'))
        self.merge_virus_btn.setIconSize(QSize(20, 20))

        self.merge_contour_btn = QPushButton()
        self.merge_contour_btn.setFixedSize(24, 24)
        self.merge_contour_btn.setStyleSheet(btm_style)
        self.merge_contour_btn.setIcon(QIcon('icons/sidebar/contour.svg'))
        self.merge_contour_btn.setIconSize(QSize(20, 20))

        self.add_object_btn = QPushButton()
        self.add_object_btn.setFixedSize(24, 24)
        self.add_object_btn.setStyleSheet(btm_style)
        self.add_object_btn.setIcon(QIcon('icons/sidebar/add.png'))
        self.add_object_btn.setIconSize(QSize(20, 20))

        self.delete_object_btn = QPushButton()
        self.delete_object_btn.setFixedSize(24, 24)
        self.delete_object_btn.setStyleSheet(btm_style)
        self.delete_object_btn.setIcon(QIcon('icons/sidebar/trash.png'))
        self.delete_object_btn.setIconSize(QSize(20, 20))
        self.delete_object_btn.clicked.connect(self.delete_object_btn_clicked)

    def blend_mode_changed(self):
        blend_mode = self.obj_blend_combo.currentText()
        if 'merged' not in self.obj_type[self.current_obj_index]:
            return
        if blend_mode != self.obj_comp_mode[self.current_obj_index]:
            self.obj_comp_mode[self.current_obj_index] = blend_mode
            self.sig_blend_mode_changed.emit(blend_mode)

    def change_opacity_label_value(self):
        da_val = self.obj_opacity_slider.value()
        self.obj_opacity_val_label.setText('{} %'.format(da_val))

    def send_opacity_changed_signal(self):
        da_val = self.obj_opacity_slider.value()
        if 'merged' not in self.obj_type[self.current_obj_index]:
            self.obj_opacity_slider.setValue(da_val)
            return
        self.obj_opacity[self.current_obj_index] = da_val
        self.sig_opacity_changed.emit(da_val)

    def change_size_label_value(self):
        da_val = self.obj_size_slider.value()
        self.obj_size_val_label.setText(str(da_val))

    def send_size_changed_signal(self):
        da_val = self.obj_size_slider.value()
        if 'merged' not in self.obj_type[self.current_obj_index]:
            self.obj_size_slider.setValue(da_val)
            return
        self.obj_size[self.current_obj_index] = da_val
        self.sig_size_changed.emit((self.obj_type[self.current_obj_index], da_val))

    def obj_piece_name_changed(self, ev):
        clicked_id = ev[0]
        name = ev[1]
        clicked_index = np.where(np.ravel(self.obj_id) == clicked_id)[0][0]
        self.current_obj_index = clicked_index
        self.obj_name[clicked_index] = name

    def delete_object_btn_clicked(self):
        if self.current_obj_index is None:
            return
        obj_type = self.obj_type[self.current_obj_index]
        if 'probe' in obj_type:
            if 'merged' in obj_type:
                self.reg_probe_count -= 1
            else:
                self.probe_piece_count -= 1
        elif 'virus' in obj_type:
            if 'merged' in obj_type:
                self.reg_virus_count -= 1
            else:
                self.virus_piece_count -= 1
        elif 'cell' in obj_type:
            if 'merged' in obj_type:
                self.reg_cell_count -= 1
            else:
                self.cell_piece_count -= 1
        elif 'contour' in obj_type:
            if 'merged' in obj_type:
                self.reg_contour_count -= 1
            else:
                self.contour_piece_count -= 1
        else:
            if 'merged' in obj_type:
                self.reg_drawing_count -= 1
            else:
                self.drawing_piece_count -= 1
        self.delete_objects(self.current_obj_index)

    def obj_clicked(self, clicked_id):
        self.set_active_layer_to_current(clicked_id)
        if 'merged' in self.obj_type[self.current_obj_index]:
            self.obj_info_on_click()

    def obj_info_on_click(self):
        da_data = self.obj_data[self.current_obj_index]
        da_name = self.obj_name[self.current_obj_index]
        if 'probe' in self.obj_type[self.current_obj_index]:
            self.info_window = ProbeInfoWindow(da_name, da_data)
        elif 'virus' in self.obj_type[self.current_obj_index]:
            self.info_window = VirusInfoWindow(da_name, da_data)
        elif 'cell' in self.obj_type[self.current_obj_index]:
            self.info_window = CellsInfoWindow(da_name, da_data)
        else:
            return
        self.info_window.exec()

    def set_active_layer_to_current(self, clicked_id):
        previous_obj_id = self.obj_id[self.current_obj_index]
        size_val = self.obj_size_slider.value()
        opacity_val = self.obj_opacity_slider.value()
        compo_mode = self.obj_blend_combo.currentText()
        if previous_obj_id != clicked_id:
            active_index = np.where(np.ravel(self.obj_id) == clicked_id)[0][0]
            self.current_obj_index = active_index
            # self.obj_list[active_index].set_checked(True)
            inactive_id = np.where(np.ravel(self.obj_id) == previous_obj_id)[0][0]
            self.obj_list[inactive_id].set_checked(False)
            if 'merged' in self.obj_type[self.current_obj_index]:
                if self.obj_size[self.current_obj_index] != size_val:
                    self.obj_size_slider.setValue(self.obj_size[self.current_obj_index])
                if self.obj_opacity[self.current_obj_index] != opacity_val:
                    self.obj_opacity_slider.setValue(self.obj_opacity[self.current_obj_index])
                if self.obj_comp_mode[self.current_obj_index] != compo_mode:
                    self.obj_blend_combo.setCurrentText(self.obj_comp_mode[self.current_obj_index])
        else:
            return

    def obj_color_changed(self, clicked_id):
        self.set_active_layer_to_current(clicked_id)
        color = QColorDialog.getColor()
        if color.isValid():
            self.obj_list[self.current_obj_index].set_icon_style(color)
            da_color = (color.red(), color.green(), color.blue(), 255)
            self.sig_color_changed.emit((self.current_obj_index, da_color))

    def obj_eye_clicked(self, ev):
        clicked_id = ev[0]
        vis = ev[1]
        self.set_active_layer_to_current(clicked_id)
        self.sig_visible_changed.emit((self.current_obj_index, vis))

    # delete a object
    def delete_objects(self, delete_index):
        del_ind = np.ravel(delete_index)
        if len(del_ind) > 1:
            del_ind = np.sort(delete_index)[::-1]

        current_obj_id = self.obj_id[self.current_obj_index]
        for da_ind in del_ind:
            self.layer_layout.removeWidget(self.obj_list[da_ind])
            self.obj_list[da_ind].deleteLater()
            del self.obj_list[da_ind]
            del self.obj_id[da_ind]
            del self.obj_name[da_ind]
            del self.obj_group_id[da_ind]
            del self.obj_type[da_ind]
            del self.obj_data[da_ind]
            del self.obj_comp_mode[da_ind]
            del self.obj_opacity[da_ind]
            del self.obj_size[da_ind]
            self.sig_delete_object.emit(da_ind)
        if self.current_obj_index in del_ind:
            if self.obj_list:
                self.obj_list[-1].set_checked(True)
                self.current_obj_index = len(self.obj_list) - 1
            else:
                self.current_obj_index = None
        else:
            active_index = np.where(np.ravel(self.obj_id) == current_obj_id)[0][0]
            self.current_obj_index = active_index

    #
    def get_index_and_icon(self, object_type):
        if 'probe' in object_type:
            if 'merged' in object_type:
                group_index = self.reg_probe_count
            else:
                group_index = self.probe_piece_count
            object_icon = self.probe_icon
        elif 'virus' in object_type:
            if 'merged' in object_type:
                group_index = self.reg_virus_count
            else:
                group_index = self.virus_piece_count
            object_icon = self.virus_icon
        elif 'cell' in object_type:
            if 'merged' in object_type:
                group_index = self.reg_cell_count
            else:
                group_index = self.cell_piece_count
            object_icon = self.cell_icon
        elif 'contour' in object_type:
            if 'merged' in object_type:
                group_index = self.reg_contour_count
            else:
                group_index = self.contour_piece_count
            object_icon = self.contour_icon
        elif 'drawing' in object_type:
            if 'merged' in object_type:
                group_index = self.reg_drawing_count
            else:
                group_index = self.drawing_piece_count
            object_icon = self.drawing_icon
        else:
            group_index = None
            object_icon = None
        return group_index, object_icon

    def add_object(self, object_type, object_data):
        group_index, object_icon = self.get_index_and_icon(object_type)
        if group_index is None:
            return
        self.obj_id.append(self.obj_count)
        self.obj_data.append(object_data)
        self.obj_name.append("{} {}".format(object_type, group_index + 1))
        self.obj_type.append(object_type)
        if 'merged' in object_type:
            print('merged')
            new_layer = RegisteredObject(index=self.obj_count, object_type=object_type,
                                         object_icon=object_icon, group_index=group_index)
            new_layer.eye_clicked.connect(self.obj_eye_clicked)
            new_layer.sig_object_color_changed.connect(self.obj_color_changed)
            self.obj_opacity.append(self.default_opacity_val)
            self.obj_size.append(self.default_size_val)
            self.obj_comp_mode.append('opaque')
            da_color = (new_layer.color.red(), new_layer.color.green(), new_layer.color.blue(), 255)
            self.obj_data[-1]['vis_color'] = da_color
            if self.obj_size_slider.value() != self.default_size_val:
                self.obj_size_slider.setValue(self.default_size_val)
            if self.obj_opacity_slider.value() != self.default_opacity_val:
                self.obj_opacity_slider.setValue(self.default_opacity_val)
            if self.obj_blend_combo.currentText() != 'opaque':
                self.obj_blend_combo.setCurrentText('opaque')

        else:
            new_layer = SinglePiece(index=self.obj_count, object_type=object_type,
                                    object_icon=object_icon, group_index=group_index)
            new_layer.sig_name_changed.connect(self.obj_piece_name_changed)
            self.obj_opacity.append([])
            self.obj_size.append([])
            self.obj_comp_mode.append([])

        new_layer.text_btn.setText("{} {}".format(object_type, group_index + 1))
        new_layer.set_checked(True)
        new_layer.sig_clicked.connect(self.obj_clicked)
        self.obj_list.append(new_layer)
        self.obj_group_id.append(group_index)

        active_index = np.where(np.ravel(self.obj_id) == self.obj_count)[0][0]
        if self.current_obj_index is None:
            self.current_obj_index = active_index
        else:
            print(self.current_obj_index)
            self.obj_list[self.current_obj_index].set_checked(False)
            self.current_obj_index = active_index

        self.layer_layout.addWidget(self.obj_list[-1])
        self.obj_count += 1
        if 'probe' in object_type:
            if 'merged' in object_type:
                self.reg_probe_count += 1
            else:
                self.probe_piece_count += 1
        elif 'virus' in object_type:
            if 'merged' in object_type:
                self.reg_virus_count += 1
            else:
                self.virus_piece_count += 1
        elif 'cell' in object_type:
            if 'merged' in object_type:
                self.reg_cell_count += 1
            else:
                self.cell_piece_count += 1
        elif 'contour' in object_type:
            if 'merged' in object_type:
                self.reg_contour_count += 1
            else:
                self.contour_piece_count += 1
        else:
            if 'merged' in object_type:
                self.reg_drawing_count += 1
            else:
                self.drawing_piece_count += 1

    # merge object piece
    def get_merged_data(self, obj_type='probe'):
        if obj_type not in ['probe', 'virus', 'contour', 'drawing', 'cell']:
            return
        n_obj = len(self.obj_id)
        cind = [ind for ind in range(n_obj) if obj_type in self.obj_type[ind] and 'merged' not in self.obj_type[ind]]
        print('cind', cind)
        da_type_object_names = np.ravel(self.obj_name)[cind]
        n_pieces = len(da_type_object_names)
        pieces_names = []
        for i in range(n_pieces):
            da_name = da_type_object_names[i]
            da_name = da_name.replace(" ", "")
            da_name_split = da_name.split('-')
            pieces_names.append(da_name_split[0])
        unique_object_names = np.unique(pieces_names)
        n_object = len(unique_object_names)
        data = [[] for i in range(n_object)]
        for i in range(n_object):
            da_piece_name = unique_object_names[i]
            da_piece_ind_in_obj_order = [cind[ind] for ind in range(n_pieces) if pieces_names[ind] == da_piece_name]
            temp = self.obj_data[da_piece_ind_in_obj_order[0]].T
            if len(da_piece_ind_in_obj_order) > 1:
                for j in range(1, len(da_piece_ind_in_obj_order)):
                    print(self.obj_data[da_piece_ind_in_obj_order[j]].T)
                    temp = np.hstack([temp, self.obj_data[da_piece_ind_in_obj_order[j]].T])
            data[i] = temp.T
            print(data[i])
        if obj_type == 'probe':
            self.probe_piece_count = 0
        elif obj_type == 'virus':
            self.virus_piece_count = 0
        elif obj_type == 'contour':
            self.contour_piece_count = 0
        elif obj_type == 'drawing':
            self.drawing_piece_count = 0
        else:
            self.cell_piece_count = 0
        self.delete_objects(cind)
        print(self.current_obj_index)
        return data

    # get obj data
    def get_obj_data(self):
        data = {'obj_list': self.obj_list,
                'obj_id': self.obj_id,
                'obj_name':  self.obj_name,
                'obj_type': self.obj_type,
                'obj_data': self.obj_data,
                'obj_group_id': self.obj_group_id,
                'obj_size': self.obj_size,
                'obj_opacity': self.obj_opacity,
                'obj_comp_mode': self.obj_comp_mode,
                'obj_count': self.obj_count,
                'current_obj_index': self.current_obj_index}
        return data

    def set_obj_data(self, data):
        self.obj_list = data['obj_list']
        self.obj_id = data['obj_id']
        self.obj_name = data['obj_name']
        self.obj_type = data['obj_type']
        self.obj_data = data['obj_data']
        self.obj_group_id = data['obj_group_id']
        self.obj_size = data['obj_size']
        self.obj_opacity = data['obj_opacity']
        self.obj_comp_mode = data['obj_comp_mode']
        self.obj_count = data['obj_count']
        self.current_obj_index = data['current_obj_index']

        for i in range(len(self.obj_list)):
            self.layer_layout.addWidget(self.obj_list[i])




