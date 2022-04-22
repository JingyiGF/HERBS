import os
import numpy as np
import math
import pandas as pd
import cv2
import pickle
import csv
import time
import scipy.ndimage as ndi
from numba import jit
import colorsys
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import tifffile
from aicspylibczi import CziFile
from pathlib import Path
from os.path import dirname, realpath, join
from scipy.interpolate import interp1d, splprep, splev


def read_label(file):
    lines = []
    for line in file:
        lines.append(line)
    
    n_lines = len(lines)
    label_index = np.zeros(n_lines - 14, 'i')
    label_index[:] = np.nan
    label_colors = np.zeros((n_lines - 14, 3), 'i')
    label_colors[:] = np.nan
    label_names = []
    for i in range(n_lines - 14):
        split_lines = lines[i + 14].split()
        label_index[i] = int(split_lines[0])
        label_colors[i] = np.array([split_lines[1], split_lines[2], split_lines[3]]).astype(int)
        split_lines2 = lines[i + 14].split('"')
        label_names.append(split_lines2[1])
    
    return label_index, label_names, label_colors


def rotation_x(theta):
    ct = np.cos(theta)
    st = np.sin(theta)
    rx = np.array([[1, 0, 0], [0, ct, -st], [0, st, ct]])
    return rx


def rotation_y(theta):
    ct = np.cos(theta)
    st = np.sin(theta)
    ry = np.array([[ct, 0, st], [0, 1, 0], [-st, 0, ct]])
    return ry


def rotation_z(theta):
    ct = np.cos(theta)
    st = np.sin(theta)
    rz = np.array([[ct, -st, 0], [st, ct, 0], [0, 0, 1]])
    return rz



def d2td3(pos2d, ax, ay, o):
    pos3d = pos2d[0] * ax + pos2d[1] * ay + o
    return pos3d


def get_closest_point_to_line(p0, r, p):
    ap = p - p0
    res = p0 + np.dot(ap, r) * r
    return res
    

def line_fit(points):
    points = np.asarray(points)
    avg = np.mean(points, 0)
    substracted = points - avg
    u, s, vh = np.linalg.svd(substracted, full_matrices=True)
    direction = vh[0, :] / np.linalg.norm(vh[0, :])
    p1 = points[np.where(points[:, 2] == np.max(points[:, 2]))[0], :]
    p2 = points[np.where(points[:, 2] == np.min(points[:, 2]))[0], :]
    sp = get_closest_point_to_line(avg, direction, p1)
    ep = get_closest_point_to_line(avg, direction, p2)
    print(sp, ep)
    return sp, ep, avg, direction


def get_angles(direction):
    direction = direction / np.linalg.norm(direction)
    
    vertical_vec = np.array([0, 0, -1])
    horizon_vec = np.array([1, 0, 0])
    
    dir_proj = direction.copy()
    dir_proj[2] = 0
    dir_proj = dir_proj / np.linalg.norm(dir_proj)
    
    theta = math.acos(np.max([np.min([np.dot(direction, vertical_vec), 1]), -1]))
    phi = math.acos(np.max([np.min([np.dot(dir_proj, horizon_vec), 1]), -1]))
    
    theta = theta * 180 / np.pi
    if theta > 90:
        theta = 180 - theta
    phi = phi * 180 / np.pi

    return theta, phi


def pandas_to_str(label_name, label_ano, length, channels):
    df = pd.DataFrame({
        'Brain Regions': label_name,
        'Ano': label_ano,
        'Probe Length': length,
        'Probe Channels': channels
        })
    return df.to_string(col_space=30, justify="justify")


def get_probe_length(segmentation_data, sp, ep, direction, resolution, tip_length, channel_size, bregma):
    probe_length = np.sqrt(np.sum((sp - ep)**2)) * resolution - tip_length
    pix_probe_length = probe_length / resolution

    if tip_length != 0:
        if probe_length > 9600:
            probe_length = 9600
        total_chn_lines = int(np.round(probe_length / channel_size))
        chk_pnts = np.zeros((total_chn_lines, 3))
        step_length = pix_probe_length / total_chn_lines

        for i in range(total_chn_lines):
            chk_pnts[i] = sp + step_length * i * direction

        new_ep = chk_pnts[-1]
        # chk_vox = chk_vox + 0.5 * (chk_vox[1] - chk_vox[0])
        chk_vox = chk_pnts + bregma
        chk_vox = chk_vox.astype(int)

        chn_lines_labels = np.zeros(total_chn_lines)
        for i in range(total_chn_lines):
            chn_lines_labels[i] = segmentation_data[chk_vox[i, 0], chk_vox[i, 1], chk_vox[i, 2]]

        region_label = np.unique(chn_lines_labels).astype(int)
        region_length = np.zeros(len(region_label))
        region_channels = np.zeros(len(region_label))
        for i in range(len(region_label)):
            region_channels[i] = np.sum(chn_lines_labels == region_label[i]) * 2
            region_length[i] = np.sum(chn_lines_labels == region_label[i]) * channel_size
    else:
        chn_lines_labels = None
        region_label = None
        region_length = None
        region_channels = None
        new_ep = None
        
    return probe_length, chn_lines_labels, region_label, region_length, region_channels, new_ep


def get_label_name(label_info, unique_label, chn_lines_labels):
    label_names = []
    label_acronym = []
    label_color = []
    chn_line_color = np.zeros((len(chn_lines_labels), 3), 'i')
    for i in range(len(unique_label)):
        # print(unique_label[i])
        if unique_label[i] == 0:
            label_names.append(' ')
            label_acronym.append(' ')
            label_color.append((128, 128, 128))
            cind = np.where(chn_lines_labels == unique_label[i])[0]
            chn_line_color[cind, 0] = 128
            chn_line_color[cind, 1] = 128
            chn_line_color[cind, 2] = 128
        else:
            da_ind = np.where(label_info['index'] == unique_label[i])[0][0]
            label_names.append(label_info['label'][da_ind])
            label_acronym.append(label_info['abbrev'][da_ind])
            label_color.append(label_info['color'][da_ind])
            cind = np.where(chn_lines_labels == unique_label[i])[0]
            chn_line_color[cind, 0] = label_info['color'][da_ind][0]
            chn_line_color[cind, 1] = label_info['color'][da_ind][1]
            chn_line_color[cind, 2] = label_info['color'][da_ind][2]

    return label_names, label_acronym, label_color, chn_line_color


def block_same_label(chn_lines_labels, chn_line_color):
    merged_labels = [chn_lines_labels[0]]
    merged_colors = [chn_line_color[0]]
    in_block_count = 1
    block_count = []
    for i in range(1, len(chn_lines_labels)):
        if chn_lines_labels[i] == chn_lines_labels[i - 1]:
            in_block_count += 1
        else:
            block_count.append(in_block_count)
            in_block_count = 1
            merged_labels.append(chn_lines_labels[i])
            merged_colors.append(chn_line_color[i])
        if i == len(chn_lines_labels) - 1:
            block_count.append(in_block_count)
    return merged_labels, merged_colors, block_count


def correct_start_pnt(label_data, start_pnt, direction):
    temp = start_pnt - direction
    if temp[2] < start_pnt[2]:
        direction = - direction

    for i in range(1000):
        temp = start_pnt - i * direction
        check_vox = temp.astype(int)
        if label_data[check_vox[0], check_vox[1], check_vox[2]] == 0:
            break
    new_sp = start_pnt - (i - 1) * direction
    return new_sp, direction


def calculate_probe_info(data, label_data, label_info, vxsize_um, tip_length, channel_size, bregma):
    start_pnt, end_pnt, avg, direction = line_fit(data)
    start_vox = start_pnt + bregma
    end_vox = end_pnt + bregma
    theta, phi = get_angles(direction)
    # print(theta, phi)
    new_start_vox, direction = correct_start_pnt(label_data, start_vox, direction)
    new_sp = new_start_vox - bregma
    probe_length, chn_lines_labels, region_label, region_length, region_channels, new_ep = \
        get_probe_length(label_data, new_sp, end_pnt, direction, vxsize_um, tip_length, channel_size, bregma)
    # print(chn_lines_labels, region_label, region_length, region_channels, new_ep)
    enter_coords = new_sp * vxsize_um
    label_names, label_acronym, label_color, chn_line_color = get_label_name(label_info, region_label, chn_lines_labels)
    # print(label_names, label_acronym, label_color, chn_line_color)

    merged_labels, merged_colors, block_count = block_same_label(chn_lines_labels, chn_line_color)
    # print(merged_labels, merged_colors, block_count)

    da_dict = {'object_name': 'probe', 'data': data, 'sp': start_pnt, 'ep': end_pnt, 'direction': direction,
               'probe_length': probe_length, 'new_sp': new_sp, 'new_ep': new_ep, 'theta': theta, 'phi': phi,
               'coords': enter_coords, 'enter_vox': new_start_vox,
               'chn_lines_labels': merged_labels, 'chn_lines_color': merged_colors, 'block_count': block_count,
               'region_label': region_label, 'region_length': region_length, 'region_channels': region_channels,
               'label_name': label_names, 'label_acronym': label_acronym, 'label_color': label_color}
    return da_dict


def get_region_label(data, label_data, bregma):
    region_label = []
    for i in range(len(data)):
        temp = data[i] + bregma
        temp = temp.astype(int)
        region_label.append(label_data[temp[0], temp[1], temp[2]])
    return region_label


def get_region_label_info(region_label, label_info):
    unique_label = np.unique(region_label)
    label_names = []
    label_acronym = []
    label_color = []
    region_count = []
    for i in range(len(unique_label)):
        # print(unique_label[i])
        if unique_label[i] == 0:
            label_names.append(' ')
            label_acronym.append(' ')
            label_color.append((128, 128, 128))
        else:
            da_ind = np.where(label_info['index'] == unique_label[i])[0][0]
            label_names.append(label_info['label'][da_ind])
            label_acronym.append(label_info['abbrev'][da_ind])
            label_color.append(label_info['color'][da_ind])

        region_count.append(len(np.where(np.ravel(region_label) == unique_label[i])[0]))

    return region_count, label_names, label_acronym, label_color


def calculate_virus_info(data, label_data, label_info, bregma):
    region_label = get_region_label(data, label_data, bregma)
    region_count, label_names, label_acronym, label_color = get_region_label_info(region_label, label_info)

    res_dict = {'object_name': 'virus', 'data': data, 'label_name': label_names,
                'label_acronym': label_acronym, 'label_color': label_color}

    return res_dict


def calculate_cells_info(data, label_data, label_info, bregma):
    region_label = get_region_label(data, label_data, bregma)
    region_count, label_names, label_acronym, label_color = get_region_label_info(region_label, label_info)

    res_dict = {'object_name': 'cell', 'data': data, 'label_name': label_names,
                'label_acronym': label_acronym, 'label_color': label_color, 'region_count': region_count}
    return res_dict


def order_contour_pnt(pnt):
    order_ind = []
    x_min = np.min(pnt[:, 0])
    left_ind = np.where(pnt[:, 0] == x_min)[0]
    if len(left_ind) > 1:
        low_ind = np.where(pnt[left_ind, :] == np.min(pnt[left_ind, :]))[0]
        left_ind = left_ind[low_ind]
    left_pnt = pnt[left_ind, :]
    lower_inds = np.where(pnt[:, 1] <= left_pnt[1])[0]
    lower_pnts = pnt[:, lower_inds]






def calculate_contour_line(data):
    data = np.asarray(data)
    res = splprep([data[:, 0], data[:, 1], data[:, 2]], s=2)
    tck = res[0]
    x_knots, y_knots, z_knots = splev(tck[0], tck)
    u_fine = np.linspace(0, 1, len(data))
    x_fine, y_fine, z_fine = splev(u_fine, tck)
    pnts = np.stack([x_fine, y_fine, z_fine], axis=1)
    print(pnts)
    return pnts


def get_object_vis_color(color):
    vis_color_r = color.red()
    vis_color_g = color.green()
    vis_color_b = color.blue()
    vis_color = (vis_color_r / 255, vis_color_g / 255, vis_color_b / 255, 1)
    return vis_color


def create_plot_points_in_3d(data_dict):
    pnts = data_dict['data']
    print(pnts)
    vis_color = get_object_vis_color(data_dict['vis_color'])
    print(vis_color)
    vis_points = gl.GLScatterPlotItem(pos=pnts, color=vis_color, size=3)
    vis_points.setGLOptions('opaque')
    return vis_points

# def shift_left(xy, val):
#     return xy - np.array([-val, 0])[None, :]
#
# def shift_up(xy, val):
#     return xy - np.array([0, val])[None, :]

    
def check_plotting_2d(points):
    points = np.asarray(points)


def hex2rgb(hex):
    if '#' in hex:
        hex = hex.lstrip('#')
        rgb_color = [int(hex[i:i + 2], 16) for i in (0, 2, 4)]
    else:
        if len(hex) == 6:
            rgb_color = [int(hex[i:i + 2], 16) for i in (0, 2, 4)]
    return rgb_color[0], rgb_color[1], rgb_color[2]


# @jit()
def hsv2rgb(h, s, v):
    # h [0, 1], s, v [0, 1]
    h = h * 360
    c = v * s
    m = v - c
    x = c * (1 - np.abs(np.mod(h / 60, 2) - 1))
    if 0 <= h < 60:
        r, g, b = (c + m, x + m, m)
    elif 60 <= h < 120:
        r, g, b = (x + m, c + m, m)
    elif 120 <= h < 180:
        r, g, b = (m, c + m, x + m)
    elif 180 <= h < 240:
        r, g, b = (m, x + m, c + m)
    elif 240 <= h < 300:
        r, g, b = (x + m, m, c + m)
    elif 300 <= h < 360:
        r, g, b = (c + m, m, x + m)
    else:
        r, g, b = (m, m, m)
    r = r * 65535
    b = b * 65535
    g = g * 65535
    return r, g, b


def color_img(h, s, v):
    r, g, b = hsv2rgb(h, s, v)
    da_image = cv2.merge((r, g, b))
    return da_image


def merge_channels_into_single_img(czi_img, channel_colors):
    merged_img = np.zeros((czi_img.shape[0], czi_img.shape[1], 3))
    frac = 1 / len(channel_colors)
    print(frac)
    for i in range(len(channel_colors)):
        temp_v = czi_img[:, :, i] / 65535
        temp_h = channel_colors[i][0]
        temp_s = channel_colors[i][1]
        print(temp_h, temp_s)
        da_img = color_img(temp_h, temp_s, temp_v)
        merged_img = merged_img + frac * da_img
    return merged_img


def make_color_lut(channel_color: tuple):
    r, g, b = colorsys.hsv_to_rgb(channel_color[0], channel_color[1], channel_color[2])
    # colors = [(0, 0, 0), (r, g, b)]
    colors = [(0, 0, 0), (r * 255, g * 255, b * 255)]
    color_map = pg.ColorMap(pos=[0, 1], color=colors)
    da_lut = color_map.getLookupTable(nPts=65536, mode=pg.ColorMap.FLOAT)
    da_lut = da_lut * 255
    return da_lut


def get_qhsv_from_czi_hsv(hsv_color: tuple):
    """
    Get QColor HSV color format (360, 255, 255) from czi HSV color format (1, 1, 1).
    :param hsv_color: (float [0., 1.], float [0., 1.], float [0., 1.])
    :return: QColor
    """
    h_val = int(hsv_color[0] * 360)
    s_val = int(hsv_color[1] * 255)
    v_val = int(hsv_color[2] * 255)
    da_color = (h_val, s_val, v_val)
    return da_color


def gamma_line(input, lims, gamma, dtype='uint16'):
    if dtype == 'uint16':
        const = 65535
    else:
        const = 255
    inv_gamma = 1.0 / gamma
    y = np.zeros(len(input))
    y[np.logical_and(input >= lims[0], input <= lims[1])] = np.power((input[np.logical_and(input >= lims[0], input <= lims[1])] - lims[0]) / (lims[1] - lims[0]), gamma) * const
    y[input <= lims[0]] = 0
    y[input >= lims[1]] = const
    y.astype(dtype)
    return y


def crop_landscape(image, dim):
    r = (dim[0] / image.shape[0]) / (dim[0] / dim[1])
    nw = int(image.shape[1] * r)

    resized = cv2.resize(image, (nw, int(dim[1])), interpolation=cv2.INTER_AREA)

    half_width = int(dim[0]) / 2
    half_shape_width = int(resized.shape[1]) / 2

    start_x = half_shape_width - half_width
    end_x = half_width + half_shape_width
    cropped = resized[0:dim[1], start_x:end_x]

    return cropped


def crop_portrait(image, dim):
    r = dim[1] / image.shape[1] / (dim[1] / dim[0])
    nh = int(image.shape[0] * r)

    resized = cv2.resize(image, (int(dim[0]), nh), interpolation=cv2.INTER_AREA)
    half_height = int(dim[1]) / 2
    half_shape_height = int(resized.shape[0]) / 2

    start_y = half_shape_height - half_height
    end_y = half_height + half_shape_height
    cropped = resized[start_y:end_y, 0:dim[0]]

    return cropped


def create_other_size(image, file_name, dim, location):
    # 1 => width index, 0 => height index
    if image.shape[0] > image.shape[1]:
      cropped = crop_portrait(image, dim)
    else:
      cropped = crop_landscape(image, dim)

    cv2.imwrite(os.path.join(location, file_name), cropped)


def make_hist_data(image_data, max_val):
    hist_data_list = []
    for i in range(image_data.shape[2]):
        hist_y, x = np.histogram(image_data[:, :, i], bins=np.max(image_data[:, :, i]))
        y = np.log1p(hist_y)
        y = y / np.max(y) * max_val
        y = np.append(y, 0)
        sfunc = interp1d(x, y, 'cubic')
        inter_x = np.linspace(np.min(x), np.max(x), 200)
        inter_y = sfunc(inter_x)
        inter_y[inter_y < 0] = 0
        hist_data_list.append([inter_x, inter_y])
    return hist_data_list


def rect_contains(rect, point):
    if point[0] < rect[0]:
        return False
    elif point[1] < rect[1]:
        return False
    elif point[0] > rect[2] + rect[0]:
        return False
    elif point[1] > rect[3] + rect[1]:
        return False
    return True


def get_warp_matrix(src_tri_pnts, dst_tri_pnts):
    # Given a pair of triangles, find the affine transform.
    warp_mat = cv2.getAffineTransform(np.float32(src_tri_pnts), np.float32(dst_tri_pnts))
    return warp_mat


def apply_affine_transform(src_img, warp_mat, size_dst):
    # Apply the Affine Transform just found to the src image
    dst = cv2.warpAffine(src_img.astype(np.float32), warp_mat, (size_dst[0], size_dst[1]), None,
                         flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
    return dst


def warp_triangle(img1, img2, t1, t2, is_rgb=False):

    # Find bounding rectangle for each triangle
    r1 = cv2.boundingRect(t1.astype(np.float32))
    r2 = cv2.boundingRect(t2.astype(np.float32))

    # Offset points by left top corner of the respective rectangles
    t1_rect = t1 - r1[:2]
    t2_rect = t2 - r2[:2]
    t2_rect_int = t2_rect.astype(int)

    # Get mask by filling triangle
    if is_rgb:
        mask = np.zeros((r2[3], r2[2], 3), dtype=np.float32)
        cv2.fillConvexPoly(mask, np.int32(t2_rect_int), (1.0, 1.0, 1.0), 16, 0)
    else:
        mask = np.zeros((r2[3], r2[2]), dtype=np.float32)
        cv2.fillConvexPoly(mask, np.int32(t2_rect_int), 1, 16, 0)

    # Apply warpImage to small rectangular patches
    img1_rect = img1[r1[1]:r1[1] + r1[3], r1[0]:r1[0] + r1[2]]
    # img2Rect = np.zeros((r2[3], r2[2]), dtype = img1Rect.dtype)

    size = (r2[2], r2[3])

    warp_mat = get_warp_matrix(t1_rect, t2_rect)

    img2_rect = apply_affine_transform(img1_rect, warp_mat, size)
    img2_rect = img2_rect * mask

    # Copy triangular region of the rectangular patch to the output image
    yr = (r2[0], r2[0] + r2[2])
    xr = (r2[1], r2[1] + r2[3])
    if is_rgb:
        img2[xr[0]:xr[1], yr[0]:yr[1]] = img2[xr[0]:xr[1], yr[0]:yr[1]] * ((1.0, 1.0, 1.0) - mask)
    else:
        img2[xr[0]:xr[1], yr[0]:yr[1]] = img2[xr[0]:xr[1], yr[0]:yr[1]] * (1 - mask)
    img2[xr[0]:xr[1], yr[0]:yr[1]] = img2[xr[0]:xr[1], yr[0]:yr[1]] + img2_rect


def warp_points(pnts, t1, t2):
    # Find bounding rectangle for each triangle
    # r1 = cv2.boundingRect(t1.astype(np.float32))
    # r2 = cv2.boundingRect(t2.astype(np.float32))
    # print(r1)
    # print(r2)

    # pnts =

    da_pnts = np.hstack([pnts, np.ones((len(pnts), 1))])
    # Offset points by left top corner of the respective rectangles
    # t1_rect = t1 - r1[:2]
    # t2_rect = t2 - r2[:2]

    warp_mat = get_warp_matrix(t1, t2)
    output = np.dot(warp_mat, da_pnts.T).T

    return output



# calculate delanauy triangle
def calculateDelaunayTriangles(rect, points):
    # create subdiv
    subdiv = cv2.Subdiv2D(rect)

    # Insert points into subdiv
    for p in points:
        subdiv.insert(p)

    triangleList = subdiv.getTriangleList()

    delaunayTri = []

    pt = []

    for t in triangleList:
        pt.append((t[0], t[1]))
        pt.append((t[2], t[3]))
        pt.append((t[4], t[5]))

        pt1 = (t[0], t[1])
        pt2 = (t[2], t[3])
        pt3 = (t[4], t[5])

        if rect_contains(rect, pt1) and rect_contains(rect, pt2) and rect_contains(rect, pt3):
            ind = []
            for j in range(0, 3):
                for k in range(0, len(points)):
                    if (abs(pt[j][0] - points[k][0]) < 1.0 and abs(pt[j][1] - points[k][1]) < 1.0):
                        ind.append(k)
            if len(ind) == 3:
                delaunayTri.append((ind[0], ind[1], ind[2]))

        pt = []

    return delaunayTri


def get_vertex_ind_in_triangle(subdiv):
    triangles = subdiv.getTriangleList()
    n_triangles = len(triangles)
    tri_vet_inds = []
    for i in range(n_triangles):
        da_triangle = triangles[i]
        p1 = [da_triangle[0], da_triangle[1]]
        p2 = [da_triangle[2], da_triangle[3]]
        p3 = [da_triangle[4], da_triangle[5]]
        tri_vet_inds.append([subdiv.locate(p1)[2], subdiv.locate(p2)[2], subdiv.locate(p3)[2]])
    tri_vet_inds = np.asarray(tri_vet_inds) - 4
    return tri_vet_inds


def get_pnts_triangle_ind(tri_vet_inds, tri_data, size, pnts):
    # import cv2
    # import numpy as np
    # img_rec = (0, 0, 100, 200)
    # da_triangle = np.array([[0, 0], [0, 50], [100, 100]])
    # size = (200, 100)
    # pnts = np.array([[0, 1], [0, 2], [60, 200]])


    update_pnts = pnts.copy()
    n_pnts = len(pnts)
    loc = np.zeros(n_pnts)
    loc[:] = np.nan
    da_order = []

    ct_list = []
    for i in range(len(tri_vet_inds)):
        da_inds = tri_vet_inds[i]
        da_triangle = np.array([tri_data[da_inds[0]], tri_data[da_inds[1]], tri_data[da_inds[2]]])
        mask = np.zeros(size, dtype=np.uint8)
        cv2.fillPoly(mask, pts=[da_triangle], color=255)
        ct, hc = cv2.findContours(image=mask, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
        ct_list.append(ct[0])

        # range_y = (np.min(da_triangle[:, 1]), np.max(da_triangle[:, 1]))
        # range_x = (np.min(da_triangle[:, 0]), np.max(da_triangle[:, 0]))
        #
        # valid_pnts_ind = [ind for ind in range(n_pnts) if range_x[0] <= pnts[ind][0] <= range_x[1] and range_y[0] <= pnts[ind][1] <= range_y[1]]
        # valid_pnts_ind = [ind for ind in valid_pnts_ind if ind not in da_order]
        # valid_pnts = pnts[valid_pnts_ind]
        # for j in range(len(valid_pnts)):
        #     res = cv2.pointPolygonTest(ct_list[i], (int(pnts[j][0]), int(pnts[j][1])), True)
        #     if res >= 0:
        #         loc.append(i)
        #         da_order.append(valid_pnts_ind[j])

    #     temp = np.zeros(len(update_pnts))
    #
    #
    # for i in range(len(tri_vet_inds)):
    #     da_
    #
    for i in range(len(pnts)):
        for j in range(len(ct_list)):
            da_ct = ct_list[j]
            res = cv2.pointPolygonTest(da_ct, (int(pnts[i][0]), int(pnts[i][1])), False)
            if res >= 0:
                loc[i] = j
                break


    return loc




def get_sides_points(img_size):
    size0 = img_size[1] - 1
    size1 = img_size[0] - 1
    side_lines = np.asarray([[[0, 0], [size0, 0]], [[size0, 0], [size0, size1]],
                             [[0, size1], [size0, size1]], [[0, 0], [0, size1]]])
    corner_points = [[0, 0], [size0, 0], [size0, size1], [0, size1]]
    return side_lines, corner_points


def num_side_pnt_changed(num_pnt, corner_points, side_lines):
    n_pnts_to_make = num_pnt - 2
    onside_data = corner_points.copy()
    if n_pnts_to_make > 0:
        for i in range(4):
            da_line = side_lines[i]
            for j in range(n_pnts_to_make):
                inline_point = da_line[0] + (da_line[1] - da_line[0]) / (n_pnts_to_make + 1) * (j + 1)
                onside_data.append([inline_point[0], inline_point[1]])
    return onside_data


def match_sides_points(rect_atlas, size_atlas, rect_image, size_image):
    print(rect_atlas)
    print(size_atlas)
    print(rect_image)
    print(size_image)
    x_factor = rect_atlas[2] / rect_image[2]
    y_factor = rect_atlas[3] / rect_image[3]

    actual_left_dist_image = size_image[1] - (rect_image[0] + rect_image[2])
    actual_bottom_dist_image = size_image[0] - (rect_image[1] + rect_image[3])

    actual_left_dist_atlas = size_atlas[1] - (rect_atlas[0] + rect_atlas[2])
    actual_bottom_dist_atlas = size_atlas[0] - (rect_atlas[1] + rect_atlas[3])

    left_dist_atlas = rect_image[0] * x_factor
    right_dist_atlas = actual_left_dist_image * x_factor

    top_dist_atlas = rect_image[1] * y_factor
    bottom_dist_atlas = actual_bottom_dist_image * y_factor

    if left_dist_atlas <= rect_atlas[0]:
        atlas_corner_x = int(rect_atlas[0] - left_dist_atlas)
        image_corner_x = 0
    else:
        atlas_corner_x = 0
        left_dist_image = rect_atlas[0] / x_factor
        image_corner_x = int(rect_image[0] - left_dist_image)

    if right_dist_atlas <= actual_left_dist_atlas:
        atlas_width = int(size_atlas[1] - atlas_corner_x - (actual_left_dist_atlas - right_dist_atlas))
        image_width = size_image[1]
    else:
        atlas_width = size_atlas[1] - atlas_corner_x
        right_dist_image = actual_left_dist_atlas / x_factor
        image_width = int(size_image[1] - image_corner_x - (actual_left_dist_image - right_dist_image))

    if top_dist_atlas <= rect_atlas[1]:
        atlas_corner_y = int(rect_atlas[1] - top_dist_atlas)
        image_corner_y = 0
    else:
        atlas_corner_y = 0
        top_dist_image = rect_atlas[1] / y_factor
        image_corner_y = int(rect_image[1] - top_dist_image)

    if bottom_dist_atlas <= actual_bottom_dist_atlas:
        atlas_height = int(size_atlas[0] - atlas_corner_y - (actual_bottom_dist_atlas - bottom_dist_atlas))
        image_height = size_image[0]
    else:
        atlas_height = size_atlas[0] - atlas_corner_y
        bottom_dist_image = actual_bottom_dist_atlas / y_factor
        image_height = int(size_image[0] - image_corner_y - (actual_bottom_dist_image - bottom_dist_image))

    atlas_rect = (atlas_corner_x, atlas_corner_y, atlas_width, atlas_height)
    image_rect = (image_corner_x, image_corner_y, image_width, image_height)

    atlas_corners, atlas_lines = get_corner_line_from_rect(atlas_rect)
    image_corners, image_lines = get_corner_line_from_rect(image_rect)

    return atlas_corners, atlas_lines, image_corners, image_lines


def get_corner_line_from_rect(rect):
    corners = [[rect[0], rect[1]], [rect[0] + rect[2] - 1, rect[1]],
               [rect[0] + rect[2] - 1, rect[1] + rect[3] - 1], [rect[0], rect[1] + rect[3] - 1]]

    lines = np.asarray([[corners[0], corners[1]], [corners[1], corners[2]],
                        [corners[3], corners[2]], [corners[0], corners[3]]])

    return corners, lines


def make_label_rgb_img(label_img, lut):
    fimg = np.dstack([label_img, label_img, label_img])
    unique_label = np.unique(label_img).astype(int)
    for ind in np.unique(unique_label):
        if ind == 0:
            continue
        loc = np.where(label_img == ind)
        print(lut[ind])
        fimg[loc[0], loc[1], 0] = lut[ind][0]
        fimg[loc[0], loc[1], 1] = lut[ind][1]
        fimg[loc[0], loc[1], 2] = lut[ind][2]
    return fimg.astype('uint8')


def make_contour_img(lable_img):
    unique_label = np.unique(lable_img).astype('int')
    img_size = lable_img.shape
    contour_img = np.zeros(img_size, 'uint8')
    for label_ind in unique_label:
        if label_ind == 0:
            continue
        temp = np.zeros(img_size, 'uint8')
        temp[lable_img == label_ind] = 1
        ct, hc = cv2.findContours(image=temp, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
        for j in range(len(ct)):
            da_contour = ct[j].copy()
            da_shp = da_contour.shape
            da_contour = np.reshape(da_contour, (da_shp[0], da_shp[2]))
            contour_img[da_contour[:, 1], da_contour[:, 0]] = 1
    return contour_img


def get_tri_lines(rect, pnts):
    subdiv = cv2.Subdiv2D(rect)
    for p in pnts:
        subdiv.insert(p)
    edge_list = subdiv.getEdgeList()
    lines_list = []
    for el in edge_list:
        pt1 = [el[0], el[1]]
        pt2 = [el[2], el[3]]
        if rect_contains(rect, pt1) and rect_contains(rect, pt2):
            lines_list.append(el)
    return lines_list


# czi_img = image_file.data['scene 0'].copy()
# channel_hsv = image_file.hsv_colors
# temp_img = merge_channels_into_single_img(czi_img, channel_hsv)





def get_lower_val(val, tol, lim):
    lower_val = val - tol if tol < val else lim
    return lower_val


def get_upper_val(val, tol, lim):
    upper_val = val + tol
    upper_val = upper_val if upper_val <= lim else lim
    return upper_val


def get_bound_color(color, tol, level, mode):
    tol = float(tol)
    if mode == 'gray':
        lower_val = get_lower_val(color, tol, 0)
        upper_val = get_upper_val(color, tol, level)
    elif mode == 'hsv':
        lower_val = [get_lower_val(color[0], 1., 0)]
        upper_val = [get_upper_val(color[0], 1., 180)]
        for i in range(1, 3):
            lower_val.append(get_lower_val(color[i], tol, 0))
            upper_val.append(get_upper_val(color[i], tol, 255))
    else:
        lower_val = []
        upper_val = []
        for i in range(3):
            lower_val.append(get_lower_val(color[i], tol, 0))
            upper_val.append(get_upper_val(color[i], tol, 255))
    return lower_val, upper_val


# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
def render_volume(atlas_data, atlas_folder, factor=2, level=0.1):
    da_data = atlas_data.copy()
    img = np.ascontiguousarray(da_data[::factor, ::factor, ::factor])
    verts, faces = pg.isosurface(ndi.gaussian_filter(img.astype('float64'), (2, 2, 2)), np.max(da_data) * level)

    md = gl.MeshData(vertexes=verts * factor, faces=faces)

    outfile = open(os.path.join(atlas_folder, 'atlas_meshdata.pkl'), 'wb')
    pickle.dump(md, outfile)
    outfile.close()

    return


def render_small_volume(atlas_data, atlas_label, atlas_folder, factor=2, level=0.1):
    # small_verts_list = {}
    # small_faces_list = {}
    small_meshdata_list = {}

    all_unique_label = np.unique(atlas_label)

    for id in all_unique_label:
        id = int(id)
        print(id)
        if id == 0:
            continue
        temp_atlas = atlas_data.copy()
        temp_atlas[atlas_label != id] = 0
        pimg = np.ascontiguousarray(temp_atlas[::factor, ::factor, ::factor])
        verts, faces = pg.isosurface(ndi.gaussian_filter(pimg.astype('float64'), (2, 2, 2)), np.max(temp_atlas) * level)
        # small_verts_list[str(id)] = verts
        # small_faces_list[str(id)] = faces

        md = gl.MeshData(vertexes=verts * factor, faces=faces)

        small_meshdata_list[str(id)] = md

    outfile = open(os.path.join(atlas_folder, 'atlas_small_meshdata.pkl'), 'wb')
    pickle.dump(small_meshdata_list, outfile)
    outfile.close()
    return





