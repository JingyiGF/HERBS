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


obj_normal_style = '''
QPushButton {
    background-color: transparent;
    border: None;
}

QToolButton {
    border: None;
}

QLabel {
    border:1px solid black;
}

QFrame {
    background-color:rgb(83, 83, 83); 
    border-right: 1px solid rgb(71, 71, 71)
}

LineEditEntered {
    border:None; 
    color:white; 
    padding-left:5px; 
    padding-right: 0px;
    background-color:rgb(83, 83, 83);
}


QDoubleButton {
    border:None; 
    text-align:left; 
    padding-left:5px; 
    padding-right: 0px;
    color:rgb(240, 240, 240);
}

'''


class SingleLayer(QWidget):
    sig_clicked = pyqtSignal(object)
    eye_clicked = pyqtSignal(object)

    def __init__(self, parent=None, index=0, link='None'):
        QWidget.__init__(self, parent=parent)

        self.uncheck_style = 'background-color:rgb(83, 83, 83);'
        self.check_style = 'background-color:rgb(107, 107, 107);'

        self.setStyleSheet('border: 1px solid rgb(71, 71, 71)')
        # self.setFixedWidth(280)
        self.id = index
        self.link = link
        self.active = True
        self.vis = True
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
        self.tbnail.setStyleSheet('border:1px solid black;')
        self.tbnail.setFixedWidth(50)

        self.text_btn = QDoubleButton()
        self.text_btn.setText(link)
        self.text_btn.setFixedWidth(100)
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
        self.outer_layout.addWidget(left_frame)
        self.outer_layout.addWidget(self.inner_frame)

        self.l_line_edit.hide()

        self.setLayout(self.outer_layout)
        self.setMaximumHeight(100)
        self.setMinimumHeight(60)
        # self.show()

    # def frame_on_click(self, info):
    #     if info == 'Click':
    #         self.sig_clicked.emit(self.id)
    #     else:
    #         pass
    def set_link(self, link):
        self.link = link

    def eye_on_click(self):
        if self.vis:
            self.vis = False
        else:
            self.vis = True
        self.set_checked(self.vis)
        self.sig_clicked.emit((self.id, self.link))
        self.eye_clicked.emit((self.id, self.link, self.vis))
        if self.inner_frame.isEnabled():
            self.tbnail.setEnabled(False)
            self.text_btn.setEnabled(False)
            self.l_line_edit.setEnabled(False)
            self.empty_btn.setEnabled(False)
        else:
            self.tbnail.setEnabled(True)
            self.text_btn.setEnabled(True)
            self.l_line_edit.setEnabled(True)
            self.empty_btn.setEnabled(True)

    @pyqtSlot()
    def on_click(self):
        print("Click")
        # self.inner_frame.setStyleSheet('background-color:rgb(107, 107, 107); ')
        self.set_checked(True)
        self.sig_clicked.emit((self.id, self.link))


    @pyqtSlot()
    def on_doubleclick(self):
        print("Doubleclick")
        # self.inner_frame.setStyleSheet('background-color:rgb(107, 107, 107); ')
        self.l_line_edit.setText(self.text_btn.text())
        self.l_line_edit.setVisible(True)
        self.text_btn.setVisible(False)
        self.l_line_edit.setFocus(True)
        self.set_checked(True)
        self.sig_clicked.emit((self.id, self.link))

    @pyqtSlot()
    def enter_pressed(self):
        print('return')
        self.l_line_edit.setVisible(False)
        self.text_btn.setText(self.l_line_edit.text())
        self.text_btn.setVisible(True)

    def set_thumbnail_data(self, thumbnail_data):

        if len(thumbnail_data.shape) == 2:
            im = np.zeros((thumbnail_data.shape[0], thumbnail_data.shape[1], 3)).astype(np.uint8)
            # im = thumbnail_data.copy()
            im[:, :, 0] = thumbnail_data
            im[:, :, 1] = thumbnail_data
            im[:, :, 2] = thumbnail_data
        else:
            im = thumbnail_data.astype('uint8')

        im_shape = np.ravel(im.shape[:2])

        size = QSize(int(im_shape[1] / 2), int(im_shape[0] / 2))
        image = QImage(im.data, im_shape[1], im_shape[0], im.strides[0], QImage.Format_RGB888)
        pixmap = QPixmap(image)

        self.tbnail.setIcon(QIcon(pixmap.scaled(size)))
        self.tbnail.setIconSize(size)

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

    def get_link(self):
        return self.link

    # def mousePressEvent(self, event):
    #     if event.button() == Qt.LeftButton:
    #         self.sig_left_clicked.emit(self.id)
    #     elif event.button() == Qt.RightButton:
    #         self.sig_right_clicked.emit(self.id)
    #     self.update()


class LayersControl(QWidget):

    class SignalProxy(QObject):
        sigOpacityChanged = pyqtSignal(object)
        sigVisChanged = pyqtSignal(object)

    def __init__(self, parent=None):

        self._sigprox = LayersControl.SignalProxy()
        self.sig_opacity_changed = self._sigprox.sigOpacityChanged
        self.sig_visible_changed = self._sigprox.sigVisChanged

        QWidget.__init__(self)

        self.aimg = None
        self.himg = None

        # self.active_layer_index = None
        self.current_layer_ind = []

        self.layer_list = []
        self.layer_index = []
        self.layer_link = []

        self.layer_count = 0

        self.top_frame = QFrame()
        top_layout = QGridLayout(self.top_frame)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(5)

        combo_label = QLabel('Composition:')
        self.layer_blend_combo = QComboBox()
        self.layer_blend_combo.setEditable(False)
        combo_value = ['Multiply', 'Overlay', 'SourceOver']
        self.layer_blend_combo.addItems(combo_value)
        self.layer_blend_combo.setCurrentText('Multiply')

        layer_opacity_label = QLabel('Opacity:')
        self.layer_opacity_slider = QSlider(Qt.Horizontal)
        # self.layer_opacity_slider.setFixedWidth(100)
        self.layer_opacity_slider.setMaximum(100)
        self.layer_opacity_slider.setMinimum(0)
        self.layer_opacity_slider.setValue(100)
        self.layer_opacity_slider.valueChanged.connect(self.change_opacity_label_value)
        self.layer_opacity_val_label = QLabel('100%')

        top_layout.addWidget(combo_label, 0, 0, 1, 1)
        top_layout.addWidget(self.layer_blend_combo, 0, 1, 1, 3)
        top_layout.addWidget(layer_opacity_label, 1, 0, 1, 1)
        top_layout.addWidget(self.layer_opacity_slider, 1, 1, 2, 1)
        top_layout.addWidget(self.layer_opacity_val_label, 1, 3, 1, 1)

        self.layer_frame = QFrame()
        self.layer_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layer_layout = QBoxLayout(QBoxLayout.BottomToTop, self.layer_frame)
        self.layer_layout.setAlignment(Qt.AlignBottom)
        self.layer_layout.setContentsMargins(0, 0, 0, 0)
        self.layer_layout.setSpacing(0)

        self.layer_scroll = QScrollArea()
        self.layer_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layer_scroll.setWidget(self.layer_frame)
        self.layer_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.layer_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.layer_scroll.setWidgetResizable(True)

        mid_frame = QFrame()
        mid_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        mid_layout = QGridLayout(mid_frame)
        mid_layout.setContentsMargins(0, 0, 0, 0)
        mid_layout.setSpacing(0)
        mid_layout.setAlignment(Qt.AlignBottom)
        mid_layout.addWidget(self.layer_scroll, 0, 0, 1, 1)


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


        outer_layout = QGridLayout()
        outer_layout.setSpacing(0)
        # outer_layout.setAlignment(Qt.AlignTop)
        outer_layout.addWidget(self.top_frame, 0, 0, 1, 1)
        outer_layout.addWidget(mid_frame, 1, 0, 1, 1)
        # outer_layout.addWidget(self.btm_frame, 2, 0, 1, 1)


        # self.top_frame.setEnabled(False)
        # self.btm_frame.setEnabled(False)
        # self.vis_ai_layer_btn.setEnabled(False)
        # self.vis_hi_layer_btn.setEnabled(False)


        self.setLayout(outer_layout)
        # self.show()

    def change_opacity_label_value(self):
        da_val = self.layer_opacity_slider.value()
        self.layer_opacity_val_label.setText('{} %'.format(da_val))
        self.sig_opacity_changed.emit(da_val)

    def add_layer(self, widget_link):
        print(widget_link)
        new_layer = SingleLayer(index=self.layer_count, link=widget_link)
        print(widget_link)
        # new_layer.text_btn.setText(widget_link)
        new_layer.set_checked(True)
        new_layer.sig_clicked.connect(self.layer_clicked)
        new_layer.eye_clicked.connect(self.layer_eye_clicked)
        self.layer_list.append(new_layer)
        self.layer_index.append(self.layer_count)
        self.layer_link.append(widget_link)
        if not self.current_layer_ind:
            self.current_layer_ind.append(self.layer_count)
        else:
            for ind in self.current_layer_ind:
                # unactive_layer_ind = [ind for ind in range(len(self.lay))]
                unactive_layer_ind = np.where(np.asarray(self.layer_index) == ind)[0][0]
                self.layer_list[unactive_layer_ind].set_checked(False)
            self.current_layer_ind = [self.layer_count]
        self.layer_layout.addWidget(self.layer_list[-1])
        self.layer_count += 1
        print(self.layer_count)

    def delete_layer_btn_clicked(self):
        if len(self.current_layer_ind) == 0:
            return
        current_ids_copy = np.ravel(self.current_layer_ind).copy()
        for ind in current_ids_copy:
            self.delete_layer(ind)
        if len(self.layer_index) != 0:
            self.layer_list[-1].set_checked(True)
            self.current_layer_ind.append(self.layer_index[-1])
        print('current layer', self.current_layer_ind)
        print('layer index', self.layer_index)

    def delete_layer(self, ind):
        layer_ind = np.where(np.asarray(self.layer_index) == ind)[0][0]
        self.layer_layout.removeWidget(self.layer_list[layer_ind])
        self.layer_list[layer_ind].deleteLater()
        del self.layer_list[layer_ind]
        del self.layer_index[layer_ind]
        del self.layer_link[layer_ind]
        self.layer_count -= 1
        print(self.layer_count)
        n_current_layer = len(self.current_layer_ind)
        if ind in self.current_layer_ind:
            remove_from_current_ind = [i for i in range(n_current_layer) if self.current_layer_ind[i] == ind][0]
            del self.current_layer_ind[remove_from_current_ind]



    def layer_clicked(self, ev):
        # a bit slow
        index = ev[0]
        link = ev[1]
        print(('layer clicked', index))
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            if index in self.current_layer_ind:
                id2unactive = np.where(np.asarray(self.layer_index) == index)[0][0]
                self.layer_list[id2unactive].set_checked(False)
                ind = np.where(np.asarray(self.current_layer_ind) == index)[0][0]
                self.current_layer_ind.pop(ind)
            else:
                id2active = np.where(np.asarray(self.layer_index) == index)[0][0]
                self.layer_list[id2active].set_checked(True)
                self.current_layer_ind.append(index)
        else:
            current_ids_copy = np.ravel(self.current_layer_ind).copy()
            for ind in current_ids_copy:
                id2unactive = np.where(np.asarray(self.layer_index) == ind)[0][0]
                self.layer_list[id2unactive].set_checked(False)
                unactive_ind = np.where(np.asarray(self.current_layer_ind) == ind)[0][0]
                self.current_layer_ind.pop(unactive_ind)
            id2active = np.where(np.asarray(self.layer_index) == index)[0][0]
            self.layer_list[id2active].set_checked(True)
            self.current_layer_ind.append(index)
        print(self.current_layer_ind)
        print(('index', self.layer_index))

    def layer_eye_clicked(self, event):
        self.sig_visible_changed.emit(event)
        print(event)







