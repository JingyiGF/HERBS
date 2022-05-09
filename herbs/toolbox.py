from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore


toolbar_spinbox_textedit_style = '''
QLineEdit { 
    background-color: #292929;
    border: 0px;
    color: white;
}
'''


class ToolBox(QObject):

    def __init__(self):
        QObject.__init__(self)

        self.moving_px = 0
        self.base_lut = np.array([[0, 0, 0, 0], [128, 128, 128, 255]])

        self.pencil_mask = np.ones((3, 3), 'uint8')

        # action version
        self.add_atlas = QAction(QIcon('icons/toolbar/atlas_icon.png'), 'Upload Waxholm Rat Brain Atlas', self)
        self.add_image_stack = QAction(QIcon('icons/toolbar/image_icon.svg'), 'upload histological image', self)

        self.vis2 = QAction(QIcon( 'icons/toolbar/two_window.png'), 'show 2 windows', self)
        self.vis4 = QAction(QIcon('icons/toolbar/window4.png'), 'show 4 windows', self)
        self.vis3 = QAction(QIcon('icons/toolbar/window3.png'), 'show 3 windows', self)

        self.toa_btn_off_icon = QIcon('icons/toolbar/toa.svg')
        self.toa_btn_on_icon = QIcon('icons/toolbar/toa_delete.svg')

        self.toh_btn_off_icon = QIcon('icons/toolbar/toh.svg')
        self.toh_btn_on_icon = QIcon('icons/toolbar/toh_delete.svg')

        self.toa_btn = QAction(QIcon('icons/toolbar/toa.svg'), 'transform to atlas slice window', self)
        self.toh_btn = QAction(QIcon('icons/toolbar/toh.svg'), 'transform to histologist image window', self)
        self.check_btn = QAction(QIcon('icons/toolbar/accept.svg'), 'accept transformation', self)

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

        probe_btn = QAction(QIcon('icons/toolbar/probe.svg'), 'probe', self)
        probe_btn.setCheckable(True)

        # anchor_btn = QAction(QIcon('icons/toolbar/gps.svg'), 'anchor', self)
        # anchor_btn.setCheckable(True)

        triang_btn = QAction(QIcon('icons/toolbar/triangulation.svg'), 'triangulation', self)
        triang_btn.setCheckable(True)

        loc_btn = QAction(QIcon('icons/toolbar/location.svg'), 'location', self)
        loc_btn.setCheckable(True)

        self.checkable_btn_dict = {'pencil_btn': pencil_btn,
                                   'eraser_btn': eraser_btn,
                                   'lasso_btn': lasso_btn,
                                   'magic_wand_btn': magic_wand_btn,
                                   'probe_btn': probe_btn,
                                   'triang_btn': triang_btn,
                                   'loc_btn': loc_btn}

        # 'moving_btn': moving_btn,
        # 'rotation_btn': rotation_btn,

        self.toolbox_btn_keys = list(self.checkable_btn_dict.keys())

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
        self.moving_valt = QSpinBox()
        self.moving_valt.lineEdit().setStyleSheet(toolbar_spinbox_textedit_style)
        self.moving_valt.setFixedSize(80, 22)
        self.moving_valt.setAlignment(Qt.AlignLeft)
        self.moving_valt.setRange(0, 50)
        self.moving_valt.setSingleStep(1)
        self.moving_valt.setValue(0)
        self.moving_valt.valueChanged.connect(self.moving_dist_changed)

        self.moving_wrap = QFrame()
        moving_layout = QHBoxLayout(self.moving_wrap)
        moving_layout.setAlignment(Qt.AlignVCenter)
        moving_layout.setContentsMargins(0, 0, 0, 0)
        moving_layout.addWidget(self.left_button)
        moving_layout.addWidget(self.right_button)
        moving_layout.addWidget(self.up_button)
        moving_layout.addWidget(self.down_button)
        moving_layout.addWidget(self.moving_valt)

        # for rotation_btn, rotation wrap
        rotation_label = QLabel("Angle: ")
        self.rotation_slider = QSlider(Qt.Horizontal)
        self.rotation_slider.setFixedWidth(200)
        self.rotation_slider.setMinimum(-1800)
        self.rotation_slider.setMaximum(1800)
        self.rotation_slider.setSingleStep(1)
        self.rotation_slider.setValue(0)
        self.rotation_valt = QDoubleSpinBox()
        self.rotation_valt.lineEdit().setStyleSheet(toolbar_spinbox_textedit_style)
        self.rotation_valt.setFixedSize(80, 22)
        self.rotation_valt.setAlignment(Qt.AlignLeft)
        self.rotation_valt.setDecimals(2)
        self.rotation_valt.setRange(-45, 45)
        self.rotation_valt.setSingleStep(0.05)
        self.rotation_valt.setValue(0)

        self.rotation_wrap = QFrame()
        rotation_layout = QHBoxLayout(self.rotation_wrap)
        rotation_layout.setAlignment(Qt.AlignVCenter)
        rotation_layout.setContentsMargins(0, 0, 0, 0)
        rotation_layout.setSpacing(10)
        rotation_layout.addWidget(rotation_label)
        rotation_layout.addWidget(self.rotation_slider)
        rotation_layout.addWidget(self.rotation_valt)
        rotation_layout.addStretch(1)

        # for magic wand, magic wand wrap
        magic_color_label = QLabel('Color:')
        self.magic_color_btn = pg.ColorButton(padding=0)
        self.magic_color_btn.setFixedSize(60, 15)
        magic_tol_label = QLabel('Tolerance:')
        self.magic_tol_val = QLineEdit()
        self.magic_tol_val.setFixedWidth(40)
        # self.magic_tol_val.setAlignment(Qt.AlignLeft)
        self.magic_tol_val.setValidator(QIntValidator())
        self.magic_tol_val.setText('0')

        self.magic_wand_kernel = QComboBox()
        self.magic_wand_kernel.setFixedSize(150, 22)
        self.magic_wand_kernel.addItems(["Kernel", "Rectangular", "Elliptical", "Cross-shaped"])

        magic_wand_ksize_label = QLabel('Size:')
        self.magic_wand_ksize = QLineEdit()
        self.magic_wand_ksize.setFixedWidth(40)
        # self.magic_tol_val.setAlignment(Qt.AlignLeft)
        self.magic_wand_ksize.setValidator(QIntValidator())
        self.magic_wand_ksize.setText('0')

        self.magic_wand_virus_register = QPushButton()
        self.magic_wand_virus_register.setFocusPolicy(Qt.NoFocus)
        self.magic_wand_virus_register.setIcon(QIcon('icons/toolbar/virus_register.svg'))
        self.magic_wand_virus_register.setIconSize(QSize(20, 20))
        self.magic_wand_bnd_register = QPushButton()
        self.magic_wand_bnd_register.setFocusPolicy(Qt.NoFocus)
        self.magic_wand_bnd_register.setIcon(QIcon('icons/toolbar/boundary_register.svg'))
        self.magic_wand_bnd_register.setIconSize(QSize(20, 20))

        self.magic_wand_wrap = QFrame()
        # self.magic_wand_wrap.setFixedHeight(32)
        magic_wand_layout = QHBoxLayout(self.magic_wand_wrap)
        magic_wand_layout.setAlignment(Qt.AlignVCenter)
        magic_wand_layout.setContentsMargins(0, 0, 0, 0)
        magic_wand_layout.setSpacing(10)
        magic_wand_layout.addWidget(magic_color_label)
        magic_wand_layout.addWidget(self.magic_color_btn)
        magic_wand_layout.addSpacing(10)
        magic_wand_layout.addWidget(magic_tol_label)
        magic_wand_layout.addWidget(self.magic_tol_val)
        magic_wand_layout.addWidget(self.magic_wand_kernel)
        magic_wand_layout.addWidget(magic_wand_ksize_label)
        magic_wand_layout.addWidget(self.magic_wand_ksize)
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
        self.pencil_size_slider.sliderMoved.connect(self.change_pencil_slider)

        self.pencil_size_valt = QLineEdit()
        self.pencil_size_valt.setFixedSize(50, 24)
        self.pencil_size_valt.setAlignment(Qt.AlignLeft)
        self.pencil_size_valt.setValidator(QIntValidator(1, 30))
        self.pencil_size_valt.setText('3')

        pencil_color_label = QLabel('Color:')
        self.pencil_color_btn = pg.ColorButton(padding=0)
        self.pencil_color_btn.setFixedSize(60, 15)

        self.pencil_wrap = QFrame()
        pencil_layout = QHBoxLayout(self.pencil_wrap)
        pencil_layout.setAlignment(Qt.AlignVCenter)
        pencil_layout.setContentsMargins(0, 0, 0, 0)
        pencil_layout.setSpacing(10)
        pencil_layout.addWidget(pencil_color_label)
        pencil_layout.addWidget(self.pencil_color_btn)
        pencil_layout.addSpacing(15)
        pencil_layout.addWidget(pencil_size_label)
        pencil_layout.addWidget(self.pencil_size_slider)
        pencil_layout.addWidget(self.pencil_size_valt)
        pencil_layout.addStretch(1)

        # for eraser_btn, eraser wrap
        eraser_color_label = QLabel('Color:')
        self.eraser_color_btn = pg.ColorButton(padding=0)
        self.eraser_color_btn.setColor('red')
        self.eraser_color_btn.setFixedSize(60, 15)
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
        eraser_layout.setAlignment(Qt.AlignVCenter)
        eraser_layout.setContentsMargins(0, 0, 0, 0)
        eraser_layout.setSpacing(10)
        eraser_layout.addWidget(eraser_color_label)
        eraser_layout.addWidget(self.eraser_color_btn)
        eraser_layout.addSpacing(15)
        eraser_layout.addWidget(eraser_size_label)
        eraser_layout.addWidget(self.eraser_size_slider)
        eraser_layout.addWidget(self.eraser_size_valt)
        eraser_layout.addStretch(1)

        # for lasso_btn, lasso wrap
        lasso_color_label = QLabel('Color:')
        self.lasso_color_btn = pg.ColorButton(padding=0)
        self.lasso_color_btn.setFixedSize(60, 15)

        self.lasso_wrap = QFrame()
        lasso_layout = QHBoxLayout(self.lasso_wrap)
        lasso_layout.setAlignment(Qt.AlignVCenter)
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
        mask_layout.setAlignment(Qt.AlignVCenter)
        mask_layout.setContentsMargins(0, 0, 0, 0)
        mask_layout.setSpacing(10)
        mask_layout.addWidget(kernel_size_label)
        mask_layout.addWidget(self.kernel_size_slider)
        mask_layout.addStretch(1)

        # for probe_btn, probe wrap
        probe_color_label = QLabel('Color:')
        self.probe_color_btn = pg.ColorButton(padding=0)
        self.probe_color_btn.setColor(QColor(0, 0, 255))
        self.probe_color_btn.setFixedSize(60, 15)
        probe_type_label = QLabel('Type:')
        self.probe_type1 = QRadioButton("Neuropixel 1.0")
        self.probe_type1.setChecked(True)
        self.probe_type2 = QRadioButton("Neuropixel 2.0")
        self.probe_type3 = QRadioButton("Tetrode")
        # self.probe_style_circle = QRadioButton("Circle")
        # self.probe_style_circle.setChecked(True)
        # self.probe_style_circle.toggled.connect(self.probe_style_changed)
        # self.probe_style_square = QRadioButton("Square")
        # self.probe_style_square.toggled.connect(self.probe_style_changed)

        self.probe_wrap = QFrame()
        probe_layout = QHBoxLayout(self.probe_wrap)
        probe_layout.setAlignment(Qt.AlignVCenter)
        probe_layout.setContentsMargins(0, 0, 0, 0)
        probe_layout.setSpacing(10)
        probe_layout.addWidget(probe_color_label)
        probe_layout.addWidget(self.probe_color_btn)
        probe_layout.addSpacing(20)
        # probe_layout.addWidget(probe_style_label)
        # probe_layout.addWidget(self.probe_style_circle)
        # probe_layout.addWidget(self.probe_style_square)
        # probe_layout.addSpacing(10)
        probe_layout.addWidget(probe_type_label)
        probe_layout.addWidget(self.probe_type1)
        probe_layout.addWidget(self.probe_type2)
        probe_layout.addWidget(self.probe_type3)
        probe_layout.addStretch(1)

        # for triang_btn, triang wrap
        triang_color_label = QLabel('Color:')
        self.triang_color_btn = pg.ColorButton(padding=0)
        self.triang_color_btn.setFixedSize(60, 15)
        bound_pnts_num_label = QLabel('Points Number:')
        self.bound_pnts_num = QLineEdit()
        self.bound_pnts_num.setFixedSize(50, 24)
        self.bound_pnts_num.setAlignment(Qt.AlignLeft)
        self.bound_pnts_num.setValidator(QIntValidator(2, 15))
        self.bound_pnts_num.setText('2')
        self.triang_vis_btn = QPushButton()
        self.triang_vis_btn.setCheckable(True)
        vis_icon = QIcon()
        vis_icon.addPixmap(QPixmap("icons/toolbar/eye.svg"), QIcon.Normal, QIcon.On)
        vis_icon.addPixmap(QPixmap("icons/toolbar/eye_closed.svg"), QIcon.Normal, QIcon.Off)
        self.triang_vis_btn.setIcon(vis_icon)
        self.triang_vis_btn.setIconSize(QSize(20, 20))
        self.triang_match_bnd = QPushButton()
        self.triang_match_bnd.setIcon(QIcon('icons/toolbar/matchbnd.svg'))
        self.triang_match_bnd.setIconSize(QSize(20, 20))

        self.triang_wrap = QFrame()
        self.triang_wrap.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        triang_layout = QHBoxLayout(self.triang_wrap)
        triang_layout.setAlignment(Qt.AlignVCenter)
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
        cell_color_label = QLabel('Color:')
        self.cell_color_btn = pg.ColorButton(padding=0)
        self.cell_color_btn.setColor(QColor(0, 255, 0))
        self.cell_color_btn.setFixedSize(60, 15)

        self.cell_count_label_list = [QLabel('Count: ')]
        self.cell_count_val_list = [QLabel('0')]

        for i in range(4):
            self.cell_count_label_list.append(QLabel('Count {}: '.format(i+1)))
            self.cell_count_val_list.append(QLabel('0'))

        for i in range(5):
            self.cell_count_label_list[i].setVisible(False)
            self.cell_count_val_list[i].setVisible(False)

        self.cell_selector_btn = QPushButton()
        self.cell_selector_btn.setToolTip('select cells manually')
        self.cell_selector_btn.setCheckable(True)
        selector_icon = QIcon()
        selector_icon.addPixmap(QPixmap("icons/toolbar/cell_select_not.svg"), QIcon.Normal, QIcon.Off)
        selector_icon.addPixmap(QPixmap("icons/toolbar/cell_select.svg"), QIcon.Normal, QIcon.On)
        self.cell_selector_btn.setIcon(selector_icon)
        self.cell_selector_btn.setIconSize(QSize(20, 20))

        self.cell_aim_btn = QPushButton()
        self.cell_aim_btn.setToolTip('select single cell body area')
        self.cell_aim_btn.setCheckable(True)
        aim_icon = QIcon()
        aim_icon.addPixmap(QPixmap("icons/toolbar/aim_not.svg"), QIcon.Normal, QIcon.Off)
        aim_icon.addPixmap(QPixmap("icons/toolbar/aim.svg"), QIcon.Normal, QIcon.On)
        self.cell_aim_btn.setIcon(aim_icon)
        self.cell_aim_btn.setIconSize(QSize(20, 20))
        self.cell_radar_btn = QPushButton()
        self.cell_radar_btn.setToolTip('automatically search for similar cell bodies')
        self.cell_radar_btn.setIcon(QIcon('icons/toolbar/radar.svg'))
        self.cell_radar_btn.setIconSize(QSize(20, 20))

        self.cell_count_wrap = QFrame()
        cell_layout = QHBoxLayout(self.cell_count_wrap)
        cell_layout.setAlignment(Qt.AlignVCenter)
        cell_layout.setContentsMargins(0, 0, 0, 0)
        cell_layout.setSpacing(10)
        cell_layout.addWidget(cell_color_label)
        cell_layout.addWidget(self.cell_color_btn)
        cell_layout.addSpacing(15)
        cell_layout.addWidget(self.cell_selector_btn)
        cell_layout.addSpacing(10)
        cell_layout.addWidget(self.cell_aim_btn)
        cell_layout.addSpacing(10)
        cell_layout.addWidget(self.cell_radar_btn)
        cell_layout.addSpacing(10)
        cell_layout.addWidget(self.cell_count_label_list[0])
        cell_layout.addWidget(self.cell_count_val_list[0])
        for i in range(1, 5):
            cell_layout.addWidget(self.cell_count_label_list[i])
            cell_layout.addWidget(self.cell_count_val_list[i])
            cell_layout.addSpacing(10)
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

        # triangle style
        self.tri_line_style = pg.mkPen(color=(128, 128, 128), width=0.5, style=Qt.DashLine)

        # probe style
        # self.probe_style =


        # ---------------------------- define all cursor shape
        # self.eraser_cursor = QCursor(QPixmap('icons/eraser_cursor.png'), hotX=7, hotY=27)


    def change_pencil_slider(self):
        val = self.pencil_size_slider.value()
        self.pencil_size_valt.setText(str(val))

    def change_eraser_slider(self):
        val = self.eraser_size_slider.value()
        self.eraser_size_valt.setText(str(val))
        self.circle = self.original_circle * val

    def change_eraser_val(self):
        val = int(self.eraser_size_valt.text())
        self.eraser_size_slider.setValue(val)

    def moving_dist_changed(self):
        self.moving_px = self.moving_valt.value()

    def get_tool_data(self):
        data = {'pencil_color': self.pencil_color_btn.color(),
                'pencil_size': self.pencil_size_valt.text(),
                'eraser_color': self.eraser_color_btn.color(),
                'eraser_size': self.eraser_size_valt.text(),
                'magic_wand_color': self.magic_color_btn.color(),
                'magic_wand_tol': self.magic_tol_val.text(),
                'magic_wand_kernel': self.magic_wand_kernel.currentText(),
                'magic_wand_ksize': self.magic_wand_ksize.text(),
                'probe_color': self.probe_color_btn.color(),
                'triangle_color': self.triang_color_btn.color(),
                'cell_color': self.cell_color_btn.color()}
        # 'moving_valt': self.moving_valt.value(),
        # 'rotation_valt': self.rotation_valt.value(),
        return data

    def set_tool_data(self, data):
        # self.moving_valt.setValue(data['moving_valt'])
        # self.rotation_valt.setValue(data['rotation_valt'])
        self.pencil_color_btn.setColor(data['pencil_color'])
        self.pencil_size_valt.setText(data['pencil_size'])
        self.eraser_color_btn.setColor(data['eraser_color'])
        self.eraser_size_valt.setText(data['eraser_size'])
        self.magic_color_btn.setColor(data['magic_wand_color'])
        self.magic_tol_val.setText(data['magic_wand_tol'])
        self.magic_wand_kernel.setCurrentText(data['magic_wand_kernel'])
        self.magic_wand_ksize.setText(data['magic_wand_ksize'])
        self.probe_color_btn.setColor(data['probe_color'])
        self.triang_color_btn.setColor(data['triangle_color'])
        self.cell_color_btn.setColor(data['cell_color'])












