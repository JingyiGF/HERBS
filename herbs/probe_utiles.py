import os
import numpy as np
import math
import pandas as pd
import cv2
import pickle
import colorsys
import pyqtgraph as pg
from scipy.interpolate import interp1d, splprep, splev
from .uuuuuu import rotation_z, rotation_x, rotation_y


def get_closest_point_to_line(p0, r, p):
    ap = p - p0
    res = p0 + np.dot(ap, r) * r
    return res


def line_fit_2d(points_2d, image=None):
    msg = None
    points = np.asarray(points_2d)
    sort_order = np.argsort(points[:, 1])
    points = points[sort_order, :]
    avg = np.mean(points, 0)
    subtracted = points - avg
    u, s, vh = np.linalg.svd(subtracted)
    direction = vh[0, :] / np.linalg.norm(vh[0, :])
    p1 = points[0, :]
    p2 = points[-1, :]
    sp = get_closest_point_to_line(avg, direction, p1)
    ep = get_closest_point_to_line(avg, direction, p2)

    if image is not None:
        direction = sp - ep
        direction = direction / np.linalg.norm(direction)

        valid_ind = np.where(image[:, int(sp[0])] != 0)[0]
        if len(valid_ind) > 0:
            valid_ind = valid_ind[0]
        else:
            msg = 'something went wrong for the probe location.'

        if int(sp[1]) < valid_ind:
            sign_flag = -1
        elif int(sp[1]) > valid_ind:
            sign_flag = 1
        else:
            sign_flag = 0

        stop_steps = 0
        temp = sp + 0
        while int(temp[1]) != valid_ind:
            stop_steps += 1
            temp = sp + sign_flag * stop_steps * direction
            valid_ind = np.where(image[:, int(temp[0])] != 0)[0]
            if len(valid_ind) > 0:
                valid_ind = valid_ind[0]
            else:
                msg = 'something went wrong for the probe location.'
                break

        sp = sp + sign_flag * stop_steps * direction

    p2 = np.array([sp, ep])
    return p2, msg


def line_fit(points):
    points = np.asarray(points)
    sort_order = np.argsort(points[:, 2])[::-1]
    points = points[sort_order, :]
    avg = np.mean(points, 0)
    substracted = points - avg
    u, s, vh = np.linalg.svd(substracted)
    direction = vh[0, :] / np.linalg.norm(vh[0, :])
    p1 = points[0, :]
    p2 = points[-1, :]
    sp = get_closest_point_to_line(avg, direction, p1)
    ep = get_closest_point_to_line(avg, direction, p2)
    return sp, ep, avg, direction


def get_angles(direction):
    direction = direction / np.linalg.norm(direction)

    vertical_vec = np.array([0, 0, 1])
    ap_proj = direction.copy()
    ap_proj[0] = 0
    ap_proj = ap_proj / np.linalg.norm(ap_proj)
    ml_proj = direction.copy()
    ml_proj[1] = 0
    ml_proj = ml_proj / np.linalg.norm(ml_proj)

    ap_val = math.acos(np.max([np.min([np.dot(ap_proj, vertical_vec), 1]), -1]))
    ml_val = math.acos(np.max([np.min([np.dot(ml_proj, vertical_vec), 1]), -1]))

    ap_angle = np.degrees(ap_val)
    ml_angle = np.degrees(ml_val)

    if ap_angle > 90:
        ap_angle = 180 - ap_angle
    if ml_angle > 90:
        ml_angle = 180 - ml_angle

    return ap_angle, ml_angle


def get_tilt_info(sp, ep):
    if ep[1] < sp[1]:
        ap_tilt = 'posterior'
    elif ep[1] > sp[1]:
        ap_tilt = 'anterior'
    else:
        ap_tilt = 'no tilt'

    if sp[0] > 0:
        if ep[0] < sp[0]:
            ml_tilt = 'medial'
        elif ep[0] > sp[0]:
            ml_tilt = 'lateral'
        else:
            ml_tilt = 'no tilt'
    elif sp[0] < 0:
        if ep[0] < sp[0]:
            ml_tilt = 'lateral'
        elif ep[0] > sp[0]:
            ml_tilt = 'medial'
        else:
            ml_tilt = 'no tilt'
    else:
        if ep[0] != sp[0]:
            ml_tilt = 'lateral'
        else:
            ml_tilt = 'no tilt'
    return ap_tilt, ml_tilt


def get_tilt_sign(sp, ep):
    if ep[1] < sp[1]:
        ap_tilt = -1
    elif ep[1] > sp[1]:
        ap_tilt = 1
    else:
        ap_tilt = 0

    if ep[0] < sp[0]:
        ml_tilt = -1
    elif ep[0] > sp[0]:
        ml_tilt = 1
    else:
        ml_tilt = 0
    return ap_tilt, ml_tilt


def pandas_to_str(label_name, label_ano, length, channels):
    df = pd.DataFrame({
        'Brain Regions': label_name,
        'Ano': label_ano,
        'Probe Length': length,
        'Probe Channels': channels
    })
    return df.to_string(col_space=30, justify="justify")


def correct_start_pnt(label_data, start_pnt, start_vox, direction, bregma):
    error_index = 0
    direction = direction / np.linalg.norm(direction)
    check_vec = label_data[int(start_vox[0]), int(start_vox[1]), :]
    top_vox = np.where(check_vec != 0)[0][-1]
    check_vox = start_vox.astype(int)
    new_sp = start_pnt.copy()

    # if int(start_vox[2]) < top_vox:
    #     steps = 0
    #     while label_data[check_vox[0], check_vox[1], check_vox[2]] != 0:
    #         steps += 1
    #         new_sp = start_pnt - steps * direction
    #         check_vox = new_sp + bregma
    #         check_vox = check_vox.astype(int)
    #         if steps == 1000:
    #             raise Exception('higher limit, please contact maintainer')
    # elif int(start_vox[2]) > top_vox:
    #     steps = 0
    #     while label_data[check_vox[0], check_vox[1], check_vox[2]] == 0:
    #         steps += 1
    #         new_sp = start_pnt + steps * direction
    #         check_vox = new_sp + bregma
    #         check_vox = check_vox.astype(int)
    #         if steps == 1000:
    #             raise Exception('higher limit, please contact maintainer')
    # else:
    #     new_sp = start_pnt
    enter_label = label_data[check_vox[0], check_vox[1], check_vox[2]]
    z_diff = new_sp[2] + bregma[2] - top_vox
    if z_diff >= 1:
        sign_flag = -1
        if enter_label != 0:
            error_index = 10
            return new_sp, error_index
    elif z_diff < 0:
        sign_flag = 1
        if enter_label == 0:
            error_index = 11
            return new_sp, error_index
    else:
        sign_flag = 0

    # ToDo: the following code only works when there is no 0 label inside the brain (label data)
    # that means label 0 only indicates the area outside the brain
    # if some atlas uses label 0 to indicate the unspecified area inside the brain, this code may have problems
    # should make a pseudo label index (xxxx) inside the brain for unspecified regions ===> need to re-process atlas

    stop_steps = 0
    if sign_flag != 0:
        enter_condition = (enter_label == 0) if z_diff >= 1 else (enter_label != 0)
        while enter_condition:
            stop_steps += 1
            new_sp = start_pnt - sign_flag * stop_steps * direction
            check_vox = new_sp + bregma
            check_vox = check_vox.astype(int)
            if np.any(check_vox >= np.ravel(label_data.shape)) or np.any(check_vox) < 0:
                error_index = 12
                break
            enter_label = label_data[check_vox[0], check_vox[1], check_vox[2]]
            enter_condition = (enter_label == 0) if z_diff >= 1 else (enter_label != 0)
        if error_index != 0:
            return new_sp, error_index

        new_sp = start_pnt - sign_flag * (stop_steps - 1) * direction if z_diff < 0 else new_sp
        print('correct enter pnt with {} steps'.format(stop_steps))

    return new_sp, error_index


def correct_end_point(sp, ep, direction, vox_size, tip_length, max_probe_length):
    probe_length_with_tip = np.sqrt(np.sum((sp - ep) ** 2)) * vox_size  # in um
    probe_length_without_tip = probe_length_with_tip - tip_length  # in um
    if max_probe_length is not None:
        if probe_length_with_tip > max_probe_length:
            probe_length_with_tip = max_probe_length
            probe_length_without_tip = probe_length_with_tip - tip_length
            new_ep = sp + direction * probe_length_with_tip / vox_size
        else:
            new_ep = ep
    else:
        new_ep = ep
    return new_ep, probe_length_with_tip, probe_length_without_tip


def check_parallel_to_z(direction):
    is_parallel = False
    if abs(direction[2] + 1) < 1e-6:
        is_parallel = True
    return is_parallel


def angle_between_2vectors(vector1, vector2):
    unit_vector_1 = vector1 / np.linalg.norm(vector1)
    unit_vector_2 = vector2 / np.linalg.norm(vector2)
    dot_product = np.dot(unit_vector_1, unit_vector_2)
    angle = np.arccos(dot_product)
    return angle


def get_probe_info(probe_type):
    if probe_type == 0:
        tip_length = 175
        channel_size = 20
        channel_number_in_banks = (384, 384, 192)
    elif probe_type == 1:
        tip_length = 175
        channel_size = 15
        channel_number_in_banks = (384, 384, 192)
    else:
        tip_length = 0
        channel_size = None
        channel_number_in_banks = None
    return tip_length, channel_size, channel_number_in_banks


def get_direction_rotation(direction):
    # rotation matrix
    if check_parallel_to_z(direction):
        rot_m = np.dot(rotation_z(np.radians(90)), rotation_y(np.radians(90)))
    else:
        x_vec = np.array([1, 0, 0])
        vec2 = direction.copy()
        vec2[2] = 0
        ang_alpha = angle_between_2vectors(vec2, x_vec)
        ang_beta = angle_between_2vectors(direction, vec2)
        print(ang_alpha)
        print(ang_beta)
        rot_m = np.dot(rotation_z(ang_alpha), rotation_y(ang_beta))
    return rot_m


def get_base_start(site_face, x_bias, base_thickness):
    zero_vec = np.zeros(len(x_bias))

    if site_face == 0:
        base_loc = x_bias.copy()
        base_start = np.vstack([zero_vec, base_loc, zero_vec]).T
        base_start[:, 2] = base_start[:, 2] + base_thickness
    elif site_face == 1:
        base_loc = x_bias[::-1]
        base_start = np.vstack([zero_vec, base_loc, zero_vec]).T
        base_start[:, 2] = base_start[:, 2] - base_thickness
    elif site_face == 2:
        base_loc = x_bias[::-1]
        base_start = np.vstack([zero_vec, zero_vec, base_loc]).T
        base_start[:, 1] = base_start[:, 1] + base_thickness
    else:
        base_loc = x_bias.copy()
        base_start = np.vstack([zero_vec, zero_vec, base_loc]).T
        base_start[:, 1] = base_start[:, 1] - base_thickness

    return base_start


def correct_base_sp(base_start, sp, rot_mat, direction, bregma, label_data):
    n_base = len(base_start)
    ct_sp = sp + np.dot(rot_mat, base_start.T).T
    ct_start_vox = ct_sp + bregma
    start_vox = ct_start_vox.astype(int)
    ct_sp_new = np.zeros((n_base, 3))
    error_index_vec = np.zeros(n_base)
    for i in range(n_base):
        ct_sp_new[i], error_index_vec[i] = correct_start_pnt(label_data, ct_sp[i], start_vox[i], direction, bregma)

    if not np.all(error_index_vec == 0):
        base_start_new = None
        error_index = 1
    else:
        rotate_base_start = ct_sp_new - sp
        base_start_new = np.dot(rot_mat.T, rotate_base_start.T).T
        error_index = 0

    return base_start_new, ct_sp_new, error_index


def get_length_without_bias(probe_length_without_tip, y_bias, vxsize_um):
    y_bias = np.ravel(y_bias)
    n_column = len(y_bias)
    sp_to_bottom_site_center = (np.repeat(probe_length_without_tip, n_column) - y_bias) / vxsize_um
    return sp_to_bottom_site_center


def get_base_end(base_start, probe_length_without_tip_um, vox_size):
    base_end = base_start.copy()
    base_end[:, 0] = probe_length_without_tip_um / vox_size
    return base_end


def get_sites_center_base(new_base_start, base_end, y_bias, sites_distance, per_max_sites):
    n_column = len(y_bias)
    sites_center_base = []

    for i in range(n_column):
        valid_val = base_end[i, 0] - y_bias[i]
        center_base = np.arange(valid_val, new_base_start[i, 0], -sites_distance[i])
        if len(center_base) > per_max_sites[i]:
            sites_center_base.append(center_base[:per_max_sites[i]])
        else:
            sites_center_base.append(center_base)

    return sites_center_base


def get_plot_sites_loc(sites_center_base, base_end):
    n_column = len(sites_center_base)
    plot_sites_loc = []

    for i in range(n_column):
        temp = base_end[i, 0] - sites_center_base[i]
        plot_sites_loc.append(temp)
    return plot_sites_loc


def get_base_columns(base_start, sites_center_base):
    n_column = len(base_start)
    base_columns = []
    for i in range(n_column):
        base_column = np.repeat(np.array([base_start[i]]), len(sites_center_base[i]), axis=0)
        base_column[:, 0] = sites_center_base[i] + 0.
        base_columns.append(base_column)
    return base_columns


def get_sites(sp, base_columns, rot_mat, bregma, label_data):
    n_column = len(base_columns)
    # sites location
    sites_loc = []
    sites_vox = []
    sites_label = []
    for i in range(n_column):
        sites_loc_temp = sp + np.dot(rot_mat, base_columns[i].T).T
        sites_loc.append(sites_loc_temp)

        site_vox = sites_loc_temp + bregma
        site_vox = site_vox.astype(int)
        sites_vox.append(site_vox)

        sites_label_column = label_data[site_vox[:, 0], site_vox[:, 1], site_vox[:, 2]]
        sites_label.append(sites_label_column)

    return sites_loc, sites_vox, sites_label


def get_shank_columns(base_start, base_end, step_length):
    n_column = len(base_start)
    shank_columns = []
    for i in range(n_column):
        shank_center_base = np.arange(base_end[i, 0], base_start[i, 0], -step_length)
        shank_column = np.repeat(np.array([base_start[i]]), len(shank_center_base), axis=0)
        shank_column[:, 0] = shank_center_base + 0.
        shank_columns.append(shank_column)
    return shank_columns

def get_traveling_label_mat(sp, shank_columns, rot_mat, bregma, label_data):
    n_column = len(shank_columns)
    n_rows = []
    c_loc = []
    c_vox = []
    c_label = []
    for i in range(n_column):
        c_loc_temp = sp + np.dot(rot_mat, shank_columns[i].T).T
        c_loc.append(c_loc_temp)

        n_rows.append(len(c_loc_temp))
        temp_vox = c_loc_temp + bregma
        temp_vox = temp_vox.astype(int)
        c_vox.append(temp_vox)

        c_label_column = label_data[temp_vox[:, 0], temp_vox[:, 1], temp_vox[:, 2]]
        c_label.append(c_label_column)

    n_row = np.max(n_rows)
    fine_label_mat = np.zeros((n_row, n_column))
    for i in range(n_column):
        fine_label_mat[:n_rows[i], i] = c_label[i]

    return fine_label_mat


# def get_traveling_label_mat(ct_sp, ct_ep, direction, bregma, label_data, step_length):
#     column_fine_label = []
#     n_rows = []
#     n_column = len(ct_sp)
#     for i in range(n_column):
#         column_length = np.sqrt(np.sum((ct_sp[i] - ct_ep[i]) ** 2))
#         step_dist = np.arange(0, column_length, step_length)
#         n_pnt = len(step_dist)
#         pnt_vec = np.zeros((n_pnt, 3))
#         for j in range(n_pnt):
#             pnt_vec[j] = ct_ep[i] - step_dist[j] * direction
#         pnt_vec = np.vstack([pnt_vec, ct_sp[i]])
#         n_rows.append(len(pnt_vec))
#         vox_vec = pnt_vec + bregma
#         vox_vec = vox_vec.astype(int)
#         column_label = label_data[vox_vec[:, 0], vox_vec[:, 1], vox_vec[:, 2]]
#         column_fine_label.append(column_label)
#
#     n_row = np.max(n_rows)
#     fine_label_mat = np.zeros((n_row, n_column))
#     for i in range(n_column):
#         fine_label_mat[:n_rows[i], i] = column_fine_label[i]
#
#     return fine_label_mat


def group_labels(fine_label_mat):
    n_row, n_column = fine_label_mat.shape
    group_mat = np.zeros(fine_label_mat.shape)
    group_id = 0
    group_id_label = []

    previous_row = np.zeros(n_column)
    previous_row[:] = np.nan
    for base_level in range(0, n_row):
        check_label = fine_label_mat[base_level]
        unique_label = np.unique(check_label)
        for da_label in unique_label:
            if da_label in previous_row:
                continue
            add_row = 0
            row_index = add_row + base_level
            label_check = (fine_label_mat[row_index] == da_label)
            group_mat[row_index, label_check] = group_id
            while np.any(label_check):
                add_row += 1
                row_index = add_row + base_level
                if row_index == n_row:
                    break
                label_check = (fine_label_mat[row_index] == da_label)
                group_mat[row_index, label_check] = group_id
            group_id_label.append(da_label)
            group_id += 1
        previous_row = fine_label_mat[base_level]

    return group_mat, group_id_label


def get_group_bounds(group_mat, step_length):
    n_groups = len(np.unique(group_mat))
    n_row, n_column = group_mat.shape

    gr_start = np.zeros((n_groups, n_column))
    gr_start[:] = np.nan
    gr_end = np.zeros((n_groups, n_column))
    gr_end[:] = np.nan

    region_length = []
    region_text_loc = []
    for i in range(n_groups):
        rl = 0
        for j in range(n_column):
            valid_ind = np.where(group_mat[:, j] == i)[0]
            stk = len(valid_ind)
            if stk == 0:
                continue
            gr_start[i, j] = valid_ind[0] * step_length
            gr_end[i, j] = (valid_ind[0] + stk) * step_length
            rl += stk
        region_length.append(rl * step_length / n_column)
        region_text_loc.append(np.nanmin(gr_start[i]) + 0.5 * (np.nanmax(gr_end[i]) - np.nanmin(gr_start[i])))

    return gr_start, gr_end, region_length, region_text_loc


def get_n_sites_in_region(gr_start, gr_end, plot_sites_column):
    n_groups, n_column = gr_start.shape

    region_site_num = []
    for i in range(n_groups):
        n_sites = 0
        for j in range(n_column):
            if np.isnan(gr_start[i, j]):
                continue
            valid_ind = np.logical_and(plot_sites_column[j] >= gr_start[i, j], plot_sites_column[j] < gr_end[i, j])
            n_sites += np.sum(valid_ind)
        region_site_num.append(n_sites)

    return region_site_num


# def get_traveling_info(sp, ep, probe_length, direction, bregma, label_data):
#     if probe_length is None:
#         probe_length = np.sqrt(np.sum((sp - ep) ** 2))
#     step_dist = np.arange(0, probe_length, 0.5)
#     n_pnt = len(step_dist)
#     pnt_vec = np.zeros((n_pnt, 3))
#     for i in range(n_pnt):
#         pnt_vec[i] = ep - step_dist[i] * direction
#     pnt_vec = np.vstack([pnt_vec, sp])
#
#     vox_vec = pnt_vec + bregma
#
#     label_vec = label_data[vox_vec[:, 0], vox_vec[:, 1], vox_vec[:, 2]]
#
#     dist_vec = []
#     region_vec = [label_vec[0]]
#     region_start_pnt_vec = [pnt_vec[0]]
#     for i in range(1, len(label_vec)):
#         if label_vec[i] != region_vec[-1]:
#             dists = np.sqrt(np.sum((pnt_vec[i] - region_start_pnt_vec[-1]) ** 2))
#             dist_vec.append(dists)
#             region_vec.append(label_vec[i])
#             region_start_pnt_vec.append(pnt_vec[i])
#
#     return region_vec, dist_vec


def get_label_name(label_info, region_label):
    label_names = []
    label_acronym = []
    label_color = []
    for i in range(len(region_label)):
        if region_label[i] == 0:
            label_names.append(' ')
            label_acronym.append(' ')
            label_color.append((128, 128, 128))
        else:
            da_ind = np.where(np.ravel(label_info['index']) == region_label[i])[0][0]
            label_names.append(label_info['label'][da_ind])
            label_acronym.append(label_info['abbrev'][da_ind])
            label_color.append(label_info['color'][da_ind])

    label_color = np.asarray(label_color)
    return label_names, label_acronym, label_color


# def get_sites_label(label_info, sites_label):
#     label_names = []
#     label_acronym = []
#     label_color = []
#     for i in range(len(region_label)):
#         if region_label[i] == 0:
#             label_names.append(' ')
#             label_acronym.append(' ')
#             label_color.append((128, 128, 128))
#         else:
#             da_ind = np.where(np.ravel(label_info['index']) == region_label[i])[0][0]
#             label_names.append(label_info['label'][da_ind])
#             label_acronym.append(label_info['abbrev'][da_ind])
#             label_color.append(label_info['color'][da_ind])
#
#     label_color = np.asarray(label_color)
#     return label_names, label_acronym, label_color


def calculate_probe_info(data_list, pieces_names, label_data, label_info, vxsize_um, probe_settings,
                         bregma, site_face, step_length=0.01):
    """

    :param data: 3d coordinates for all the points
    :param label_data: original brain region segmentation
    :param label_info:
    :param vxsize_um:
    :param tip_length:
    :param channel_size:
    :param bregma:
    :return:
    """

    data_dict = None
    data = data_list[0]
    for i in range(1, len(data_list)):
        data = np.vstack([data, data_list[i]])
    print('data', data)

    # start_pnt and end_pnt are coordinates related to the given Bregma
    probe_type = probe_settings['probe_type']
    probe_type_name = probe_settings['probe_type_name']
    probe_max_length_um = probe_settings['probe_length']
    tip_length_um = probe_settings['tip_length']
    site_height_um = probe_settings['site_height']
    probe_thickness_um = probe_settings['probe_thickness']
    per_max_sites = probe_settings['per_max_sites']
    sites_distance_um = probe_settings['sites_distance']
    x_bias_um = probe_settings['x_bias']
    y_bias_um = probe_settings['y_bias']

    n_column = len(x_bias_um)

    base_thickness = 0.5 * probe_thickness_um / vxsize_um
    sites_distance = np.ravel(sites_distance_um) / vxsize_um
    x_bias = np.ravel(x_bias_um) / vxsize_um
    y_bias = np.ravel(y_bias_um) / vxsize_um

    # get direction and probe center start and end (pc - probe center)
    pc_start_pnt, pc_end_pnt, avg, direction = line_fit(data)
    direction = pc_end_pnt - pc_start_pnt
    direction = direction / np.linalg.norm(direction)
    pc_start_vox = pc_start_pnt + bregma
    pc_end_vox = pc_end_pnt + bregma

    # get angels
    ap_angle, ml_angle = get_angles(direction)
    print('ap_angle', ap_angle)
    print(ml_angle)

    # correct probe center start point
    pc_sp, error_index = correct_start_pnt(label_data, pc_start_pnt, pc_start_vox, direction, bregma)
    if error_index != 0:
        return data_dict, 15

    pc_ep, probe_length_with_tip_um, probe_length_without_tip_um = correct_end_point(
        pc_sp, pc_end_pnt, direction, vxsize_um, tip_length_um, probe_max_length_um)

    pv_sp = pc_sp + bregma
    pv_sp = pv_sp.astype(int)
    pv_ep = pc_ep + bregma
    pv_ep = pv_ep.astype(int)

    enter_coords = pc_sp * vxsize_um
    end_coords = pc_ep * vxsize_um

    dv = (pc_sp[2] - pc_ep[2]) * vxsize_um
    ap_tilt, ml_tilt = get_tilt_info(pc_sp, pc_ep)


    # get rotation matrix
    rot_mat = get_direction_rotation(direction)
    # base start=pseudo enter, base end=pseudo terminus, assume the initial direction of probe is (1,0,0)
    base_start = get_base_start(site_face, x_bias, base_thickness)

    base_end = get_base_end(base_start, probe_length_without_tip_um, vxsize_um)

    # get column center bottom points, bottom is the base of tip
    ct_ep = pc_sp + np.dot(rot_mat, base_end.T).T
    print('pc_sp', pc_sp)
    print('pc_ep', pc_ep)
    print('ct_ep', ct_ep)

    # correct the base_start, minor correction
    base_start_new, ct_sp, error_index = correct_base_sp(base_start, pc_sp, rot_mat, direction, bregma, label_data)

    print('base_start', base_start_new)
    print('base_end', base_end)

    if error_index != 0:
        return data_dict, 16

    shank_columns = get_shank_columns(base_start_new, base_end, step_length)
    fine_label_mat = get_traveling_label_mat(pc_sp, shank_columns, rot_mat, bregma, label_data)
    # fine_label_mat = get_traveling_label_mat(ct_sp, ct_ep, direction, bregma, label_data, step_length)
    group_mat, group_id_label = group_labels(fine_label_mat)

    gr_start, gr_end, region_length, region_text_loc = get_group_bounds(group_mat, step_length)

    region_length = np.ravel(region_length) * vxsize_um

    label_names, label_acronym, label_color = get_label_name(label_info, group_id_label)

    if probe_type_name != 'Tetrode':
        # get sites information
        sites_x = get_sites_center_base(base_start_new, base_end, y_bias, sites_distance, per_max_sites)
        columns_loc_base = get_base_columns(base_start, sites_x)
        sites_loc, sites_vox, sites_label = get_sites(pc_sp, columns_loc_base, rot_mat, bregma, label_data)
        region_site_num = get_n_sites_in_region(gr_start, gr_end, sites_x)
        plot_sites_loc = get_plot_sites_loc(sites_x, base_end)

    else:
        sites_loc = np.repeat(np.array([pc_ep]), 4, axis=0)
        sites_vox = sites_loc + bregma
        sites_vox = sites_vox.astype(int)
        sites_label = label_data[sites_vox[:, 0], sites_vox[:, 1], sites_vox[:, 2]]
        region_site_num = None
        plot_sites_loc = None

    data_dict = {'object_name': 'probe', 'probe_type_name': probe_type_name,
                 'data': data_list, 'pieces_names': pieces_names, 'ap_tilt': ap_tilt, 'ml_tilt': ml_tilt,
                 'insertion_coords_3d': pc_sp, 'terminus_coords_3d': pc_ep,
                 'direction': direction, 'probe_length': probe_length_with_tip_um, 'dv': dv,
                 'ap_angle': ap_angle, 'ml_angle': ml_angle,
                 'insertion_coords': enter_coords, 'insertion_vox': pv_sp,
                 'terminus_coords': end_coords, 'terminus_vox': pv_ep,
                 'sites_label': sites_label, 'sites_loc_b': sites_loc, 'sites_vox': sites_vox,
                 'region_label': group_id_label, 'region_length': region_length,
                 'region_sites': region_site_num, 'text_loc': region_text_loc,
                 'label_name': label_names, 'label_acronym': label_acronym, 'label_color': label_color,
                 'group_region_start': gr_start, 'group_region_end': gr_end, 'sites_columns': plot_sites_loc}
    return data_dict, error_index


class Probe(object):
    def __init__(self):
        self.probe_length = None
        self.tip_length = None
        self.site_width = None
        self.site_height = None
        self.total_sites = None
        self.site_number_in_banks = None
        self.sites_distance = None
        self.probe_type = None
        self.x_bias = None
        self.per_max_sites = None
        self.sites_distance = None
        self.y_bias = None
        self.probe_type_name = None
        self.probe_thickness = None
        self.get_np1()

    def get_np2(self):
        self.probe_type = 1
        self.probe_type_name = 'NP2.0'
        self.probe_thickness = 24
        self.probe_length = 10000
        self.tip_length = 175
        self.site_width = 16
        self.site_height = 15
        self.x_bias = [-8, 16]
        self.per_max_sites = [480, 480]
        self.sites_distance = [15, 15]
        self.y_bias = [7.5, 7.5]
        self.site_number_in_banks = (384, 384, 192)

    def get_np1(self):
        self.probe_type = 0
        self.probe_type_name = 'NP1.0'
        self.probe_thickness = 24
        self.probe_length = 10000
        self.tip_length = 175
        self.site_width = 16
        self.site_height = 20
        self.x_bias = [-16, -8, 8, 16]
        self.per_max_sites = [240, 240, 240, 240]
        self.sites_distance = [40, 40, 40, 40]
        self.y_bias = [30, 10, 30, 10]
        self.site_number_in_banks = (384, 384, 192)

    def get_tetrode(self):
        self.probe_type = 3
        self.probe_type_name = 'Tetrode'
        self.probe_thickness = None
        self.probe_length = None
        self.tip_length = 0
        self.site_width = None
        self.site_height = None
        self.x_bias = None
        self.per_max_sites = 4
        self.sites_distance = None
        self.y_bias = 0
        self.site_number_in_banks = None

    def set_linear_silicon(self, pss):
        self.probe_type = 2
        self.probe_type_name = 'Linear-Silicon'
        self.probe_length = pss['probe_length']
        self.probe_thickness = pss['probe_thickness']
        self.tip_length = pss['tip_length']
        self.site_width = pss['site_width']
        self.site_height = pss['site_height']

        self.per_max_sites = pss['per_max_sites']
        self.sites_distance = pss['sites_distance']
        self.x_bias = pss['x_bias']
        self.y_bias = pss['y_bias']
        self.site_number_in_banks = None


    def get_settings(self):
        data = {'probe_type': self.probe_type,
                'probe_type_name': self.probe_type_name,
                'probe_thickness': self.probe_thickness,
                'probe_length': self.probe_length,
                'tip_length': self.tip_length,
                'site_height': self.site_height,
                'site_width': self.site_width,
                'per_max_sites': self.per_max_sites,
                'sites_distance': self.sites_distance,
                'x_bias': self.x_bias,
                'y_bias': self.y_bias,
                'site_number_in_banks': self.site_number_in_banks}
        return data
