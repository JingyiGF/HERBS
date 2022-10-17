import os
import pickle
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np
import scipy.ndimage as ndi


def get_object_vis_color(color):
    vis_color = (color[0] / 255, color[1] / 255, color[2] / 255, 1)
    return vis_color


def create_plot_points_in_3d(data_dict):
    pnts = data_dict['data']
    vis_color = get_object_vis_color(data_dict['vis_color'])
    vis_points = gl.GLScatterPlotItem(pos=pnts, color=vis_color, size=3)
    return vis_points


def create_probe_line_in_3d(data_dict):
    pos = np.stack([data_dict['new_insertion_coords_3d'], data_dict['new_terminus_coords_3d']], axis=0)
    vis_color = get_object_vis_color(data_dict['vis_color'])
    probe_line = gl.GLLinePlotItem(pos=pos, color=vis_color, width=2, mode='line_strip')
    return probe_line


def create_drawing_line_in_3d(data_dict):
    pos = np.asarray(data_dict['data'])
    vis_color = get_object_vis_color(data_dict['vis_color'])
    if np.all(pos[0] == pos[-1]):
        drawing_obj = gl.GLSurfacePlotItem(x=pos[:, 0], y=pos[:, 1], z=pos[:, 2], colors=vis_color)
    else:
        drawing_obj = gl.GLLinePlotItem(pos=pos, color=vis_color, width=2, mode='line_strip')
    return drawing_obj


def create_contour_line_in_3d(data_dict):
    temp = data_dict['data'].tolist()
    if temp[0] != temp[-1]:
        temp.append(temp[0])
    pos = np.asarray(temp)
    vis_color = get_object_vis_color(data_dict['vis_color'])
    contour_obj = gl.GLLinePlotItem(pos=pos, color=vis_color, width=2, mode='line_strip')
    return contour_obj


def make_3d_gl_widget(data_dict, obj_type):
    if obj_type == 'merged probe':
        obj_3d = create_probe_line_in_3d(data_dict)
    elif obj_type == 'merged virus':
        obj_3d = create_plot_points_in_3d(data_dict)
    elif obj_type == 'merged cells':
        obj_3d = create_plot_points_in_3d(data_dict)
    elif obj_type == 'merged contour':
        obj_3d = create_contour_line_in_3d(data_dict)
    else:
        obj_3d = create_drawing_line_in_3d(data_dict)
    return obj_3d


def render_volume(atlas_data, atlas_folder, factor=2, level=0.1):
    da_data = atlas_data.copy()
    img = np.ascontiguousarray(da_data[::factor, ::factor, ::factor])
    verts, faces = pg.isosurface(ndi.gaussian_filter(img.astype('float64'), (2, 2, 2)), np.max(da_data) * level)

    md = gl.MeshData(vertexes=verts * factor, faces=faces)

    outfile = open(os.path.join(atlas_folder, 'atlas_meshdata.pkl'), 'wb')
    pickle.dump(md, outfile)
    outfile.close()

    return md


def render_small_volume(label_id, save_path, atlas_data, atlas_label, factor=2, level=0.1):
    temp_atlas = atlas_data.copy()
    temp_atlas[atlas_label != label_id] = 0
    pimg = np.ascontiguousarray(temp_atlas[::factor, ::factor, ::factor])
    verts, faces = pg.isosurface(ndi.gaussian_filter(pimg.astype('float64'), (2, 2, 2)), np.max(temp_atlas) * level)
    # small_verts_list[str(id)] = verts
    # small_faces_list[str(id)] = faces

    md = gl.MeshData(vertexes=verts * factor, faces=faces)

    outfile = open(os.path.join(save_path, '{}.pkl'.format(label_id)), 'wb')
    pickle.dump(md, outfile)
    outfile.close()


