import os
import sys
import numpy as np
import pyqtgraph as pg
import pyqtgraph.functions as fn
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import cv2

from .wtiles import *


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
    border-right: 1px solid rgb(128, 128, 128);
    border-top: None;
    border-bottom: None;
    border-radius:0px;
    background: transparent;
'''

text_btn_style = '''
QDoubleButton {
    background: transparent;
    border: None;
    border-radius:0px;
    text-align:left; 
    padding-left: 5px; 
    padding-right: 0px;
    color:rgb(240, 240, 240);
    margin: 0px;
    height: 60px;
    width: 160px;
}

QDoubleButton:disabled {
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
    height: 60px;
    width: 160px; 
}
'''


class SingleLayer(QWidget):
    sig_clicked = pyqtSignal(object)
    eye_clicked = pyqtSignal(object)
    sig_delete = pyqtSignal(object)

    def __init__(self, parent=None, layer_id=0, link='None'):
        QWidget.__init__(self, parent=parent)

        self.inactive_style = 'QFrame{background-color:rgb(83, 83, 83); border: 1px solid rgb(128, 128, 128);}'
        self.active_style = 'QFrame{background-color:rgb(107, 107, 107); border: 1px solid rgb(128, 128, 128);}'

        # self.setFixedWidth(280)
        self.id = layer_id
        self.link = link
        self.active = True
        self.vis = True
        self.thumbnail_data = None
        self.eye_button = QPushButton()
        self.eye_button.setFixedSize(QSize(30, 60))
        self.eye_button.setStyleSheet(eye_button_style)
        self.eye_button.setCheckable(True)
        eye_icon = QIcon()
        eye_icon.addPixmap(QPixmap("icons/layers/eye_on.png"), QIcon.Normal, QIcon.Off)
        eye_icon.addPixmap(QPixmap("icons/layers/eye_off.png"), QIcon.Normal, QIcon.On)
        self.eye_button.setIcon(eye_icon)
        self.eye_button.setIconSize(QSize(20, 20))
        self.eye_button.clicked.connect(self.eye_on_click)

        self.tbnail = QPushButton()
        self.tbnail.setStyleSheet('border:1px solid black; border-radius:0px;')
        self.tbnail.setFixedWidth(50)
        self.tbnail.clicked.connect(self.on_click)

        self.text_btn = QPushButton()
        self.text_btn.setStyleSheet(text_btn_style)
        self.text_btn.setText(link)
        self.text_btn.setFixedSize(QSize(140, 60))
        self.text_btn.clicked.connect(self.on_click)
        # self.text_btn.double_clicked.connect(self.on_doubleclick)

        # self.l_line_edit = QLineEdit()
        # self.l_line_edit.setStyleSheet(line_edit_style)
        # self.l_line_edit.setFixedSize(QSize(140, 60))
        # self.l_line_edit.editingFinished.connect(self.enter_pressed)
        # self.l_line_edit.setVisible(False)

        self.trash_button = QPushButton()
        self.trash_button.setFixedSize(QSize(25, 60))
        self.trash_button.setStyleSheet(eye_button_style)
        self.trash_button.setIcon(QIcon('icons/sidebar/trash.png'))
        self.trash_button.setIconSize(QSize(20, 20))
        self.trash_button.clicked.connect(self.on_delete)

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
        # self.inner_layout.addWidget(self.l_line_edit)
        self.inner_layout.addWidget(self.trash_button)
        self.inner_layout.addStretch()

        outer_layout = QHBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)
        outer_layout.setAlignment(Qt.AlignVCenter)
        outer_layout.addWidget(self.inner_frame)

        self.setLayout(outer_layout)
        self.setFixedHeight(60)

    def set_checked(self, check):
        self.active = check
        if not self.active:
            self.inner_frame.setStyleSheet(self.inactive_style)
        else:
            self.inner_frame.setStyleSheet(self.active_style)

    def on_click(self):
        self.set_checked(True)
        self.sig_clicked.emit(self.id)

    def eye_on_click(self):
        if self.eye_button.isChecked():
            self.vis = False
        else:
            self.vis = True
        self.tbnail.setEnabled(self.vis)
        self.text_btn.setEnabled(self.vis)
        # self.l_line_edit.setEnabled(self.vis)
        self.eye_clicked.emit((self.id, self.link, self.vis))

    def on_delete(self):
        self.sig_delete.emit(self.id)

    # @pyqtSlot()
    # def on_doubleclick(self):
    #     self.l_line_edit.setText(self.text_btn.text())
    #     self.l_line_edit.setVisible(True)
    #     self.text_btn.setVisible(False)
    #     self.l_line_edit.setFocus(True)
    #     self.on_click()
    #
    # def enter_pressed(self):
    #     self.l_line_edit.setVisible(False)
    #     self.text_btn.setText(self.l_line_edit.text())
    #     self.text_btn.setVisible(True)

    def set_thumbnail_data(self, thumbnail_data):
        if len(thumbnail_data.shape) == 2:
            im = np.zeros((thumbnail_data.shape[0], thumbnail_data.shape[1], 3)).astype(np.uint8)
            # im = thumbnail_data.copy()
            im[:, :, 0] = thumbnail_data
            im[:, :, 1] = thumbnail_data
            im[:, :, 2] = thumbnail_data
        else:
            im = thumbnail_data.astype('uint8')

        self.thumbnail_data = im.copy()

        im_shape = np.ravel(im.shape[:2])

        size = QSize(int(im_shape[1] / 2), int(im_shape[0] / 2))
        image = QImage(im.data, im_shape[1], im_shape[0], im.strides[0], QImage.Format_RGB888)
        pixmap = QPixmap(image)

        self.tbnail.setIcon(QIcon(pixmap.scaled(size)))
        self.tbnail.setIconSize(size)

    def is_checked(self):
        return self.active

    def get_link(self):
        return self.link


class LayersControl(QWidget):

    class SignalProxy(QObject):
        sigOpacityChanged = pyqtSignal(object)
        sigVisChanged = pyqtSignal(object)
        sigBlendModeChanged = pyqtSignal(object)
        sigDeleteLayer = pyqtSignal(object)

    def __init__(self, parent=None):

        self._sigprox = LayersControl.SignalProxy()
        self.sig_opacity_changed = self._sigprox.sigOpacityChanged
        self.sig_visible_changed = self._sigprox.sigVisChanged
        self.sig_blend_mode_changed = self._sigprox.sigBlendModeChanged
        self.sig_layer_deleted = self._sigprox.sigDeleteLayer

        QWidget.__init__(self)

        self.valid_blendable_link = ['img-mask', 'img-virus', 'img-contour', 'img-overlay', 'Image', 'atlas-overlay']

        self.current_layer_index = []

        self.layer_list = []
        self.layer_id = []
        self.layer_link = []
        self.layer_opacity = []
        self.layer_blend_mode = []
        self.layer_color = []

        self.layer_count = 0

        blend_frame = QFrame()
        blend_layout = QHBoxLayout(blend_frame)
        blend_layout.setContentsMargins(0, 0, 0, 0)
        blend_layout.setSpacing(5)

        combo_label = QLabel('Composition:')
        self.layer_blend_combo = QComboBox()
        self.layer_blend_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.layer_blend_combo.setEditable(False)
        combo_value = ['Plus', 'Multiply', 'Overlay', 'SourceOver']
        self.layer_blend_combo.addItems(combo_value)
        self.layer_blend_combo.setCurrentText('Plus')
        self.layer_blend_combo.currentTextChanged.connect(self.blend_mode_changed)

        blend_layout.addWidget(combo_label)
        blend_layout.addWidget(self.layer_blend_combo)

        # opacity wrap
        opacity_frame = QFrame()
        opacity_layout = QHBoxLayout(opacity_frame)
        opacity_layout.setContentsMargins(0, 0, 0, 0)
        opacity_layout.setSpacing(5)

        layer_opacity_label = QLabel('Opacity:')
        self.layer_opacity_slider = QSlider(Qt.Horizontal)
        # self.layer_opacity_slider.setFixedWidth(100)
        self.layer_opacity_slider.setMaximum(100)
        self.layer_opacity_slider.setMinimum(0)
        self.layer_opacity_slider.setValue(100)
        self.layer_opacity_slider.sliderMoved.connect(self.opacity_slider_moved)
        self.layer_opacity_slider.valueChanged.connect(self.change_opacity_label_value)
        self.layer_opacity_val_label = QLabel('100%')

        opacity_layout.addWidget(layer_opacity_label)
        opacity_layout.addWidget(self.layer_opacity_slider)
        opacity_layout.addWidget(self.layer_opacity_val_label)

        self.layer_frame = QFrame()
        self.layer_frame.setStyleSheet('background: transparent; border: 0px;')
        self.layer_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layer_layout = QBoxLayout(QBoxLayout.BottomToTop, self.layer_frame)
        self.layer_layout.setAlignment(Qt.AlignBottom)
        self.layer_layout.setContentsMargins(0, 0, 0, 0)
        self.layer_layout.setSpacing(0)

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

        # extra btn
        self.add_layer_btn = QPushButton()
        self.add_layer_btn.setFixedSize(24, 24)
        self.add_layer_btn.setStyleSheet(btm_style)
        self.add_layer_btn.setIcon(QIcon('icons/layers/add.png'))
        self.add_layer_btn.setIconSize(QSize(20, 20))
        self.add_layer_btn.clicked.connect(lambda: self.add_layer('Layer'))

        self.delete_layer_btn = QPushButton()
        self.delete_layer_btn.setFixedSize(24, 24)
        self.delete_layer_btn.setStyleSheet(btm_style)
        self.delete_layer_btn.setIcon(QIcon('icons/layers/trash.png'))
        self.delete_layer_btn.setIconSize(QSize(20, 20))
        self.delete_layer_btn.clicked.connect(self.delete_layer_btn_clicked)

        outer_layout = QVBoxLayout()
        outer_layout.setSpacing(10)
        outer_layout.addWidget(blend_frame)
        outer_layout.addWidget(opacity_frame)
        outer_layout.addWidget(mid_frame)

        self.setLayout(outer_layout)

    def add_layer(self, widget_link, color):
        self.layer_id.append(self.layer_count)
        self.layer_link.append(widget_link)
        print(self.layer_link)
        self.layer_opacity.append(100)
        self.layer_blend_mode.append('Plus')
        self.sig_blend_mode_changed.emit((widget_link, 
                                          self.layer_blend_mode[-1]))
        self.layer_color.append(color)
        # self.layer_data.append(data)

        new_layer = SingleLayer(layer_id=self.layer_count, link=widget_link)
        new_layer.sig_clicked.connect(self.layer_clicked)
        new_layer.eye_clicked.connect(self.layer_eye_clicked)
        new_layer.sig_delete.connect(self.delete_layer_btn_clicked)

        active_index = len(self.layer_id) - 1
        print('add', active_index)
        if self.current_layer_index:
            for da_ind in self.current_layer_index:
                self.layer_list[da_ind].set_checked(False)
        self.current_layer_index = [active_index]

        self.layer_list.append(new_layer)
        self.layer_layout.addWidget(self.layer_list[-1])
        self.layer_count += 1

        if self.layer_opacity[-1] != self.layer_opacity_slider.value():
            self.layer_opacity_slider.setValue(self.layer_opacity[-1])
        if self.layer_blend_mode[-1] != self.layer_blend_combo.currentText():
            self.layer_blend_combo.setCurrentText(self.layer_blend_mode[-1])

    def master_layers(self, res, layer_type, color):
        if layer_type not in self.layer_link:
            self.add_layer(layer_type, color)
            self.layer_list[-1].set_thumbnail_data(res)
        else:
            da_ind = np.where(np.ravel(self.layer_link) == layer_type)[0][0]
            self.layer_list[da_ind].set_thumbnail_data(res)

    def delete_layer_btn_clicked(self, clicked_id):
        delete_index = np.where(np.ravel(self.layer_id) == clicked_id)[0][0]
        self.sig_layer_deleted.emit(self.layer_link[delete_index])
        self.delete_layer(delete_index)

    def delete_layer(self, delete_index):
        self.layer_layout.removeWidget(self.layer_list[delete_index])
        self.layer_list[delete_index].deleteLater()
        del self.layer_list[delete_index]
        del self.layer_id[delete_index]
        del self.layer_link[delete_index]
        del self.layer_opacity[delete_index]
        del self.layer_blend_mode[delete_index]
        del self.layer_color[delete_index]
        # del self.layer_data[delete_index]
        self.correct_current_layer_index(delete_index)

    def correct_current_layer_index(self, delete_index):
        if delete_index in self.current_layer_index:
            remove_ind = np.where(np.ravel(self.current_layer_index) == delete_index)[0][0]
            del self.current_layer_index[remove_ind]
        for i in range(len(self.current_layer_index)):
            if self.current_layer_index[i] > delete_index:
                self.current_layer_index[i] -= 1

    def layer_clicked(self, clicked_id):
        clicked_index = np.where(np.ravel(self.layer_id) == clicked_id)[0][0]

        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            if clicked_index in self.current_layer_index:
                self.layer_list[clicked_index].set_checked(False)
                remove_ind = np.where(np.ravel(self.current_layer_index) == clicked_index)[0][0]
                self.current_layer_index.pop(remove_ind)
            else:
                self.layer_list[clicked_index].set_checked(True)
                self.current_layer_index.append(clicked_index)
        else:
            for da_ind in self.current_layer_index:
                self.layer_list[da_ind].set_checked(False)
            self.layer_list[clicked_index].set_checked(True)
            self.current_layer_index = [clicked_index]

            if self.layer_opacity[clicked_index] != self.layer_opacity_slider.value():
                self.layer_opacity_slider.setValue(self.layer_opacity[clicked_index])
            if self.layer_blend_mode[clicked_index] != self.layer_blend_combo.currentText():
                self.layer_blend_combo.setCurrentText(self.layer_blend_mode[clicked_index])

    def layer_eye_clicked(self, event):
        self.sig_visible_changed.emit(event)

    def blend_mode_changed(self):
        if not self.current_layer_index:
            return
        if len(self.current_layer_index) > 1:
            return
        blend_mode = self.layer_blend_combo.currentText()
        if blend_mode != self.layer_blend_mode[self.current_layer_index[0]]:
            current_link = self.layer_link[self.current_layer_index[0]]
            self.layer_blend_mode[self.current_layer_index[0]] = blend_mode
            self.sig_blend_mode_changed.emit((current_link, blend_mode))

    def opacity_slider_moved(self):
        if not self.current_layer_index:
            return
        if len(self.current_layer_index) > 1:
            return
        val = self.layer_opacity_slider.value()
        if val != self.layer_opacity[self.current_layer_index[0]]:
            current_link = self.layer_link[self.current_layer_index[0]]
            current_color = self.layer_color[self.current_layer_index[0]]
            self.layer_opacity[self.current_layer_index[0]] = val
            self.sig_opacity_changed.emit((current_link, current_color, val))

    def change_opacity_label_value(self):
        da_val = self.layer_opacity_slider.value()
        self.layer_opacity_val_label.setText('{} %'.format(da_val))

    def get_layer_data(self):
        tb_list = []
        for i in range(len(self.layer_link)):
            da_tb = self.layer_list[i].thumbnail_data
            tb_list.append(da_tb)
        print(self.layer_link)
        data = {'layer_link': self.layer_link,
                'layer_color': self.layer_color,
                'layer_thumbnail': tb_list,
                'layer_opacity': self.layer_opacity,
                'layer_blend_mode': self.layer_blend_mode,
                'current_layer_index': self.current_layer_index}
        return data

    def set_layer_data(self, data):
        for i in range(len(data['layer_link'])):
            self.master_layers(data['layer_thumbnail'][i], data['layer_link'][i], data['layer_color'][i])
        self.layer_color = data['layer_color']
        self.layer_opacity = data['layer_opacity']
        self.layer_blend_mode = data['layer_blend_mode']
        self.current_layer_index = data['current_layer_index']
        self.layer_list[-1].set_checked(False)
        for i in range(len(self.current_layer_index)):
            self.layer_list[i].set_checked(True)

    def clear_all(self):
        ind = np.arange(len(self.layer_list))[::-1]
        for i in ind:
            self.layer_layout.removeWidget(self.layer_list[i])
            self.layer_list[i].deleteLater()
            del self.layer_list[i]
        self.layer_link = []
        self.layer_id = []
        self.layer_link = []
        self.layer_color = []
        self.layer_opacity = []
        self.layer_blend_mode = []
        self.layer_count = []
        self.current_layer_index = []
        self.layer_count = 0











