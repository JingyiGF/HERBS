import cv2
from aicspylibczi import CziFile
from pathlib import Path
from os.path import dirname, realpath, join
import pickle
import numpy as np
import colorsys
from .uuuuuu import hex2rgb

# czi_path = '~/Work/Kavli/Data/HERBS_DATA/abraham/Pecorino_mec_slide_1.czi'

class CZIReader(object):
    def __init__(self, czi_path):
        self.error_index = 0
        self.is_czi = True
        self.status = None
        self.file_name_list = [czi_path[:-4]]
        self.czi = CziFile(czi_path)
        self.czi_info = self.czi.dims
        self.dimensions = self.czi.get_dims_shape()
        self.is_mosaic = self.czi.is_mosaic()
        self.pixel_type = self.czi.pixel_type
        self.n_pages = 1
        self.data = {}
        self.scale = {}

        if 'T' in self.czi_info:
            if self.dimensions[0]['T'][1] != 1:
                self.status = 'multi-T'

        if 'A' in self.czi_info:
            self.is_rgb = True
            self.n_channels = 3
            if self.pixel_type == 'bgr24':
                self.pixel_type = 'rgb24'
                self.level = 255
                self.data_type = 'uint8'
            else:
                da_power = int(self.pixel_type[-2:]) / 3
                self.pixel_type = 'rgb' + self.pixel_type[-2:]
                self.level = int(np.power(2, da_power)) - 1
                self.data_type = 'uint' + str(int(da_power))
        else:
            self.is_rgb = False
            if self.pixel_type == 'gray16':
                self.level = 65535
                self.data_type = 'uint16'
            else:
                da_power = int(self.pixel_type[-2:]) / 3
                self.level = int(np.power(2, da_power)) - 1
                self.data_type = 'uint' + str(int(da_power))
            self.n_channels = self.dimensions[0]['C'][1]

        self.n_scenes = len(self.dimensions)
        self.scene_bbox = []
        if self.is_mosaic:
            for i in range(self.n_scenes):
                bbox = self.czi.get_mosaic_scene_bounding_box(index=i)
                self.scene_bbox.append((bbox.x, bbox.y, bbox.w, bbox.h))
        else:
            for i in range(self.n_scenes):
                bbox = self.czi.get_scene_bounding_box(index=i)
                self.scene_bbox.append((bbox.x, bbox.y, bbox.w, bbox.h))

        # get colors from metadata
        metadata = self.czi.meta[0]
        all_tags = [metadata[i].tag for i in range(len(metadata))]
        ds_ind = [ind for ind in range(len(all_tags)) if all_tags[ind] == 'DisplaySetting'][0]
        ds_tags = [metadata[ds_ind][i].tag for i in range(len(metadata[ds_ind]))]
        ch_ind = [ind for ind in range(len(ds_tags)) if ds_tags[ind] == 'Channels'][0]
        ch_tags = [metadata[ds_ind][ch_ind][i].tag for i in range(len(metadata[ds_ind][ch_ind]))]

        scale_ind = [ind for ind in range(len(all_tags)) if all_tags[ind] == 'Scaling'][0]
        scale_tags = [metadata[scale_ind][i].tag for i in range(len(metadata[scale_ind]))]
        scale_item_ind = [ind for ind in range(len(scale_tags)) if scale_tags[ind] == 'Items'][0]
        scale_item_tags = [metadata[scale_ind][scale_item_ind][i].tag for i in range(len(metadata[scale_ind][scale_item_ind]))]

        scaling_vals = []
        for i in range(len(scale_item_tags)):
            scale_info = metadata[scale_ind][scale_item_ind]
            single_scaling_tags = [scale_info[i][ind].tag for ind in range(len(scale_info[i]))]
            for j in range(len(single_scaling_tags)):
                scaling_vals.append(metadata[scale_ind][scale_item_ind][i][j].text)

        self.scaling_val = float(scaling_vals[0]) * 1e6

        self.rgb_colors = []
        self.hsv_colors = []
        self.channel_name = []
        self.gamma_val = []

        if self.is_rgb:
            self.rgb_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
            self.channel_name = ['Red', 'Green', 'Blue']
            for i in range(3):
                chsv = colorsys.rgb_to_hsv(self.rgb_colors[i][0], self.rgb_colors[i][1], self.rgb_colors[i][2])
                hsv_color = (chsv[0], chsv[1], chsv[2] / 255)
                self.hsv_colors.append(hsv_color)
            for i in range(len(ch_tags)):
                chn_info = metadata[ds_ind][ch_ind]
                single_channel_tags = [chn_info[i][ind].tag for ind in range(len(chn_info[i]))]
                channel_vals = []
                for j in range(len(single_channel_tags)):
                    channel_vals.append(metadata[ds_ind][ch_ind][i][j].text)
                if len(np.where(np.ravel(single_channel_tags) == 'Gamma')[0]) > 0:
                    self.gamma_val.append(channel_vals[np.where(np.ravel(single_channel_tags) == 'Gamma')[0][0]])
        else:
            for i in range(len(ch_tags)):
                chn_info = metadata[ds_ind][ch_ind]
                single_channel_tags = [chn_info[i][ind].tag for ind in range(len(chn_info[i]))]
                channel_vals = []
                for j in range(len(single_channel_tags)):
                    channel_vals.append(metadata[ds_ind][ch_ind][i][j].text)
                hex_color = channel_vals[np.where(np.ravel(single_channel_tags) == 'Color')[0][0]]
                self.channel_name.append(channel_vals[np.where(np.ravel(single_channel_tags) == 'ShortName')[0][0]])
                if len(np.where(np.ravel(single_channel_tags) == 'Gamma')[0]) > 0:
                    self.gamma_val.append(channel_vals[np.where(np.ravel(single_channel_tags) == 'Gamma')[0][0]])
                da_color = hex_color[0] + hex_color[3:]
                r, g, b = hex2rgb(da_color)
                chsv = colorsys.rgb_to_hsv(r, g, b)
                hsv_color = (chsv[0], chsv[1], chsv[2] / 255)
                self.hsv_colors.append(hsv_color)
                self.rgb_colors.append((r, g, b))

    def read_data(self, scale, scene_index=None):
        if scene_index is None:
            scene_index = np.arange(self.n_scenes)
        else:
            scene_index = [scene_index]

        for scind in scene_index:
            if self.is_rgb:
                if self.is_mosaic:
                    image_data = self.czi.read_mosaic(C=0, scale_factor=scale, region=self.scene_bbox[scind])
                    if len(image_data.shape) == 4:
                        image_data = image_data[0]
                else:
                    image_data_full = self.czi.read_image(region=self.scene_bbox[scind])
                    image_data = image_data_full[0]
                    image_info = image_data_full[1]
                    if image_info[0][0] == 'C':
                        image_data = image_data[0]
                img = image_data.copy()
                if self.pixel_type == 'rgb24':
                    img_data_temp = img.astype(np.uint8)
                else:
                    img_data_temp = img.astype(np.uint16)
                img_data_temp = cv2.cvtColor(img_data_temp, cv2.COLOR_BGR2RGB)
                self.data['scene %d' % scind] = img_data_temp
                self.scale['scene %d' % scind] = scale
            else:
                if self.n_channels != 1:
                    temp = []
                    for j in range(self.n_channels):
                        mosaic_data = self.czi.read_mosaic(C=j, scale_factor=scale, region=self.scene_bbox[scind])
                        img = mosaic_data[0].copy()
                        temp.append(img)
                    img_data_temp = np.dstack(temp)
                    self.data['scene %d' % scind] = img_data_temp
                    self.scale['scene %d' % scind] = scale
                else:
                    mosaic_data = self.czi.read_mosaic(C=0, scale_factor=scale, region=self.scene_bbox[scind])
                    img = mosaic_data[0].copy()
                    img_data_temp = img
                    self.data['scene %d' % scind] = img_data_temp.reshape(img.shape[0], img.shape[1], 1)
                    self.scale['scene %d' % scind] = scale
