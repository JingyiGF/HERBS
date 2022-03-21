from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore


class ToolBox(QObject):

    def __init__(self):
        QObject.__init__(self)

        # action version
        self.add_atlas = QAction(QIcon('icons/toolbar/atlas_icon.png'), 'Upload Waxholm Rat Brain Atlas', self)
        self.add_image_stack = QAction(QIcon('icons/toolbar/image_icon.svg'), 'upload histological image', self)

        self.vis2 = QAction(QIcon('icons/toolbar/two_window.png'), 'show 2 windows', self)
        self.vis4 = QAction(QIcon('icons/toolbar/window4.png'), 'show 4 windows', self)
        self.vis3 = QAction(QIcon('icons/toolbar/window3.png'), 'show 3 windows', self)

        self.toa_btn_off_icon = QIcon('icons/toolbar/toa.svg')
        self.toa_btn_on_icon = QIcon('icons/toolbar/toa_delete.svg')

        self.toh_btn_off_icon = QIcon('icons/toolbar/toh.svg')
        self.toh_btn_on_icon = QIcon('icons/toolbar/toh_delete.svg')

        self.toa_btn = QAction(QIcon('icons/toolbar/toa.svg'), 'transform to atlas slice window', self)
        self.toh_btn = QAction(QIcon('icons/toolbar/toh.svg'), 'transform to histologist image window', self)

        moving_btn = QAction(QIcon('icons/toolbar/moving.png'), 'move image 1px', self)
        moving_btn.setCheckable(True)

        rotation_btn = QAction(QIcon('icons/toolbar/rotation.svg'), 'rotate image 1°', self)
        rotation_btn.setCheckable(True)

        lasso_btn = QAction(QIcon('icons/toolbar/lasso.svg'), 'polygon lasso', self)
        lasso_btn.setCheckable(True)

        magic_wand_btn = QAction(QIcon('icons/toolbar/magic-wand.svg'), 'magic wand', self)
        magic_wand_btn.setCheckable(True)

        pencil_btn = QAction(QIcon('icons/toolbar/pencil.svg'), 'pencil', self)
        pencil_btn.setCheckable(True)

        eraser_btn = QAction(QIcon('icons/toolbar/eraser.svg'), 'eraser', self)
        eraser_btn.setCheckable(True)

        mask_btn = QAction(QIcon('icons/toolbar/mask.svg'), 'mask', self)
        mask_btn.setCheckable(True)

        line_btn = QAction(QIcon('icons/toolbar/line.svg'), 'line', self)
        line_btn.setCheckable(True)

        # anchor_btn = QAction(QIcon('icons/toolbar/gps.svg'), 'anchor', self)
        # anchor_btn.setCheckable(True)

        triang_btn = QAction(QIcon('icons/toolbar/triangulation.svg'), 'triangulation', self)
        triang_btn.setCheckable(True)

        loc_btn = QAction(QIcon('icons/toolbar/location.svg'), 'location', self)
        loc_btn.setCheckable(True)

        self.boundary_btn = QAction(QIcon('icons/toolbar/boundary.png'), 'draw boundary', self)
        self.transfer_btn = QAction(QIcon('icons/toolbar/trans.png'), 'transfer', self)
        self.check_btn = QAction(QIcon('icons/toolbar/check.svg'), 'accept projection', self)

        self.checkable_btn_dict = {'moving_btn': moving_btn,
                                   'rotation_btn': rotation_btn,
                                   'pencil_btn': pencil_btn,
                                   'eraser_btn': eraser_btn,
                                   'lasso_btn': lasso_btn,
                                   'magic_wand_btn': magic_wand_btn,
                                   'line_btn': line_btn,
                                   'triang_btn': triang_btn,
                                   'loc_btn': loc_btn}

        # for moving_btn, moving wrap
        self.left_button = QPushButton()
        # self.left_button.setStyleSheet(toolbox_bnt_style)
        self.left_button.setFocusPolicy(Qt.NoFocus)
        self.left_button.setIcon(QIcon('icons/toolbar/move_left.png'))
        self.right_button = QPushButton()
        self.right_button.setFocusPolicy(Qt.NoFocus)
        self.right_button.setIcon(QIcon('icons/toolbar/move_right.png'))
        self.up_button = QPushButton()
        self.up_button.setFocusPolicy(Qt.NoFocus)
        self.up_button.setIcon(QIcon('icons/toolbar/move_up.png'))
        self.down_button = QPushButton()
        self.down_button.setFocusPolicy(Qt.NoFocus)
        self.down_button.setIcon(QIcon('icons/toolbar/move_down.png'))

        self.moving_wrap = QFrame()
        moving_layout = QHBoxLayout(self.moving_wrap)
        moving_layout.setContentsMargins(0, 0, 0, 0)
        moving_layout.addWidget(self.left_button)
        moving_layout.addWidget(self.right_button)
        moving_layout.addWidget(self.up_button)
        moving_layout.addWidget(self.down_button)

        # for rotation_btn, rotation wrap
        self.rotation_slider = QSlider(Qt.Horizontal)
        self.rotation_slider.setFixedWidth(100)
        self.rotation_slider.setMinimum(-180)
        self.rotation_slider.setMaximum(180)
        self.rotation_slider.setValue(0)
        self.rotation_slider.valueChanged.connect(self.change_rotation_slider)

        self.rotation_valt = QLineEdit()
        self.rotation_valt.setFixedSize(50, 24)
        self.rotation_valt.setAlignment(Qt.AlignLeft)
        self.rotation_valt.setValidator(QIntValidator(-180, 180))
        self.rotation_valt.setText('0')
        self.rotation_valt.textChanged.connect(self.change_rotation_val)

        self.rotation_wrap = QFrame()
        rotation_layout = QHBoxLayout(self.rotation_wrap)
        rotation_layout.setContentsMargins(0, 0, 0, 0)
        rotation_layout.setSpacing(10)
        rotation_layout.addWidget(self.rotation_slider)
        rotation_layout.addWidget(self.rotation_valt)
        rotation_layout.addStretch(1)

        # for magic wand, magic wand wrap
        magic_tol_label = QLabel('Tolerance:')
        self.magic_tol_val = QLineEdit()
        self.magic_tol_val.setFixedWidth(40)
        # self.magic_tol_val.setAlignment(Qt.AlignLeft)
        self.magic_tol_val.setValidator(QIntValidator())
        self.magic_tol_val.setText('0')

        self.magic_wand_kernel = QComboBox()
        self.magic_wand_kernel.setFixedWidth(100)
        self.magic_wand_kernel.addItems(["Kernel", "Rectangular", "Elliptical", "Cross-shaped"])

        magic_wand_ksize_label = QLabel('Size:')
        self.magic_wand_ksize = QLineEdit()
        self.magic_wand_ksize.setFixedWidth(40)
        # self.magic_tol_val.setAlignment(Qt.AlignLeft)
        self.magic_wand_ksize.setValidator(QIntValidator())
        self.magic_wand_ksize.setText('0')

        # self.magic_wand_cb1 = QCheckBox('Anti Alias')
        # self.magic_wand_cb1.setStyleSheet('color: #d6d6d6;')
        # self.magic_wand_cb1.setChecked(True)
        # self.magic_wand_cb2 = QCheckBox('Contiguous')
        # self.magic_wand_cb2.setStyleSheet('color: #d6d6d6;')
        # self.magic_wand_cb2.setChecked(True)

        self.magic_wand_virus_register = QPushButton()
        self.magic_wand_virus_register.setFocusPolicy(Qt.NoFocus)
        self.magic_wand_virus_register.setIcon(QIcon('icons/toolbar/virus_register.svg'))
        self.magic_wand_virus_register.setIconSize(QSize(20, 20))
        self.magic_wand_bnd_register = QPushButton()
        self.magic_wand_bnd_register.setFocusPolicy(Qt.NoFocus)
        self.magic_wand_bnd_register.setIcon(QIcon('icons/toolbar/boundary_register.svg'))
        self.magic_wand_bnd_register.setIconSize(QSize(20, 20))

        self.magic_wand_wrap = QFrame()
        self.magic_wand_wrap.setFixedHeight(32)
        # self.magic_wand_wrap.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        magic_wand_layout = QHBoxLayout(self.magic_wand_wrap)
        magic_wand_layout.setContentsMargins(0, 0, 0, 0)
        magic_wand_layout.setSpacing(10)
        magic_wand_layout.addWidget(magic_tol_label)
        magic_wand_layout.addWidget(self.magic_tol_val)
        magic_wand_layout.addWidget(self.magic_wand_kernel)
        magic_wand_layout.addWidget(magic_wand_ksize_label)
        magic_wand_layout.addWidget(self.magic_wand_ksize)
        # magic_wand_layout.addWidget(self.magic_wand_cb1)
        # magic_wand_layout.addWidget(self.magic_wand_cb2)
        magic_wand_layout.addWidget(self.magic_wand_virus_register)
        magic_wand_layout.addWidget(self.magic_wand_bnd_register)
        magic_wand_layout.addStretch(1)
        # magic_wand_layout.insertStretch(1, -1)

        # for pencil_btn, pencil wrap
        pencil_size_label = QLabel('Size:')
        self.pencil_size_slider = QSlider(Qt.Horizontal)
        self.pencil_size_slider.setFixedWidth(100)
        self.pencil_size_slider.setMinimum(1)
        self.pencil_size_slider.setMaximum(30)
        self.pencil_size_slider.setValue(1)
        self.pencil_size_slider.valueChanged.connect(self.change_pencil_slider)

        self.pencil_size_valt = QLineEdit()
        self.pencil_size_valt.setFixedSize(50, 24)
        self.pencil_size_valt.setAlignment(Qt.AlignLeft)
        self.pencil_size_valt.setValidator(QIntValidator(1, 30))
        self.pencil_size_valt.setText('1')
        self.pencil_size_valt.textChanged.connect(self.change_pencil_val)

        self.pencil_wrap = QFrame()
        pencil_layout = QHBoxLayout(self.pencil_wrap)
        pencil_layout.setContentsMargins(0, 0, 0, 0)
        pencil_layout.setSpacing(10)
        pencil_layout.addWidget(pencil_size_label)
        pencil_layout.addWidget(self.pencil_size_slider)
        pencil_layout.addWidget(self.pencil_size_valt)
        pencil_layout.addStretch(1)

        # for eraser_btn, eraser wrap
        eraser_size_label = QLabel('Size:')
        self.eraser_size_slider = QSlider(Qt.Horizontal)
        self.eraser_size_slider.setFixedWidth(100)
        self.eraser_size_slider.setMinimum(1)
        self.eraser_size_slider.setMaximum(300)
        self.eraser_size_slider.setValue(20)
        self.eraser_size_slider.valueChanged.connect(self.change_eraser_slider)

        self.eraser_size_valt = QLineEdit()
        self.eraser_size_valt.setFixedSize(50, 24)
        self.eraser_size_valt.setAlignment(Qt.AlignLeft)
        self.eraser_size_valt.setValidator(QIntValidator(1, 100))
        self.eraser_size_valt.setText('1')
        self.eraser_size_valt.textChanged.connect(self.change_eraser_val)

        self.eraser_wrap = QFrame()
        eraser_layout = QHBoxLayout(self.eraser_wrap)
        eraser_layout.setContentsMargins(0, 0, 0, 0)
        eraser_layout.setSpacing(10)
        eraser_layout.addWidget(eraser_size_label)
        eraser_layout.addWidget(self.eraser_size_slider)
        eraser_layout.addWidget(self.eraser_size_valt)
        eraser_layout.addStretch(1)

        # for lasso_btn, lasso wrap
        lasso_color_label = QLabel('Color:')
        self.lasso_color_btn = pg.ColorButton()
        self.lasso_color_btn.setFixedSize(80, 24)

        self.lasso_wrap = QFrame()
        lasso_layout = QHBoxLayout(self.lasso_wrap)
        lasso_layout.setContentsMargins(0, 0, 0, 0)
        lasso_layout.setSpacing(10)
        lasso_layout.addWidget(lasso_color_label)
        lasso_layout.addWidget(self.lasso_color_btn)
        lasso_layout.addStretch(1)

        # mask wrap
        kernel_size_label = QLabel('Kernel Size: ')
        self.kernel_size_slider = QSlider(Qt.Horizontal)
        self.kernel_size_slider.setFixedWidth(100)
        self.kernel_size_slider.setMinimum(1)
        self.kernel_size_slider.setMaximum(50)
        self.kernel_size_slider.setValue(10)

        self.mask_wrap = QFrame()
        mask_layout = QHBoxLayout(self.mask_wrap)
        mask_layout.setContentsMargins(0, 0, 0, 0)
        mask_layout.setSpacing(10)
        mask_layout.addWidget(kernel_size_label)
        mask_layout.addWidget(self.kernel_size_slider)
        mask_layout.addStretch(1)

        # for line_btn, line wrap
        line_color_label = QLabel('Color:')
        self.line_color_btn = pg.ColorButton()
        self.line_color_btn.setFixedSize(80, 24)

        self.line_wrap = QFrame()
        line_layout = QHBoxLayout(self.line_wrap)
        line_layout.setContentsMargins(0, 0, 0, 0)
        line_layout.setSpacing(10)
        line_layout.addWidget(line_color_label)
        line_layout.addWidget(self.line_color_btn)
        line_layout.addStretch(1)

        # for triang_btn, triang wrap
        triang_color_label = QLabel('Color:')
        self.triang_color_btn = pg.ColorButton()
        self.triang_color_btn.setFixedSize(80, 24)
        bound_pnts_num_label = QLabel('Points Number:')
        self.bound_pnts_num = QLineEdit()
        self.bound_pnts_num.setFixedSize(50, 24)
        self.bound_pnts_num.setAlignment(Qt.AlignLeft)
        self.bound_pnts_num.setValidator(QIntValidator(2, 15))
        self.bound_pnts_num.setText('2')
        self.triang_vis_btn = QPushButton()
        self.triang_vis_btn.setCheckable(True)
        vis_icon = QIcon()
        vis_icon.addPixmap(QPixmap("icons/toolbar/eye.svg"), QIcon.Normal, QIcon.Off)
        vis_icon.addPixmap(QPixmap("icons/toolbar/eye_closed.svg"), QIcon.Normal, QIcon.On)
        self.triang_vis_btn.setIcon(vis_icon)
        self.triang_vis_btn.setIconSize(QSize(20, 20))
        self.triang_match_bnd = QPushButton()
        self.triang_match_bnd.setIcon(QIcon('icons/toolbar/matchbnd.svg'))
        self.triang_match_bnd.setIconSize(QSize(20, 20))

        self.triang_wrap = QFrame()
        self.triang_wrap.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        triang_layout = QHBoxLayout(self.triang_wrap)
        triang_layout.setContentsMargins(0, 0, 0, 0)
        triang_layout.setSpacing(10)
        triang_layout.addWidget(self.triang_vis_btn)
        triang_layout.addSpacing(10)
        triang_layout.addWidget(self.triang_match_bnd)
        triang_layout.addSpacing(10)
        triang_layout.addWidget(triang_color_label)
        triang_layout.addWidget(self.triang_color_btn)
        triang_layout.addSpacing(10)
        triang_layout.addWidget(bound_pnts_num_label)
        triang_layout.addWidget(self.bound_pnts_num)

        triang_layout.addStretch(1)

        # cell count wrap
        cell_count_label = QLabel('Count: ')
        self.cell_count_val = QLabel('0')
        self.cell_selector_btn = QPushButton()
        self.cell_selector_btn.setIcon(QIcon('icons/toolbar/cell_selecte.svg'))
        self.cell_selector_btn.setIconSize(QSize(20, 20))
        self.cell_aim_btn = QPushButton()
        self.cell_aim_btn.setIcon(QIcon('icons/toolbar/aim.svg'))
        self.cell_aim_btn.setIconSize(QSize(20, 20))
        self.cell_radar_btn = QPushButton()
        self.cell_radar_btn.setIcon(QIcon('icons/toolbar/radar.svg'))
        self.cell_radar_btn.setIconSize(QSize(20, 20))

        self.cell_count_wrap = QFrame()
        cell_layout = QHBoxLayout(self.cell_count_wrap)
        cell_layout.setContentsMargins(0, 0, 0, 0)
        cell_layout.setSpacing(10)
        cell_layout.addWidget(self.cell_selector_btn)
        cell_layout.addWidget(self.cell_aim_btn)
        cell_layout.addWidget(self.cell_radar_btn)
        cell_layout.addWidget(cell_count_label)
        cell_layout.addWidget(self.cell_count_val)
        cell_layout.addStretch(1)

        # separator
        self.sep_label = QLabel()
        self.sep_label.setPixmap(QPixmap('icons/toolbar/handle.png'))

        # circle
        angle = np.deg2rad(np.arange(0, 360, 1))
        x = np.cos(angle)
        y = np.sin(angle)
        self.original_circle = np.vstack([x, y]).T
        self.circle = self.original_circle.copy()

    def change_pencil_slider(self):
        val = self.pencil_size_slider.value()
        self.pencil_size_valt.setText(str(val))

    def change_pencil_val(self):
        val = int(self.pencil_size_valt.text())
        self.pencil_size_slider.setValue(val)

    def change_eraser_slider(self):
        val = self.eraser_size_slider.value()
        self.eraser_size_valt.setText(str(val))
        self.circle = self.original_circle * val

    def change_eraser_val(self):
        val = int(self.eraser_size_valt.text())
        self.eraser_size_slider.setValue(val)

    def change_rotation_val(self):
        val = int(self.rotation_valt.text())
        self.rotation_slider.setValue(val)

    def change_rotation_slider(self):
        val = self.rotation_slider.value()
        self.rotation_valt.setText(str(val))







