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


class VirusInfoWindow(QDialog):
    def __init__(self, num, probe_color, theta, phi, r, label_name, label_ano, values, channels, colors):
        super().__init__()

        self.setWindowTitle("Virus Information Window")


class ProbeInfoWindow(QDialog):
    def __init__(self, group_id, data):
        super().__init__()

        self.setWindowTitle("Probe Information Window")

        # 'sp': start_pnt, 'ep': end_pnt, 'direction': direction, 'data': data,
        # 'new_sp': new_sp, 'new_ep': new_ep, 'theta': theta, 'phi': phi,
        # 'chn_lines_labels': chn_lines_labels, 'chn_lines_color': chn_line_color,
        # 'region_label': region_label, 'region_length': region_length, 'region_channels': region_channels,
        # 'label_name': label_names, 'label_acronym': label_acronym, 'label_color': label_color


        layout = QGridLayout()
        self.label = QLabel("Probe % d " % group_id)
        self.label.setStyleSheet('QLabel {background-color: ' + data['probe_color'] + ';}')
        self.label.setFont(QFont('Arial', 20))

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

        # self.l_line_edit = LineEditEntered()
        # self.l_line_edit.setStyleSheet('border:None; color:white; padding-left:5px; background-color:rgb(83, 83, 83);')
        # # self.l_line_edit.setText(self.text_btn.text())
        # self.l_line_edit.setFixedWidth(100)
        # self.l_line_edit.sig_return_pressed.connect(self.enter_pressed)

        self.l_line_edit = QLineEdit()
        self.l_line_edit.setStyleSheet('border:None; color:white; padding-left:5px; background-color:rgb(83, 83, 83);')
        # self.l_line_edit.setText(self.text_btn.text())
        self.l_line_edit.setFixedWidth(120)
        self.l_line_edit.editingFinished.connect(self.enter_pressed)

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
    """

    """

    class SignalProxy(QObject):
        sigOpacityChanged = pyqtSignal(object)
        sigVisChanged = pyqtSignal(object)

    def __init__(self, parent=None):

        self._sigprox = ObjectControl.SignalProxy()
        self.sig_opacity_changed = self._sigprox.sigOpacityChanged
        self.sig_visible_changed = self._sigprox.sigVisChanged

        QObject.__init__(self)

        styles = Styles()

        self.current_obj_ind = None

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

        self.obj_list = []
        self.obj_index = []
        self.obj_name = []
        self.obj_data = []

        self.piece_list = []
        self.piece_index = []
        self.piece_name = []
        self.piece_data = []

        self.probe_icon = QIcon('icons/sidebar/probe.svg')
        self.virus_icon = QIcon('icons/sidebar/virus.svg')
        self.drawing_icon = QIcon('icons/toolbar/pencil.svg')
        self.cell_icon = QIcon('icons/toolbar/location.svg')
        self.contour_icon = QIcon('icons/sidebar/contour.svg')

        combo_label = QLabel('Composition:')
        self.obj_blend_combo = QComboBox()
        self.obj_blend_combo.setEditable(False)
        combo_value = ['Multiply', 'Overlay', 'SourceOver']
        self.obj_blend_combo.addItems(combo_value)
        self.obj_blend_combo.setCurrentText('Multiply')
        self.obj_blend_combo.setFixedHeight(24)
        combo_list = QListView(self.obj_blend_combo)
        combo_list.setStyleSheet(styles.text_combo_list_style)
        self.obj_blend_combo.setView(combo_list)

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

        top_frame = QFrame()
        top_layout = QGridLayout(top_frame)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(5)
        top_layout.addWidget(combo_label, 0, 0, 1, 1)
        top_layout.addWidget(self.obj_blend_combo, 0, 1, 1, 3)
        top_layout.addWidget(obj_opacity_label, 1, 0, 1, 1)
        top_layout.addWidget(self.obj_opacity_slider, 1, 1, 1, 2)
        top_layout.addWidget(self.obj_opacity_val_label, 1, 3, 1, 1)
        # top_layout.addWidget(point_size_label, 2, 0, 1, 1)
        # top_layout.addWidget(self.point_size_slider, 2, 1, 1, 2)
        # top_layout.addWidget(self.obj_opacity_val_label, 1, 3, 1, 1)
        # top_layout.addWidget(line_width_label, 3, 0, 1, 1)
        # top_layout.addWidget(self.line_width_slider, 3, 1, 1, 2)

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

    def change_opacity_label_value(self):
        da_val = self.layer_opacity_slider.value()
        self.layer_opacity_val_label.setText('{} %'.format(da_val))
        self.sig_opacity_changed.emit(da_val)

    def obj_piece_name_changed(self, ev):
        id = ev[0]
        name = ev[1]
        cind = np.where(np.ravel(self.obj_index) == id)[0][0]
        self.obj_name[cind] = name

    def delete_object_btn_clicked(self):
        if self.current_obj_ind is None:
            return
        ind2del = np.where(np.asarray(self.obj_index) == self.current_obj_ind)[0][0]
        if 'probe' in self.obj_name[self.current_obj_ind]:
            self.probe_piece_count -= 1
        elif 'virus' in self.obj_name[self.current_obj_ind]:
            self.virus_piece_count -= 1
        elif 'cell' in self.obj_name[self.current_obj_ind]:
            self.cell_piece_count -= 1
        elif 'contour' in self.obj_name[self.current_obj_ind]:
            self.contour_piece_count -= 1
        else:
            self.drawing_piece_count -= 1
        self.delete_objects(ind2del)

    def obj_clicked(self, ev):
        index = ev[0]
        self.set_active_layer_to_current(index)

    def set_active_layer_to_current(self, ind):
        if self.current_obj_ind != ind:
            id2unactive = np.where(np.ravel(self.obj_index) == self.current_obj_ind)[0][0]
            self.obj_list[id2unactive].set_checked(False)
            id2active = np.where(np.ravel(self.obj_index) == ind)[0][0]
            self.obj_list[id2active].set_checked(True)
            self.current_obj_ind = ind

    def delete_objects(self, inds):
        inds = np.ravel(inds)
        del_ind = np.sort(inds)[::-1]
        real_del_ind = [self.obj_index[ind] for ind in del_ind]
        for da_ind in del_ind:
            self.layer_layout.removeWidget(self.obj_list[da_ind])
            self.obj_list[da_ind].deleteLater()
            del self.obj_list[da_ind]
            del self.obj_index[da_ind]
            del self.obj_name[da_ind]
            del self.obj_data[da_ind]
        if self.current_obj_ind in real_del_ind:
            if self.obj_list:
                self.obj_list[-1].set_checked(True)
                self.current_obj_ind = self.obj_index[-1]
            else:
                self.current_obj_ind = None

    def add_object_piece(self, object_name, object_data=None):
        if 'probe' in object_name:
            group_index = self.probe_piece_count
            object_icon = self.probe_icon
        elif 'virus' in object_name:
            group_index = self.virus_piece_count
            object_icon = self.virus_icon
        elif 'cell' in object_name:
            group_index = self.cell_piece_count
            object_icon = self.cell_icon
        elif 'contour' in object_name:
            group_index = self.contour_piece_count
            object_icon = self.contour_icon
        elif 'drawing' in object_name:
            group_index = self.drawing_piece_count
            object_icon = self.drawing_icon
        else:
            return
        new_layer = SinglePiece(index=self.obj_count, object_name=object_name,
                                 object_icon=object_icon, group_index=group_index)
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
            ind2unactive = np.where(np.ravel(self.obj_index) == self.current_obj_ind)[0][0]
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
        elif 'contour' in object_name:
            self.contour_piece_count += 1
        else:
            self.drawing_piece_count += 1

    def add_merged_object(self, object_name, object_data=None):
        if 'probe' in object_name:
            group_index = self.reg_probe_count
            object_icon = self.probe_icon
        elif 'virus' in object_name:
            group_index = self.reg_virus_count
            object_icon = self.virus_icon
        elif 'cell' in object_name:
            group_index = self.reg_cell_count
            object_icon = self.cell_icon
        elif 'contour' in object_name:
            group_index = self.reg_contour_count
            object_icon = self.contour_icon
        elif 'drawing' in object_name:
            group_index = self.reg_drawing_count
            object_icon = self.drawing_icon
        else:
            return
        new_layer = RegisteredObject(index=self.obj_count, object_name=object_name,
                                     object_icon=object_icon, group_index=group_index)
        new_layer.text_btn.setText("{} {}".format(object_name, group_index + 1))
        new_layer.set_checked(True)
        self.obj_data.append(object_data)
        self.obj_list.append(new_layer)
        self.obj_index.append(self.obj_count)
        self.obj_name.append("{} {}".format(object_name, group_index + 1))

        if self.current_obj_ind is None:
            self.current_obj_ind = self.obj_count
        else:
            ind2unactive = np.where(np.ravel(self.obj_index) == self.current_obj_ind)[0][0]
            self.obj_list[ind2unactive].set_checked(False)
            self.current_obj_ind = self.obj_count

        self.layer_layout.addWidget(self.obj_list[-1])
        self.obj_count += 1
        if 'probe' in object_name:
            self.reg_probe_count += 1
        elif 'virus' in object_name:
            self.reg_virus_count += 1
        elif 'cell' in object_name:
            self.reg_cell_count += 1
        elif 'contour' in object_name:
            self.reg_contour_count += 1
        else:
            self.reg_drawing_count += 1





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



    # merge probe piece
    def merge_probe_pieces(self):
        if self.probe_piece_count == 0:
            return
        n_obj = len(self.obj_index)
        cind = [ind for ind in range(n_obj) if 'probe' in self.obj_name[ind] and 'merged' not in self.obj_name[ind]]
        print('cind', cind)
        all_probe_names = np.ravel(self.obj_name)[cind]
        n_pieces = len(all_probe_names)
        probe_names = []
        for i in range(n_pieces):
            da_name = all_probe_names[i]
            da_name = da_name.replace(" ", "")
            da_name_split = da_name.split('-')
            probe_names.append(da_name_split[0])
        unique_probe_names = np.unique(probe_names)
        n_probes = len(unique_probe_names)
        data = [[] for i in range(n_probes)]
        for i in range(n_probes):
            da_probe_name = unique_probe_names[i]
            da_probe_ind_in_obj_order = [cind[ind] for ind in range(n_pieces) if probe_names[ind] == da_probe_name]
            temp = self.obj_data[da_probe_ind_in_obj_order[0]].T
            if len(da_probe_ind_in_obj_order) > 1:
                for j in range(1, len(da_probe_ind_in_obj_order)):
                    print(self.obj_data[da_probe_ind_in_obj_order[j]].T)
                    temp = np.hstack([temp, self.obj_data[da_probe_ind_in_obj_order[j]].T])
            data[i] = temp.T
        self.probe_piece_count = 0
        self.delete_objects(cind)
        return data

    def merge_cells(self):
        print('merge_cells')

    def merge_virus_piece(self):
        if self.virus_piece_count == 0:
            return
        n_obj = len(self.obj_index)
        cind = [ind for ind in range(n_obj) if 'virus' in self.obj_name[ind] and 'merged' not in self.obj_name[ind]]
        print('cind', cind)
        all_virus_names = np.ravel(self.obj_name)[cind]
        n_pieces = len(all_virus_names)
        virus_names = []
        for i in range(n_pieces):
            da_name = all_virus_names[i]
            da_name = da_name.replace(" ", "")
            da_name_split = da_name.split('-')
            virus_names.append(da_name_split[0])
        unique_virus_names = np.unique(virus_names)
        n_virus = len(unique_virus_names)
        data = [[] for i in range(n_virus)]
        for i in range(n_virus):
            da_virus_name = unique_virus_names[i]
            da_virus_ind_in_obj_order = [cind[ind] for ind in range(n_pieces) if virus_names[ind] == da_virus_name]
            temp = self.obj_data[da_virus_ind_in_obj_order[0]].T
            if len(da_virus_ind_in_obj_order) > 1:
                for j in range(1, len(da_virus_ind_in_obj_order)):
                    print(self.obj_data[da_virus_ind_in_obj_order[j]].T)
                    temp = np.hstack([temp, self.obj_data[da_virus_ind_in_obj_order[j]].T])
            data[i] = temp.T
        self.virus_piece_count = 0
        self.delete_objects(cind)
        return data

    def merge_lines(self):
        print('merge_lines')

    def merge_boundaries(self):
        print('merge bnd')