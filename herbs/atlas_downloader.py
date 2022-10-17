import urllib.request
import numpy as np
import time
import os
import sys
from os.path import dirname, realpath, join
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import pickle
import shutil
import requests

from .atlas_loader import process_atlas_raw_data
from .obj_items import render_volume, render_small_volume


class DownloadThread(QThread):
    download_process_signal = pyqtSignal(int)

    def __init__(self, url, filesize, fileobj, buffer):
        super(DownloadThread, self).__init__()
        self.url = url
        self.filesize = filesize
        self.fileobj = fileobj
        self.buffer = buffer

    def run(self):
        try:
            rsp = requests.get(self.url, stream=True)
            offset = 0
            for chunk in rsp.iter_content(chunk_size=self.buffer):
                if not chunk:
                    break
                self.fileobj.seek(offset)
                self.fileobj.write(chunk)
                offset = offset + len(chunk)
                proess = offset / int(self.filesize) * 100
                self.download_process_signal.emit(int(proess))
            self.fileobj.close()
            self.exit(0)

        except Exception as e:
            print(e)


class WorkerProcessData(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self):
        super(WorkerProcessData, self).__init__()
        self.saving_folder = None
        self.data_local = None
        self.segmentation_local = None
        self.mask_local = None
        self.b_val = None
        self.l_val = None
        self.vox_size = None

        self.atlas_data = None
        self.atlas_info = None
        self.segmentation_data = None
        self.unique_label = None
        self.label_info = None
        self.boundary = None
        self.small_mesh_list = None
        self.mesh_data = None

    def set_data(self, saving_folder, data_local, segmentation_local, mask_local, b_val, l_val, vox_size):
        self.saving_folder = saving_folder
        self.data_local = data_local
        self.segmentation_local = segmentation_local
        self.mask_local = mask_local
        self.b_val = b_val
        self.l_val = l_val
        self.vox_size = vox_size

    def run(self):
        target = os.path.join(self.saving_folder, 'atlas_labels.pkl')
        if not os.path.exists(target):
            shutil.copyfile(join(dirname(__file__), "data/atlas_labels.pkl"), target)

        self.progress.emit(1)

        infile = open(os.path.join(self.saving_folder, 'atlas_labels.pkl'), 'rb')
        self.label_info = pickle.load(infile)
        infile.close()

        self.progress.emit(5)

        self.atlas_data, self.atlas_info, self.segmentation_data, self.unique_label, self.boundary, msg = \
            process_atlas_raw_data(self.saving_folder, data_file=self.data_local,
                                   segmentation_file=self.segmentation_local, mask_file=self.mask_local,
                                   bregma_coordinates=self.b_val, lambda_coordinates=self.l_val,
                                   voxel_size=self.vox_size)

        if msg == 'Atlas loaded successfully.':
            self.progress.emit(40)
            self.mesh_data = render_volume(self.atlas_data, self.saving_folder, factor=2, level=0.1)
            self.progress.emit(50)
            save_path = os.path.join(self.saving_folder, 'meshes')
            if not os.path.exists(save_path):
                os.mkdir(save_path)

            n_label = len(self.unique_label)
            progress_step = np.linspace(50, 95, n_label)

            for i in range(n_label):
                self.progress.emit(progress_step[i])
                label_id = int(self.unique_label[i])

                if label_id == 0:
                    continue
                render_small_volume(label_id, save_path, self.atlas_data, self.segmentation_data, factor=2, level=0.1)

            self.small_mesh_list = {}
            file_list = os.listdir(save_path)
            for da_file in file_list:
                file_name = os.path.basename(da_file)
                da_name, file_extension = os.path.splitext(file_name)
                if file_extension == '.pkl':
                    infile = open(os.path.join(save_path, da_file), 'rb')
                    md = pickle.load(infile)
                    infile.close()

                    self.small_mesh_list[str(da_name)] = md

            self.progress.emit(97)
            outfile = open(os.path.join(self.saving_folder, 'atlas_small_meshdata.pkl'), 'wb')
            pickle.dump(self.small_mesh_list, outfile)
            outfile.close()

            self.progress.emit(100)

        self.finished.emit()


class AtlasDownloader(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        layout = QVBoxLayout(self)

        self.setWindowTitle("Waxholm Rat Atlas Downloader")

        self.continue_process = True

        self.label_url = "https://www.nitrc.org/frs/download.php/12261/WHS_SD_rat_atlas_v4.label"
        self.data_url = "https://www.nitrc.org/frs/downloadlink.php/9423/WHS_SD_rat_T2star_v1.01.nii.gz"
        self.mask_url = "https://www.nitrc.org/frs/downloadlink.php/9425/WHS_SD_rat_brainmask_v1.01.nii.gz"
        self.segmentation_url = "https://www.nitrc.org/frs/download.php/12260/WHS_SD_rat_atlas_v4.nii.gz"

        self.label_local = "WHS_SD_rat_atlas_v4.label"
        self.data_local = "WHS_SD_rat_T2star_v1.01.nii.gz"
        self.mask_local = "WHS_SD_rat_brainmask_v1.01.nii.gz"
        self.segmentation_local = "WHS_SD_rat_atlas_v4.nii.gz"

        self.saving_folder = None

        self.thread = QThread()
        self.worker = WorkerProcessData()

        self.b_val = (246, 653, 440)
        self.l_val = (244, 442, 464)
        self.vox_size = 39.0625

        self.finish = [False, False, False, False]
        self.process_finished = False

        self.label_bar = QProgressBar()
        self.label_bar.setMinimumWidth(400)
        self.label_bar.setValue(0)

        self.data_bar = QProgressBar()
        self.data_bar.setMinimumWidth(400)
        self.data_bar.setValue(0)

        self.mask_bar = QProgressBar()
        self.mask_bar.setMinimumWidth(400)
        self.mask_bar.setValue(0)

        self.segmentation_bar = QProgressBar()
        self.segmentation_bar.setMinimumWidth(400)
        self.segmentation_bar.setValue(0)

        self.download_btn = QPushButton()
        self.download_btn. setMinimumWidth(100)
        self.download_btn.setText("Download")

        self.process_btn = QPushButton()
        self.process_btn.setMinimumWidth(100)
        self.process_btn.setText("Process")

        self.process_label = QLabel()
        self.process_label.setMinimumWidth(100)
        self.process_label.setText("")

        self.progress = QProgressBar(self)
        self.progress.setMinimumWidth(100)

        self.process_info = QLabel('The whole process takes around 40 min - 1 hour. \n'
                                   'This window will be closed automatically when processing finished.\n')

        # ok button, used to close window
        ok_btn = QDialogButtonBox(QDialogButtonBox.Ok)
        ok_btn.accepted.connect(self.accept)

        layout.addWidget(self.label_bar)
        layout.addWidget(self.data_bar)
        layout.addWidget(self.mask_bar)
        layout.addWidget(self.segmentation_bar)
        layout.addWidget(self.download_btn)
        layout.addWidget(self.process_info)
        layout.addWidget(self.process_btn)
        layout.addWidget(self.progress)
        layout.addWidget(self.process_label)
        # layout.addWidget(ok_btn)

        # Binding Button Event
        self.download_btn.clicked.connect(self.download_start)
        self.process_btn.clicked.connect(self.process_start)

    # Download button event
    def download_start(self):
        self.saving_folder = str(QFileDialog.getExistingDirectory(self, "Select Folder to Save Atlas"))

        if self.saving_folder != '':
            self.download_btn.setVisible(False)
            target = os.path.join(self.saving_folder, 'atlas_labels.pkl')
            if not os.path.exists(target):
                shutil.copyfile(join(dirname(__file__), "data/atlas_labels.pkl"), target)

            self.start_thread(self.label_url, self.label_local, self.set_label_bar_value)
            self.start_thread(self.mask_url, self.mask_local, self.set_mask_bar_value)
            time.sleep(0.1)
            self.start_thread(self.segmentation_url, self.segmentation_local, self.set_segmentation_bar_value)
            time.sleep(0.1)
            self.start_thread(self.data_url, self.data_local, self.set_data_bar_value)

    #
    def start_thread(self, url, local, func):
        file_size = requests.get(url, stream=True).headers['Content-Length']
        file_obj = open(os.path.join(self.saving_folder, local), 'wb')

        self.da_thread = DownloadThread(url, file_size, file_obj, buffer=1024)
        self.da_thread.download_process_signal.connect(func)
        self.da_thread.start()

    # Setting progress bar
    def set_label_bar_value(self, value):
        self.label_bar.setValue(value)
        if value == 100:
            self.finish[0] = True
            return

    def set_data_bar_value(self, value):
        self.data_bar.setValue(value)
        if value == 100:
            self.finish[1] = True
            return

    def set_mask_bar_value(self, value):
        self.mask_bar.setValue(value)
        if value == 100:
            self.finish[2] = True
            return

    def set_segmentation_bar_value(self, value):
        self.segmentation_bar.setValue(value)
        if value == 100:
            self.finish[3] = True
            return

    def report_progress(self, i):
        self.progress.setValue(i)

    def process_start(self):
        # if not np.all(self.finish):
        #     return
        if self.saving_folder is not None:
            saving_folder = self.saving_folder
        else:
            saving_folder = str(QFileDialog.getExistingDirectory(self, "Select Atlas Folder"))

        if saving_folder != '':
            self.process_btn.setVisible(False)
            self.worker.set_data(saving_folder, self.data_local, self.segmentation_local, self.mask_local,
                                 self.b_val, self.l_val, self.vox_size)
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

    # def accept(self) -> None:
    #     if self.process_finished:
    #         self.close()
    #     else:
    #         return


