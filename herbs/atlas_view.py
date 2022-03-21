import os
import sys
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph.functions as fn
import pyqtgraph.opengl as gl
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize, QObject

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


atlas_rotation_gb_style = '''
QGroupBox {
    background-color: transparent; 
    border: 1px solid gray; 
    border-radius: 3px; 
    padding: 5px;  
    margin-top: 20px
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding-left: 10px;
    padding-right: 3px;
    padding-top: 10px;
}

'''

atlas_tab_spinbox_textedit_style = '''
QLineEdit { 
    background-color: #292929;
    border: 0px;
    color: white;
}
'''


class PageController(QWidget):
    class SignalProxy(QtCore.QObject):
        sigPageChanged = QtCore.Signal(object)  # id

    def __init__(self):
        self._sigprox = PageController.SignalProxy()
        self.sig_page_changed = self._sigprox.sigPageChanged

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


class SliceRotation(QWidget):

    class SignalProxy(QtCore.QObject):
        sigSliceRotated = QtCore.Signal(object)  # id

    def __init__(self):
        self._sigprox = SliceRotation.SignalProxy()
        self.sig_slice_rotated = self._sigprox.sigSliceRotated

        QWidget.__init__(self)

        self.h_slider = QSlider(QtCore.Qt.Horizontal)
        self.h_slider.valueChanged.connect(self.h_slider_changed)
        self.h_slider.setValue(0)
        self.h_slider.setRange(-900, 900)

        self.h_spinbox = QDoubleSpinBox()
        self.h_spinbox.lineEdit().setStyleSheet(atlas_tab_spinbox_textedit_style)
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

        self.v_spinbox = QDoubleSpinBox()
        self.v_spinbox.lineEdit().setStyleSheet(atlas_tab_spinbox_textedit_style)
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
        self.sig_slice_rotated.emit(np.deg2rad([self.h_spinbox.value(), self.v_spinbox.value()]))

    def v_slider_changed(self):
        val = self.v_slider.value() / 20
        self.v_spinbox.setValue(val)

    def v_spinbox_changed(self):
        val = int(self.v_spinbox.value() * 20)
        self.v_slider.setValue(val)
        self.sig_slice_rotated.emit(np.deg2rad([self.h_spinbox.value(), self.v_spinbox.value()]))


class ImageLabel(QWidget):
    def __init__(self, img, title):
        super(QWidget, self).__init__()
        layout = QHBoxLayout(self)
        self.label3 = QLabel(self)
        self.title = QLabel(title)
        self.pixmap = QPixmap(img)
        self.pixmap = self.pixmap.scaled(QSize(20, 10))
        self.label3.setPixmap(self.pixmap)
        self.label3.setAlignment(Qt.AlignCenter)
        self.title.setMinimumHeight(self.pixmap.height())
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label3)
        layout.addWidget(self.title)
        self.label3.setStyleSheet("""
            background-color: transparent;
        """)
        self.title.setStyleSheet("""
            background-color: transparent;
            color: black;
            padding: 0px 3px 0px 0px;
        """)
        layout.setSpacing(0)
        layout.addStretch()


class AtlasView(QObject):
    """
    A collection of user interface elements bound together:


    """
    def __init__(self):
        super(AtlasView, self).__init__()
        QObject.__init__(self)
        self.atlas_data = None
        self.atlas_label = None
        self.atlas_info = None
        self.label_info = None
        self.atlas_contour = None
        self.atlas_boundary = None
        self.slice_size = None

        self.working_atlas = None
        self.working_page_control = None
        self.label_level = None

        self.side_lines = None
        self.corner_points = None

        self.current_coronal_index = None
        self.current_sagital_index = None
        self.current_horizontal_index = None

        self.display_atlas = None
        self.display_label = None
        self.scale = None
        self.interpolate = True
        self.oy_vector = np.array([0, 1, 0])
        self.oz_vector = np.array([0, 0, 1])
        self.ox_vector = np.array([1, 0, 0])

        self.cimg = SliceStacks()  # ap - coronal
        self.cproxy = pg.SignalProxy(self.cimg.vb.scene().sigMouseMoved, rateLimit=60, slot=self.coronal_crosshair)
        self.cpage_ctrl = PageController()
        self.cpage_ctrl.sig_page_changed.connect(self.coronal_slice_page_changed)
        self.clut = pg.HistogramLUTWidget()
        self.clut.setImageItem(self.cimg.img)

        self.simg = SliceStacks()
        self.sproxy = pg.SignalProxy(self.simg.vb.scene().sigMouseMoved, rateLimit=60, slot=self.sagital_crosshair)
        self.spage_ctrl = PageController()
        self.spage_ctrl.sig_page_changed.connect(self.sagital_slice_page_changed)
        self.slut = pg.HistogramLUTWidget()
        self.slut.setImageItem(self.simg.img)

        # self.scimg = SliceStacks()
        # self.sproxy = pg.SignalProxy(self.scimg.vb.scene().sigMouseMoved, rateLimit=60, slot=self.sagital_crosshair)
        # # self.scpage_ctrl = PageController()
        # # self.scpage_ctrl.sig_page_changed.connect(self.sagital_copy_slice_page_changed)
        # self.sclut = pg.HistogramLUTWidget()
        # self.sclut.setImageItem(self.scimg.img)


        self.himg = SliceStacks()
        self.hproxy = pg.SignalProxy(self.himg.vb.scene().sigMouseMoved, rateLimit=60, slot=self.horizontal_crosshair)
        self.hpage_ctrl = PageController()
        self.hpage_ctrl.sig_page_changed.connect(self.horizontal_slice_page_changed)
        self.hlut = pg.HistogramLUTWidget()
        self.hlut.setImageItem(self.himg.img)

        self.label_tree = LabelTree()
        # self.label_tree.labels_changed.connect(self.labels_changed)


        # self.working_cut_changed('coronal')

        # radio buttons
        self.radio_group = QFrame()
        self.radio_group.setFixedHeight(50)
        self.radio_group.setStyleSheet('QFrame{border: 1px solid gray; border-radius: 3px}')
        radio_group_layout = QHBoxLayout(self.radio_group)
        radio_group_layout.setContentsMargins(0, 0, 0, 0)
        self.section_rabnt1 = QRadioButton('Coronal')
        self.section_rabnt1.setChecked(True)
        self.section_rabnt2 = QRadioButton('Sagital')
        self.section_rabnt3 = QRadioButton('Horizontal')
        radio_group_layout.addWidget(self.section_rabnt1)
        radio_group_layout.addWidget(self.section_rabnt2)
        radio_group_layout.addWidget(self.section_rabnt3)

        # angles
        self.crotation_ctrl = SliceRotation()
        # self.crotation_ctrl.sig_slice_rotated.connect(self.coronal_slice_rotated)
        self.srotation_ctrl = SliceRotation()
        # self.srotation_ctrl.sig_slice_rotated.connect(self.sagital_slice_rotated)
        self.hrotation_ctrl = SliceRotation()
        # self.hrotation_ctrl.sig_slice_rotated.connect(self.horizontal_slice_rotated)


        # opacity
        atlas_op_label = QLabel('Opacity: ')
        self.atlas_op_slider = QSlider(QtCore.Qt.Horizontal)
        self.atlas_op_slider.setValue(100)
        self.atlas_op_slider.setMinimum(0)
        self.atlas_op_slider.setMaximum(100)
        # self.atlas_op_slider.valueChanged.connect(self.sig_rescale_slider)

        self.atlas_op_spinbox = QDoubleSpinBox()
        self.atlas_op_spinbox.lineEdit().setStyleSheet(atlas_tab_spinbox_textedit_style)
        self.atlas_op_spinbox.setValue(1)
        self.atlas_op_spinbox.setRange(0, 1)
        self.atlas_op_spinbox.setSingleStep(0.05)
        self.atlas_op_spinbox.setMinimumSize(50, 20)
        self.atlas_op_spinbox.valueChanged.connect(self.opacity_changed)

        opacity_wrap = QFrame()
        opacity_layout = QHBoxLayout(opacity_wrap)
        opacity_layout.setSpacing(2)
        opacity_layout.setContentsMargins(0, 0, 0, 0)
        opacity_layout.addWidget(atlas_op_label)
        opacity_layout.addWidget(self.atlas_op_slider)
        opacity_layout.addWidget(self.atlas_op_spinbox)

        # boundary
        self.show_boundary_btn = QPushButton('Show Boundary')
        self.show_boundary_btn.setCheckable(True)

        #
        self.navigation_btn = QPushButton('Navigation')
        self.navigation_btn.setCheckable(True)
        self.navigation_btn.clicked.connect(self.navigation_btn_clicked)

        # coronal section control
        coronal_rotation_wrap = QGroupBox('Coronal Section')
        coronal_rotation_wrap.setStyleSheet(atlas_rotation_gb_style)
        coronal_wrap_layout = QGridLayout(coronal_rotation_wrap)
        coronal_wrap_layout.setContentsMargins(0, 0, 0, 0)

        c_section_label_img = QPixmap('icons/c_section.png')
        c_section_label_img = c_section_label_img.scaled(QSize(40, 40))
        c_section_label = QLabel('Tilt Z: ')
        c_section_label.setPixmap(c_section_label_img)

        c_lr_label = QLabel()
        c_lr_label.setPixmap(QPixmap('icons/rotate_left_right.png').scaled(QSize(15, 15)))
        c_ud_label = QLabel()
        c_ud_label.setPixmap(QPixmap('icons/rotate_up_down.png').scaled(QSize(15, 15)))

        coronal_wrap_layout.addWidget(c_section_label, 0, 0, 2, 1)
        coronal_wrap_layout.addWidget(c_lr_label, 0, 1, 1, 1)
        coronal_wrap_layout.addWidget(self.crotation_ctrl.h_slider, 0, 2, 1, 1)
        coronal_wrap_layout.addWidget(self.crotation_ctrl.h_spinbox, 0, 3, 1, 1)
        coronal_wrap_layout.addWidget(c_ud_label, 1, 1, 1, 1)
        coronal_wrap_layout.addWidget(self.crotation_ctrl.v_slider, 1, 2, 1, 1)
        coronal_wrap_layout.addWidget(self.crotation_ctrl.v_spinbox, 1, 3, 1, 1)

        # sagital section control
        sagital_rotation_wrap = QGroupBox('Sagital Section')
        sagital_rotation_wrap.setStyleSheet(atlas_rotation_gb_style)
        sagital_wrap_layout = QGridLayout(sagital_rotation_wrap)
        sagital_wrap_layout.setContentsMargins(0, 0, 0, 0)

        s_section_label_img = QPixmap('icons/s_section.png')
        s_section_label_img = s_section_label_img.scaled(QSize(40, 40))
        s_section_label = QLabel()
        s_section_label.setPixmap(s_section_label_img)

        s_lr_label = QLabel()
        s_lr_label.setPixmap(QPixmap('icons/rotate_left_right.png').scaled(QSize(15, 15)))
        s_ud_label = QLabel()
        s_ud_label.setPixmap(QPixmap('icons/rotate_up_down.png').scaled(QSize(15, 15)))

        sagital_wrap_layout.addWidget(s_section_label, 0, 0, 2, 1)
        sagital_wrap_layout.addWidget(s_lr_label, 0, 1, 1, 1)
        sagital_wrap_layout.addWidget(self.srotation_ctrl.h_slider, 0, 2, 1, 1)
        sagital_wrap_layout.addWidget(self.srotation_ctrl.h_spinbox, 0, 3, 1, 1)
        sagital_wrap_layout.addWidget(s_ud_label, 1, 1, 1, 1)
        sagital_wrap_layout.addWidget(self.srotation_ctrl.v_slider, 1, 2, 1, 1)
        sagital_wrap_layout.addWidget(self.srotation_ctrl.v_spinbox, 1, 3, 1, 1)

        # horizontal section control
        horizontal_rotation_wrap = QGroupBox('Horizontal Section')
        horizontal_rotation_wrap.setStyleSheet(atlas_rotation_gb_style)
        horizontal_wrap_layout = QGridLayout(horizontal_rotation_wrap)
        horizontal_wrap_layout.setContentsMargins(0, 0, 0, 0)

        h_section_label_img = QPixmap('icons/h_section.png')
        h_section_label_img = h_section_label_img.scaled(QSize(40, 40))
        h_section_label = QLabel()
        h_section_label.setPixmap(h_section_label_img)

        h_lr_label = QLabel()
        h_lr_label.setPixmap(QPixmap('icons/rotate_left_right.png').scaled(QSize(15, 15)))
        h_ud_label = QLabel()
        h_ud_label.setPixmap(QPixmap('icons/rotate_up_down.png').scaled(QSize(15, 15)))

        horizontal_wrap_layout.addWidget(h_section_label, 0, 0, 2, 1)
        horizontal_wrap_layout.addWidget(h_lr_label, 0, 1, 1, 1)
        horizontal_wrap_layout.addWidget(self.hrotation_ctrl.h_slider, 0, 2, 1, 1)
        horizontal_wrap_layout.addWidget(self.hrotation_ctrl.h_spinbox, 0, 3, 1, 1)
        horizontal_wrap_layout.addWidget(h_ud_label, 1, 1, 1, 1)
        horizontal_wrap_layout.addWidget(self.hrotation_ctrl.v_slider, 1, 2, 1, 1)
        horizontal_wrap_layout.addWidget(self.hrotation_ctrl.v_spinbox, 1, 3, 1, 1)

        self.sidebar_wrap = QFrame()
        sidebar_wrap_layout = QVBoxLayout(self.sidebar_wrap)
        sidebar_wrap_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_wrap_layout.setSpacing(10)
        sidebar_wrap_layout.addWidget(self.radio_group)
        sidebar_wrap_layout.addWidget(opacity_wrap)
        sidebar_wrap_layout.addWidget(self.show_boundary_btn)
        sidebar_wrap_layout.addWidget(coronal_rotation_wrap)
        sidebar_wrap_layout.addWidget(sagital_rotation_wrap)
        sidebar_wrap_layout.addWidget(horizontal_rotation_wrap)
        sidebar_wrap_layout.addWidget(self.navigation_btn)

        # 3d things
        self.plate_color = [0.5, 0.5, 0.5, 0.2]
        self.ap_plate_verts = np.array([[-1, 0, -2.5], [-1, 0, 0.5], [1, 0, 0.5], [1, 0, -2.5]]) * 80
        self.ap_plate_faces = np.array([[0, 1, 2], [0, 2, 3]])
        self.ap_plate_md = gl.MeshData(vertexes=self.ap_plate_verts, faces=self.ap_plate_faces)
        self.ap_plate_mesh = gl.GLMeshItem(meshdata=self.ap_plate_md, smooth=False, color=self.plate_color)
        self.ap_plate_mesh.setGLOptions('additive')

        self.dv_plate_verts = np.array([[-1, -4.5, 0], [-1, 2, 0], [1, 2, 0], [1, -4.5, 0]]) * 80
        self.dv_plate_faces = np.array([[0, 1, 2], [0, 2, 3]])
        self.dv_plate_md = gl.MeshData(vertexes=self.dv_plate_verts, faces=self.dv_plate_faces)
        self.dv_plate_mesh = gl.GLMeshItem(meshdata=self.dv_plate_md, smooth=False, color=self.plate_color)
        self.dv_plate_mesh.setGLOptions('additive')

        self.ml_plate_verts = np.array([[0, -4.5, -2.5], [0, 2, -2.5], [0, 2, 0.5], [0, -4.5, 0.5]]) * 80
        self.ml_plate_faces = np.array([[0, 1, 2], [0, 2, 3]])
        self.ml_plate_md = gl.MeshData(vertexes=self.ml_plate_verts, faces=self.ml_plate_faces)
        self.ml_plate_mesh = gl.GLMeshItem(meshdata=self.ml_plate_md, smooth=False, color=self.plate_color)
        self.ml_plate_mesh.setGLOptions('additive')

        self.axis = gl.GLAxisItem()
        self.axis.setSize(20, 40, 5)

        self.grid = gl.GLGridItem()
        self.grid.scale(2, 2, 1)


        self.mesh = gl.GLMeshItem(smooth=True, color=[0.5, 0.5, 0.5, 0.2], shader='balloon')
        self.mesh.setGLOptions('additive')

        # self.lut.sigLookupTableChanged.connect(self.histlut_changed)
        # self.lut.sigLevelsChanged.connect(self.histlut_changed)

    def set_data(self, atlas_data, atlas_label, atlas_info, label_info, boundaries):
        self.atlas_data = atlas_data
        self.atlas_label = atlas_label
        self.label_info = label_info
        self.atlas_boundary = boundaries
        self.label_tree.set_labels(label_info)

        self.atlas_size = self.atlas_data.shape
        self.anterior_info = atlas_info[0]
        self.dorsal_info = atlas_info[1]
        self.right_info = atlas_info[2]
        self.vxsize_um = atlas_info[3]['vxsize']
        inverse_b2 = self.atlas_size[0] - atlas_info[3]['Bregma'][2]
        self.Bregma = (inverse_b2, atlas_info[3]['Bregma'][0], atlas_info[3]['Bregma'][1])
        inverse_l2 = self.atlas_size[0] - atlas_info[3]['Lambda'][2]
        self.Lambda = (inverse_l2, atlas_info[3]['Lambda'][0], atlas_info[3]['Lambda'][1])

        self.current_coronal_index = self.Bregma[2]
        self.current_sagital_index = self.Bregma[1]
        self.current_horizontal_index = self.Bregma[0]
        print(atlas_info[3]['Bregma'])
        print(self.Bregma)

        self.cpage_ctrl.set_max(self.atlas_size[2] - 1)
        self.cpage_ctrl.set_val(self.current_coronal_index)
        self.spage_ctrl.set_max(self.atlas_size[1] - 1)
        self.spage_ctrl.set_val(self.current_sagital_index)
        # self.scpage_ctrl.set_max(self.atlas_size[1] - 1)
        # self.scpage_ctrl.set_val(self.current_sagital_index)
        self.hpage_ctrl.set_max(self.atlas_size[0] - 1)
        self.hpage_ctrl.set_val(self.current_horizontal_index)

        self.cimg.label_img.setLevels(levels=[0, self.label_tree.label_level])
        self.simg.label_img.setLevels(levels=[0, self.label_tree.label_level])
        self.himg.label_img.setLevels(levels=[0, self.label_tree.label_level])
        # self.scimg.label_img.setLevels(levels=[0, self.label_tree.label_level])

        lut = self.label_tree.lookup_table()
        # self.scimg.label_img.setLookupTable(lut=lut)
        self.cimg.label_img.setLookupTable(lut=lut)
        self.simg.label_img.setLookupTable(lut=lut)
        self.himg.label_img.setLookupTable(lut=lut)

    def working_cut_changed(self, atlas_display):
        if atlas_display == "coronal":
            self.working_atlas = self.cimg
            self.working_page_control = self.cpage_ctrl
            self.slice_tb_size = (80, 80)
        elif atlas_display == "sagital":
            self.working_atlas = self.simg
            self.working_page_control = self.spage_ctrl
            self.slice_tb_size = (40, 80)
        else:
            self.working_atlas = self.himg
            self.working_page_control = self.hpage_ctrl
            self.slice_tb_size = (80, 40)
        self.slice_size = self.working_atlas.label_img.image.shape[:2]
        rect = (0, 0, self.slice_size[1], self.slice_size[0])
        self.corner_points, self.side_lines = get_corner_line_from_rect(rect)
        self.working_atlas.tri_pnts.set_range(x_range=self.slice_size[1] - 1, y_range=self.slice_size[0] - 1)

    def navigation_btn_clicked(self):
        if self.navigation_btn.isChecked():
            self.cimg.v_line.setVisible(True)
            self.cimg.h_line.setVisible(True)
            self.himg.v_line.setVisible(True)
            self.himg.h_line.setVisible(True)
            # self.scimg.v_line.setVisible(True)
            # self.scimg.h_line.setVisible(True)
            self.simg.v_line.setVisible(True)
            self.simg.h_line.setVisible(True)
        else:
            self.cimg.v_line.setVisible(False)
            self.cimg.h_line.setVisible(False)
            self.himg.v_line.setVisible(False)
            self.himg.h_line.setVisible(False)
            # self.scimg.v_line.setVisible(False)
            # self.scimg.h_line.setVisible(False)
            self.simg.v_line.setVisible(False)
            self.simg.h_line.setVisible(False)

    def coronal_crosshair(self, evt):
        if self.radio_group.isVisible():
            return
        if self.navigation_btn.isChecked():
            pos = evt[0]
            if self.cimg.vb.sceneBoundingRect().contains(pos):
                mouse_point = self.cimg.vb.mapSceneToView(pos)
                da_pos = [int(mouse_point.x()), int(mouse_point.y())]
                self.cimg.v_line.setPos(da_pos[0])
                self.cimg.h_line.setPos(da_pos[1])
                self.scimg.v_line.setPos(self.current_coronal_index)
                self.scimg.h_line.setPos(da_pos[1])
                self.himg.v_line.setPos(da_pos[0])
                self.himg.h_line.setPos(self.current_coronal_index)

                self.scpage_ctrl.set_val(da_pos[0])
                self.hpage_ctrl.set_val(da_pos[1])

    def sagital_crosshair(self, evt):
        if self.radio_group.isVisible():
            return
        if self.navigation_btn.isChecked():
            pos = evt[0]
            if self.scimg.vb.sceneBoundingRect().contains(pos):
                mouse_point = self.scimg.vb.mapSceneToView(pos)
                da_pos = [int(mouse_point.x()), int(mouse_point.y())]
                self.scimg.v_line.setPos(da_pos[0])
                self.scimg.h_line.setPos(da_pos[1])
                self.cimg.v_line.setPos(self.current_sagital_index)
                self.cimg.h_line.setPos(da_pos[1])
                self.himg.v_line.setPos(self.current_sagital_index)
                self.himg.h_line.setPos(da_pos[0])

                self.cpage_ctrl.set_val(da_pos[0])
                self.hpage_ctrl.set_val(da_pos[1])

    def horizontal_crosshair(self, evt):
        if self.radio_group.isVisible():
            return
        if self.navigation_btn.isChecked():
            pos = evt[0]
            if self.himg.vb.sceneBoundingRect().contains(pos):
                mouse_point = self.himg.vb.mapSceneToView(pos)
                da_pos = [int(mouse_point.x()), int(mouse_point.y())]
                self.himg.v_line.setPos(da_pos[0])
                self.himg.h_line.setPos(da_pos[1])
                self.cimg.v_line.setPos(da_pos[0])
                self.cimg.h_line.setPos(self.current_horizontal_index)
                self.scimg.v_line.setPos(da_pos[1])
                self.scimg.h_line.setPos(self.current_horizontal_index)

                self.cpage_ctrl.set_val(da_pos[1])
                self.scpage_ctrl.set_val(da_pos[0])

    def opacity_changed(self):
        val = self.atlas_op_spinbox.value()
        self.cimg.label_img.setOpts(opacity=val)
        self.simg.label_img.setOpts(opacity=val)
        # self.scimg.label_img.setOpts(opacity=val)
        self.himg.label_img.setOpts(opacity=val)

    # slice number changed
    def coronal_slice_page_changed(self, page_number):
        self.crotation_ctrl.h_spinbox.setValue(0)
        self.crotation_ctrl.v_spinbox.setValue(0)
        if self.atlas_data is None or self.atlas_label is None:
            return
        self.current_coronal_index = page_number
        da_atlas_slice = self.atlas_data[:, :, page_number]
        da_atlas_label = self.atlas_label[:, :, page_number]
        da_atlas_contour = self.atlas_boundary['c_contour'][:, :, page_number]
        self.cimg.set_data(da_atlas_slice, da_atlas_label, da_atlas_contour, scale=None)

        slide_dist = (page_number - self.Bregma[2]) / 2
        ap_plate_verts = self.ap_plate_verts + np.array([0, slide_dist, 0])
        ap_plate_md = gl.MeshData(vertexes=ap_plate_verts, faces=self.ap_plate_faces)
        self.ap_plate_mesh.setMeshData(meshdata=ap_plate_md)

    def sagital_slice_page_changed(self, page_number):
        self.srotation_ctrl.h_spinbox.setValue(0)
        self.srotation_ctrl.v_spinbox.setValue(0)
        # self.scpage_ctrl.set_val(page_number)
        if self.atlas_data is None or self.atlas_label is None:
            return
        self.current_sagital_index = page_number
        print(self.current_sagital_index)
        da_atlas_slice = self.atlas_data[:, page_number, :]
        da_atlas_label = self.atlas_label[:, page_number, :]
        da_atlas_contour = self.atlas_boundary['s_contour'][:, page_number, :]
        self.simg.set_data(da_atlas_slice, da_atlas_label, da_atlas_contour, scale=None)
        # self.scimg.set_data(da_atlas_slice, da_atlas_label, da_atlas_contour, scale=None)
        # if self.scpage_ctrl.page_slider.value() != page_number:
        #     self.scpage_ctrl.set_val(page_number)

        slide_dist = (page_number - self.Bregma[1]) / 2
        ml_plate_verts = self.ml_plate_verts + np.array([slide_dist, 0, 0])
        ml_plate_md = gl.MeshData(vertexes=ml_plate_verts, faces=self.ml_plate_faces)
        self.ml_plate_mesh.setMeshData(meshdata=ml_plate_md)

    # def sagital_copy_slice_page_changed(self, page_number):
    #     if self.atlas_data is None or self.atlas_label is None:
    #         return
    #     da_atlas_slice = self.atlas_data[:, page_number, :]
    #     da_atlas_label = self.atlas_label[:, page_number, :]
    #     da_atlas_contour = self.atlas_boundary['s_contour'][:, page_number, :]
    #     self.scimg.set_data(da_atlas_slice, da_atlas_label, da_atlas_contour, scale=None)
    #     self.spage_ctrl.set_val(page_number)

    def horizontal_slice_page_changed(self, page_number):
        self.hrotation_ctrl.h_spinbox.setValue(0)
        self.hrotation_ctrl.v_spinbox.setValue(0)
        if self.atlas_data is None or self.atlas_label is None:
            return
        self.current_horizontal_index = page_number
        da_atlas_slice = self.atlas_data[page_number, :, :]
        da_atlas_label = self.atlas_label[page_number, :, :]
        da_atlas_contour = self.atlas_boundary['h_contour'][page_number, :, :]
        self.himg.set_data(da_atlas_slice, da_atlas_label, da_atlas_contour, scale=None)

        slide_dist = (page_number - self.Bregma[0]) / 2
        dv_plate_verts = self.dv_plate_verts + np.array([0, 0, slide_dist])
        dv_plate_md = gl.MeshData(vertexes=dv_plate_verts, faces=self.dv_plate_faces)
        self.dv_plate_mesh.setMeshData(meshdata=dv_plate_md)

    def coronal_slice_rotated(self, radians):
        if self.atlas_data is None or self.atlas_label is None or np.all(np.ravel(radians) == 0):
            return

        z_angle = radians[0]
        x_angle = radians[1]
        rotm = np.dot(rotation_z(z_angle), rotation_x(x_angle))

        o_val = np.array([0, self.current_coronal_index, 0])
        o_rot = np.array([256, self.current_coronal_index, 256])

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

        slide_dist = (self.current_coronal_index - self.atlas_info[3]['Bregma'][1]) / 2
        ap_plate_verts = self.ap_plate_verts + np.array([0, slide_dist, 0])
        origin = np.array([0, slide_dist, 0])
        ap_plate_verts = np.dot(rotm, (ap_plate_verts - origin).T).T + origin
        ap_plate_md = gl.MeshData(vertexes=ap_plate_verts, faces=self.ap_plate_faces)
        self.ap_plate_mesh.setMeshData(meshdata=ap_plate_md)

    def sagital_slice_rotated(self, radians):
        if self.atlas_data is None or self.atlas_label is None or np.all(np.ravel(radians) == 0):
            return
        z_angle = radians[0]
        y_angle = radians[1]
        rotm = np.dot(rotation_z(z_angle), rotation_y(y_angle))


        o_val = np.array([self.current_sagital_index, 0, 0])
        o_rot = np.array([self.current_sagital_index, 512, 256])

        oz_vector = np.dot(rotm, np.array([0, 0, 1]))
        oy_vector = np.dot(rotm, np.array([0, 1, 0]))

        oval_new = o_rot + np.dot(rotm, o_val - o_rot)

        oy_length = 1024
        oz_length = 512

        atlas = fn.affineSlice(self.atlas_data, shape=(oy_length, oz_length), vectors=[oy_vector, oz_vector],
                               origin=(oval_new[0], oval_new[1], oval_new[2]), axes=(0, 1, 2), order=1)
        label = fn.affineSlice(self.atlas_label, shape=(oy_length, oz_length), vectors=[oy_vector, oz_vector],
                               origin=(oval_new[0], oval_new[1], oval_new[2]), axes=(0, 1, 2), order=0)

        self.simg.set_data(atlas, label, scale=None)
        self.scimg.set_data(atlas, label, scale=None)

        slide_dist = (self.current_sagital_index - self.atlas_info[3]['Bregma'][0]) / 2
        ml_plate_verts = self.ml_plate_verts + np.array([slide_dist, 0, 0])
        origin = np.array([slide_dist, 0, 0])
        ml_plate_verts = np.dot(rotm, (ml_plate_verts - origin).T).T + origin
        ml_plate_md = gl.MeshData(vertexes=ml_plate_verts, faces=self.ml_plate_faces)
        self.ml_plate_mesh.setMeshData(meshdata=ml_plate_md)

    def horizontal_slice_rotated(self, radians):
        if self.atlas_data is None or self.atlas_label is None or np.all(np.ravel(radians) == 0):
            return
        x_angle = radians[1]
        y_angle = radians[0]
        rotm = np.dot(rotation_y(y_angle), rotation_x(x_angle))

        o_val = np.array([0, 0, self.current_horizontal_index])
        o_rot = np.array([256, 512, self.current_horizontal_index])

        ox_vector = np.dot(rotm, np.array([1, 0, 0]))
        oy_vector = np.dot(rotm, np.array([0, 1, 0]))

        oval_new = o_rot + np.dot(rotm, o_val - o_rot)

        oy_length = 1024
        ox_length = 512

        atlas = fn.affineSlice(self.atlas_data, shape=(ox_length, oy_length), vectors=[ox_vector, oy_vector],
                               origin=(oval_new[0], oval_new[1], oval_new[2]), axes=(0, 1, 2), order=1)
        label = fn.affineSlice(self.atlas_label, shape=(ox_length, oy_length), vectors=[ox_vector, oy_vector],
                               origin=(oval_new[0], oval_new[1], oval_new[2]), axes=(0, 1, 2), order=0)

        self.himg.set_data(atlas, label, scale=None)

        slide_dist = (self.current_horizontal_index - self.atlas_info[3]['Bregma'][2]) / 2
        dv_plate_verts = self.dv_plate_verts + np.array([0, 0, slide_dist])
        origin = np.array([0, 0, slide_dist])
        dv_plate_verts = np.dot(rotm, (dv_plate_verts - origin).T).T + origin
        dv_plate_md = gl.MeshData(vertexes=dv_plate_verts, faces=self.dv_plate_faces)
        self.dv_plate_mesh.setMeshData(meshdata=dv_plate_md)





    # def labels_changed(self):
    #     # reapply label colors
    #     lut = self.label_tree.lookup_table()
    #     self.scimg.label_img.setImage(lut=lut)
    #     self.cimg.label_img.setImage(lut=lut)
    #     self.simg.label_img.setImage(lut=lut)
    #     self.himg.label_img.setImage(lut=lut)
    #     self.sig_label_changed.emit(lut)

    # def labels_changed(self):
    #     # reapply label colors
    #     lut = self.acontrols.atlas_view.label_tree.lookup_table()
    #     self.acontrols.atlas_view.simg_copy.label_img.setImage(lut=lut)
    #     self.acontrols.atlas_view.cimg.label_img.setImage(lut=lut)
    #     self.acontrols.atlas_view.simg.label_img.setImage(lut=lut)
    #     self.acontrols.atlas_view.himg.label_img.setImage(lut=lut)
    #     # self.sig_label_changed.emit(lut)
    #     check_id = list(self.acontrols.atlas_view.label_tree.checked())
    #     if len(self.working_mesh) != 0:
    #         for i in range(len(self.working_mesh)):
    #             self.view3d.removeItem(self.working_mesh[i])
    #
    #     for i in range(len(check_id)):
    #         id = check_id[i]
    #         self.working_mesh[i] = self.small_mesh_list[str(id)]
    #
    #         self.view3d.addItem(self.working_mesh[i])


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
