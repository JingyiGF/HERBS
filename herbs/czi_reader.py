from aicspylibczi import CziFile
from pathlib import Path
from os.path import dirname, realpath, join
import pickle
import numpy as np
import colorsys
from uuuuuu import hex2rgb


class CZIReader(object):
    def __init__(self, czi_path):
        self.is_czi = True
        self.file_name_list = [czi_path[:-4]]
        self.czi = CziFile(czi_path)
        self.czi_info = self.czi.dims
        self.dimensions = self.czi.get_dims_shape()
        self.is_mosaic = self.czi.is_mosaic()
        self.data = {}

        if 'A' in self.czi_info:
            self.is_rgb = True
            self.level = 255
            self.data_type = 'uint8'
            self.n_channels = 3
        else:
            self.is_rgb = False
            self.level = 65535
            self.data_type = 'uint16'
            self.n_channels = self.dimensions[0]['C'][1]

        self.n_scenes = len(self.dimensions)
        if self.n_scenes == 1:
            if isinstance(self.dimensions, list):
                print('list')
            if isinstance(self.dimensions, dict):
                print('dict')
            raise Exception('Coder never met this situation, please give coder an example.')
        else:
            self.scene_bbox = []
            for i in range(self.n_scenes):
                bbox = self.czi.get_mosaic_scene_bounding_box(index=i)
                self.scene_bbox.append((bbox.x, bbox.y, bbox.w, bbox.h))

        # get colors from metadata
        metadata = self.czi.meta[0]
        all_tags = [metadata[i].tag for i in range(len(metadata))]
        ds_ind = [ind for ind in range(len(all_tags)) if all_tags[ind] == 'DisplaySetting'][0]
        ds_tags = [metadata[ds_ind][i].tag for i in range(len(metadata[ds_ind]))]
        ch_ind = [ind for ind in range(len(ds_tags)) if ds_tags[ind] == 'Channels'][0]
        ch_tags = [metadata[ds_ind][ch_ind][i].tag for i in range(len(metadata[ds_ind][ch_ind]))]
        self.rgb_colors = []
        self.hsv_colors = []
        self.channel_name = []
        self.gamma_val = []
        if self.is_rgb:
            for i in range(len(ch_tags)):
                chn_info = metadata[ds_ind][ch_ind]
                single_channel_tags = [chn_info[i][ind].tag for ind in range(len(chn_info[i]))]
                channel_vals = []
                for j in range(len(single_channel_tags)):
                    channel_vals.append(metadata[ds_ind][ch_ind][i][j].text)
                self.gamma_val.append(channel_vals[np.where(np.ravel(single_channel_tags) == 'Gamma')[0][0]])
            self.hsv_colors = [(0, self.level, self.level),
                               (120, self.level, self.level),
                               (240, self.level, self.level)]
            self.rgb_colors = [(self.level, 0, 0), (0, self.level, 0), (0, 0, self.level)]
            self.channel_name = ['Red', 'Green', 'Blue']
        else:
            for i in range(len(ch_tags)):
                chn_info = metadata[ds_ind][ch_ind]
                single_channel_tags = [chn_info[i][ind].tag for ind in range(len(chn_info[i]))]
                channel_vals = []
                for j in range(len(single_channel_tags)):
                    channel_vals.append(metadata[ds_ind][ch_ind][i][j].text)
                hex_color = channel_vals[np.where(np.ravel(single_channel_tags) == 'Color')[0][0]]
                self.channel_name.append(channel_vals[np.where(np.ravel(single_channel_tags) == 'ShortName')[0][0]])
                self.gamma_val.append(channel_vals[np.where(np.ravel(single_channel_tags) == 'Gamma')[0][0]])
                da_color = hex_color[0] + hex_color[3:]
                r, g, b = hex2rgb(da_color)
                chsv = colorsys.rgb_to_hsv(r, g, b)
                hsv_color = (chsv[0], chsv[1], chsv[2] / 255)
                # hsv_color = (int(chsv[0] * 360), int(chsv[1]), chsv[2])
                self.hsv_colors.append(hsv_color)
                self.rgb_colors.append((r, g, b))

    def read_data(self, scale, scene_index=None):
        if scene_index is None:
            scene_index = np.arange(self.n_scenes)
        else:
            scene_index = [scene_index]

        for scind in scene_index:
            if self.is_rgb:
                mosaic_data = self.czi.read_mosaic(C=0, scale_factor=scale, region=self.scene_bbox[scind])
                img = mosaic_data[0].copy()
                img_data_temp = img.astype(np.uint8)
                self.data['scene %d' % scind] = img_data_temp
            else:
                if self.n_channels != 1:
                    temp = []
                    for j in range(self.n_channels):
                        mosaic_data = self.czi.read_mosaic(C=j, scale_factor=scale, region=self.scene_bbox[scind])
                        img = mosaic_data[0].copy()
                        temp.append(img.astype(np.uint16))
                    img_data_temp = np.dstack(temp)
                    self.data['scene %d' % scind] = img_data_temp
                else:
                    mosaic_data = self.czi.read_mosaic(C=0, scale_factor=scale, region=self.scene_bbox[scind])
                    img = mosaic_data[0].copy()
                    img_data_temp = img.astype(np.uint16)
                    self.data['scene %d' % scind] = img_data_temp.reshape(img.shape[0], img.shape[1], 1)
