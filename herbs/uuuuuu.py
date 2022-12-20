import os
import numpy as np
import math
import pandas as pd
import cv2
import pickle
import colorsys
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import scipy.ndimage as ndi
from scipy.interpolate import interp1d, splprep, splev



def read_qss_file(qss_file_name):
    with open(qss_file_name, 'r', encoding='UTF-8') as file:
        return file.read()


def check_loading_pickle_file(file_path):
    layer_dict, msg = None, None
    try:
        infile = open(file_path, 'rb')
        layer_dict = pickle.load(infile)
        infile.close()
    except OSError:
        msg = 'OSError: possible reason - disk full, please contact maintainers.'
        return msg
    except (pickle.PickleError, pickle.UnpicklingError):
        msg = 'Pickling error, please check your file or contact maintainers.'
        return msg
    except EOFError:
        msg = 'EOFError: possible reason - suspecting loading a broken file, please contact maintainers.'
        return msg

    return layer_dict, msg


def read_excel_file(file_path):
    msg = None
    file_name, file_extension = os.path.splitext(file_path)
    if file_extension == '.csv':
        df = pd.read_csv(file_path)
    elif file_extension == '.xlsx':
        df = pd.read_excel(file_path)
    else:
        df = None
        msg = 'Only CSV file and Excel file works.'
    return df, msg


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


def get_region_label(data, label_data, bregma):
    region_label = []
    for i in range(len(data)):
        temp = data[i] + bregma
        temp = temp.astype(int)
        region_label.append(label_data[temp[0], temp[1], temp[2]])
    return region_label


def get_region_label_info(region_label, label_info):
    unique_label = np.sort(np.unique(region_label))
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

    return region_count, label_names, label_acronym, label_color, unique_label


def calculate_virus_info(data_list, pieces_names, label_data, label_info, bregma):
    temp_data = data_list[0]
    for i in range(1, len(data_list)):
        temp_data = np.vstack([temp_data, data_list[i]])

    data = temp_data.astype(int)

    # data = np.array([vox_data[0]])
    # for i in range(1, len(vox_data)):
    #     if np.any(vox_data[i] != data[-1]):
    #         data = np.vstack([data, vox_data[i]])

    region_label = get_region_label(data, label_data, bregma)
    unique_region = np.sort(np.unique(region_label))
    region_volume = []
    for c_region in unique_region:
        region_volume.append(len(np.where(label_data == c_region)[0]))

    print(region_volume)
    region_count, label_names, label_acronym, label_color, unique_label = get_region_label_info(region_label, label_info)
    print(region_count)

    res_dict = {'object_name': 'virus', 'data': data_list, 'pieces_names': pieces_names,
                'label_id': unique_label, 'label_name': label_names, 'label_acronym': label_acronym,
                'label_color': label_color, 'region_volume': region_volume, 'virus_volume': region_count}

    return res_dict


def calculate_cells_info(data_list, pieces_names, label_data, label_info, bregma):
    data = data_list[0]
    for i in range(1, len(data_list)):
        data = np.vstack([data, data_list[i]])

    region_label = get_region_label(data, label_data, bregma)
    region_count, label_names, label_acronym, label_color, unique_label = get_region_label_info(region_label, label_info)

    res_dict = {'object_name': 'cell', 'pieces_names': pieces_names, 'data': data_list, 'label_name': label_names,
                'label_acronym': label_acronym, 'label_color': label_color, 'region_count': region_count}
    return res_dict


def calculate_drawing_info(data_list, pieces_names, label_data, label_info, bregma):
    data = data_list[0]
    for i in range(1, len(data_list)):
        data = np.vstack([data, data_list[i]])
    print(data)
    if 'area' in pieces_names[0]:
        plot_mode = 'area'
    else:
        plot_mode = 'line'

    region_label = get_region_label(data, label_data, bregma)
    region_count, label_names, label_acronym, label_color, unique_label = get_region_label_info(region_label, label_info)

    res_dict = {'object_name': 'drawing', 'pieces_names': pieces_names, 'data': data_list, 'label_name': label_names,
                'label_acronym': label_acronym, 'label_color': label_color, 'region_count': region_count,
                'plot_mode': plot_mode}
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
    # x_knots, y_knots, z_knots = splev(tck[0], tck)
    u_fine = np.linspace(0, 1, len(data))
    x_fine, y_fine, z_fine = splev(u_fine, tck)
    pnts = np.stack([x_fine, y_fine, z_fine], axis=1)
    print(pnts)
    return pnts



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


def make_color_lut(channel_color: tuple, bit_level: int):
    r, g, b = colorsys.hsv_to_rgb(channel_color[0], channel_color[1], channel_color[2])
    colors = [(0, 0, 0), (r * 255, g * 255, b * 255)]
    color_map = pg.ColorMap(pos=[0, 1], color=colors)
    da_lut = color_map.getLookupTable(nPts=bit_level, mode=pg.ColorMap.FLOAT)
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


def gamma_line(input, lims, gamma, depth_level):
    inv_gamma = 1.0 / gamma
    y = np.zeros(len(input))
    inds = np.logical_and(input >= lims[0], input <= lims[1])
    y[inds] = np.power((input[inds] - lims[0]) / (lims[1] - lims[0]), gamma) * depth_level
    y[input <= lims[0]] = 0
    y[input >= lims[1]] = depth_level
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
        if np.max(image_data[:, :, i]) == 0:
            da_bins = max_val
        else:
            da_bins = np.max(image_data[:, :, i])
        hist_y, x = np.histogram(image_data[:, :, i], bins=da_bins)
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
        mask = np.zeros((r2[3], r2[2], img1.shape[2]), dtype=np.float32)
        cv2.fillConvexPoly(mask, np.int32(t2_rect_int), tuple(np.repeat(1.0, img1.shape[2])), 16, 0)
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
        img2[xr[0]:xr[1], yr[0]:yr[1]] = img2[xr[0]:xr[1], yr[0]:yr[1]] * (tuple(np.repeat(1.0, img1.shape[2])) - mask)
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
                onside_data.append([int(inline_point[0]), int(inline_point[1])])
    return onside_data


def match_sides_points(rect_atlas, size_atlas, rect_image, size_image):
    x_factor = rect_atlas[2] / rect_image[2]
    y_factor = rect_atlas[3] / rect_image[3]

    actual_right_dist_image = size_image[1] - (rect_image[0] + rect_image[2])
    actual_bottom_dist_image = size_image[0] - (rect_image[1] + rect_image[3])

    actual_right_dist_atlas = size_atlas[1] - (rect_atlas[0] + rect_atlas[2])
    actual_bottom_dist_atlas = size_atlas[0] - (rect_atlas[1] + rect_atlas[3])

    left_dist_atlas = rect_image[0] * x_factor
    right_dist_atlas = actual_right_dist_image * x_factor

    top_dist_atlas = rect_image[1] * y_factor
    bottom_dist_atlas = actual_bottom_dist_image * y_factor

    if left_dist_atlas <= rect_atlas[0]:
        atlas_corner_x = int(rect_atlas[0] - left_dist_atlas)
        image_corner_x = 0
    else:
        atlas_corner_x = 0
        left_dist_image = rect_atlas[0] / x_factor
        image_corner_x = int(rect_image[0] - left_dist_image)

    if right_dist_atlas <= actual_right_dist_atlas:
        atlas_right_side = size_atlas[1] - (actual_right_dist_atlas - right_dist_atlas)
        atlas_width = int(atlas_right_side - atlas_corner_x)
        image_width = size_image[1] - image_corner_x
    else:
        atlas_width = size_atlas[1] - atlas_corner_x
        right_dist_image = actual_right_dist_atlas / x_factor
        image_width = int(size_image[1] - image_corner_x - (actual_right_dist_image - right_dist_image))

    if top_dist_atlas <= rect_atlas[1]:
        atlas_corner_y = int(rect_atlas[1] - top_dist_atlas)
        image_corner_y = 0
    else:
        atlas_corner_y = 0
        top_dist_image = rect_atlas[1] / y_factor
        image_corner_y = int(rect_image[1] - top_dist_image)

    if bottom_dist_atlas <= actual_bottom_dist_atlas:
        atlas_height = int(size_atlas[0] - atlas_corner_y - (actual_bottom_dist_atlas - bottom_dist_atlas))
        image_height = size_image[0] - image_corner_y
    else:
        atlas_height = size_atlas[0] - atlas_corner_y
        bottom_dist_image = actual_bottom_dist_atlas / y_factor
        image_height = int(size_image[0] - image_corner_y - (actual_bottom_dist_image - bottom_dist_image))

    atlas_rect = (atlas_corner_x, atlas_corner_y, atlas_width, atlas_height)
    image_rect = (image_corner_x, image_corner_y, image_width, image_height)

    return atlas_rect, image_rect


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
    print(rect)
    subdiv = cv2.Subdiv2D(rect)
    for p in pnts:
        print(p)
        subdiv.insert((int(p[0]), int(p[1])))
    edge_list = subdiv.getEdgeList()
    lines_list = []
    # special_pnt = []
    for el in edge_list:
        pt1 = [el[0], el[1]]
        pt2 = [el[2], el[3]]
        if rect_contains(rect, pt1) and rect_contains(rect, pt2):
            lines_list.append(el)
        # else:
        #     if not rect_contains(rect, pt1) and pt1 not in special_pnt:
        #         special_pnt.append(pt1)
        #     if not rect_contains(rect, pt2) and pt2 not in special_pnt:
        #         special_pnt.append(pt2)
    return lines_list  #, special_pnt


# czi_img = image_file.data['scene 0'].copy()
# channel_hsv = image_file.hsv_colors
# temp_img = merge_channels_into_single_img(czi_img, channel_hsv)

def gamma_correction(src, gamma):
    inv_gamma = 1 / gamma

    table = [((i / 255) ** inv_gamma) * 255 for i in range(256)]
    table = np.array(table, np.uint8)

    return cv2.LUT(src, table)



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
            upper_val.append(get_upper_val(color[i], tol, level))
    return lower_val, upper_val


# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------



def get_statusbar_style(col):
    style = 'background-color: #323232;' \
            ' color: {}; border-top: 1px solid #272727; ' \
            'padding-left: 30px;'.format(col)
    return style


def rotate(image, angle, img_center=None, scale=1.0):
    (h, w) = image.shape[:2]

    if img_center is None:
        img_center = (w // 2, h // 2)

    rot_mat = cv2.getRotationMatrix2D(img_center, angle, scale)
    rotated_img = cv2.warpAffine(image, rot_mat, (w, h))

    return rotated_img


def rotate_bound(image, angle):
    (h, w) = image.shape[:2]
    (center_x, center_y) = (w / 2, h / 2)

    rot_mat = cv2.getRotationMatrix2D((center_x, center_y), -angle, 1.0)
    cos = np.abs(rot_mat[0, 0])
    sin = np.abs(rot_mat[0, 1])

    bound_w = int((h * sin) + (w * cos))
    bound_h = int((h * cos) + (w * sin))

    rot_mat[0, 2] += (bound_w / 2) - center_x
    rot_mat[1, 2] += (bound_h / 2) - center_y

    return cv2.warpAffine(image, rot_mat, (bound_w, bound_h))


def center_resize(img, dim):
    img_shape = img.shape
    width, height = img_shape[1], img_shape[0]
    scale_factor = np.min(np.array([dim[0] / width, dim[1] / height]))
    resize_dim = (int(width * scale_factor), int(height * scale_factor))
    resize_img = cv2.resize(img, resize_dim, interpolation=cv2.INTER_LINEAR)

    y = int(0.5 * (dim[0] - resize_dim[0]))
    x = int(0.5 * (dim[1] - resize_dim[1]))

    if len(img_shape) == 3:
        center_img = np.zeros((dim[1], dim[0], img.shape[2])).astype(img.dtype)
    else:
        center_img = np.zeros((dim[1], dim[0])).astype(img.dtype)

    center_img[x:(x + resize_dim[1]), y:(y + resize_dim[0])] = resize_img

    return center_img


def get_tb_size(img_size):
    scale_factor = np.max(np.ravel(img_size) / 80)
    tb_size = (int(img_size[1] / scale_factor), int(img_size[0] / scale_factor))
    return tb_size


def get_slice_atlas_coord(points, cut, size, width, height, distance, origin):
    """

    :param points: pnts on image
    :param cut: the cut of slice image
    :param size: the size (height, width) of slice image in pixel
    :param width: width of image in mm
    :param height: height of image in mm
    :param distance: distance of slice with respect to Bregma in mm
    :param origin: the coord of bregma on the current slice image
    :return:
    """
    width_factor = width / size[1] * 1000
    height_factor = height / size[0] * 1000
    if cut == 'Coronal':
        y_val = np.repeat(distance * 1000, len(points))
        x_val = (points[:, 0] - origin[0]) * width_factor
        z_val = (points[:, 1] - origin[1]) * height_factor
    elif cut == 'Sagittal':
        x_val = np.repeat(distance * 1000, len(points))
        y_val = (points[:, 0] - origin[0]) * width_factor
        z_val = (points[:, 1] - origin[1]) * height_factor
    else:
        z_val = np.repeat(distance * 1000, len(points))
        y_val = (points[:, 0] - origin[0]) * width_factor
        x_val = (points[:, 1] - origin[1]) * height_factor
    return x_val, y_val, z_val


def delete_points_inside_eraser(points, ct, r):
    x_min, y_min, x_max, y_max = ct[0] - r, ct[1] - r, ct[0] + r, ct[1] + r
    x_bool = np.logical_and(points[:, 0] <= x_max, points[:, 0] >= x_min)
    y_bool = np.logical_and(points[:, 1] <= y_max, points[:, 1] >= y_min)
    chk_inds = np.where(np.logical_and(x_bool, y_bool))[0]
    if len(chk_inds) == 0:
        return None, None
    chk_pnt = points[chk_inds]
    dist = np.sum(np.power(chk_pnt - ct, 2), 1)
    del_ind = np.where(dist < np.power(r, 2))[0]
    if len(del_ind) == 0:
        return None, None
    real_del_ind = chk_inds[del_ind]
    remain_inds = np.zeros(len(points)) < 1
    remain_inds[real_del_ind] = False
    remain_points = points[remain_inds]
    return remain_points, real_del_ind


def interpolate_contour_points(points):
    if not np.all(points[-1] == points[0]):
        points[:, 0] = np.r_[points[:, 0], points[:, 0]]
        points[:, 1] = np.r_[points[:, 1], points[:, 1]]

    tck = splprep([points[:, 0], points[:, 1]], s=0, per=True)

    xi, yi = splev(np.linspace(0, 1, 1000), tck[0])
    return xi, yi


def create_vis_img(size, point_data, color, vis_type='p', closed=False):
    if isinstance(point_data, list):
        point_data = np.asarray(point_data).astype(int)
    else:
        point_data = point_data.astype(int)
    img = np.zeros((size[0], size[1], 3), 'uint8')
    da_color = (int(color[0]), int(color[1]), int(color[2]))
    if vis_type == 'p':
        for i in range(len(point_data)):
            cv2.circle(img, (int(point_data[i][0]), int(point_data[i][1])), radius=5, color=da_color, thickness=-1)
    else:
        if closed:
            cv2.fillPoly(img, pts=[point_data], color=da_color)
        else:
            for i in range(len(point_data) - 1):
                cv2.line(img, (int(point_data[i][0]), int(point_data[i][1])),
                         (int(point_data[i + 1][0]), int(point_data[i + 1][1])),
                         color=da_color, thickness=8)
    return img


def color_vis_img(img, color):
    temp = np.zeros((img.shape[0], img.shape[1], 3), 'uint8')
    temp[img != 0, 0] = color[0]
    temp[img != 0, 1] = color[1]
    temp[img != 0, 2] = color[2]
    return temp


def check_loaded_project(project_dict):
    all_keys = list(project_dict.keys())
    valid_keys = ['atlas_path', 'current_atlas', 'num_windows', 'probe_type', 'np_onside', 'processing_slice',
                  'processing_img', 'overlay_img', 'atlas_control', 'img_ctrl_data', 'setting_data', 'tool_data',
                  'layer_data', 'working_img_data', 'working_atlas_data', 'object_data']
    valid_project = True
    for da_key in all_keys:
        if da_key not in valid_keys:
            valid_project = False
    return valid_project


def check_bounding_contains(points, size):
    if np.any(points[:, 0] > size[1]) or np.any(points[:, 1] > size[0]):
        return False
    else:
        return True


def obj_data_to_mesh3d(filename):
    vertices = []
    faces = []

    with open(filename, 'r') as objf:
        for line in objf:
            slist = line.split()
            if slist:
                if slist[0] == 'v':
                    vertex = np.array(slist[1:], dtype=float)
                    vertices.append(vertex)
                elif slist[0] == 'f':
                    face = []
                    for k in range(1, len(slist)):
                        face.append([int(s) for s in slist[k].replace('//', '/').split('/')])
                    if len(face) > 3:  # triangulate the n-polyonal face, n>3
                        faces.extend(
                            [[face[0][0] - 1, face[k][0] - 1, face[k + 1][0] - 1] for k in range(1, len(face) - 1)])
                    else:
                        faces.append([face[j][0] - 1 for j in range(len(face))])
                else:
                    pass

    return np.array(vertices), np.array(faces)


def make_atlas_label_contour(atlas_folder, segmentation_data):
    sagital_contour_img = np.zeros(segmentation_data.shape, 'i')
    coronal_contour_img = np.zeros(segmentation_data.shape, 'i')
    horizontal_contour_img = np.zeros(segmentation_data.shape, 'i')

    # pre-process boundary
    for i in range(len(segmentation_data)):
        da_slice = segmentation_data[i, :, :].copy()
        contour_img = make_contour_img(da_slice)
        sagital_contour_img[i, :, :] = contour_img

    for i in range(segmentation_data.shape[1]):
        da_slice = segmentation_data[:, i, :].copy()
        contour_img = make_contour_img(da_slice)
        coronal_contour_img[:, i, :] = contour_img

    for i in range(segmentation_data.shape[2]):
        da_slice = segmentation_data[:, :, i].copy()
        contour_img = make_contour_img(da_slice)
        horizontal_contour_img[:, :, i] = contour_img

    boundary = {'s_contour': sagital_contour_img,
                'c_contour': coronal_contour_img,
                'h_contour': horizontal_contour_img}

    bnd = {'data': boundary}

    outfile_ct = open(os.path.join(atlas_folder, 'contour_pre_made.pkl'), 'wb')
    pickle.dump(bnd, outfile_ct)
    outfile_ct.close()

    return boundary


def get_angle_two_vector(vec1, vec2):
    """
    in 2d
    :param vec1:
    :param vec2:
    :return:
    """

    vec = np.array([-vec2[1], vec2[0]])
    b_coord = np.dot(vec1, vec2)
    p_coord = np.dot(vec1, vec)
    da_ang = np.arctan2(p_coord, b_coord)

    return da_ang


def rotate_base_points(data, base_loc):
    temp = np.stack([base_loc, np.repeat(0, len(base_loc))], axis=1)
    vec1 = data[1] - data[0]
    vec2 = np.array([0, 1])
    ang = get_angle_two_vector(vec1, vec2)
    rotm = np.array([[np.cos(ang), -np.sin(ang)], [np.sin(ang), np.cos(ang)]])
    base_pnt = np.dot(rotm, temp.T).T
    start_pnt = base_pnt + data[0]
    end_pnt = base_pnt + data[1]
    return start_pnt, end_pnt


def get_cell_count(cell_layer_index):
    cell_count = [0 for _ in range(5)]
    cell_layer_index = np.ravel(cell_layer_index)
    for i in range(5):
        cell_count[i] = np.sum(cell_layer_index == i)
    return cell_count


def load_point_data(data_file_path):
    file_basename = os.path.basename(data_file_path)
    file_name, file_ext = os.path.splitext(file_basename)
    msg = None
    data = None
    try:
        if file_ext == '.npy':
            data = np.load(data_file_path)
        elif file_ext == '.pkl':
            with open(data_file_path, 'rb') as f:
                data = pickle.load(f)
            # data = data_file['points']
    except (IOError, OSError, ValueError, KeyError, IndexError, pickle.PickleError, pickle.UnpicklingError):
        msg = 'Can not open atlas axis information file, please check the Tutorial on GitHub.'
        return data, msg

    if not isinstance(data, np.ndarray):
        msg = 'Data is not numpy ndarray, please check the Tutorial on GitHub.'
        return data, msg

    data_shape = data.shape
    if len(data_shape) != 2:
        msg = 'Data has wrong size, please check the Tutorial on GitHub.'
        return data, msg

    if data_shape[1] != 3:
        msg = 'Data has wrong size, please check the Tutorial on GitHub.'
        return data, msg

    return data, msg

