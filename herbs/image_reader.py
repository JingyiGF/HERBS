import os
import cv2
import tifffile
import colorsys
import numpy as np


# image_file_path = '/Users/jingyig/Work/Kavli/Data/HERBS_DATA/test_image_type/image_0195.tif'

class ImageReader(object):
    def __init__(self, image_file_path):
        self.error_index = 0
        self.is_czi = False
        self.file_name_list = [image_file_path[:-4]]
        if self.file_name_list[0][-1] == '.':
            self.file_name_list[0] = self.file_name_list[0][:-1]
        self.n_scenes = 1
        self.n_pages = 1

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

        img_data = cv2.imread(image_file_path)
        img_data = cv2.cvtColor(img_data, cv2.COLOR_BGR2RGB)

        self.data['scene 0'] = img_data
        self.scale['scene 0'] = 1



# image_file_path = '/Users/jingyig/Work/Kavli/Data/HERBS_DATA/TIF_test/13234_PHALDAB_s3_g004_tiff_30_s3.tif'
#
#
# import h5py
# filename = '/Users/jingyig/Work/Kavli/Data/HERBS_DATA/RAW-TILE_Cam_Left_00000.lux.h5'
#
# with h5py.File(filename, "r") as f:
#     # List all groups
#     all_keys = list(f.keys())
#     # Get the data
#     data = f[all_keys[0]]
#     print(data.shape)
#     plt.imshow(data[800, :, :])
#     a = data[800, :, :]
#     plt.show()
#     meta_data = f[all_keys[1]]
#
#
#
#     print(meta_data)
#
# f = h5py.File(filename, "r")
# list(f.keys())
#
# f['Data'].attrs.keys()
# f['Data'].attrs['CLASS']
# f['Data'].attrs['element_size_um']
# f.close()
# array([6.  , 1.95, 1.95])

# image_file_path = '/Users/jingyig/Work/Kavli/Data/HERBS_DATA/TIF_test/2_2_rotated.tif'


class TIFFReader(object):
    def __init__(self, image_file_path):
        self.error_index = 0
        self.is_czi = False
        self.file_name_list = [image_file_path[:-4]]
        if self.file_name_list[0][-1] == '.':
            self.file_name_list[0] = self.file_name_list[0][:-1]

        da_file = tifffile.TiffFile(image_file_path)
        self.n_scenes = len(da_file.series)

        if self.n_scenes > 1:
            self.error_index = 1
        else:
            self.n_pages = len(da_file.pages)
            self.pixel_type = da_file.pages[0].dtype
            self.software = da_file.pages[0].software
            self.is_imagej = da_file.is_imagej

            self.scaling_val = None

            self.hsv_colors = []
            self.gamma_val = []
            self.data = {}
            self.scale = {}

            if self.pixel_type == 'uint8':
                self.pixel_type = 'rgb24'
                self.level = 255
                self.data_type = 'uint8'
                self.is_rgb = True
                self.n_channels = 3
            elif self.pixel_type == 'uint16':
                self.pixel_type = 'gray16'
                self.level = 65535
                self.data_type = 'uint16'
                self.is_rgb = False
                self.n_channels = 1
            else:
                self.error_index = 2

            if da_file.is_imagej:
                if da_file.is_bigtiff:
                    if self.n_pages == 1:
                        self.error_index = 3
                    else:
                        self.data['scene 0'] = da_file.asarray()
                        self.scale['scene 0'] = 100
                        self.error_index = 7
                else:
                    if self.n_pages == 1:
                        img_data = da_file.asarray()
                        if len(img_data.shape) == 2:
                            img_data = [img_data]
                            img_data = np.dstack(img_data)
                        self.data['scene 0'] = img_data
                        self.scale['scene 0'] = 100
                    else:
                        temp = da_file.asarray()
                        img_data = []
                        for i in range(self.n_pages):
                            img_data.append(temp[i])
                        img_data = np.dstack(img_data)
                        img_data = img_data.astype(self.data_type)
                        self.data['scene 0'] = img_data
                        self.scale['scene 0'] = 100
                        self.n_channels = self.n_pages
                        self.is_rgb = False
                        self.n_pages = 1
                        self.pixel_type = 'gray8'
            else:
                if da_file.is_bigtiff:
                    if self.n_pages == 1:
                        self.error_index = 4
                    else:
                        self.data['scene 0'] = da_file.asarray()
                        self.scale['scene 0'] = 100
                        self.error_index = 7
                else:
                    if self.n_pages == 1:
                        img_data = da_file.asarray()
                        if len(img_data.shape) == 2:
                            img_data = [img_data]
                            img_data = np.dstack(img_data)
                        self.data['scene 0'] = img_data
                        self.scale['scene 0'] = 100
                    else:
                        self.error_index = 5

        if self.pixel_type == 'rgb24':
            self.rgb_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
            self.channel_name = ['Red', 'Green', 'Blue']
            for i in range(3):
                chsv = colorsys.rgb_to_hsv(self.rgb_colors[i][0], self.rgb_colors[i][1], self.rgb_colors[i][2])
                hsv_color = (chsv[0], chsv[1], chsv[2] / 255)
                self.hsv_colors.append(hsv_color)
        elif self.pixel_type == 'gray16':
            self.rgb_colors = [(128, 128, 128)]
            chsv = colorsys.rgb_to_hsv(self.rgb_colors[0][0], self.rgb_colors[0][1], self.rgb_colors[0][2])
            hsv_color = (chsv[0], chsv[1], chsv[2] / 255)
            self.hsv_colors.append(hsv_color)
            self.channel_name = ['Gray']
        elif self.pixel_type == 'gray8':
            possible_rgb_color = [(128, 128, 128), (255, 0, 0), (0, 255, 0), (0, 0, 255)]
            possible_channel_name = ['Gray', 'Red', 'Green', 'Blue']
            self.rgb_colors = []
            self.channel_name = []
            for i in range(self.n_channels):
                self.rgb_colors.append(possible_rgb_color[i])
                chsv = colorsys.rgb_to_hsv(self.rgb_colors[i][0], self.rgb_colors[i][1], self.rgb_colors[i][2])
                hsv_color = (chsv[0], chsv[1], chsv[2] / 255)
                self.hsv_colors.append(hsv_color)
                self.channel_name.append(possible_channel_name[i])
        else:
            self.error_index = 6

        da_file.close()

        # for tag in da_file.pages[0].tags:
        #     tag_name, tag_value = tag.name, tag.value
        #     print(tag_name, tag_value)






class ImagesReader(object):
    def __init__(self, folder_path):

        all_files_in_folder = os.listdir(folder_path)
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
