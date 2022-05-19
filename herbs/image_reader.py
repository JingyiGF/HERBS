import os
import cv2
import tifffile
import colorsys
import numpy as np


class ImageReader(object):
    def __init__(self, image_file_path):
        self.is_czi = False
        self.file_name_list = [image_file_path[:-4]]
        if self.file_name_list[0][-1] == '.':
            self.file_name_list[0] = self.file_name_list[0][:-1]
        self.n_scenes = 1

        file_type = image_file_path[-4:].lower()

        self.scaling_val = None
        self.is_rgb = True
        self.pixel_type = 'rgb24'
        self.level = 255
        self.n_channels = 3
        self.data_type = 'uint8'
        self.rgb_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        self.channel_name = ['Red', 'Green', 'Blue']
        self.hsv_colors = []
        for i in range(3):
            chsv = colorsys.rgb_to_hsv(self.rgb_colors[i][0], self.rgb_colors[i][1], self.rgb_colors[i][2])
            hsv_color = (chsv[0], chsv[1], chsv[2] / 255)
            self.hsv_colors.append(hsv_color)
        self.gamma_val = []

        self.data = {}
        self.scale = {}
        if file_type in ['.jpg', 'jpeg', '.png', '.bmp']:
            img_data = cv2.imread(image_file_path)
            img_data = cv2.cvtColor(img_data, cv2.COLOR_BGR2RGB)
        else:
            print('tiff test')
            img_data = tifffile.imread(image_file_path)
        self.data['scene 0'] = img_data
        self.scale['scene 0'] = 1


class ImagesReader(object):
    def __init__(self, folder_path):
        if os.path.exists(folder_path):
            all_files_in_folder = os.listdir(folder_path)
        else:
            return

        self.is_czi = False
        self.is_rgb = True
        self.n_channels = 3
        self.level = 255
        self.data_type = 'uint8'
        self.hsv_colors = [(0, 255, 255), (120, 255, 255), (240, 255, 255)]
        self.rgb_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        self.channel_name = ['Red', 'Green', 'Blue']
        self.file_name_list = []
        self.data = {}
        scene_id = 0

        for i in range(len(all_files_in_folder)):
            da_image_file = all_files_in_folder[i]
            da_file_name = da_image_file[:-4]
            if da_file_name[-1] == '.':
                da_file_name = da_file_name[:-1]

            file_type = da_image_file[-4:]
            if file_type in ['.bmp', '.jpg', '.png', 'jpeg', '.tif', '.pdf']:
                self.file_name_list.append(da_file_name)
                da_file_path = os.path.join(folder_path, da_image_file)

                if file_type in ['.bmp', '.jpg', '.png', 'jpeg']:
                    data = cv2.imread(da_file_path)
                    img_data = cv2.cvtColor(data, cv2.COLOR_BGR2RGB)
                else:
                    print('TIFF file is testing')
                    img_data = tifffile.imread(da_file_path)

                self.data['scene %d' % scene_id] = img_data

                scene_id += 1

        self.n_scenes = len(self.data)
