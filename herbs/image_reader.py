import os
import cv2
import tifffile
import numpy as np
from aicspylibczi import CziFile
from pathlib import Path
from os.path import dirname, realpath, join
from herrbs.czi_reader import CZIReader


# class ImageReader(object):
#     def __init__(self, file_path, scale=0.5, scene_index=None):
#         self.is_czi = False
#         self.n_scenes = 1
#         self.pth = Path(file_path)
#         self.file_type = file_path[-4:].lower()
#
#         self.image_file = {}
#         if self.file_type == '.czi':
#             self.czi = CziFile(self.pth)
#             self.czi_info = CZIInfoReader(self.czi)
#             czi_data = CZIDataReader(self.czi, self.czi_info, scale, scene_index)
#             self.scene_bbox = self.czi_info.da_bbox
#             self.is_rgb = self.czi_info.is_rgb
#             self.n_scenes = self.czi_info.n_scenes
#             self.n_channels = self.czi_info.n_channels
#             self.data_type = self.czi_info.data_type
#             self.data = czi_data.data
#             self.channel_name = self.czi_info.channel_name
#             self.hsv_colors = self.czi_info.hsv_colors
#             self.rgb_colors = self.czi_info.rgb_colors
#         else:
#             self.czi = None
#             self.scene_bbox = None
#             self.is_rgb = True
#             self.gray_max = 255
#             self.n_scenes = 1
#             self.n_channels = 3
#             self.data_type = 'uint8'
#             self.data = {}
#             if self.file_type in ['.jpg', 'jpeg', '.png']:
#                 data = cv2.imread(file_path)
#                 img_data = cv2.cvtColor(data, cv2.COLOR_BGR2RGB)
#             elif self.file_type == '.tif':
#                 print('TIFF file is testing')
#                 img_data = tifffile.imread(file_path)
#             self.data['scene 0'] = [img_data]
#             self.hsv_colors = [(0, 255, 255), (120, 255, 255), (240, 255, 255)]
#             self.rgb_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
#             self.channel_name = ['Red', 'Green', 'Blue']


class ImageReader(object):
    def __init__(self, image_file_path):
        self.is_czi = False
        self.file_name_list = [image_file_path[:-4]]
        if self.file_name_list[0][-1] == '.':
            self.file_name_list[0] = self.file_name_list[0][:-1]
        self.n_scenes = 1
        self.is_rgb = True
        self.gray_max = 255
        self.n_channels = 3
        self.data_type = 'uint8'
        self.hsv_colors = [(0, 255, 255), (120, 255, 255), (240, 255, 255)]
        self.rgb_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        self.channel_name = ['Red', 'Green', 'Blue']

        file_type = image_file_path[-4:].lower()

        self.color_data = {}
        self.gray_data = {}
        if file_type in ['.jpg', 'jpeg', '.png', '.bmp']:
            data = cv2.imread(image_file_path)
            img_data = cv2.cvtColor(data, cv2.COLOR_BGR2RGB)
        else:
            print('TIFF file is testing')
            img_data = tifffile.imread(image_file_path)
        self.color_data['scene 0'] = img_data
        self.gray_data['scene 0'] = cv2.cvtColor(img_data, cv2.COLOR_RGB2GRAY)
        self.hsv_colors = cv2.cvtColor(img_data, cv2.COLOR_RGB2HSV)


class ImagesReader(object):
    def __init__(self, folder_path, image_files_list):
        self.folder_path = folder_path
        self.is_czi = False
        self.is_rgb = True
        self.n_channels = 3
        self.gray_max = 255
        self.data_type = 'uint8'
        self.hsv_colors = [(0, 255, 255), (120, 255, 255), (240, 255, 255)]
        self.rgb_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        self.channel_name = ['Red', 'Green', 'Blue']
        self.file_name_list = []
        self.images_shape = []
        self.color_data = {}
        self.gray_data = {}

        for i in range(len(image_files_list)):
            da_image = image_files_list[i]
            if da_image[-4:] in ['.bmp', '.jpg', '.tif', '.png', 'jpeg']:
                self.file_name_list.append(da_image)
        self.n_scenes = len(self.file_name_list)

        for i in range(self.n_scenes):
            if self.file_name_list[i][-4:] in ['.jpg', 'jpeg', '.png', '.bmp']:
                data = cv2.imread(os.path.join(folder_path, self.file_name_list[i]))
                img_data = cv2.cvtColor(data, cv2.COLOR_BGR2RGB)
            else:
                print('TIFF file is testing')
                img_data = tifffile.imread(os.path.join(folder_path, self.file_name_list[i]))
            self.color_data['scene %d' % i] = img_data
            self.gray_data['scene %d' % i] = cv2.cvtColor(img_data, cv2.COLOR_RGB2GRAY)

