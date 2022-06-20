import os
import cv2
import tifffile
import colorsys
import numpy as np
import imagecodecs


# image_file_path = '/Users/jingyig/Work/Kavli/Data/HERBS_DATA/test_image_type/image_0195.tif'

class ImageReader(object):
    def __init__(self, image_file_path):
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



# image_file_path = '/Users/jingyig/Work/Kavli/Data/HERBS_DATA/BIGTIF_uni_tp-0_ch-0_st-0-x00-y00_obj-left_cam-left_etc.lux.tif'
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

# image_file_path = '/Users/jingyig/Work/Kavli/Data/HERBS_DATA/test_image_type/image_0195.tif'


class TIFFReader(object):
    def __init__(self, image_file_path):
        self.is_czi = False
        self.file_name_list = [image_file_path[:-4]]
        if self.file_name_list[0][-1] == '.':
            self.file_name_list[0] = self.file_name_list[0][:-1]

        da_file = tifffile.TiffFile(image_file_path)
        self.n_scenes = len(da_file.series)
        self.n_pages = len(da_file.pages)
        self.pixel_type = da_file.pages[0].dtype

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
            print('please contact maintainer.')

        if self.is_rgb:
            self.rgb_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
            self.channel_name = ['Red', 'Green', 'Blue']
            for i in range(3):
                chsv = colorsys.rgb_to_hsv(self.rgb_colors[i][0], self.rgb_colors[i][1], self.rgb_colors[i][2])
                hsv_color = (chsv[0], chsv[1], chsv[2] / 255)
                self.hsv_colors.append(hsv_color)
        else:
            self.rgb_colors = [(128, 128, 128)]
            chsv = colorsys.rgb_to_hsv(self.rgb_colors[0][0], self.rgb_colors[0][1], self.rgb_colors[0][2])
            hsv_color = (chsv[0], chsv[1], chsv[2] / 255)
            self.hsv_colors.append(hsv_color)
            self.channel_name = ['Gray']

        if da_file.is_bigtiff:
            if self.n_scenes > 1 or self.n_pages == 1:
                print('test multi series')
            else:
                self.data['scene 0'] = da_file.asarray()
                self.scale['scene 0'] = 100
        else:
            if self.n_scenes > 1 or self.n_pages > 1:
                print('test multi series')
            else:
                img_data = da_file.asarray()
                if len(img_data.shape) == 2:
                    img_data = [img_data]
                    img_data = np.dstack(img_data)
                self.data['scene 0'] = img_data
                self.scale['scene 0'] = 100

        da_file.close()

        # for tag in da_file.pages[0].tags:
        #     tag_name, tag_value = tag.name, tag.value
        #     print(tag_name, tag_value)






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
