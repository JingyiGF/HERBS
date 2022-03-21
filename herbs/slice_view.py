import os
import sys
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph.functions as fn
import pyqtgraph.opengl as gl
from PyQt5.QtWidgets import *

from herrbs.slice_stacks import SliceStacks
from herrbs.label_tree import LabelTree
from herrbs.uuuuuu import *


# class AtlasDisplayCtrl(pg.parametertree.ParameterTree):
#     """UI for controlling how the atlas is displayed.
#     """
#     def __init__(self, parent=None):
#         pg.parametertree.ParameterTree.__init__(self, parent=parent)
#         params = [
#             {'name': 'Orientation', 'type': 'list', 'values': ['right', 'anterior', 'dorsal']},
#             {'name': 'Opacity', 'type': 'float', 'limits': [0, 1], 'value': 0.5, 'step': 0.1},
#             {'name': 'Composition', 'type': 'list', 'values': ['Multiply', 'Overlay', 'SourceOver']},
#             {'name': 'Downsample', 'type': 'int', 'value': 1, 'limits': [1, None], 'step': 1},
#             {'name': 'Interpolate', 'type': 'bool', 'value': True},
#         ]
#         self.params = pg.parametertree.Parameter(name='params', type='group', children=params)
#         self.setParameters(self.params, showTop=False)
#         self.setHeaderHidden(True)


class PageController(QWidget):

    def __init__(self):

        self.sig_page_changed = QtCore.Signal(object)

        QWidget.__init__(self)

        self.max_val = None

        self.page_slider = QSlider(QtCore.Qt.Horizontal)
        self.page_slider.setMinimum(0)
        self.page_slider.valueChanged.connect(self.slider_value_changed)

        self.page_label = QLabel()
        self.page_label.setFixedSize(50, 20)

        self.page_left_btn = QPushButton()
        self.page_left_btn.setIcon(QtGui.QIcon("icons/triangle_left.png"))
        self.page_left_btn.setIconSize(QtCore.QSize(10, 10))
        # self.page_left_btn.setFixedSize(30, 20)
        self.page_left_btn.clicked.connect(self.left_btn_clicked)

        self.page_right_btn = QPushButton()
        self.page_right_btn.setIcon(QtGui.QIcon("icons/triangle_right.png"))
        self.page_right_btn.setIconSize(QtCore.QSize(10, 10))
        # self.page_right_btn.setFixedSize(30, 20)
        self.page_right_btn.clicked.connect(self.right_btn_clicked)

        self.page_fast_left_btn = QPushButton()
        self.page_fast_left_btn.setIcon(QtGui.QIcon("icons/double_triangle_left.png"))
        self.page_fast_left_btn.setIconSize(QtCore.QSize(10, 10))
        # self.page_fast_left_btn.setFixedSize(30, 20)
        self.page_fast_left_btn.clicked.connect(self.fast_left_btn_clicked)

        self.page_fast_right_btn = QPushButton()
        self.page_fast_right_btn.setIcon(QtGui.QIcon("icons/double_triangle_right.png"))
        self.page_fast_right_btn.setIconSize(QtCore.QSize(10, 10))
        # self.page_fast_right_btn.setFixedSize(30, 20)
        self.page_fast_right_btn.clicked.connect(self.fast_right_btn_clicked)

        page_ctrl_layout = QHBoxLayout()
        page_ctrl_layout.setSpacing(3)
        page_ctrl_layout.setContentsMargins(0, 0, 0, 0)
        page_ctrl_layout.addWidget(self.page_left_btn)
        page_ctrl_layout.addWidget(self.page_fast_left_btn)
        page_ctrl_layout.addWidget(self.page_slider)
        page_ctrl_layout.addWidget(self.page_label)
        page_ctrl_layout.addWidget(self.page_fast_right_btn)
        page_ctrl_layout.addWidget(self.page_right_btn)

        self.setLayout(page_ctrl_layout)

    def set_val(self, val):
        self.page_slider.setValue(val)

    def set_max(self, val):
        self.max_val = val
        self.page_slider.setMaximum(val)

    def slider_value_changed(self):
        val = self.page_slider.value()
        self.page_label.setText(str(val))
        self.sig_page_changed.emit(val)

    def left_btn_clicked(self):
        val = self.page_slider.value() - 1
        if val < 0:
            val = 0
        self.set_val(val)

    def right_btn_clicked(self):
        val = self.page_slider.value() + 1
        if val > self.max_val:
            val = self.max_val
        self.set_val(val)

    def fast_left_btn_clicked(self):
        val = self.page_slider.value() - 10
        if val < 0:
            val = 0
        self.set_val(val)

    def fast_right_btn_clicked(self):
        val = self.page_slider.value() + 10
        if val > self.max_val:
            val = self.max_val
        self.set_val(val)


class SliceRotator(QWidget):

    def __init__(self):

        self.sig_slice_rotated = QtCore.Signal(object)

        QWidget.__init__(self)

        self.h_slider = QSlider(QtCore.Qt.Horizontal)
        self.h_slider.valueChanged.connect(self.h_slider_changed)
        self.h_slider.setValue(0)
        self.h_slider.setRange(-900, 900)

        self.h_spinbox = QDoubleSpinBox()
        self.h_spinbox.valueChanged.connect(self.h_spinbox_changed)
        self.h_spinbox.setValue(0)
        self.h_spinbox.setRange(-45, 45)
        self.h_spinbox.setSingleStep(0.05)
        self.h_spinbox.setMinimumSize(50, 20)

        self.v_slider = QSlider(QtCore.Qt.Horizontal)
        self.v_slider.valueChanged.connect(self.v_slider_changed)
        # self.v_slider.sliderMoved.connect(self.update_cx_angle_spinbox)
        self.v_slider.setValue(0)
        self.v_slider.setRange(-900, 900)

        self.v_spinbox = QSpinBox()
        self.v_spinbox.valueChanged.connect(self.v_spinbox_changed)
        self.v_spinbox.setValue(0)
        self.v_spinbox.setRange(-45, 45)
        self.h_spinbox.setSingleStep(0.05)
        self.v_spinbox.setMinimumSize(50, 20)

    def h_slider_changed(self):
        val = self.h_slider.value() / 20
        self.h_spinbox.setValue(val)

    def h_spinbox_changed(self):
        val = int(self.h_spinbox.value() * 20)
        self.h_slider.setValue(val)
        self.sig_slice_rotated.emit([self.h_spinbox.value(), self.v_spinbox.value()])

    def v_slider_changed(self):
        val = self.v_slider.value() / 20
        self.v_spinbox.setValue(val)

    def v_spinbox_changed(self):
        val = int(self.v_spinbox.value() * 20)
        self.v_slider.setValue(val)
        self.sig_slice_rotated.emit([self.h_spinbox.value(), self.v_spinbox.value()])







class SliceView(QWidget):
    """
    A collection of user interface elements bound together:


    """
    
    sig_c_slice_changed = QtCore.Signal()  # coronal slice plane changed
    sig_s_slice_changed = QtCore.Signal()  # sagital slice plane changed
    sig_sc_slice_changed = QtCore.Signal()  # sagital copy slice plane changed
    sig_h_slice_changed = QtCore.Signal()  # horizontal  slice plane changed
    sig_image_changed = QtCore.Signal()  # orthogonal image changed
    sig_c_angle_changed = QtCore.Signal()  # coronal slice plane changed
    sig_s_angle_changed = QtCore.Signal()  # sagital slice plane changed
    sig_h_angle_changed = QtCore.Signal()  # horizontal  slice plane changed
    sig_image_changed = QtCore.Signal()  # orthogonal image changed
    
    sig_label_changed = QtCore.Signal()
    
    mouseHovered = QtCore.Signal(object)
    mouseClicked = QtCore.Signal(object)
    
    def __init__(self):
        # QtCore.QObject.__init__(self)
        QWidget.__init__(self)

        self.atlas_data = None
        self.atlas_label = None
        self.atlas_info = None
        self.label_info = None
        self.display_atlas = None
        self.display_label = None
        self.scale = None
        self.interpolate = True
        self.oy_vector = np.array([0, 1, 0])
        self.oz_vector = np.array([0, 0, 1])
        self.ox_vector = np.array([1, 0, 0])
        
        self.cimg = SliceStacks()  # ap - coronal
        self.coronal_window = pg.GraphicsLayoutWidget()
        coronal_vb = self.coronal_window.addViewBox()
        coronal_vb.setAspectLocked()
        coronal_vb.invertY(False)
        coronal_vb.addItem(self.cimg)
        self.cpage_ctrl = PageController()
        self.clut = pg.HistogramLUTWidget()
        self.clut.setImageItem(self.cimg.atlas_img)

        self.simg = SliceStacks()
        self.spage_ctrl = PageController()
        self.slut = pg.HistogramLUTWidget()
        self.slut.setImageItem(self.simg.atlas_img)
        self.sagital_window = pg.GraphicsLayoutWidget()
        sagital_vb = self.sagital_window.addViewBox()
        sagital_vb.setAspectLocked()
        sagital_vb.invertY(False)
        sagital_vb.addItem(self.simg)

        self.scimg = SliceStacks()
        self.scpage_ctrl = PageController()
        self.sclut = pg.HistogramLUTWidget()
        self.sclut.setImageItem(self.scimg.atlas_img)
        self.sagital_copy_window = pg.GraphicsLayoutWidget()
        sagital_copy_vb = self.sagital_copy_window.addViewBox()
        sagital_copy_vb.setAspectLocked()
        sagital_copy_vb.invertY(False)
        sagital_copy_vb.addItem(self.simg)

        self.himg = SliceStacks()
        self.hpage_ctrl = PageController()
        self.hlut = pg.HistogramLUTWidget()
        self.hlut.setImageItem(self.himg.atlas_img)
        self.horizontal_window = pg.GraphicsLayoutWidget()
        horizontal_vb = self.horizontal_window.addViewBox()
        horizontal_vb.setAspectLocked()
        horizontal_vb.invertY(False)
        horizontal_vb.addItem(self.simg)


        # 3d things
        self.plate_color = [0.5, 0.5, 0.5, 0.2]
        self.ap_plate_verts = np.array([[-1, 0, -1], [-1, 0, 1], [1, 0, 1], [1, 0, -1]]) * 80
        self.ap_plate_faces = np.array([[0, 1, 2], [0, 2, 3]])
        self.ap_plate_md = gl.MeshData(vertexes=self.ap_plate_verts, faces=self.ap_plate_faces)
        self.ap_plate_mesh = gl.GLMeshItem(meshdata=self.ap_plate_md, smooth=False, color=self.plate_color)
        self.ap_plate_mesh.setGLOptions('additive')

        self.dv_plate_verts = np.array([[-1, -2, 0], [-1, 2, 0], [1, 2, 0], [1, -2, 0]]) * 80
        self.dv_plate_faces = np.array([[0, 1, 2], [0, 2, 3]])
        self.dv_plate_md = gl.MeshData(vertexes=self.dv_plate_verts, faces=self.dv_plate_faces)
        self.dv_plate_mesh = gl.GLMeshItem(meshdata=self.dv_plate_md, smooth=False, color=self.plate_color)
        self.dv_plate_mesh.setGLOptions('additive')

        self.ml_plate_verts = np.array([[0, -2, -1], [0, 2, -1], [0, 2, 1], [0, -2, 1]]) * 80
        self.ml_plate_faces = np.array([[0, 1, 2], [0, 2, 3]])
        self.ml_plate_md = gl.MeshData(vertexes=self.ml_plate_verts, faces=self.ml_plate_faces)
        self.ml_plate_mesh = gl.GLMeshItem(meshdata=self.ml_plate_md, smooth=False, color=self.plate_color)
        self.ml_plate_mesh.setGLOptions('additive')

        self.axix = gl.GLAxisItem()
        self.axix.setSize(2, 2, 2)

        self.grid = gl.GLGridItem()
        self.grid.scale(2, 2, 1)

        md = gl.MeshData()
        mesh = gl.GLMeshItem(smooth=True, color=[0.5, 0.5, 0.5, 0.2], shader='balloon')
        mesh.setGLOptions('additive')

        




        # self.lut.sigLookupTableChanged.connect(self.histlut_changed)
        # self.lut.sigLevelsChanged.connect(self.histlut_changed)
        
        
        self.label_tree = LabelTree()
        # self.label_tree.labels_changed.connect(self.labels_changed)

        outer_outer_layout = QVBoxLayout()

        outer_outer_layout.addWidget(self.coronal_window)
        # outer_outer_layout.addWidget(self.clut)
        outer_outer_layout.addWidget(self.cpage_ctrl)

        self.setLayout(outer_outer_layout)

        self.show()
    
    def set_data(self, atlas_data, atlas_label, atlas_info, label_info):
        self.atlas_data = atlas_data
        self.atlas_label = atlas_label
        self.atlas_info = atlas_info
        self.label_info = label_info
        self.label_tree.set_labels(label_info)
        self.update_image_data()
        self.labels_changed()
        
        

    
    

    def c_rotation(self):
        if self.atlas_data is None or self.atlas_label is None:
            return

        z_angle = np.radians(self.cz_angle_slider.value())
        x_angle = np.radians(self.cx_angle_slider.value())

        # oy_vector = np.array([0, 1, 0])  # norm vector
        #
        # rotm = rotation_z(z_rad)
        # rotated_oy_vector = np.dot(rotm, oy_vector)
        #
        # oz_vector = np.array([0, 0, 1])
        # ox_vector = np.cross(rotated_oy_vector, oz_vector)
        #
        # start_origin = (0, 512, 0)
        #
        # oz_length = 512
        # ox_length = 512 / np.cos(z_rad)
        #
        # da_origin = 512 - 256 * np.tan(z_rad)
        # oval_new = (0, da_origin, 0)
        
        

        o_val = np.array([0, self.c_page_slider.value(), 0])
        o_rot = np.array([256, self.c_page_slider.value(), 256])

        rotm = np.dot(rotation_z(z_angle), rotation_x(x_angle))

        oz_vector = np.dot(rotm, np.array([0, 0, 1]))
        ox_vector = np.dot(rotm, np.array([1, 0, 0]))


        oval_new = o_rot + np.dot(rotm, o_val - o_rot)

        ox_length = 512
        oz_length = 512

        atlas = fn.affineSlice(self.atlas_data, shape=(ox_length, oz_length), vectors=[ox_vector, oz_vector],
                               origin=(oval_new[0], oval_new[1], oval_new[2]), axes=(0, 1, 2), order=1)
        label = fn.affineSlice(self.atlas_label, shape=(ox_length, oz_length), vectors=[ox_vector, oz_vector],
                               origin=(oval_new[0], oval_new[1], oval_new[2]), axes=(0, 1, 2), order=0)
        

        self.cimg.set_data(atlas, label, scale=None)
        self.sig_c_angle_changed.emit()
        
        
    # def s_rotation(self):
    #     if self.atlas_data is None or self.atlas_label is None:
    #         return
    #     z_angle = np.radians(self.sz_angle_slider.value())
    #     y_angle = np.radians(self.sy_angle_slider.value())
    #
    #
    #     o_val = np.array([self.sc_page_slider.value(), 0, 0])
    #     o_rot = np.array([self.sc_page_slider.value(), 512, 256])
    #
    #     rotm = np.dot(rotation_z(z_angle), rotation_y(y_angle))
    #
    #     oz_vector = np.dot(rotm, np.array([0, 0, 1]))
    #     oy_vector = np.dot(rotm, np.array([0, 1, 0]))
    #
    #     oval_new = o_rot + np.dot(rotm, o_val - o_rot)
    #
    #     oy_length = 1024
    #     oz_length = 512
    #
    #     atlas = fn.affineSlice(self.atlas_data, shape=(oy_length, oz_length), vectors=[oy_vector, oz_vector],
    #                            origin=(oval_new[0], oval_new[1], oval_new[2]), axes=(0, 1, 2), order=1)
    #     label = fn.affineSlice(self.atlas_label, shape=(oy_length, oz_length), vectors=[oy_vector, oz_vector],
    #                            origin=(oval_new[0], oval_new[1], oval_new[2]), axes=(0, 1, 2), order=0)
    #
    #     self.simg.set_data(atlas, label, scale=None)
    #     self.simg_copy.set_data(atlas, label, scale=None)
    #     self.sig_s_angle_changed.emit()
    #
    #
    # def h_rotation(self):
    #     if self.atlas_data is None or self.atlas_label is None:
    #         return
    #     x_angle = np.radians(self.hx_angle_slider.value())
    #     y_angle = np.radians(self.hy_angle_slider.value())
    #
    #
    #     o_val = np.array([0, 0, self.h_page_slider.value()])
    #     o_rot = np.array([256, 512, self.h_page_slider.value()])
    #
    #     rotm = np.dot(rotation_y(y_angle), rotation_x(x_angle))
    #
    #     ox_vector = np.dot(rotm, np.array([1, 0, 0]))
    #     oy_vector = np.dot(rotm, np.array([0, 1, 0]))
    #
    #     oval_new = o_rot + np.dot(rotm, o_val - o_rot)
    #
    #     oy_length = 1024
    #     ox_length = 512
    #
    #     atlas = fn.affineSlice(self.atlas_data, shape=(ox_length, oy_length), vectors=[ox_vector, oy_vector],
    #                            origin=(oval_new[0], oval_new[1], oval_new[2]), axes=(0, 1, 2), order=1)
    #     label = fn.affineSlice(self.atlas_label, shape=(ox_length, oy_length), vectors=[ox_vector, oy_vector],
    #                            origin=(oval_new[0], oval_new[1], oval_new[2]), axes=(0, 1, 2), order=0)
    #
    #     self.himg.set_data(atlas, label, scale=None)
    #     self.sig_h_angle_changed.emit()
    #
    #
    #
    # def update_s_through_sc(self):
    #     if self.atlas_data is None or self.atlas_label is None:
    #         return
    #     page_number = self.sc_page_slider.value()
    #     self.s_page_slider.setValue(page_number)
    #
    #
    # def update_sc_through_s(self):
    #     if self.atlas_data is None or self.atlas_label is None:
    #         return
    #     page_number = self.s_page_slider.value()
    #     self.sc_page_slider.setValue(page_number)
    #
    #
    # def update_cslice(self):
    #     if self.atlas_data is None or self.atlas_label is None:
    #         return
    #     self.cx_angle_spinbox.setValue(0)
    #     self.cz_angle_spinbox.setValue(0)
    #     page_number = self.c_page_slider.value()
    #     self.c_page_label.setText(str(page_number))
    #     # print(self.atlas_data[:, page_number, :])
    #     self.cimg.set_data(self.atlas_data[:, page_number, :], self.atlas_label[:, page_number, :], scale=None)
    #     self.sig_c_slice_changed.emit()
    #
    # def update_sslice(self):
    #     if self.atlas_data is None or self.atlas_label is None:
    #         return
    #     page_number = self.s_page_slider.value()
    #     self.s_page_label.setText(str(page_number))
    #     self.simg.set_data(self.atlas_data[page_number, :, :], self.atlas_label[page_number, :, :], scale=None)
    #     # self.sig_s_slice_changed.emit()
    #
    # def update_scslice(self):
    #     if self.atlas_data is None or self.atlas_label is None:
    #         return
    #     self.sy_angle_spinbox.setValue(0)
    #     self.sz_angle_spinbox.setValue(0)
    #     page_number = self.sc_page_slider.value()
    #     self.sc_page_label.setText(str(page_number))
    #     self.simg_copy.set_data(self.atlas_data[page_number, :, :], self.atlas_label[page_number, :, :], scale=None)
    #     self.sig_sc_slice_changed.emit()
    #
    # def update_hslice(self):
    #     if self.atlas_data is None or self.atlas_label is None:
    #         return
    #     self.hx_angle_spinbox.setValue(0)
    #     self.hy_angle_spinbox.setValue(0)
    #     page_number = self.h_page_slider.value()
    #     self.h_page_label.setText(str(page_number))
    #     self.himg.set_data(self.atlas_data[:, :, page_number], self.atlas_label[:, :, page_number], scale=None)
    #     self.sig_h_slice_changed.emit()
    #
    # def update_image_data(self):
    #     if self.atlas_data is None or self.atlas_label is None:
    #         return
    #
    #     self.atlas_data = self.atlas_data.view(np.ndarray)
    #     self.atlas_label = self.atlas_label.view(np.ndarray)
    #
    #     scale = self.atlas_info[-1]['vxsize']  # * ds
    #     self.scale = (scale, scale)
    #
    #     atlas_shape = self.atlas_data.shape
    #
    #     self.c_page_slider.setMaximum(atlas_shape[1] - 1)
    #     self.c_page_slider.setValue(atlas_shape[1] // 2)
    #     # self.c_page_label.setText(str(self.display_atlas.shape[0] // 2))
    #
    #     self.s_page_slider.setMaximum(atlas_shape[0] - 1)
    #     self.s_page_slider.setValue(atlas_shape[0] // 2)
    #     # self.s_page_label.setText(str(self.display_atlas.shape[0] // 2))
    #
    #     self.sc_page_slider.setMaximum(atlas_shape[0] - 1)
    #     self.sc_page_slider.setValue(atlas_shape[0] // 2)
    #
    #     self.h_page_slider.setMaximum(atlas_shape[2] - 1)
    #     self.h_page_slider.setValue(atlas_shape[2] // 2)
    #     # self.c_page_label.setText(str(self.atlas_data.shape[0] // 2))
    #
    #     self.update_cslice()
    #     self.update_sslice()
    #     self.update_scslice()
    #     self.update_hslice()
    #
    #     # self.update_slice_image()
    #     lut_min = float(self.atlas_data.min())
    #     lut_max = float(self.atlas_data.max())
    #     self.clut.setLevels(lut_min, lut_max)
    #     self.slut.setLevels(lut_min, lut_max)
    #     self.sclut.setLevels(lut_min, lut_max)
    #     self.hlut.setLevels(lut_min, lut_max)



        
    
    # def update_slice(self):
    #     page_number = self.page_slider.value()
    #     self.page_label.setText(str(page_number))
    #     self.img1.set_data(self.display_atlas[page_number], self.display_label[page_number], scale=self.scale)
    #     self.sig_image_changed.emit()

    # def y_rotate_slice(self):
    #     theta1 = self.y_angle_slider.value()
    #     trad1 = theta1 / 180 * np.pi
    #
    #     theta2 = self.x_angle_slider.value()
    #     trad2 = theta2 / 180 * np.pi
    #
    #     rot_mat = np.dot(rotation_z(trad1), rotation_y(trad2))
    #     ox_vector = np.array([1, 0, 0])  # norm vector
    #     self.ox_vector = np.dot(rot_mat, ox_vector)  # norm vector
    #
    #     # oz_vector = np.array([0, 0, 1])
    #     self.oz_vector = np.cross(self.ox_vector, self.oy_vector)
    #
    #     dims = self.display_atlas.shape
    #
    #     base_val = self.page_slider.value()
    #     oz_length = dims[2]
    #     oy_length = dims[1] / np.cos(trad1)
    #
    #     da_origin = base_val - 0.5 * dims[1] * np.tan(trad1)
    #
    #     atlas = fn.affineSlice(self.display_atlas, shape=(oy_length, oz_length), vectors=[self.oy_vector, self.oz_vector],
    #                            origin=(da_origin, 0, 0), axes=(0, 1, 2), order=1)
    #     label = fn.affineSlice(self.display_label, shape=(oy_length, oz_length), vectors=[self.oy_vector, self.oz_vector],
    #                            origin=(da_origin, 0, 0), axes=(0, 1, 2), order=0)
    #
    #     self.img1.set_data(atlas, label, scale=self.scale)
    #
    # def x_rotate_slice(self):
    #     theta = self.x_angle_slider.value()
    #     trad = theta / 180 * np.pi
    #     rot_mat = rotation_y(trad)
    #     oy_vector = np.array([1, 0, 0])  # norm vector
    #     rotated_oy_vector = np.dot(rot_mat, oy_vector)
    #
    #     oz_vector = np.array([0, 0, 1])
    #     ox_vector = np.cross(rotated_oy_vector, oz_vector)
    #
    #     start_origin = (0, 512, 0)
    #
    #     base_val = self.display_atlas.shape[0]
    #     oz_length = base_val
    #     ox_length = base_val / np.cos(trad)
    #
    #     da_origin = base_val - 0.5 * base_val * np.tan(trad)
    #
    #     atlas = fn.affineSlice(self.display_atlas, shape=(ox_length, oz_length), vectors=[ox_vector, oz_vector],
    #                            origin=(da_origin, 0, 0), axes=(0, 1, 2), order=1)
    #     label = fn.affineSlice(self.display_label, shape=(ox_length, oz_length), vectors=[ox_vector, oz_vector],
    #                            origin=(da_origin, 0, 0), axes=(0, 1, 2), order=0)
    #
    #     self.img1.set_data(atlas, label, scale=self.scale)
        
    
    
    # def labels_changed(self):
    #     # reapply label colors
    #     lut = self.label_tree.lookup_table()
    #     self.simg_copy.label_img.setImage(lut=lut)
    #     self.cimg.label_img.setImage(lut=lut)
    #     self.simg.label_img.setImage(lut=lut)
    #     self.himg.label_img.setImage(lut=lut)
    #     self.sig_label_changed.emit()
        
    #
    # def display_ctrl_changed(self, param, changes):
    #     update = False
    #     for param, change, value in changes:
    #         if param.name() == 'Composition':
    #             self.set_overlay(value)
    #         elif param.name() == 'Opacity':
    #             self.set_label_opacity(value)
    #         elif param.name() == 'Interpolate':
    #             self.set_interpolation(value)
    #         else:
    #             update = True
    #     if update:
    #         self.update_image_data()
    #
    
    
    
   
    
    # def angle_slider_changed(self):
    #     # rotation = self.angle_slider.value()
    #     # self.set_rotation_roi(self.img1.atlas_img, rotation)
    #     self.update_slice_image()
    
    def close(self):
        self.data = None
    #
    # def set_overlay(self, o):
    #     self.cimg.set_overlay(o)
    #     self.simg.set_overlay(o)
    #     self.himg.set_overlay(o)
    #     self.simg_copy.set_overlay(o)
        
    #     self.img2.set_overlay(o)
    #
    # def set_label_opacity(self, o):
    #     self.cimg.set_label_opacity(o)
    #     self.simg.set_label_opacity(o)
    #     self.himg.set_label_opacity(o)
    #     self.simg_copy.set_label_opacity(o)


    # def set_interpolation(self, interp):
    #     assert isinstance(interp, bool)
    #     self.interpolate = interp
    #
    # def set_label_lut(self, lut):
    #     self.cimg.set_lut(lut)
    #     self.simg.set_lut(lut)
    #     self.himg.set_lut(lut)
    #     self.simg_copy.set_lut(lut)
    
    # def histlut_changed(self):
    #     # note: img1 is updated automatically; only bneed to update img2 to match
    #     self.img2.atlas_img.setLookupTable(self.lut.getLookupTable(n=256))
    #     self.img2.atlas_img.setLevels(self.lut.getLevels())
    

    
    # def get_offset(self, rotation):
    #     theta = np.radians(-rotation)
    #
    #     # Figure out the unit vector with theta angle
    #     x, z = 0, 1
    #     dc, ds = np.cos(theta), np.sin(theta)
    #     xv = dc * x - ds * z
    #     zv = ds * x + dc * z
    #
    #     # Figure out the slope of the unit vector
    #     m = zv / xv
    #
    #     # y = mx + b
    #     # Calculate the x-intercept. using half the distance in the z-dimension as b. Since we want the axis of rotation in the middle
    #     offset = (-self.atlas_data.shape[0] / 2) / m
    #
    #     return abs(offset)


app = QApplication(sys.argv)
win = SliceView()
sys.exit(app.exec_())