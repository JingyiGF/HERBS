import time
import os
import sys
from os.path import dirname, realpath, join
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import pyqtgraph.opengl as gl

import nrrd
import pickle
import shutil
import requests
import numpy as np
import pandas as pd

from .atlas_loader import process_atlas_raw_data
from .uuuuuu import hex2rgb, obj_data_to_mesh3d, make_contour_img
from .obj_items import render_volume, render_small_volume
from .atlas_downloader import DownloadThread


class WorkerProcessAllen(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(float)

    def __init__(self):
        super(WorkerProcessAllen, self).__init__()
        self.saving_folder = None
        self.data_local = None
        self.segmentation_local = None
        self.label_local = None
        self.b_val = None
        self.l_val = None
        self.vox_size = None

        self.atlas_data = None
        self.atlas_info = None
        self.segmentation_data = None
        self.unique_label = None
        self.label_info = None
        self.boundary = None
        self.small_mesh_list = {}
        self.mesh_data = None

    def set_data(self, saving_folder, data_local, segmentation_local, label_local, b_val, vox_size):
        self.saving_folder = saving_folder
        self.data_local = data_local
        self.segmentation_local = segmentation_local
        self.label_local = label_local
        self.b_val = b_val
        self.vox_size = vox_size

    def progress_control(self, total_count):
        self.progress.emit(total_count)

    def run(self):
        self.progress.emit(1)
        label_data, header = nrrd.read(os.path.join(self.saving_folder, self.segmentation_local))
        self.progress.emit(10)
        self.unique_label = np.unique(label_data)
        self.progress.emit(14)

        n_unique_labels = len(self.unique_label)
        mesh_path = os.path.join(self.saving_folder, 'meshes')
        if not os.path.exists(mesh_path):
            os.mkdir(mesh_path)
        self.progress.emit(15)

        atlas_size = label_data.shape

        axis_info = {'to_HERBS': (2, 0, 1), 'from_HERBS': (1, 2, 0), 'direction_change': (True, True, False),
                     'size': tuple(atlas_size)}

        outfile_axis = open(os.path.join(self.saving_folder, 'atlas_axis_info.pkl'), 'wb')
        pickle.dump(axis_info, outfile_axis)
        outfile_axis.close()

        downloaded_mesh_path = os.path.join(self.saving_folder, 'downloaded_meshes')

        progress_step = np.linspace(15, 30, n_unique_labels)
        missing_mesh_index = []
        for i in range(n_unique_labels):
            ind = self.unique_label[i]
            self.progress.emit(progress_step[i])
            if ind in [0]:
                continue

            filename = os.path.join(downloaded_mesh_path, '{}.obj'.format(ind))

            if os.path.exists(filename):
                try:
                    vertices, faces = obj_data_to_mesh3d(filename)
                    vertices = vertices / self.vox_size

                    vertices[:, 0] = atlas_size[0] - vertices[:, 0]
                    vertices[:, 1] = atlas_size[1] - vertices[:, 1]

                    verts = vertices.copy()
                    verts[:, 0] = vertices[:, 2].copy()
                    verts[:, 1] = vertices[:, 0].copy()
                    verts[:, 2] = vertices[:, 1].copy()

                    md = gl.MeshData(vertexes=verts, faces=faces)

                    outfile = open(os.path.join(mesh_path, '{}.pkl'.format(ind)), 'wb')
                    pickle.dump(md, outfile)
                    outfile.close()
                except IndexError:
                    missing_mesh_index.append(ind)
            else:
                missing_mesh_index.append(ind)

        target = os.path.join(self.saving_folder, "atlas_meshdata.pkl")
        shutil.copyfile(join(mesh_path, '997.pkl'), target)

        self.progress.emit(31)

        infile = open(os.path.join(self.saving_folder, 'atlas_meshdata.pkl'), 'rb')
        self.mesh_data = pickle.load(infile)
        infile.close()
        self.progress.emit(33)

        df = pd.read_csv(os.path.join(self.saving_folder, self.label_local))

        da_labels = df['safe_name'].values
        da_labels[da_labels == 'root'] = 'Brain'
        self.progress.emit(34)

        da_short_label = df['acronym'].values
        da_short_label[da_short_label == 'root'] = 'Brain'
        self.progress.emit(35)

        hex_colors = df['color_hex_triplet'].values
        rgb_colors = []
        for i in range(len(hex_colors)):
            r, g, b = hex2rgb(hex_colors[i])
            rgb_colors.append([r, g, b])
        rgb_colors = np.asarray(rgb_colors)

        self.progress.emit(36)

        levels = []
        structure_id_path = df['structure_id_path'].values
        for i in range(len(structure_id_path)):
            da_path = structure_id_path[i]
            da_path_split = da_path.split('/')
            for j in np.arange(len(da_path_split))[::-1]:
                if da_path_split[j] == '':
                    da_path_split.pop(j)
            levels.append(len(da_path_split))

        self.progress.emit(37)

        self.label_info = {'index': df['id'].values.astype(int),
                           'label': da_labels,
                           'parent': df['parent_structure_id'].values.astype(int),
                           'abbrev': da_short_label,
                           'color': rgb_colors,
                           'level_indicator': levels}

        with open(os.path.join(self.saving_folder, 'atlas_labels.pkl'), 'wb') as handle:
            pickle.dump(self.label_info, handle, protocol=pickle.HIGHEST_PROTOCOL)

        self.progress.emit(38)

        volume_data, header = nrrd.read(os.path.join(self.saving_folder, self.data_local))
        self.progress.emit(45)
        volume_data = np.transpose(volume_data[::-1, ::-1, :], (2, 0, 1))
        self.progress.emit(46)
        self.atlas_data = volume_data.copy()
        self.atlas_data = self.atlas_data - np.min(self.atlas_data)
        self.atlas_data = self.atlas_data / np.max(self.atlas_data)
        self.progress.emit(47)

        b_val = self.b_val.copy()
        if self.b_val[0] == 0:
            b_val[0] = int(atlas_size[0] / 2)
        if self.b_val[2] == 0:
            b_val[2] = int(atlas_size[2] / 2)
        self.progress.emit(48)

        self.atlas_info = [
            {'name': 'anterior', 'values': np.arange(self.atlas_data.shape[0]) * self.vox_size, 'units': 'um'},
            {'name': 'dorsal', 'values': np.arange(self.atlas_data.shape[1]) * self.vox_size, 'units': 'um'},
            {'name': 'right', 'values': np.arange(self.atlas_data.shape[2]) * self.vox_size, 'units': 'um'},
            {'vxsize': self.vox_size,
             'Bregma': [b_val[2], atlas_size[0] - 1 - b_val[0], atlas_size[1] - 1 - b_val[1]]}
        ]
        self.progress.emit(49)

        atlas = {'data': self.atlas_data, 'info': self.atlas_info}

        outfile = open(os.path.join(self.saving_folder, 'atlas_pre_made.pkl'), 'wb')
        pickle.dump(atlas, outfile)
        outfile.close()
        self.progress.emit(53)

        self.segmentation_data = np.transpose(label_data[::-1, ::-1, :], (2, 0, 1))
        self.segmentation_data = self.segmentation_data.astype(int)
        print(self.segmentation_data.shape)

        self.progress.emit(54)

        segment = {'data': self.segmentation_data, 'unique_label': self.unique_label}

        outfile = open(os.path.join(self.saving_folder, 'segment_pre_made.pkl'), 'wb')
        pickle.dump(segment, outfile)
        outfile.close()

        self.progress.emit(58)

        if missing_mesh_index:
            for da_ind in missing_mesh_index:
                render_small_volume(da_ind, mesh_path, self.atlas_data, self.segmentation_data, factor=2, level=0.1)

        self.progress.emit(60)

        file_list = os.listdir(mesh_path)
        progress_step = np.linspace(60, 68, len(file_list))
        for i in range(len(file_list)):
            self.progress.emit(progress_step[i])
            da_file = file_list[i]
            file_name = os.path.basename(da_file)
            da_name, file_extension = os.path.splitext(file_name)
            if file_extension == '.pkl':
                infile = open(os.path.join(mesh_path, da_file), 'rb')
                md = pickle.load(infile)
                infile.close()

                self.small_mesh_list[str(da_name)] = md

        outfile = open(os.path.join(self.saving_folder, 'atlas_small_meshdata.pkl'), 'wb')
        pickle.dump(self.small_mesh_list, outfile)
        outfile.close()
        self.progress.emit(70)

        segment_data_shape = self.segmentation_data.shape

        sagital_contour_img = np.zeros(segment_data_shape, 'i')
        coronal_contour_img = np.zeros(segment_data_shape, 'i')
        horizontal_contour_img = np.zeros(segment_data_shape, 'i')

        # pre-process boundary ----- todo: change this part as optional
        process_index = np.linspace(70, 78, segment_data_shape[0])
        for i in range(segment_data_shape[0]):
            self.progress.emit(process_index[i])
            da_slice = self.segmentation_data[i, :, :].copy()
            contour_img = make_contour_img(da_slice)
            sagital_contour_img[i, :, :] = contour_img

        outfile_ct = open(os.path.join(self.saving_folder, 'sagital_contour_pre_made.pkl'), 'wb')
        pickle.dump(sagital_contour_img, outfile_ct)
        outfile_ct.close()
        self.progress.emit(80)

        process_index = np.linspace(80, 88, segment_data_shape[1])
        for i in range(segment_data_shape[1]):
            self.progress.emit(process_index[i])
            da_slice = self.segmentation_data[:, i, :].copy()
            contour_img = make_contour_img(da_slice)
            coronal_contour_img[:, i, :] = contour_img

        outfile_ct = open(os.path.join(self.saving_folder, 'coronal_contour_pre_made.pkl'), 'wb')
        pickle.dump(coronal_contour_img, outfile_ct)
        outfile_ct.close()
        self.progress.emit(90)

        process_index = np.linspace(90, 98, segment_data_shape[2])
        for i in range(segment_data_shape[2]):
            self.progress.emit(process_index[i])
            da_slice = self.segmentation_data[:, :, i].copy()
            contour_img = make_contour_img(da_slice)
            horizontal_contour_img[:, :, i] = contour_img

        outfile_ct = open(os.path.join(self.saving_folder, 'horizontal_contour_pre_made.pkl'), 'wb')
        pickle.dump(horizontal_contour_img, outfile_ct)
        outfile_ct.close()
        self.progress.emit(100)

        # boundary = {'s_contour': sagital_contour_img,
        #             'c_contour': coronal_contour_img,
        #             'h_contour': horizontal_contour_img}
        #
        # self.boundary = {'data': boundary}

        # self.boundary = make_atlas_label_contour(self.saving_folder, self.segmentation_data)

        # target = os.path.join(self.saving_folder, 'atlas_labels.pkl')
        # if not os.path.exists(target):
        #     shutil.copyfile(join(dirname(__file__), "data/atlas_labels.pkl"), target)

        # self.progress.emit(100)

        self.finished.emit()


class MeshDownloader(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self):
        super(MeshDownloader, self).__init__()

        self.save_folder = None
        self.segmentation_local = None

    def set_data(self, save_folder, segmentation_local):
        self.save_folder = save_folder
        self.segmentation_local = os.path.join(save_folder, segmentation_local)

    def run(self):
        label_data, header = nrrd.read(self.segmentation_local)
        unique_label = np.unique(label_data)

        n_unique_labels = len(unique_label)
        progress_step = np.linspace(0, 100, n_unique_labels)

        downloaded_mesh_path = os.path.join(self.save_folder, 'downloaded_meshes')
        if not os.path.exists(downloaded_mesh_path):
            os.mkdir(downloaded_mesh_path)

        for i in range(n_unique_labels):
            ind = unique_label[i]
            self.progress.emit(progress_step[i])
            if ind in [0, 545]:
                continue
            url = 'http://download.alleninstitute.org/informatics-archive/current-release/mouse_ccf/annotation/ccf_2017/structure_meshes/{}.obj'.format(
                ind)
            r = requests.get(url, allow_redirects=True)
            da_file = open(os.path.join(downloaded_mesh_path, '{}.obj'.format(ind)), 'wb')
            da_file.write(r.content)
            da_file.close()
        self.finished.emit()


class AllenDownloader(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        layout = QVBoxLayout(self)

        self.setWindowTitle("Allen Mice Atlas Downloader")

        self.thread = QThread()
        self.worker = WorkerProcessAllen()
        self.mesh_thread = QThread()
        self.mesh_worker = MeshDownloader()

        self.continue_process = True

        self.voxel_size = 10
        self.bregma_coord = [0, 0, 0]
        radio_group = QFrame()
        radio_group.setStyleSheet('QFrame{border: 1px solid gray; border-radius: 3px}')
        radio_group_layout = QHBoxLayout(radio_group)
        radio_group_layout.setContentsMargins(5, 0, 5, 0)
        radio_group_layout.setAlignment(Qt.AlignCenter)
        self.vs_rabnt1 = QRadioButton('10 um')
        self.vs_rabnt1.setChecked(True)
        self.vs_rabnt2 = QRadioButton('25 um')
        self.vs_rabnt3 = QRadioButton('50 um')
        radio_group_layout.addWidget(self.vs_rabnt1)
        radio_group_layout.addWidget(self.vs_rabnt2)
        radio_group_layout.addWidget(self.vs_rabnt3)

        self.vs_rabnt1.toggled.connect(self.voxel_size_radio_clicked)
        self.vs_rabnt2.toggled.connect(self.voxel_size_radio_clicked)
        self.vs_rabnt3.toggled.connect(self.voxel_size_radio_clicked)

        self.data_url = "http://download.alleninstitute.org/informatics-archive/current-release/mouse_ccf/average_template/average_template_10.nrrd"
        self.segmentation_url = "http://download.alleninstitute.org/informatics-archive/current-release/mouse_ccf/annotation/ccf_2017/annotation_10.nrrd"

        self.label_local = "query.csv"
        self.data_local = "average_template_10.nrrd"
        self.segmentation_local = "annotation_10.nrrd"

        self.saving_folder = None

        self.finish = [False, False, False]
        self.process_finished = False
        self.downloading_atlas = False
        self.downloading_meshes = False

        self.label_bar = QProgressBar()
        self.label_bar.setMinimumWidth(400)
        self.label_bar.setValue(0)

        self.data_bar = QProgressBar()
        self.data_bar.setMinimumWidth(400)
        self.data_bar.setValue(0)

        self.segmentation_bar = QProgressBar()
        self.segmentation_bar.setMinimumWidth(400)
        self.segmentation_bar.setValue(0)

        self.mesh_bar = QProgressBar()
        self.mesh_bar.setMinimumWidth(400)
        self.mesh_bar.setValue(0)

        self.download_btn = QPushButton()
        self.download_btn. setMinimumWidth(100)
        self.download_btn.setText("Download")

        self.download_mesh_btn = QPushButton()
        self.download_mesh_btn.setMinimumWidth(100)
        self.download_mesh_btn.setText("Download Meshes")
        # self.download_mesh_btn.setEnabled(False)


        valid_input = QIntValidator(0, 99999)

        b_wrap = QFrame()
        b_layout = QHBoxLayout(b_wrap)

        b_label = QLabel('Bregma Coordinates (voxel): ')
        self.b_input1 = QLineEdit('0')
        self.b_input1.setStyleSheet('color: black')
        self.b_input1.setValidator(valid_input)
        self.b_input2 = QLineEdit('0')
        self.b_input2.setStyleSheet('color: black')
        self.b_input2.setValidator(valid_input)
        self.b_input3 = QLineEdit('0')
        self.b_input3.setStyleSheet('color: black')
        self.b_input3.setValidator(valid_input)

        b_layout.addWidget(b_label)
        b_layout.addWidget(self.b_input1)
        b_layout.addWidget(self.b_input2)
        b_layout.addWidget(self.b_input3)

        self.process_btn = QPushButton()
        self.process_btn.setMinimumWidth(100)
        self.process_btn.setText("Process")

        self.process_info = QLabel('The whole process takes some time. \n'
                                   'This window will be closed automatically when processing finished.')

        self.progress = QProgressBar(self)
        self.progress.setMinimumWidth(100)
        self.progress.setTextVisible(False)
        self.progress_label = QLabel()

        progress_wrap = QFrame()
        pw_layout = QHBoxLayout(progress_wrap)
        pw_layout.addWidget(self.progress)
        pw_layout.addWidget(self.progress_label)

        # ok button, used to close window
        ok_btn = QDialogButtonBox(QDialogButtonBox.Ok)
        ok_btn.accepted.connect(self.accept)

        layout.addWidget(radio_group)
        # layout.addWidget(self.label_bar)
        layout.addWidget(self.data_bar)
        layout.addWidget(self.segmentation_bar)
        layout.addWidget(self.download_btn)
        layout.addWidget(self.mesh_bar)
        layout.addWidget(self.download_mesh_btn)
        layout.addWidget(b_wrap)
        layout.addWidget(self.process_info)
        layout.addWidget(self.process_btn)
        layout.addWidget(progress_wrap)
        # layout.addWidget(ok_btn)

        # Binding Button Event
        self.download_btn.clicked.connect(self.download_start)
        self.download_mesh_btn.clicked.connect(self.download_mesh_start)
        self.process_btn.clicked.connect(self.process_start)

        self.b_input1.textChanged.connect(self.bregma_input1_changed)
        self.b_input2.textChanged.connect(self.bregma_input2_changed)
        self.b_input3.textChanged.connect(self.bregma_input3_changed)

    def bregma_input1_changed(self, text):
        if self.downloading_atlas:
            return
        if text == '':
            return
        self.bregma_coord[0] = int(text)

    def bregma_input2_changed(self, text):
        if self.downloading_atlas:
            return
        if text == '':
            return
        self.bregma_coord[1] = int(text)

    def bregma_input3_changed(self, text):
        if self.downloading_atlas:
            return
        if text == '':
            return
        self.bregma_coord[2] = int(text)

    def voxel_size_radio_clicked(self):
        if self.vs_rabnt1.isChecked():
            self.voxel_size = 10
            self.data_url = "http://download.alleninstitute.org/informatics-archive/current-release/mouse_ccf/average_template/average_template_10.nrrd"
            self.segmentation_url = "http://download.alleninstitute.org/informatics-archive/current-release/mouse_ccf/annotation/ccf_2017/annotation_10.nrrd"
            self.data_local = "average_template_10.nrrd"
            self.segmentation_local = "annotation_10.nrrd"
        elif self.vs_rabnt2.isChecked():
            self.voxel_size = 25
            self.data_url = 'http://download.alleninstitute.org/informatics-archive/current-release/mouse_ccf/average_template/average_template_25.nrrd'
            self.segmentation_url = 'http://download.alleninstitute.org/informatics-archive/current-release/mouse_ccf/annotation/ccf_2017/annotation_25.nrrd'
            self.data_local = "average_template_25.nrrd"
            self.segmentation_local = "annotation_25.nrrd"
        else:
            self.voxel_size = 50
            self.data_url = 'http://download.alleninstitute.org/informatics-archive/current-release/mouse_ccf/average_template/average_template_50.nrrd'
            self.segmentation_url = 'http://download.alleninstitute.org/informatics-archive/current-release/mouse_ccf/annotation/ccf_2017/annotation_50.nrrd'
            self.data_local = "average_template_50.nrrd"
            self.segmentation_local = "annotation_50.nrrd"

    # Download button event
    def download_start(self):
        self.saving_folder = str(QFileDialog.getExistingDirectory(self, "Select Folder to Save Atlas"))

        if self.saving_folder != '':
            self.download_btn.setVisible(False)
            self.process_info.setText('')
            self.downloading_atlas = True
            self.vs_rabnt1.setEnabled(False)
            self.vs_rabnt2.setEnabled(False)
            self.vs_rabnt3.setEnabled(False)

            target = os.path.join(self.saving_folder, self.label_local)
            if not os.path.exists(target):
                shutil.copyfile(join(dirname(__file__), "data/query.csv"), target)

            self.start_thread(self.segmentation_url, self.segmentation_local, self.set_segmentation_bar_value)
            time.sleep(0.1)
            self.start_thread(self.data_url, self.data_local, self.set_data_bar_value)
            time.sleep(0.1)

    def download_mesh_start(self):
        if self.downloading_atlas:
            self.process_info.setText('Please wait until the atlas finish downloading.')
            return

        self.process_info.setText('')

        if self.saving_folder is not None:
            saving_folder = self.saving_folder
        else:
            saving_folder = str(QFileDialog.getExistingDirectory(self, "Select Atlas Folder"))

        if saving_folder != '':
            exist_files = os.listdir(saving_folder)
            if self.data_local not in exist_files:
                self.process_info.setText('Atlas Data file is not in the selected folder. Please download atlas.')
                return
            if self.segmentation_local not in exist_files:
                self.process_info.setText('Segmentation Data file is not in the selected folder.')
                return

            self.download_mesh_btn.setVisible(False)
            self.downloading_meshes = True
            self.download_btn.setEnabled(False)
            self.mesh_worker.set_data(saving_folder, self.segmentation_local)
            self.mesh_worker.moveToThread(self.mesh_thread)
            self.mesh_thread.started.connect(self.mesh_worker.run)
            self.mesh_worker.finished.connect(self.mesh_thread.quit)
            self.mesh_worker.finished.connect(self.mesh_worker.deleteLater)
            self.mesh_thread.finished.connect(self.mesh_thread.deleteLater)
            self.mesh_worker.progress.connect(self.mesh_report_progress)
            self.mesh_thread.start()

    #
    def start_thread(self, url, local, func):
        file_size = requests.get(url, stream=True).headers['Content-Length']
        file_obj = open(os.path.join(self.saving_folder, local), 'wb')

        self.da_thread = DownloadThread(url, file_size, file_obj, buffer=1024)
        self.da_thread.download_process_signal.connect(func)
        self.da_thread.start()

    # Setting progress bar
    def set_data_bar_value(self, value):
        self.data_bar.setValue(value)
        if value == 100:
            self.finish[0] = True
            if self.finish[0] and self.finish[1]:
                self.downloading_atlas = False
            return

    def set_segmentation_bar_value(self, value):
        self.segmentation_bar.setValue(value)
        if value == 100:
            self.finish[1] = True
            if self.finish[0] and self.finish[1]:
                self.downloading_atlas = False
            return

    def report_progress(self, val):
        val = np.round(val, 2)
        self.progress.setValue(int(val))
        # self.progress.setFormat("%.02f %%" % val)
        self.progress_label.setText("%.02f %%" % val)

    def mesh_report_progress(self, i):
        self.mesh_bar.setValue(i)
        if i == 100:
            self.finish[2] = True
            self.downloading_meshes = False
            return

    def process_start(self):
        if self.downloading_atlas or self.downloading_meshes:
            self.process_info.setText('Please wait until finishing downloading files.')
            return
        else:
            self.process_info.setText('')

        if self.saving_folder is not None:
            saving_folder = self.saving_folder
        else:
            saving_folder = str(QFileDialog.getExistingDirectory(self, "Select Atlas Folder"))

        if saving_folder != '':
            # check files
            exist_files = os.listdir(saving_folder)
            if self.data_local not in exist_files:
                self.process_info.setText('Atlas Data file is not in the selected folder. Please download atlas.')
                return
            if self.segmentation_local not in exist_files:
                self.process_info.setText('Segmentation Data file is not in the selected folder.')
                return
            if self.label_local not in exist_files:
                target = os.path.join(self.saving_folder, self.label_local)
                if not os.path.exists(target):
                    shutil.copyfile(join(dirname(__file__), "data/query.csv"), target)
            if not os.path.exists(os.path.join(saving_folder, 'downloaded_meshes')):
                self.process_info.setText(
                    'Could not find downloaded meshes in the selected folder. Please download meshes.')
                return
            self.process_btn.setVisible(False)
            self.worker.set_data(saving_folder, self.data_local, self.segmentation_local, self.label_local,
                                 self.bregma_coord, self.voxel_size)
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.on_finish)
            # self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.worker.progress.connect(self.report_progress)
            self.thread.start()

    def on_finish(self):
        self.thread.quit()
        self.close()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
                                     "Do you want to leave?", QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.continue_process = False
            event.accept()
        else:
            event.ignore()



