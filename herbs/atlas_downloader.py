import urllib.request

import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import queue
import requests


class DownloadThread(QThread):
    download_proess_signal = pyqtSignal(int)

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
                if not chunk: break
                self.fileobj.seek(offset)
                self.fileobj.write(chunk)
                offset = offset + len(chunk)
                proess = offset / int(self.filesize) * 100
                self.download_proess_signal.emit(int(proess))
            self.fileobj.close()
            self.exit(0)

        except Exception as e:
            print(e)


class AtlasDownloader(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        layout = QVBoxLayout(self)


        self.label_url = "https://www.nitrc.org/frs/download.php/12261/WHS_SD_rat_atlas_v4.label"
        self.data_url = "https://www.nitrc.org/frs/downloadlink.php/9423/WHS_SD_rat_T2star_v1.01.nii.gz"
        self.mask_url = "https://www.nitrc.org/frs/downloadlink.php/9425/WHS_SD_rat_brainmask_v1.01.nii.gz"
        self.segmentation_url = "https://www.nitrc.org/frs/download.php/12260/WHS_SD_rat_atlas_v4.nii.gz"

        self.label_local = "WHS_SD_rat_atlas_v4.label"
        self.data_local = "WHS_SD_rat_T2star_v1.01.nii.gz"
        self.mask_local = "WHS_SD_rat_brainmask_v1.01.nii.gz"
        self.segmentation_local = "WHS_SD_rat_atlas_v4.nii.gz"

        self.finish = [False, False, False, False]

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

        # ok button, used to close window
        ok_btn = QDialogButtonBox(QDialogButtonBox.Ok)
        ok_btn.accepted.connect(self.accept)

        layout.addWidget(self.label_bar)
        layout.addWidget(self.data_bar)
        layout.addWidget(self.mask_bar)
        layout.addWidget(self.segmentation_bar)
        layout.addWidget(self.download_btn)
        layout.addWidget(ok_btn)

        # Binding Button Event
        self.download_btn.clicked.connect(self.download_start)

    # Download button event
    def download_start(self):
        self.saving_folder = str(QFileDialog.getExistingDirectory(self, "Select Folder to Save Atlas"))

        if self.saving_folder != '':
            self.start_thread(self.label_url, self.label_local, self.set_label_bar_value)
            self.start_thread(self.data_url, self.data_local, self.set_data_bar_value)
            self.start_thread(self.mask_url, self.mask_local, self.set_mask_bar_value)
            self.start_thread(self.segmentation_url, self.segmentation_local, self.set_segmentation_bar_value)

    #
    def start_thread(self, url, local, func):
        file_size = requests.get(url, stream=True).headers['Content-Length']
        file_obj = open(os.path.join(self.saving_folder, local), 'wb')

        self.da_thread = DownloadThread(url, file_size, file_obj, buffer=1024)
        self.da_thread.download_proess_signal.connect(func)
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

    def accept(self) -> None:
        self.close()




