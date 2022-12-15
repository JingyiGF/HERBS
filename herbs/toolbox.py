from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore


class ToolBox(QObject):

    def __init__(self):

        QObject.__init__(self)

        self.pencil_mask = np.ones((3, 3), 'uint8')
        self.is_closed = False
        self.multi_shanks = False

        self.remove_inside = True

        self.merge_sites = False

        # action version
        self.add_atlas = QAction(QIcon('icons/toolbar/atlas_icon.png'), 'Upload Previous Loaded Volume Atlas', self)
        self.add_image_stack = QAction(QIcon('icons/toolbar/image_icon.svg'), 'Upload Histological Image', self)

        self.vis2 = QAction(QIcon('icons/toolbar/two_window.png'), 'Show 2 Windows', self)
        self.vis4 = QAction(QIcon('icons/toolbar/window4.png'), 'Show 4 Windows', self)
        self.vis3 = QAction(QIcon('icons/toolbar/window3.png'), 'Show 3 Windows', self)

        self.toa_btn_off_icon = QIcon('icons/toolbar/toa.svg')
        self.toa_btn_on_icon = QIcon('icons/toolbar/toa_delete.svg')

        self.toh_btn_off_icon = QIcon('icons/toolbar/toh.svg')
        self.toh_btn_on_icon = QIcon('icons/toolbar/toh_delete.svg')

        self.toa_btn = QAction(QIcon('icons/toolbar/toa.svg'), 'Transform to Atlas Slice Window', self)
        self.toh_btn = QAction(QIcon('icons/toolbar/toh.svg'), 'Transform to Histologist Image Window', self)
        self.check_btn = QAction(QIcon('icons/toolbar/accept.svg'), 'Accept and Transfer', self)

        lasso_btn = QAction(QIcon('icons/toolbar/lasso.svg'), 'Polygon Lasso', self)
        lasso_btn.setCheckable(True)

        magic_wand_btn = QAction(QIcon('icons/toolbar/magic-wand.svg'), 'Magic Wand', self)
        magic_wand_btn.setCheckable(True)

        pencil_btn = QAction(QIcon('icons/toolbar/pencil.svg'), 'Pencil', self)
        pencil_btn.setCheckable(True)

        eraser_btn = QAction(QIcon('icons/toolbar/eraser.svg'), 'Eraser', self)
        eraser_btn.setCheckable(True)

        mask_btn = QAction(QIcon('icons/toolbar/mask.svg'), 'Mask Maker', self)
        mask_btn.setCheckable(True)

        probe_btn = QAction(QIcon('icons/toolbar/probe.svg'), 'Probe Marker', self)
        probe_btn.setCheckable(True)

        triang_btn = QAction(QIcon('icons/toolbar/triangulation.svg'), 'Triangulation', self)
        triang_btn.setCheckable(True)

        loc_btn = QAction(QIcon('icons/toolbar/location.svg'), 'Cell Selector', self)
        loc_btn.setCheckable(True)

        ruler_btn = QAction(QIcon('icons/toolbar/ruler.svg'), 'Ruler', self)
        ruler_btn.setCheckable(True)

        self.checkable_btn_dict = {'ruler_btn': ruler_btn,
                                   'pencil_btn': pencil_btn,
                                   'eraser_btn': eraser_btn,
                                   'lasso_btn': lasso_btn,
                                   'magic_wand_btn': magic_wand_btn,
                                   'probe_btn': probe_btn,
                                   'triang_btn': triang_btn,
                                   'loc_btn': loc_btn}

        self.toolbox_btn_keys = list(self.checkable_btn_dict.keys())

        # for ruler_btn, ruler wrap
        ruler_color_label = QLabel('Color:')
        self.ruler_color_btn = pg.ColorButton(padding=0)
        self.ruler_color_btn.setColor('yellow')
        self.ruler_color_btn.setFixedSize(60, 15)
        ruler_width_label = QLabel('Size:')
        self.ruler_width_slider = QSlider(Qt.Horizontal)
        self.ruler_width_slider.setFixedWidth(100)
        self.ruler_width_slider.setMinimum(1)
        self.ruler_width_slider.setMaximum(5)
        self.ruler_width_slider.setValue(3)
        self.ruler_width_slider.sliderMoved.connect(self.change_ruler_slider)

        self.ruler_size_valt = QLineEdit()
        self.ruler_size_valt.setFixedSize(50, 24)
        self.ruler_size_valt.setAlignment(Qt.AlignLeft)
        self.ruler_size_valt.setValidator(QIntValidator(1, 5))
        self.ruler_size_valt.setText('3')

        self.ruler_length_label = QLabel('Length: ')

        self.ruler_wrap = QFrame()
        ruler_layout = QHBoxLayout(self.ruler_wrap)
        ruler_layout.setAlignment(Qt.AlignVCenter)
        ruler_layout.setContentsMargins(0, 0, 0, 0)
        ruler_layout.setSpacing(10)
        ruler_layout.addWidget(ruler_color_label)
        ruler_layout.addWidget(self.ruler_color_btn)
        ruler_layout.addSpacing(15)
        ruler_layout.addWidget(ruler_width_label)
        ruler_layout.addWidget(self.ruler_width_slider)
        ruler_layout.addWidget(self.ruler_size_valt)
        ruler_layout.addSpacing(25)
        ruler_layout.addWidget(self.ruler_length_label)
        ruler_layout.addStretch(1)

        # for magic wand, magic wand wrap
        magic_color_label = QLabel('Color:')
        self.magic_color_btn = pg.ColorButton(padding=0)
        self.magic_color_btn.setFixedSize(60, 15)
        self.magic_color_btn.setColor(QColor(255, 0, 255, 255))
        magic_tol_label = QLabel('Tolerance:')
        self.magic_tol_val = QLineEdit()
        self.magic_tol_val.setFixedWidth(40)
        # self.magic_tol_val.setAlignment(Qt.AlignLeft)
        self.magic_tol_val.setValidator(QIntValidator())
        self.magic_tol_val.setText('0')

        self.magic_wand_kernel = QComboBox()
        self.magic_wand_kernel.setFixedSize(150, 20)
        self.magic_wand_kernel.addItems(["Kernel", "Rectangular", "Elliptical", "Cross-shaped"])

        magic_wand_ksize_label = QLabel('Size:')
        self.magic_wand_ksize = QSpinBox()
        self.magic_wand_ksize.setFixedSize(80, 20)
        self.magic_wand_ksize.setValue(0)
        self.magic_wand_ksize.setMinimum(0)

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
        self.pencil_size_slider.setMaximum(5)
        self.pencil_size_slider.setValue(2)
        self.pencil_size_slider.sliderMoved.connect(self.change_pencil_slider)

        self.pencil_size_valt = QLineEdit()
        self.pencil_size_valt.setFixedSize(50, 24)
        self.pencil_size_valt.setAlignment(Qt.AlignLeft)
        self.pencil_size_valt.setValidator(QIntValidator(1, 5))
        self.pencil_size_valt.setText('2')

        pencil_color_label = QLabel('Color:')
        self.pencil_color_btn = pg.ColorButton(padding=0)
        self.pencil_color_btn.setFixedSize(60, 15)
        self.pencil_color_btn.setColor(QColor(255, 102, 0))

        pencil_path_label = QLabel('Path Type:')
        self.pencil_path_btn = QPushButton()
        self.pencil_path_btn.setCheckable(True)
        da_icon = QIcon()
        da_icon.addPixmap(QPixmap("icons/toolbar/closed_path.svg"), QIcon.Normal, QIcon.On)
        da_icon.addPixmap(QPixmap("icons/toolbar/open_path.svg"), QIcon.Normal, QIcon.Off)
        self.pencil_path_btn.setIcon(da_icon)
        self.pencil_path_btn.setIconSize(QSize(20, 20))
        self.pencil_path_btn.clicked.connect(self.pencil_path_btn_clicked)

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
        pencil_layout.addSpacing(15)
        pencil_layout.addWidget(pencil_path_label)
        pencil_layout.addWidget(self.pencil_path_btn)
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
        self.eraser_size_slider.setMaximum(500)
        self.eraser_size_slider.setValue(20)
        self.eraser_size_slider.valueChanged.connect(self.change_eraser_slider)

        self.eraser_size_valt = QLineEdit()
        self.eraser_size_valt.setFixedSize(50, 24)
        self.eraser_size_valt.setAlignment(Qt.AlignLeft)
        self.eraser_size_valt.setValidator(QIntValidator(1, 500))
        self.eraser_size_valt.setText('20')
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
        self.lasso_color_btn.setColor(QColor(0, 255, 255))

        self.lasso_type_btn = QPushButton()
        self.lasso_type_btn.setCheckable(True)
        lt_icon = QIcon()
        lt_icon.addPixmap(QPixmap('icons/toolbar/outpart.svg'), QIcon.Normal, QIcon.On)
        lt_icon.addPixmap(QPixmap('icons/toolbar/inpart.svg'), QIcon.Normal, QIcon.Off)
        self.lasso_type_btn.setIcon(lt_icon)
        self.lasso_type_btn.setIconSize(QSize(20, 20))
        self.lasso_type_btn.clicked.connect(self.lasso_type_changed)

        self.lasso_wrap = QFrame()
        lasso_layout = QHBoxLayout(self.lasso_wrap)
        lasso_layout.setAlignment(Qt.AlignVCenter)
        lasso_layout.setContentsMargins(0, 0, 0, 0)
        lasso_layout.setSpacing(10)
        lasso_layout.addWidget(lasso_color_label)
        lasso_layout.addWidget(self.lasso_color_btn)
        lasso_layout.addSpacing(10)
        lasso_layout.addWidget(self.lasso_type_btn)
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
        self.multi_prb_btn = QPushButton()
        self.multi_prb_btn.setCheckable(True)
        mp_icon = QIcon()
        mp_icon.addPixmap(QPixmap("icons/toolbar/multi_pencil.svg"), QIcon.Normal, QIcon.On)
        mp_icon.addPixmap(QPixmap("icons/toolbar/single_pencil.svg"), QIcon.Normal, QIcon.Off)
        self.multi_prb_btn.setIcon(mp_icon)
        self.multi_prb_btn.setIconSize(QSize(20, 20))
        self.multi_prb_btn.setToolTip('Multi-shanks Switch')

        probe_color_label = QLabel('Color:')
        probe_color_label.setToolTip('Probe Color')
        self.probe_color_btn = pg.ColorButton(padding=0)
        self.probe_color_btn.setColor(QColor(0, 0, 255))
        self.probe_color_btn.setFixedSize(60, 15)
        probe_type_label = QLabel('Type:')
        probe_type_label.setToolTip('Probe type')
        self.probe_type_combo = QComboBox()
        self.probe_type_combo.setFixedSize(150, 20)
        self.probe_type_combo.addItems(["Neuropixel 1.0", "Neuropixel 2.0", "Linear-silicon", "Tetrode"])
        self.probe_type_combo.setCurrentText("Neuropixel 1.0")

        self.merge_sites_btn = QPushButton()
        self.merge_sites_btn.setCheckable(True)
        ms_icon = QIcon()
        ms_icon.addPixmap(QPixmap("icons/toolbar/line_sites.svg"), QIcon.Normal, QIcon.On)
        ms_icon.addPixmap(QPixmap("icons/toolbar/separate_sites.svg"), QIcon.Normal, QIcon.Off)
        self.merge_sites_btn.setIcon(ms_icon)
        self.merge_sites_btn.setIconSize(QSize(20, 20))
        self.merge_sites_btn.setToolTip('Merge sites')
        self.merge_sites_btn.clicked.connect(self.merge_sites_btn_clicked)

        site_face_label = QLabel('Site-face:')
        site_face_label.setToolTip('Sites Face Direction')
        self.pre_site_face_combo = QComboBox()
        self.pre_site_face_combo.setFixedSize(100, 20)
        self.pre_site_face_combo.addItems(["Out", "In", "Left", "Right"])

        self.after_site_face_combo = QComboBox()
        self.after_site_face_combo.setFixedSize(100, 20)
        self.after_site_face_combo.addItems(["Up", "Down", "Left", "Right"])
        self.after_site_face_combo.setVisible(False)

        self.linear_silicon_list = QPushButton()
        self.linear_silicon_list.setFocusPolicy(Qt.NoFocus)
        self.linear_silicon_list.setIcon(QIcon('icons/toolbar/list.svg'))
        self.linear_silicon_list.setIconSize(QSize(20, 20))
        self.linear_silicon_list.setVisible(False)
        self.linear_silicon_list.setToolTip('Linear Silicon Designer')

        self.probe_wrap = QFrame()
        probe_layout = QHBoxLayout(self.probe_wrap)
        probe_layout.setAlignment(Qt.AlignVCenter)
        probe_layout.setContentsMargins(0, 0, 0, 0)
        probe_layout.setSpacing(10)
        probe_layout.addWidget(self.multi_prb_btn)
        probe_layout.addSpacing(20)
        probe_layout.addWidget(probe_color_label)
        probe_layout.addWidget(self.probe_color_btn)
        probe_layout.addSpacing(10)
        probe_layout.addWidget(probe_type_label)
        probe_layout.addWidget(self.probe_type_combo)
        probe_layout.addSpacing(10)
        probe_layout.addWidget(self.merge_sites_btn)
        probe_layout.addWidget(site_face_label)
        probe_layout.addWidget(self.pre_site_face_combo)
        probe_layout.addWidget(self.after_site_face_combo)
        probe_layout.addStretch(1)
        probe_layout.addWidget(self.linear_silicon_list)
        probe_layout.addSpacing(10)

        # for triang_btn, triang wrap
        triang_color_label = QLabel('Color:')
        self.triang_color_btn = pg.ColorButton(padding=0)
        self.triang_color_btn.setFixedSize(60, 15)
        bound_pnts_num_label = QLabel('Points Number:')
        self.bound_pnts_num = QLineEdit()
        self.bound_pnts_num.setFixedSize(50, 24)
        self.bound_pnts_num.setAlignment(Qt.AlignLeft)
        self.bound_pnts_num.setMaxLength(2)
        self.bound_pnts_num.setValidator(QIntValidator())
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
        r = int(self.eraser_size_valt.text())
        angle = np.deg2rad(np.arange(0, 360, 1))
        x = np.cos(angle)
        y = np.sin(angle)
        self.original_circle = np.vstack([x, y]).T
        self.circle = self.original_circle * r

        # triangle style
        self.tri_line_style = pg.mkPen(color=(128, 128, 128), width=0.5, style=Qt.DashLine)

        # ---------------------------- define all cursor shape
        # self.eraser_cursor = QCursor(QPixmap('icons/eraser_cursor.png'), hotX=7, hotY=27)

    def update_cell_count_label(self, cell_count_list):
        for layer_index in range(5):
            self.update_single_cell_count_label(cell_count_list, layer_index)

    def update_single_cell_count_label(self, cell_count_list, layer_index):
        self.cell_count_val_list[layer_index].setText(str(cell_count_list[layer_index]))

    def lasso_type_changed(self):
        if self.lasso_type_btn.isChecked():
            self.remove_inside = False
        else:
            self.remove_inside = True

    def pencil_path_btn_clicked(self):
        if self.pencil_path_btn.isChecked():
            self.is_closed = True
        else:
            self.is_closed = False

    def merge_sites_btn_clicked(self):
        if self.merge_sites_btn.isChecked():
            self.merge_sites = True
        else:
            self.merge_sites = False

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

    def change_ruler_slider(self):
        val = self.ruler_width_slider.value()
        self.ruler_size_valt.setText(str(val))

    def get_tool_data(self):
        data = {'pencil_color': self.pencil_color_btn.color(),
                'pencil_size': self.pencil_size_valt.text(),
                'magic_wand_color': self.magic_color_btn.color(),
                'magic_wand_tol': self.magic_tol_val.text(),
                'magic_wand_kernel': self.magic_wand_kernel.currentText(),
                'magic_wand_ksize': self.magic_wand_ksize.value(),
                'probe_color': self.probe_color_btn.color(),
                'cell_color': self.cell_color_btn.color(),
                'is_closed': self.is_closed}
        return data

    def set_tool_data(self, data):
        self.pencil_color_btn.setColor(data['pencil_color'])
        self.pencil_size_valt.setText(str(data['pencil_size']))
        self.pencil_path_btn.setChecked(data['is_closed'])
        self.magic_color_btn.setColor(data['magic_wand_color'])
        self.magic_tol_val.setText(str(data['magic_wand_tol']))
        self.magic_wand_ksize.setValue(data['magic_wand_ksize'])
        self.magic_wand_kernel.setCurrentText(data['magic_wand_kernel'])
        self.probe_color_btn.setColor(data['probe_color'])
        self.cell_color_btn.setColor(data['cell_color'])


    def multi_prb_status_changed(self):
        if self.multi_prb_btn.isChecked():
            self.multi_shanks = True
        else:
            self.multi_shanks = False














