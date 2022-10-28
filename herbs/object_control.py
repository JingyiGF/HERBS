import os
import sys
import numpy as np
from random import randint
import pyqtgraph as pg
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from .wtiles import QDoubleButton
from .uuuuuu import read_qss_file


eye_button_style = '''
    border-left: None;
    border-right: 1px solid gray;
    border-top: None;
    border-bottom: None;
    border-radius: 0px;
    background: transparent;
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


class ObjectTextButton(QPushButton):
    def __init__(self):
        QPushButton.__init__(self)
        btn_style = read_qss_file('qss/object_text_button.qss')
        self.setStyleSheet(btn_style)
        self.setFixedSize(QSize(150, 40))


class CompareWindow(QDialog):
    def __init__(self, obj_names, obj_data):
        super().__init__()

        self.setWindowTitle("Compare Information Window")

        n_object = len(obj_names)
        all_label_names = obj_data[0]['label_name'].copy()
        all_label_acronym = obj_data[0]['label_acronym'].copy()
        all_label_color = obj_data[0]['label_color'].copy()
        all_label_channels = obj_data[0]['region_channels'].tolist()

        for i in range(1, n_object):
            check_label = obj_data[i]['label_name']
            for j in range(len(check_label)):
                if check_label[j] in all_label_names:
                    da_ind = np.where(np.ravel(all_label_names) == check_label[j])[0][0]
                    all_label_channels[da_ind] = all_label_channels[da_ind] + obj_data[i]['region_channels'][j]
                else:
                    all_label_names.append(check_label[j])
                    all_label_acronym.append(obj_data[i]['label_acronym'][j])
                    all_label_color.append(obj_data[i]['label_color'][j])
                    all_label_channels.append(obj_data[i]['region_channels'][j])

        layout = QVBoxLayout()
        full_name = obj_names[0]
        for i in range(1, n_object):
            full_name = full_name + ', '
            full_name = full_name + obj_names[i]

        self.label = QLabel('Compare {}'.format(full_name))
        color = QColor(128, 128, 128, 128)
        label_style = 'QLabel {background-color: ' + color.name() + '; font-size: 20px}'
        self.label.setStyleSheet(label_style)

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

        channels = np.ravel(all_label_channels).astype(int)

        for i in range(len(all_label_names)):
            slayout.addWidget(QLabel(all_label_names[i]), i + 1, 0, 1, 1)
            slayout.addWidget(QLabel(all_label_acronym[i]), i + 1, 1, 1, 1)
            slayout.addWidget(QLabel(str(channels[i])), i + 1, 2, 1, 1)
            clb = QLabel()
            da_color = QColor(all_label_color[i][0], all_label_color[i][1], all_label_color[i][2], 255).name()
            clb.setStyleSheet('QLabel {background-color: ' + da_color + '; width: 20px; height: 20px}')
            slayout.addWidget(clb, i + 1, 3, 1, 1)

        # make plot data
        plot_frame = QFrame()
        plot_frame.setMaximumWidth(300)
        plot_frame.setMinimumWidth(300)
        view_layout = QHBoxLayout(plot_frame)
        view_layout.setSpacing(0)
        view_layout.setContentsMargins(0, 0, 0, 0)

        w = pg.GraphicsLayoutWidget()
        view = w.addViewBox()
        view.setAspectLocked()

        view_layout.addWidget(w)

        resize_factor = 5
        max_num_channel = 0
        for i in range(n_object):
            da_sum = np.sum(obj_data[i]['block_count'][0])
            if da_sum > max_num_channel:
                max_num_channel = da_sum

        for i in range(n_object):
            count1 = obj_data[i]['block_count'][0]
            plot_data1 = np.cumsum(count1)
            plot_data1 = plot_data1 / max_num_channel * resize_factor
            plot_colors1 = np.asarray(obj_data[i]['merged_color'][0])

            count2 = obj_data[i]['block_count'][1]
            plot_data2 = np.cumsum(count2)
            plot_data2 = plot_data2 / max_num_channel * resize_factor
            plot_colors2 = np.asarray(obj_data[i]['merged_color'][1])

            # draw tips
            da_tip_loc = np.array([[i - 0.3, 0], [i, - 0.7], [i + 0.3, 0]])
            tips = pg.PlotDataItem(da_tip_loc, connect='all', fillLevel=0, fillBrush=pg.mkBrush(color=(128, 128, 128)))
            view.addItem(tips)

            # create bar chart
            bg_list1 = []
            for j in np.arange(len(plot_data1))[::-1]:
                bg = pg.BarGraphItem(x=[i - 0.15], height=plot_data1[j], width=0.3,
                                     brush=QColor(plot_colors1[j][0], plot_colors1[j][1], plot_colors1[j][2], 255))
                bg_list1.append(bg)
                view.addItem(bg_list1[-1])

            bg_list2 = []
            for j in np.arange(len(plot_data2))[::-1]:
                bg = pg.BarGraphItem(x=[i + 0.15], height=plot_data2[j], width=0.3,
                                     brush=QColor(plot_colors2[j][0], plot_colors2[j][1], plot_colors2[j][2], 255))
                bg_list2.append(bg)
                view.addItem(bg_list2[-1])

        channel_info_frame = QFrame()
        channel_info_layout = QHBoxLayout(channel_info_frame)
        channel_info_layout.setContentsMargins(0, 0, 0, 0)
        channel_info_layout.setSpacing(10)
        channel_info_layout.addWidget(plot_frame)
        channel_info_layout.addWidget(sec_group)

        # ok button, used to close window
        ok_btn = QDialogButtonBox(QDialogButtonBox.Ok)
        ok_btn.accepted.connect(self.accept)

        # add widget to layout
        layout.addWidget(self.label)
        layout.addWidget(channel_info_frame)
        layout.addWidget(ok_btn)
        self.setLayout(layout)

    def accept(self) -> None:
        self.close()


class CellsInfoWindow(QDialog):
    def __init__(self, name, data):
        super().__init__()

        self.setWindowTitle("Cell Information Window")

        layout = QVBoxLayout()
        self.label = QLabel(name)
        color = QColor(data['vis_color'][0], data['vis_color'][1], data['vis_color'][2], data['vis_color'][3])
        label_style = 'QLabel {background-color: ' + color.name() + '; font-size: 20px}'
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
    def __init__(self, name, data):
        super().__init__()

        self.setWindowTitle("Virus Information Window")

        layout = QVBoxLayout()
        self.label = QLabel(name)
        color = QColor(data['vis_color'][0], data['vis_color'][1], data['vis_color'][2], data['vis_color'][3])
        label_style = 'QLabel {background-color: ' + color.name() + '; font-size: 20px}'
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

        self.label = QLabel(name)
        # self.label = QLabel("Probe % d " % group_id)
        color = QColor(data['vis_color'][0], data['vis_color'][1], data['vis_color'][2], data['vis_color'][3])
        label_style = 'QLabel {background-color: ' + color.name() + '; font-size: 20px}'
        self.label.setStyleSheet(label_style)

        ap_angle_label = QLabel('AP Angle : ')
        ap_angle_label.setAlignment(Qt.AlignCenter)
        ml_angle_label = QLabel('ML Angle : ')
        ml_angle_label.setAlignment(Qt.AlignCenter)
        probe_length_label = QLabel('Probe Length : ')
        probe_length_label.setAlignment(Qt.AlignCenter)
        dv_label = QLabel('DV : ')
        dv_label.setAlignment(Qt.AlignCenter)
        insertion_coords_label = QLabel('Insertion coordinates : ')
        insertion_coords_label.setAlignment(Qt.AlignCenter)
        insertion_voxels_label = QLabel('Insertion voxels : ')
        insertion_voxels_label.setAlignment(Qt.AlignCenter)

        terminus_coords_label = QLabel('Terminus coordinates : ')
        terminus_coords_label.setAlignment(Qt.AlignCenter)
        terminus_voxels_label = QLabel('Terminus voxels : ')
        terminus_voxels_label.setAlignment(Qt.AlignCenter)

        ap_angle_value = QLabel('{} \u00B0'.format(np.round(data['ap_angle'], 2)))
        ml_angle_value = QLabel('{} \u00B0'.format(np.round(data['ml_angle'], 2)))
        probe_length = QLabel('{} \u03BCm'.format(np.round(data['probe_length'], 2)))
        dv = QLabel('{} \u03BCm'.format(np.round(data['dv'], 2)))
        ic_val = np.round(data['insertion_coords'], 2)
        insertion_coords = QLabel('ML: {}\u03BCm,  AP: {}\u03BCm'.format(ic_val[0], ic_val[1]))
        iv_val = data['insertion_vox'].astype(int)
        insertion_vox = QLabel('({} {} {})'.format(iv_val[0], iv_val[1], iv_val[2]))

        tc_val = np.round(data['terminus_coords'], 2)
        terminus_coords = QLabel('ML: {}\u03BCm,  AP: {}\u03BCm'.format(tc_val[0], tc_val[1]))
        tv_val = data['terminus_vox']
        terminus_vox = QLabel('({} {} {})'.format(tv_val[0], tv_val[1], tv_val[2]))

        coords_info_group = QGroupBox()
        coords_info_layout = QGridLayout(coords_info_group)
        coords_info_layout.addWidget(ap_angle_label, 0, 0, 1, 1)
        coords_info_layout.addWidget(ap_angle_value, 0, 1, 1, 1)
        coords_info_layout.addWidget(ml_angle_label, 0, 2, 1, 1)
        coords_info_layout.addWidget(ml_angle_value, 0, 3, 1, 1)

        coords_info_layout.addWidget(probe_length_label, 1, 0, 1, 1)
        coords_info_layout.addWidget(probe_length, 1, 1, 1, 1)
        coords_info_layout.addWidget(dv_label, 1, 2, 1, 1)
        coords_info_layout.addWidget(dv, 1, 3, 1, 1)

        coords_info_layout.addWidget(insertion_coords_label, 2, 0, 1, 1)
        coords_info_layout.addWidget(insertion_coords, 2, 1, 1, 1)
        coords_info_layout.addWidget(terminus_coords_label, 2, 2, 1, 1)
        coords_info_layout.addWidget(terminus_coords, 2, 3, 1, 1)

        coords_info_layout.addWidget(insertion_voxels_label, 3, 0, 1, 1)
        coords_info_layout.addWidget(insertion_vox, 3, 1, 1, 1)
        coords_info_layout.addWidget(terminus_voxels_label, 3, 2, 1, 1)
        coords_info_layout.addWidget(terminus_vox, 3, 3, 1, 1)

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

        # make plot data
        resize_factor = 5
        count1 = data['block_count'][0]
        text_data1 = count1 / np.sum(count1) * resize_factor
        plot_data1 = np.cumsum(count1)
        plot_data1 = plot_data1 / plot_data1[-1] * resize_factor
        # plot_data1 = plot_data1[::-1]
        plot_colors1 = np.asarray(data['merged_color'][0])

        count2 = data['block_count'][1]
        text_data2 = count2 / np.sum(count2) * resize_factor
        plot_data2 = np.cumsum(count2)
        plot_data2 = plot_data2 / plot_data2[-1] * resize_factor
        # plot_data2 = plot_data2[::-1]
        plot_colors2 = np.asarray(data['merged_color'][1])
        # self.label = label[::-1]


        plot_frame = QFrame()
        plot_frame.setMaximumWidth(300)
        plot_frame.setMinimumWidth(300)
        view_layout = QHBoxLayout(plot_frame)
        view_layout.setSpacing(0)
        view_layout.setContentsMargins(0, 0, 0, 0)

        w = pg.GraphicsLayoutWidget()
        view = w.addViewBox()
        view.setAspectLocked()
        # view.invertY(True)

        # draw tips
        da_tip_loc = np.array([[0.7, 0], [1, - 0.7], [1.3, 0]])
        tips = pg.PlotDataItem(da_tip_loc, connect='all', fillLevel=0, fillBrush=pg.mkBrush(color=(128, 128, 128)))
        view.addItem(tips)

        # create bar chart
        bg_list1 = []
        for i in np.arange(len(plot_data1))[::-1]:
            bg = pg.BarGraphItem(x=[1-0.15], height=plot_data1[i], width=0.3,
                                 brush=QColor(plot_colors1[i][0], plot_colors1[i][1], plot_colors1[i][2], 255))
            bg_list1.append(bg)
            view.addItem(bg_list1[-1])

        text_list1 = [pg.TextItem(str(count1[0]))]
        text_list1[-1].setPos(0.6, text_data1[0] * 0.5)
        text_list1[-1].setAnchor((0.5, 0.5))
        view.addItem(text_list1[-1])
        for i in range(1, len(plot_data1)):
            tt = pg.TextItem(str(count1[i]))
            if np.mod(i, 2) == 0:
                tt.setPos(0.6, plot_data1[i - 1] + text_data1[i] * 0.5)
            else:
                tt.setPos(0.5, plot_data1[i - 1] + text_data1[i] * 0.5)
            tt.setAnchor((0.5, 0.5))
            text_list1.append(tt)
            view.addItem(text_list1[i])

        bg_list2 = []
        for i in np.arange(len(plot_data2))[::-1]:
            bg = pg.BarGraphItem(x=[1+0.15], height=plot_data2[i], width=0.3,
                                 brush=QColor(plot_colors2[i][0], plot_colors2[i][1], plot_colors2[i][2], 255))
            bg_list2.append(bg)
            view.addItem(bg_list2[-1])

        text_list2 = [pg.TextItem(str(count2[0]))]
        text_list2[-1].setPos(1.4, text_data2[0] * 0.5)
        text_list2[-1].setAnchor((0.5, 0.5))
        view.addItem(text_list2[-1])
        for i in range(1, len(plot_data2)):
            tt = pg.TextItem(str(count2[i]))
            if np.mod(i, 2) == 0:
                tt.setPos(1.4, plot_data2[i - 1] + text_data2[i] * 0.5)
            else:
                tt.setPos(1.5, plot_data2[i - 1] + text_data2[i] * 0.5)
            tt.setAnchor((0.5, 0.5))
            text_list2.append(tt)
            view.addItem(text_list2[i])

        view_layout.addWidget(w)

        channel_info_frame = QFrame()
        channel_info_layout = QHBoxLayout(channel_info_frame)
        channel_info_layout.setContentsMargins(0, 0, 0, 0)
        channel_info_layout.setSpacing(10)
        channel_info_layout.addWidget(plot_frame)
        channel_info_layout.addWidget(sec_group)

        # ok button, used to close window
        ok_btn = QDialogButtonBox(QDialogButtonBox.Ok)
        ok_btn.accepted.connect(self.accept)

        # add widget to layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(coords_info_group)
        layout.addSpacing(10)
        layout.addWidget(channel_info_frame)
        layout.addWidget(ok_btn)
        self.setLayout(layout)

    def accept(self) -> None:
        self.close()

    def set_probe_color(self, color):
        self.label.setStyleSheet('QLabel {background-color: ' + color + ';}')


class SinglePiece(QWidget):
    sig_clicked = pyqtSignal(object)
    sig_name_changed = pyqtSignal(object)

    def __init__(self, parent=None, index=0, obj_name='', obj_type='probe piece', object_icon=None):
        QWidget.__init__(self, parent=parent)

        self.inactive_style = 'QFrame{background-color:rgb(83, 83, 83); border: 1px solid rgb(128, 128, 128);}'
        self.active_style = 'QFrame{background-color:rgb(107, 107, 107); border: 1px solid rgb(128, 128, 128);}'

        self.id = index
        self.object_name = obj_name
        self.object_type = obj_type
        self.active = True

        self.tbnail = QPushButton()
        self.tbnail.setFixedSize(QSize(40, 40))
        self.tbnail.setStyleSheet(eye_button_style)
        self.tbnail.setIcon(object_icon)
        self.tbnail.setIconSize(QSize(20, 20))
        self.tbnail.clicked.connect(self.on_click)

        self.text_btn = QDoubleButton()
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
        da_text = self.l_line_edit.text()
        if '-' not in da_text or 'piece' not in da_text:
            return
        self.l_line_edit.setVisible(False)
        self.text_btn.setText(self.l_line_edit.text())
        self.object_name = self.l_line_edit.text()
        self.text_btn.setVisible(True)
        self.sig_name_changed.emit((self.id, self.object_name))

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
    sig_link = pyqtSignal(object)
    sig_double_clicked = pyqtSignal(object)

    def __init__(self, parent=None, obj_id=0, obj_name='', obj_type='merged probe', object_icon=None):
        QWidget.__init__(self, parent=parent)

        self.inactive_style = 'QFrame{background-color:rgb(83, 83, 83); border: 1px solid rgb(128, 128, 128);}'
        self.active_style = 'QFrame{background-color:rgb(107, 107, 107); border: 1px solid rgb(128, 128, 128);}'

        self.color = QColor(randint(0, 255), randint(0, 255), randint(0, 255), 255)
        self.icon_back = 'border:1px solid black; background-color: {}'.format(self.color.name())

        self.id = obj_id
        self.object_type = obj_type
        self.object_name = obj_name
        self.active = True
        self.vis = True

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

        self.text_btn = ObjectTextButton()
        self.text_btn.setText(self.object_name)
        self.text_btn.clicked.connect(self.text_btn_on_click)
        # self.text_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)

        self.link_button = QPushButton()
        self.link_button.setFixedSize(QSize(25, 40))
        self.link_button.setCheckable(True)
        link_icon = QIcon()
        link_icon.addPixmap(QPixmap("icons/sidebar/link_off.svg"), QIcon.Normal, QIcon.Off)
        link_icon.addPixmap(QPixmap("icons/sidebar/link.svg"), QIcon.Normal, QIcon.On)
        self.link_button.setIcon(link_icon)
        self.link_button.setIconSize(QSize(20, 20))
        self.link_button.clicked.connect(self.on_linked)

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
        self.inner_layout.addWidget(self.link_button)
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

    def text_btn_on_click(self):
        self.set_checked(True)
        self.sig_clicked.emit(self.id)

    def is_checked(self):
        return self.active

    def on_linked(self):
        self.sig_link.emit(self.id)


class BottomButton(QPushButton):
    def __init__(self, icon_path):
        QPushButton.__init__(self)
        btm_style = read_qss_file('qss/obj_ctrl_bottom_button.qss')
        self.setFixedSize(24, 24)
        self.setStyleSheet(btm_style)
        self.setIcon(QIcon(icon_path))
        self.setIconSize(QSize(20, 20))



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
        self.sig_delete_object = self._sigprox.sigDeleteObject  # for delete obj 3d gl widgets
        self.sig_color_changed = self._sigprox.sigColorChanged
        self.sig_size_changed = self._sigprox.sigSizeChanged
        self.sig_blend_mode_changed = self._sigprox.sigBlendModeChanged

        QObject.__init__(self)

        self.default_size_val = 2
        self.default_opacity_val = 100

        self.valid_obj_type = ['probe piece', 'merged probe',
                               'cells piece', 'merged cells',
                               'virus piece', 'merged virus',
                               'contour piece', 'merged contour',
                               'drawing piece', 'merged drawing']

        self.current_obj_index = None

        self.obj_count = 0
        self.linked_indexes = []

        self.obj_list = []  # widgets
        self.obj_id = []  # identity
        self.obj_name = []  # names, initially the same as type, can be changed freely ???
        self.obj_type = []  # type
        self.obj_data = []  # data
        self.obj_size = []  # size
        self.obj_opacity = []
        self.obj_comp_mode = []

        self.probe_icon = QIcon('icons/sidebar/probe.svg')
        self.virus_icon = QIcon('icons/sidebar/virus.svg')
        self.drawing_icon = QIcon('icons/toolbar/pencil.svg')
        self.cell_icon = QIcon('icons/toolbar/location.svg')
        self.contour_icon = QIcon('icons/sidebar/contour.svg')
        self.compare_icon = QIcon('icons/sidebar/compare.svg')

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
        self.obj_size_slider = QSlider(Qt.Horizontal)
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
        self.info_btn = BottomButton('icons/sidebar/info.svg')
        self.info_btn.clicked.connect(self.info_btn_clicked)

        self.vis2d_btn = BottomButton('icons/toolbar/vis2d.svg')
        self.compare_btn = BottomButton('icons/sidebar/compare.svg')
        self.merge_probe_btn = BottomButton('icons/sidebar/probe.svg')
        self.merge_drawing_btn = BottomButton('icons/toolbar/pencil.svg')
        self.merge_cell_btn = BottomButton('icons/toolbar/location.svg')
        self.merge_virus_btn = BottomButton('icons/sidebar/virus.svg')
        self.merge_contour_btn = BottomButton('icons/sidebar/contour.svg')
        self.add_object_btn = BottomButton('icons/sidebar/add.png')
        self.delete_object_btn = BottomButton('icons/sidebar/trash.png')
        self.delete_object_btn.clicked.connect(self.delete_object_btn_clicked)

    def blend_mode_changed(self):
        blend_mode = self.obj_blend_combo.currentText()
        if self.current_obj_index is None:
            return
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
        if self.current_obj_index is None:
            return
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
        if self.current_obj_index is None:
            return
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
        self.delete_objects(self.current_obj_index)

    def info_btn_clicked(self):
        if 'merged' in self.obj_type[self.current_obj_index]:
            self.obj_info_on_click()

    def obj_clicked(self, clicked_id):
        self.set_active_layer_to_current(clicked_id)

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
        if previous_obj_id != clicked_id:
            active_index = np.where(np.ravel(self.obj_id) == clicked_id)[0][0]
            self.current_obj_index = active_index
            # self.obj_list[active_index].set_checked(True)
            inactive_id = np.where(np.ravel(self.obj_id) == previous_obj_id)[0][0]
            self.obj_list[inactive_id].set_checked(False)
            self.set_slider_combo_to_current()
        else:
            return

    def obj_link_changed(self, clicked_id):
        da_index = np.where(np.ravel(self.obj_id) == clicked_id)[0][0]
        if self.obj_list[da_index].link_button.isChecked():
            self.linked_indexes.append(da_index)
        else:
            if da_index in self.linked_indexes:
                del_ind = np.where(np.ravel(self.linked_indexes) == da_index)[0][0]
                self.linked_indexes.pop(del_ind)

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
    def get_object_icon(self, object_type):
        if 'probe' in object_type:
            object_icon = self.probe_icon
        elif 'virus' in object_type:
            object_icon = self.virus_icon
        elif 'cell' in object_type:
            object_icon = self.cell_icon
        elif 'contour' in object_type:
            object_icon = self.contour_icon
        elif 'drawing' in object_type:
            object_icon = self.drawing_icon
        else:
            object_icon = None
        return object_icon

    def get_group_count(self, object_type):
        group_count = len([da_type for da_type in self.obj_type if da_type == object_type])
        return group_count

    def add_object(self, object_name, object_type, object_data, object_mode):
        object_icon = self.get_object_icon(object_type)
        # group_count = self.get_group_count(object_type)
        if object_icon is None:
            return
        self.obj_id.append(self.obj_count)
        self.obj_data.append(object_data)
        self.obj_name.append(object_name)
        self.obj_type.append(object_type)
        if 'merged' in object_type:
            new_layer = RegisteredObject(obj_id=self.obj_count, obj_name=object_name,
                                         obj_type=object_type, object_icon=object_icon)
            new_layer.eye_clicked.connect(self.obj_eye_clicked)
            new_layer.sig_object_color_changed.connect(self.obj_color_changed)
            new_layer.sig_link.connect(self.obj_link_changed)
            self.obj_opacity.append(self.default_opacity_val)
            self.obj_size.append(self.default_size_val)
            self.obj_comp_mode.append(object_mode)
            da_color = (new_layer.color.red(), new_layer.color.green(), new_layer.color.blue(), 255)
            self.obj_data[-1]['vis_color'] = da_color
            if self.obj_size_slider.value() != self.default_size_val:
                self.obj_size_slider.setValue(self.default_size_val)
            if self.obj_opacity_slider.value() != self.default_opacity_val:
                self.obj_opacity_slider.setValue(self.default_opacity_val)
            if self.obj_blend_combo.currentText() != object_mode:
                self.obj_blend_combo.blockSignals(True)
                self.obj_blend_combo.setCurrentText(object_mode)
                self.obj_blend_combo.blockSignals(False)
        else:
            new_layer = SinglePiece(index=self.obj_count, obj_name=object_name,
                                    obj_type=object_type, object_icon=object_icon)
            new_layer.sig_name_changed.connect(self.obj_piece_name_changed)
            self.obj_opacity.append([])
            self.obj_size.append([])
            self.obj_comp_mode.append([])

        new_layer.text_btn.setText(self.obj_name[-1])
        new_layer.set_checked(True)
        new_layer.sig_clicked.connect(self.obj_clicked)
        self.obj_list.append(new_layer)

        active_index = np.where(np.ravel(self.obj_id) == self.obj_count)[0][0]
        if self.current_obj_index is None:
            self.current_obj_index = active_index
        else:
            self.obj_list[self.current_obj_index].set_checked(False)
            self.current_obj_index = active_index

        self.layer_layout.addWidget(self.obj_list[-1])
        self.obj_count += 1

    # merge object piece
    def merge_pieces(self, obj_type='probe piece'):
        if obj_type not in ['probe piece', 'virus piece', 'contour piece', 'drawing piece', 'cells piece']:
            return
        n_obj = len(self.obj_id)
        cind = [ind for ind in range(n_obj) if self.obj_type[ind] == obj_type]
        da_type_object_names = np.ravel(self.obj_name)[np.array(cind)]
        n_pieces = len(da_type_object_names)
        pieces_names = []
        for i in range(n_pieces):
            da_name = da_type_object_names[i]
            # da_name = da_name.replace(" ", "")
            da_name_split = da_name.split('-')
            piece_name = da_name_split[0]
            if piece_name[-1] == ' ':
                piece_name = piece_name[:-1]
            pieces_names.append(piece_name)
        object_names = np.unique(pieces_names)
        n_object = len(object_names)
        data = [[] for i in range(n_object)]
        for i in range(n_object):
            da_piece_name = object_names[i]
            da_piece_ind_in_obj_order = [cind[ind] for ind in range(n_pieces) if pieces_names[ind] == da_piece_name]
            temp = self.obj_data[da_piece_ind_in_obj_order[0]].T
            if len(da_piece_ind_in_obj_order) > 1:
                for j in range(1, len(da_piece_ind_in_obj_order)):
                    print(self.obj_data[da_piece_ind_in_obj_order[j]].T)
                    temp = np.hstack([temp, self.obj_data[da_piece_ind_in_obj_order[j]].T])
            data[i] = temp.T
        self.delete_objects(cind)
        return data, object_names

    # get obj data
    def get_obj_data(self):
        data = {'obj_name':  self.obj_name,
                'obj_type': self.obj_type,
                'obj_data': self.obj_data,
                'obj_size': self.obj_size,
                'obj_opacity': self.obj_opacity,
                'obj_comp_mode': self.obj_comp_mode,
                'current_obj_index': self.current_obj_index}
        return data

    def set_obj_data(self, data):
        for i in range(len(data['obj_type'])):
            self.add_object(data['obj_name'][i], data['obj_type'][i], data['obj_data'][i], data['obj_comp_mode'][i])

        self.obj_size = data['obj_size']
        self.obj_opacity = data['obj_opacity']
        self.obj_comp_mode = data['obj_comp_mode']
        self.current_obj_index = data['current_obj_index']

        self.obj_list[-1].set_checked(False)
        self.obj_list[self.current_obj_index].set_checked(True)

        # print(self.obj_type)

    def set_slider_combo_to_current(self):
        if 'merged' in self.obj_type[self.current_obj_index]:
            size_val = self.obj_size_slider.value()
            opacity_val = self.obj_opacity_slider.value()
            compo_mode = self.obj_blend_combo.currentText()

            if self.obj_size[self.current_obj_index] != size_val:
                self.obj_size_slider.setValue(self.obj_size[self.current_obj_index])
            if self.obj_opacity[self.current_obj_index] != opacity_val:
                self.obj_opacity_slider.setValue(self.obj_opacity[self.current_obj_index])
            if self.obj_comp_mode[self.current_obj_index] != compo_mode:
                self.obj_blend_combo.setCurrentText(self.obj_comp_mode[self.current_obj_index])
        else:
            return

    def clear_all(self):
        ind = np.arange(len(self.obj_list))[::-1]
        for i in ind:
            self.layer_layout.removeWidget(self.obj_list[i])
            self.obj_list[i].deleteLater()
            del self.obj_list[i]
        self.obj_id = []
        self.obj_name = []
        self.obj_type = []
        self.obj_data = []
        self.obj_size = []
        self.obj_opacity = []
        self.obj_comp_mode = []
        self.obj_count = 0
        self.current_obj_index = None

    def compare_obj_called(self):
        compare_names = [self.obj_name[ind] for ind in self.linked_indexes]
        compare_data = [self.obj_data[ind] for ind in self.linked_indexes]
        info_window = CompareWindow(compare_names, compare_data)
        info_window.exec()


