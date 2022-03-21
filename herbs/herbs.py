import cv2
import numpy as np

from herrbs import *



herrbs_style = '''
QMainWindow {
    background-color: rgb(50, 50, 50);
}

/*---------------------- Slider -----------------------*/
QSlider {
    min-height: 20px;
    max-height: 20px;
    background: transparent;
}

QSlider::groove:horizontal {
    border: 1px solid #999999;
    height: 2px; /* the groove expands to the size of the slider by default. by giving it a height, it has a fixed size */
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B1B1B1, stop:1 #c4c4c4);
    margin: 0px 12px;
}

QSlider::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #8f8f8f);
    border: 1px solid #5c5c5c;
    width: 2px;
    height: 30px;
    margin: -6px -2px; /* handle is placed by default on the contents rect of the groove. Expand outside the groove */
    border-radius: 0px;
}

/*---------------------- LineEdit -----------------------*/
QLineEdit { 
    background-color: transparent;
    color: white;
}

/*---------------------- SpinBox -----------------------*/
QSpinBox {
    padding-right: 0px; /* make room for the arrows */
    border-width: 0;
}

QSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right; /* position at the top right corner */
    width: 15px; 
    border-width: 0px;
}

QSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right; /* position at bottom right corner */
    width: 15px;
    border-width: 0px;
}

QSpinBox::up-button:hover {
    background-color: #282828;
}

QSpinBox::down-button:hover {
    background-color: #282828;
}

QSpinBox::up-button:pressed {
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #282828, stop: 1 #323232);
}

QSpinBox::down-button:pressed {
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #323232, stop: 1 #282828);
}

QSpinBox::up-arrow {
    image: url(icons/up-arrow.svg);
    width: 7px;
    height: 7px;
}

QSpinBox::down-arrow {
    image: url(icons/down-arrow.svg);
    width: 7px;
    height: 7px;
}

/*---------------------- DoubleSpinBox -----------------------*/
QDoubleSpinBox {
    padding-right: 0px; 
    border-width: 0;
}

QDoubleSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right; /* position at the top right corner */
    width: 15px; 
    border: None;
}

QDoubleSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right; /* position at bottom right corner */
    width: 15px;
    border: None;
}

QDoubleSpinBox::up-button:hover {
    background-color: #282828;
}

QDoubleSpinBox::down-button:hover {
    background-color: #282828;
}

QDoubleSpinBox::up-button:pressed {
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #282828, stop: 1 #000000);
}

QDoubleSpinBox::down-button:pressed {
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #000000, stop: 1 #282828);
}

QDoubleSpinBox::up-arrow {
    image: url(icons/up-arrow.svg);
    width: 7px;
    height: 7px;
}

QDoubleSpinBox::down-arrow {
    image: url(icons/down-arrow.svg);
    width: 7px;
    height: 7px;
}
'''

tab_style = '''
/*---------------------- QTabWidget -----------------------*/
QTabWidget{
    background-color: transparent;
    margin-bottom: 0px;

}

QTabWidget::pane {
    background-color: transparent;
    margin-left: 0px;
    padding-left:0px;
    border-top: 1px solid #747a80;
    border-left: 1px solid #747a80;
    border-right: 1px solid #747a80;
    border-bottom: 1px solid #747a80;
    margin-bottom: 0px;
}

QTabWidget::tab-bar {
    bottom: 0;
    border: 1px solid gray;
}

QTabBar::tab {
    background-color: #3c3f41;
    height:30px;
    width: 30px;
    border-bottom: 3px solid #323232;
    margin: 0px;
    padding-top: 5px;
    padding-left: 6px;
}

QTabBar::tab:selected {
    background: #4e5254;
    border-bottom: 3px solid #747a80;
}

QTabBar::tab:hover{
    background: #27292a;
}

QGroupBox {
    background-color: transparent; 
    border: 1px solid; 
    border-radius: 3px; 
    padding-top: 3px; 
    padding-bottom: 3px; 
    margin-top: 0px
}


'''


image_tool_frame_style = '''
QFrame {
    background-color: #535352;
    border-top-color: #2a2a2b;
    border: 2px solid;
    border-radius: 0px;
    padding-top: 0px;
    padding-bottom: 0px; 
    margin-top: 0px;
} 

'''

sidebar_title_label_style = '''
QLabel{
    color: white;
    background: #747a80;
    width: 300px;
    height: 20px;
    padding-bottom: 5px;
    padding-left: 5px;
    padding-top: 2px;
}

'''

ic_bnt_style = '''

QPushButton {
    border : None; 
    background: transparent;
    margin: 0px;
    padding-top: 0px;
    border-radius: 0px;
    min-width: 32px;
    min-height: 30px;
}
QPushButton:checked {
    background-color: #383838; 
    border: 1px solid #636363; 
}

QPushButton:pressed {
    background-color: #383838; 
    border: 1px solid #636363; 
}

QPushButton:hover {
    background-color: #383838; 
    border: 1px solid #636363; 
}

'''

toolbar_style = '''
QToolBar::separator { 
    color: white;
    background-color: gray;
    width: 1px;
    height: 10px;
    border: 5px solid rgb(50, 50, 50);
}


QToolBar {
    color: rgb(255, 255, 255);
    background-color: rgb(50, 50, 50);
    border: None;
    selection-color: rgb(50, 50, 50);
    selection-background-color: #27292a;
    spacing: 0px;
}

QToolButton {
    border-top: 2px solid rgb(50, 50, 50);
    border-bottom: 2px solid rgb(50, 50, 50);
}


QToolButton::hover {
    background-color: #27292a;
    border-top: 2px solid #27292a;
    border-bottom: 2px solid #27292a;
}

QToolButton::checked {
    border-bottom: 2px solid gray;
}

QPushButton {
    background-color: rgb(50, 50, 50);
    border: 0px solid gray;
    width: 32px;
    height: 32px;
    margin: 0px;
    padding: 0px;
}

QPushButton::hover {
    background-color: #27292a;
}

QLabel {
    color: #d6d6d6;
    background-color: rgb(50, 50, 50);
}

QLineEdit { 
    border: 1px solid gray;
}



QSlider::groove:horizontal {
    border: 1px solid #999999;
    height: 2px; 
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B1B1B1, stop:1 #c4c4c4);
    margin: 2px 0;
}

QSlider::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #8f8f8f);
    border: 1px solid #5c5c5c;
    width: 18px;
    margin: -2px 0; /* handle is placed by default on the contents rect of the groove. Expand outside the groove */
    border-radius: 3px;
}

'''

scriptDir = dirname(realpath(__file__))
FORM_Main, _ = loadUiType((join(dirname(__file__), "main_window.ui")))


class HERBS(QMainWindow, FORM_Main):
    def __init__(self, parent=FORM_Main):
        super(HERBS, self).__init__()
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.setWindowTitle("HERBS - Histological E-data Registration in Rat Brain Space")

        self.show_all_windows = False
        self.num_windows = 1

        self.np_onside = None
        self.atlas_rect = None
        self.histo_rect = None
        self.small_atlas_rect = None
        self.small_histo_rect = None

        self.atlas_folder = None

        self.exist_img = []

        self.small_mesh_list = {}
        self.lasso_pnts = []
        self.lasso_is_closure = False
        self.eraser_is_on = False

        self.registered_prob_list = []
        self.registered_img_list = []

        self.working_cell_data = []
        self.working_probe_data = []
        self.working_virus_data = None
        self.working_mask_data = None
        self.working_boundary_data = None
        self.working_line_data = []
        self.img_triang_data = []
        self.img_boundary_triang_pnts = []
        self.img_inside_triang_pnts = []
        self.triangles_movable = False

        self.atlas_corner_points = None
        self.atlas_side_lines = None
        self.atlas_tri_data = []
        self.atlas_tri_inside_data = []
        self.atlas_tri_onside_data = []

        self.histo_corner_points = None
        self.histo_side_lines = None
        self.histo_tri_data = []
        self.histo_tri_inside_data = []
        self.histo_tri_onside_data = []

        self.working_atlas_probe = []
        self.working_atlas_cell = []
        self.working_atlas_virus = None
        self.working_atlas_lines = []
        self.working_atlas_boundary = None

        self.working_atlas_pnts = []
        self.working_atlas_text = []
        self.atlas_point_count = 0
        self.working_img_pnts = []
        self.working_img_text = []
        self.img_point_count = 0

        self.is_projected = False
        self.project_matrix = None
        self.action_after_projection = {}

        self.register_cell_list = []
        self.registered_probe_pnts_list = []
        self.registered_probe_lines_list = []
        self.registered_virus_dict = {}
        self.registered_boundary_dict = {}

        self.registered_probe_count = 0

        self.probe_data_dicts = []
        self.prob_list = []
        self.probe_lines_3d = []
        self.probe_lines_2d = []

        self.cell_number = 0
        self.previous_checked_label = []
        self.atlas_display = 'coronal'
        self.show_child_mesh = False
        self.warning_status = False

        self.a2h_transferred = False
        self.h2a_transferred = False

        self.init_a2h_tri_pnts = []
        self.init_a2h_overlay_img = None

        self.init_h2a_tri_pnts = []
        self.init_h2a_overlay_img = None

        self.current_checked_tool = None

        self.atlas_adjusted_corner_points = None
        self.atlas_adjusted_side_lines = None
        self.atlas_adjusted_tri_onside_data = None

        self.histo_adjusted_corner_points = None
        self.histo_adjusted_side_lines = None
        self.histo_adjusted_tri_onside_data = None

        self.tri_line_style = pg.mkPen(color='r', width=0.5, style=Qt.DashLine)

        # ---------------------
        self.tool_box = ToolBox()
        self.toolbar_wrap_action_dict = {}

        self.statusLabel = QLabel()
        self.statusbar.addWidget(self.statusLabel)
        # self.statusLabel.setText("Ready")
        # self.statusbar.showMessage('ready')
        self.statusLabel.setFixedHeight(30)

        # ---------------------------- define all cursor shape
        self.eraser_cursor = QCursor(QPixmap('icons/eraser_cursor.png'), hotX=7, hotY=27)



        # ---------------------------- load controls, views, panels
        self.layer_ctrl = LayersControl()
        self.layer_ctrl.sig_opacity_changed.connect(self.layers_opacity_changed)
        self.layer_ctrl.sig_visible_changed.connect(self.layers_visible_changed)

        self.object_ctrl = ObjectControl()
        self.object_ctrl.add_object_btn.clicked.connect(self.make_object_pieces)
        self.object_ctrl.merge_probe_btn.clicked.connect(self.merge_probes)
        self.object_ctrl.line_width_slider.valueChanged.connect(self.obj_line_width_changed)
        # self.object_ctrl.merge_virus_btn.clicked.connect(self.merge_virus)
        # self.object_ctrl.merge_bnd_btn.clicked.connect(self.merge_bnds)

        self.image_view = ImageView()
        self.image_view.sig_image_changed.connect(self.update_histo_tri_onside_data)
        self.image_view.img_stacks.sig_mouse_clicked.connect(self.img_stacks_clicked)
        self.image_view.img_stacks.sig_mouse_hovered.connect(self.img_stacks_hovered)
        self.image_view.img_stacks.lasso_path.sigPointsClicked.connect(self.lasso_points_clicked)
        self.image_view.img_stacks.sig_key_pressed.connect(self.img_stacks_key_pressed)
        self.image_view.img_stacks.drawing_pnts.sigClicked.connect(self.img_drawing_pnts_clicked)
        self.image_view.img_stacks.tri_pnts.mouseDragged.connect(self.hist_window_tri_pnts_moving)
        self.image_view.img_stacks.tri_pnts.mouseClicked.connect(self.hist_window_tri_pnts_clicked)

        self.atlas_view = AtlasView()
        self.atlas_view.show_boundary_btn.clicked.connect(self.vis_atlas_boundary)
        self.atlas_view.section_rabnt1.toggled.connect(self.display_changed)
        self.atlas_view.section_rabnt2.toggled.connect(self.display_changed)
        self.atlas_view.section_rabnt3.toggled.connect(self.display_changed)
        self.atlas_view.label_tree.labels_changed.connect(self.sig_label_changed)
        self.atlas_view.cimg.sig_mouse_hovered.connect(self.coronal_slice_stacks_hovered)
        self.atlas_view.simg.sig_mouse_hovered.connect(self.sagital_slice_stacks_hovered)
        # self.atlas_view.himg.sig_mouse_hovered.connect(self.slice_stacks_hovered)
        # self.atlas_view.scimg.sig_mouse_hovered.connect(self.slice_stacks_hovered)
        self.atlas_view.cimg.sig_mouse_clicked.connect(self.atlas_stacks_clicked)
        self.atlas_view.cimg.drawing_pnts.sigClicked.connect(self.atlas_drawing_pnts_clicked)
        self.atlas_view.simg.drawing_pnts.sigClicked.connect(self.atlas_drawing_pnts_clicked)
        self.atlas_view.himg.drawing_pnts.sigClicked.connect(self.atlas_drawing_pnts_clicked)
        # self.atlas_view.cimg.tri_pnts.mouseDragged.connect(self.triang_pnts_moving)
        self.atlas_view.cimg.tri_pnts.mouseDragged.connect(self.atlas_window_tri_pnts_moving)
        self.atlas_view.cimg.tri_pnts.mouseClicked.connect(self.atlas_window_tri_pnts_clicked)

        # --------------------------------------------------------
        #                 connect all menu actions
        # --------------------------------------------------------
        self.actionSingle_Image.triggered.connect(self.load_image)
        # load other atlases

        self.actionCoronal_Window.triggered.connect(self.show_only_coronal_window)
        self.actionSagital_Window.triggered.connect(self.show_only_sagital_window)
        self.actionHorizontal_Window.triggered.connect(self.show_only_horizontal_window)
        self.action3D_Window.triggered.connect(self.show_only_3d_window)
        self.actionImage_Window.triggered.connect(self.show_only_image_window)
        self.action2_Windows.triggered.connect(self.show_2_windows)
        self.action4_Windows.triggered.connect(self.show_4_windows)

        # self.actionGray_Mode

        self.actionFlip_Horizontal.triggered.connect(self.image_view.image_horizon_flip)
        self.actionFlip_Vertical.triggered.connect(self.image_view.image_vertical_flip)
        self.action180.triggered.connect(self.image_view.image_180_rotate)
        self.action90_Clockwise.triggered.connect(self.image_view.image_90_rotate)
        self.action90_Counter_Clockwise.triggered.connect(self.image_view.image_90_counter_rotate)

        self.init_tool_bar()
        self.init_side_bar()

        # ------------------ coronal
        coronal_layout = QGridLayout(self.coronalframe)
        coronal_layout.setSpacing(0)
        coronal_layout.setContentsMargins(0, 0, 0, 0)
        coronal_layout.addWidget(self.atlas_view.cimg, 0, 0, 1, 1)
        coronal_layout.addWidget(self.atlas_view.clut, 0, 1, 1, 1)
        coronal_layout.addWidget(self.atlas_view.cpage_ctrl, 1, 0, 1, 2)

        # ------------------ sagital / image sagital
        self.sagital_layout = QGridLayout(self.sagitalframe)
        self.sagital_layout.setSpacing(0)
        self.sagital_layout.setContentsMargins(0, 0, 0, 0)
        self.sagital_layout.addWidget(self.atlas_view.simg, 0, 0, 1, 1)
        self.sagital_layout.addWidget(self.atlas_view.slut, 0, 1, 1, 1)
        self.sagital_layout.addWidget(self.atlas_view.spage_ctrl, 1, 0, 1, 2)


        # ------------------ horizontal
        horizontal_layout = QGridLayout(self.horizontalframe)
        horizontal_layout.setSpacing(0)
        horizontal_layout.setContentsMargins(0, 0, 0, 0)
        horizontal_layout.addWidget(self.atlas_view.himg, 0, 0, 1, 1)
        horizontal_layout.addWidget(self.atlas_view.hlut, 0, 1, 1, 1)
        horizontal_layout.addWidget(self.atlas_view.hpage_ctrl, 1, 0, 1, 2)

        # ------------------ sagital copy / atlas sagital
        self.sagital_copy_layout = QGridLayout(self.sagitalcopyframe)
        self.sagital_copy_layout.setSpacing(0)
        self.sagital_copy_layout.setContentsMargins(0, 0, 0, 0)
        # self.sagital_copy_layout.addWidget(self.atlas_view.scimg, 0, 0, 1, 1)
        # self.sagital_copy_layout.addWidget(self.atlas_view.sclut, 0, 1, 1, 1)
        # sagital_copy_layout.addWidget(self.atlas_view.spage_ctrl, 1, 0, 1, 2)

        # ------------------ image
        self.image_view_layout = QGridLayout(self.histview)
        self.image_view_layout.setSpacing(0)
        self.image_view_layout.setContentsMargins(0, 0, 0, 0)
        self.image_view_layout.addWidget(self.image_view.img_stacks, 0, 0, 1, 1)
        # self.hist_lut = pg.HistogramLUTItem()
        # self.image_view_layout.addWidget(self.hist_lut, 0, 1, 1, 1)

        # -------------------- 3D view
        self.view3d.opts['distance'] = 200  # distance of camera from center
        self.view3d.opts['elevation'] = 50  # camera's angle of elevation in degrees
        self.view3d.opts['azimuth'] = 45    # camera's azimuthal angle in degrees
        self.view3d.opts['fov'] = 60        # horizontal field of view in degrees
        self.view3d.addItem(self.atlas_view.axis)
        self.view3d.addItem(self.atlas_view.grid)
        self.view3d.addItem(self.atlas_view.mesh)
        self.view3d.addItem(self.atlas_view.ap_plate_mesh)
        self.view3d.addItem(self.atlas_view.dv_plate_mesh)
        self.view3d.addItem(self.atlas_view.ml_plate_mesh)

        # -------------------- initial window
        self.coronalframe.show()
        self.sagitalframe.hide()
        self.horizontalframe.hide()
        self.sagitalcopyframe.hide()
        self.view3d.hide()
        self.histview.hide()

        self.sidebar.setCurrentIndex(0)

    # ------------------------------------------------------------------
    #
    #                      Window Control
    #
    # ------------------------------------------------------------------

    def show_only_coronal_window(self):
        if self.atlas_view.atlas_data is None:
            return
        if self.num_windows == 4:
            self.sagital_copy_layout.removeWidget(self.atlas_view.simg)
            self.sagital_copy_layout.removeWidget(self.atlas_view.slut)
            self.sagital_copy_layout.removeWidget(self.atlas_view.spage_ctrl)
            self.sagital_layout.addWidget(self.atlas_view.simg, 0, 0, 1, 1)
            self.sagital_layout.addWidget(self.atlas_view.slut, 0, 1, 1, 1)
            self.sagital_layout.addWidget(self.atlas_view.spage_ctrl, 1, 0, 1, 2)
        self.num_windows = 1
        self.atlas_view.radio_group.setVisible(True)
        self.coronalframe.setVisible(True)
        self.sagitalframe.setVisible(False)
        self.horizontalframe.setVisible(False)
        self.sagitalcopyframe.setVisible(False)
        self.view3d.setVisible(False)
        self.histview.setVisible(False)

    def show_only_sagital_window(self):
        if self.atlas_view.atlas_data is None:
            return
        if self.num_windows == 4:
            self.sagital_copy_layout.removeWidget(self.atlas_view.simg)
            self.sagital_copy_layout.removeWidget(self.atlas_view.slut)
            self.sagital_copy_layout.removeWidget(self.atlas_view.spage_ctrl)
            self.sagital_layout.addWidget(self.atlas_view.simg, 0, 0, 1, 1)
            self.sagital_layout.addWidget(self.atlas_view.slut, 0, 1, 1, 1)
            self.sagital_layout.addWidget(self.atlas_view.spage_ctrl, 1, 0, 1, 2)
        self.num_windows = 1
        self.atlas_view.radio_group.setVisible(True)
        self.coronalframe.setVisible(False)
        self.sagitalframe.setVisible(True)
        self.horizontalframe.setVisible(False)
        self.sagitalcopyframe.setVisible(False)
        self.view3d.setVisible(False)
        self.histview.setVisible(False)

    def show_only_horizontal_window(self):
        if self.atlas_view.atlas_data is None:
            return
        if self.num_windows == 4:
            self.sagital_copy_layout.removeWidget(self.atlas_view.simg)
            self.sagital_copy_layout.removeWidget(self.atlas_view.slut)
            self.sagital_copy_layout.removeWidget(self.atlas_view.spage_ctrl)
            self.sagital_layout.addWidget(self.atlas_view.simg, 0, 0, 1, 1)
            self.sagital_layout.addWidget(self.atlas_view.slut, 0, 1, 1, 1)
            self.sagital_layout.addWidget(self.atlas_view.spage_ctrl, 1, 0, 1, 2)
        self.num_windows = 1
        self.atlas_view.radio_group.setVisible(True)
        self.coronalframe.setVisible(False)
        self.sagitalframe.setVisible(False)
        self.horizontalframe.setVisible(True)
        self.sagitalcopyframe.setVisible(False)
        self.view3d.setVisible(False)
        self.histview.setVisible(False)

    def show_only_image_window(self):
        self.atlas_view.radio_group.setVisible(True)
        self.coronalframe.setVisible(False)
        self.sagitalframe.setVisible(False)
        self.horizontalframe.setVisible(False)
        self.sagitalcopyframe.setVisible(False)
        self.view3d.setVisible(False)
        self.histview.setVisible(True)

    def show_only_3d_window(self):
        if self.atlas_view.atlas_data is None:
            return
        if self.num_windows == 4:
            self.sagital_copy_layout.removeWidget(self.atlas_view.simg)
            self.sagital_copy_layout.removeWidget(self.atlas_view.slut)
            self.sagital_copy_layout.removeWidget(self.atlas_view.spage_ctrl)
            self.sagital_layout.addWidget(self.atlas_view.simg, 0, 0, 1, 1)
            self.sagital_layout.addWidget(self.atlas_view.slut, 0, 1, 1, 1)
            self.sagital_layout.addWidget(self.atlas_view.spage_ctrl, 1, 0, 1, 2)
        self.num_windows = 1
        self.atlas_view.radio_group.setVisible(True)
        self.coronalframe.setVisible(False)
        self.sagitalframe.setVisible(False)
        self.horizontalframe.setVisible(False)
        self.sagitalcopyframe.setVisible(False)
        self.view3d.setVisible(True)
        self.histview.setVisible(False)

    def show_2_windows(self):
        if self.atlas_view.atlas_data is None:
            return
        if self.num_windows == 4:
            self.sagital_copy_layout.removeWidget(self.atlas_view.simg)
            self.sagital_copy_layout.removeWidget(self.atlas_view.slut)
            self.sagital_copy_layout.removeWidget(self.atlas_view.spage_ctrl)
            self.sagital_layout.addWidget(self.atlas_view.simg, 0, 0, 1, 1)
            self.sagital_layout.addWidget(self.atlas_view.slut, 0, 1, 1, 1)
            self.sagital_layout.addWidget(self.atlas_view.spage_ctrl, 1, 0, 1, 2)
        self.num_windows = 2
        self.atlas_view.radio_group.setVisible(True)
        if self.atlas_display == 'coronal':
            self.coronalframe.setVisible(True)
            self.sagitalframe.setVisible(False)
            self.horizontalframe.setVisible(False)
        elif self.atlas_display == 'sagital':
            self.coronalframe.setVisible(False)
            self.sagitalframe.setVisible(True)
            self.horizontalframe.setVisible(False)
        else:
            self.coronalframe.setVisible(False)
            self.sagitalframe.setVisible(False)
            self.horizontalframe.setVisible(True)

        self.sagitalcopyframe.setVisible(False)
        self.view3d.setVisible(False)
        self.histview.setVisible(True)

    def show_3_windows(self):
        if self.atlas_view.atlas_data is None:
            return
        if self.num_windows == 4:
            self.sagital_copy_layout.removeWidget(self.atlas_view.simg)
            self.sagital_copy_layout.removeWidget(self.atlas_view.slut)
            self.sagital_copy_layout.removeWidget(self.atlas_view.spage_ctrl)
            self.sagital_layout.addWidget(self.atlas_view.simg, 0, 0, 1, 1)
            self.sagital_layout.addWidget(self.atlas_view.slut, 0, 1, 1, 1)
            self.sagital_layout.addWidget(self.atlas_view.spage_ctrl, 1, 0, 1, 2)
        self.num_windows = 3
        self.atlas_view.radio_group.setVisible(True)
        if self.atlas_display == 'coronal':
            self.coronalframe.setVisible(True)
            self.sagitalframe.setVisible(False)
            self.horizontalframe.setVisible(False)
        elif self.atlas_display == 'sagital':
            self.coronalframe.setVisible(False)
            self.sagitalframe.setVisible(True)
            self.horizontalframe.setVisible(False)
        else:
            self.coronalframe.setVisible(False)
            self.sagitalframe.setVisible(False)
            self.horizontalframe.setVisible(True)

        self.sagitalcopyframe.setVisible(False)
        self.view3d.setVisible(True)
        self.histview.setVisible(True)

    def show_4_windows(self):
        if self.atlas_view.atlas_data is None:
            return
        if self.num_windows != 4:
            self.sagital_layout.removeWidget(self.atlas_view.simg)
            self.sagital_layout.removeWidget(self.atlas_view.slut)
            self.sagital_layout.removeWidget(self.atlas_view.spage_ctrl)
            self.sagital_copy_layout.addWidget(self.atlas_view.simg, 0, 0, 1, 1)
            self.sagital_copy_layout.addWidget(self.atlas_view.slut, 0, 1, 1, 1)
            self.sagital_copy_layout.addWidget(self.atlas_view.spage_ctrl, 1, 0, 1, 2)
        self.num_windows = 4
        self.atlas_view.radio_group.setVisible(False)
        self.coronalframe.setVisible(True)
        self.sagitalframe.setVisible(False)
        self.horizontalframe.setVisible(True)
        self.sagitalcopyframe.setVisible(True)
        self.view3d.setVisible(True)
        self.histview.setVisible(False)



    #
    # def clear_layout(self, layout):
    #     while layout.count() > 0:
    #         item = layout.takeAt(0)
    #         if not item:
    #             continue
    #         w = item.widget()
    #         if w:
    #             w.deleteLater()
    #

    # ------------------------------------------------------------------
    #
    #                      atlas panel related
    #
    # ------------------------------------------------------------------
    def display_changed(self):
        rbtn = self.sender()
        if rbtn.isChecked():
            if rbtn.text() == "Coronal":
                self.coronalframe.setVisible(True)
                self.sagitalframe.setVisible(False)
                self.horizontalframe.setVisible(False)
                self.atlas_display = 'coronal'
            elif rbtn.text() == "Sagital":
                self.coronalframe.setVisible(False)
                self.sagitalframe.setVisible(True)
                self.horizontalframe.setVisible(False)
                self.atlas_display = 'sagital'
            else:
                self.coronalframe.setVisible(False)
                self.sagitalframe.setVisible(False)
                self.horizontalframe.setVisible(True)
                self.atlas_display = 'horizontal'
        if self.atlas_view.atlas_data is None or self.atlas_view.atlas_label is None:
            return
        self.atlas_view.working_cut_changed(self.atlas_display)
        self.reset_corners_atlas()

    def reset_corners_atlas(self):
        self.atlas_rect = (0, 0, self.atlas_view.slice_size[1], self.atlas_view.slice_size[0])
        self.atlas_tri_inside_data = []  # renew tri_inside data to empty
        for da_item in self.working_atlas_text:
            self.atlas_view.working_atlas.vb.removeItem(da_item)
        self.working_atlas_text = []
        self.atlas_corner_points = self.atlas_view.corner_points.copy()
        self.atlas_side_lines = self.atlas_view.side_lines.copy()
        self.atlas_tri_onside_data = num_side_pnt_changed(self.np_onside, self.atlas_corner_points, self.atlas_side_lines)
        self.atlas_tri_data = self.atlas_tri_onside_data + self.atlas_tri_inside_data
        self.atlas_view.working_atlas.tri_pnts.setData(pos=np.asarray(self.atlas_tri_data))
        if self.tool_box.triang_vis_btn.isChecked():
            self.update_atlas_tri_lines()

    def reset_corners_hist(self):
        self.histo_rect = (0, 0, self.image_view.img_size[1], self.image_view.img_size[0])
        self.histo_tri_inside_data = []  # renew tri_inside data to empty
        for da_item in self.working_img_text:
            self.image_view.img_stacks.vb.removeItem(da_item)
        self.working_img_text = []
        self.histo_corner_points = self.image_view.corner_points.copy()
        self.histo_side_lines = self.image_view.side_lines.copy()
        self.histo_tri_onside_data = num_side_pnt_changed(self.np_onside, self.histo_corner_points, self.histo_side_lines)

        self.histo_tri_data = self.histo_tri_onside_data + self.histo_tri_inside_data
        self.image_view.img_stacks.tri_pnts.setData(pos=np.asarray(self.histo_tri_data))
        if self.tool_box.triang_vis_btn.isChecked():
            self.update_histo_tri_lines()

    # def slice_changed(self):
    #     self.atlas_view.autoRange(items=[self.atlas_display_image.atlas_img])
    #     self.target.setVisible(False)

    # ------------------------------------------------------------------
    #
    #                      ToolBar layout and connections
    #
    # -----------------------------------------------------------------
    def init_tool_bar(self):
        self.toolbar.setStyleSheet(toolbar_style)
        # -------------- ToolBar layout and functions -------------- #
        self.tool_box.add_atlas.triggered.connect(self.load_waxholm_rat_atlas)
        self.tool_box.add_image_stack.triggered.connect(self.load_image)
        #     add_cell_act = QAction(QIcon('icons/neuron.png'), 'upload recorded cell activities', self)
        self.tool_box.vis2.triggered.connect(self.show_2_windows)
        self.tool_box.vis3.triggered.connect(self.show_3_windows)
        self.tool_box.vis4.triggered.connect(self.show_4_windows)
        self.tool_box.toh_btn.triggered.connect(self.transfer_to_hist_clicked)
        self.tool_box.toa_btn.triggered.connect(self.transfer_to_atlas_clicked)

        self.tool_box.checkable_btn_dict['moving_btn'].triggered.connect(self.moving_btn_clicked)
        self.tool_box.checkable_btn_dict['rotation_btn'].triggered.connect(self.rotation_btn_clicked)
        self.tool_box.checkable_btn_dict['lasso_btn'].triggered.connect(self.lasso_btn_clicked)
        self.tool_box.checkable_btn_dict['magic_wand_btn'].triggered.connect(self.magic_wand_btn_clicked)
        self.tool_box.checkable_btn_dict['pencil_btn'].triggered.connect(self.pencil_btn_clicked)
        self.tool_box.checkable_btn_dict['eraser_btn'].triggered.connect(self.eraser_btn_clicked)
        self.tool_box.checkable_btn_dict['line_btn'].triggered.connect(self.line_btn_clicked)
        # self.tool_box.transfer_btn.triggered.connect(self.transfer_btn_clicked)
        # self.tool_box.checkable_btn_dict['mask_btn'].triggered.connect(self.mask_btn_clicked)
        # self.tool_box.boundary_btn.triggered.connect(self.boundary_btn_clicked)
        # self.tool_box.anchor_btn.triggered.connect(self.anchor_btn_clicked)
        self.tool_box.checkable_btn_dict['triang_btn'].triggered.connect(self.triang_btn_clicked)
        self.tool_box.checkable_btn_dict['loc_btn'].triggered.connect(self.loc_btn_clicked)
        self.tool_box.bound_pnts_num.textEdited.connect(self.number_of_side_points_changed)
        self.tool_box.triang_vis_btn.clicked.connect(self.vis_tri_lines_btn_clicked)
        self.tool_box.triang_match_bnd.clicked.connect(self.matching_tri_bnd)
        # self.tool_box.loc_btn.triggered.connect(self.loc_btn_clicked)

        self.tool_box.check_btn.triggered.connect(self.accept_projection)
        # add
        self.tool_box.left_button.clicked.connect(self.moving_left_btn_clicked)

        self.toolbar.addAction(self.tool_box.add_atlas)
        self.toolbar.addAction(self.tool_box.add_image_stack)
        #     self.toolBar.addAction(add_cell_act)
        self.toolbar.addAction(self.tool_box.vis2)
        self.toolbar.addAction(self.tool_box.vis3)
        self.toolbar.addAction(self.tool_box.vis4)
        self.toolbar.addSeparator()
        self.toolbox_btn_keys = list(self.tool_box.checkable_btn_dict.keys())
        for da_key in self.toolbox_btn_keys:
            self.toolbar.addAction(self.tool_box.checkable_btn_dict[da_key])
        # self.toolbar.addAction(self.tool_box.boundary_btn)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.tool_box.toa_btn)
        self.toolbar.addAction(self.tool_box.toh_btn)

        self.toolbar.addWidget(self.tool_box.sep_label)

        moving_action = self.toolbar.addWidget(self.tool_box.moving_wrap)
        rotation_action = self.toolbar.addWidget(self.tool_box.rotation_wrap)
        magic_wand_action = self.toolbar.addWidget(self.tool_box.magic_wand_wrap)
        pencil_action = self.toolbar.addWidget(self.tool_box.pencil_wrap)
        eraser_action = self.toolbar.addWidget(self.tool_box.eraser_wrap)
        lasso_action = self.toolbar.addWidget(self.tool_box.lasso_wrap)
        line_action = self.toolbar.addWidget(self.tool_box.line_wrap)
        triang_action = self.toolbar.addWidget(self.tool_box.triang_wrap)
        loc_action = self.toolbar.addWidget(self.tool_box.cell_count_wrap)

        self.toolbar_wrap_action_dict['moving_act'] = moving_action
        self.toolbar_wrap_action_dict['rotation_act'] = rotation_action
        self.toolbar_wrap_action_dict['pencil_act'] = pencil_action
        self.toolbar_wrap_action_dict['eraser_act'] = eraser_action
        self.toolbar_wrap_action_dict['lasso_act'] = lasso_action
        self.toolbar_wrap_action_dict['magic_wand_act'] = magic_wand_action
        self.toolbar_wrap_action_dict['line_act'] = line_action
        self.toolbar_wrap_action_dict['triang_act'] = triang_action
        self.toolbar_wrap_action_dict['loc_act'] = loc_action

        self.toolbar_wrap_action_keys = list(self.toolbar_wrap_action_dict.keys())
        for da_key in self.toolbar_wrap_action_keys:
            self.toolbar_wrap_action_dict[da_key].setVisible(False)

        self.np_onside = int(self.tool_box.bound_pnts_num.text())

    # ------------------------------------------------------------------
    #              ToolBar checkable btn clicked
    # ------------------------------------------------------------------
    def moving_btn_clicked(self):
        if self.eraser_is_on:
            self.remove_eraser_symbol()
            self.eraser_is_on = False
        self.set_toolbox_btns_unchecked('moving')

    def lasso_btn_clicked(self):
        if self.eraser_is_on:
            self.remove_eraser_symbol()
        self.set_toolbox_btns_unchecked('lasso')

    def magic_wand_btn_clicked(self):
        if self.eraser_is_on:
            self.remove_eraser_symbol()
            self.eraser_is_on = False
        self.set_toolbox_btns_unchecked('magic_wand')

    def pencil_btn_clicked(self):
        if self.eraser_is_on:
            self.remove_eraser_symbol()
            self.eraser_is_on = False
        self.set_toolbox_btns_unchecked('pencil')

    def eraser_btn_clicked(self):
        self.set_toolbox_btns_unchecked('eraser')

    def rotation_btn_clicked(self):
        if self.eraser_is_on:
            self.remove_eraser_symbol()
            self.eraser_is_on = False
        self.set_toolbox_btns_unchecked('rotation')

    def triang_btn_clicked(self):
        if self.eraser_is_on:
            self.remove_eraser_symbol()
            self.eraser_is_on = False
        self.set_toolbox_btns_unchecked('triang')
        self.show_triangle_points('triang')

    def line_btn_clicked(self):
        if self.eraser_is_on:
            self.remove_eraser_symbol()
            self.eraser_is_on = False
        self.set_toolbox_btns_unchecked('line')

    def loc_btn_clicked(self):
        if self.eraser_is_on:
            self.remove_eraser_symbol()
            self.eraser_is_on = False
        self.set_toolbox_btns_unchecked('loc')

    def set_toolbox_btns_unchecked(self, current_btn):
        if self.tool_box.checkable_btn_dict['{}_btn'.format(current_btn)].isChecked():
            self.current_checked_tool = current_btn
            for da_key in self.toolbox_btn_keys:
                if current_btn in da_key:
                    continue
                else:
                    self.tool_box.checkable_btn_dict[da_key].setChecked(False)
            for da_key in self.toolbar_wrap_action_keys:
                if current_btn in da_key:
                    self.toolbar_wrap_action_dict[da_key].setVisible(True)
                else:
                    self.toolbar_wrap_action_dict[da_key].setVisible(False)
        else:
            self.current_checked_tool = None
            self.toolbar_wrap_action_dict['{}_act'.format(current_btn)].setVisible(False)



    def remove_eraser_symbol(self):
        self.image_view.img_stacks.circle_follow.clear()
        self.image_view.img_stacks.circle_follow.updateItems()

    # ------------------------------------------------------------------
    #
    #                      SideBar layout and connections
    #
    # ------------------------------------------------------------------
    def init_side_bar(self):
        self.sidebar.setStyleSheet(tab_style)
        self.sidebar.setIconSize(QtCore.QSize(24, 24))
        self.sidebar.setTabIcon(0, QtGui.QIcon('icons/sidebar/atlascontrol.svg'))
        # self.sidebar.setIconSize(QtCore.QSize(24, 24))
        self.sidebar.setTabIcon(1, QtGui.QIcon('icons/sidebar/treeview.svg'))
        # self.sidebar.setIconSize(QtCore.QSize(24, 24))
        self.sidebar.setTabIcon(2, QtGui.QIcon('icons/sidebar/tool.svg'))
        # self.sidebar.setIconSize(QtCore.QSize(24, 24))
        self.sidebar.setTabIcon(3, QtGui.QIcon('icons/sidebar/layers.svg'))
        # self.sidebar.setIconSize(QtCore.QSize(24, 24))
        self.sidebar.setTabIcon(4, QtGui.QIcon('icons/sidebar/object.svg'))

        # ---------------------------- atlas control panel
        atlas_panel_layout = QVBoxLayout(self.atlascontrolpanel)
        atlas_panel_layout.setContentsMargins(0, 0, 0, 0)
        atlas_panel_layout.setAlignment(Qt.AlignTop)
        atlas_control_label = QLabel('Atlasing Controller')
        atlas_control_label.setStyleSheet(sidebar_title_label_style)

        atlas_panel_layout.addWidget(atlas_control_label)
        atlas_panel_layout.addWidget(self.atlas_view.sidebar_wrap)

        # ---------------------------- Label Panel
        label_panel_layout = QVBoxLayout(self.treeviewpanel)
        label_panel_layout.setContentsMargins(0, 0, 0, 0)
        label_panel_layout.setAlignment(Qt.AlignTop)
        label_control_label = QLabel('Segmentation View Controller')
        label_control_label.setStyleSheet(sidebar_title_label_style)

        label_panel_layout.addWidget(label_control_label)

        label_container = QFrame()
        label_container_layout = QVBoxLayout(label_container)
        label_container_layout.setContentsMargins(0, 0, 0, 0)
        label_container_layout.setSpacing(5)
        label_container_layout.setAlignment(Qt.AlignTop)
        show_3d_button = QPushButton()
        show_3d_button.setStyleSheet(
            'margin-left: 5px; margin-right:5px; margin-bottom:10px; padding-top:3px; height: 20px;')
        show_3d_button.setCheckable(True)
        show_3d_button.setText('Show in 3D view')
        show_3d_button.clicked.connect(self.show_small_area_in_3d)

        composition_label = QLabel('Composition: ')
        self.composition_combo = QComboBox()
        self.composition_combo.addItems(['opaque', 'translucent', 'additive'])
        self.composition_combo.currentIndexChanged.connect(self.composition_3d_changed)

        label_container_layout.addWidget(show_3d_button)
        label_container_layout.addWidget(self.composition_combo)
        label_container_layout.addWidget(self.atlas_view.label_tree)
        label_panel_layout.addWidget(label_container)

        # ---------------------------- layer panel
        layer_panel_layout = QVBoxLayout(self.layerpanel)
        layer_panel_layout.setContentsMargins(0, 0, 0, 0)
        layer_panel_layout.setSpacing(0)
        layer_panel_layout.setAlignment(Qt.AlignTop)
        layer_control_label = QLabel('Layer View Controller')
        layer_control_label.setStyleSheet(sidebar_title_label_style)

        layer_btm_ctrl = QFrame()
        layer_btm_ctrl.setStyleSheet('background-color:rgb(65, 65, 65);')
        layer_btm_ctrl.setFixedHeight(24)
        layer_btm_layout = QHBoxLayout(layer_btm_ctrl)
        layer_btm_layout.setContentsMargins(0, 0, 0, 0)
        layer_btm_layout.setSpacing(5)
        layer_btm_layout.setAlignment(Qt.AlignRight)
        # layer_btm_layout.addWidget(self.lcontrols.vis_ai_layer_btn)
        # layer_btm_layout.addWidget(self.lcontrols.vis_hi_layer_btn)
        layer_btm_layout.addWidget(self.layer_ctrl.add_layer_btn)
        layer_btm_layout.addWidget(self.layer_ctrl.delete_layer_btn)

        layer_panel_layout.addWidget(layer_control_label)
        layer_panel_layout.addWidget(self.layer_ctrl)
        layer_panel_layout.addWidget(layer_btm_ctrl)
        # self.layerpanel.setEnabled(False)

        # ---------------------------- image panel
        image_panel_layout = QVBoxLayout(self.imagecontrolpanel)
        image_panel_layout.setContentsMargins(0, 0, 0, 0)
        image_panel_layout.setSpacing(0)
        image_panel_layout.setAlignment(Qt.AlignTop)
        image_control_label = QLabel('Image View Controller')
        image_control_label.setStyleSheet(sidebar_title_label_style)

        image_panel_layout.addWidget(image_control_label)

        space_item = QSpacerItem(300, 10, QSizePolicy.Expanding)

        image_container = QFrame()
        image_container_layout = QVBoxLayout(image_container)
        image_container_layout.setSpacing(5)
        image_container_layout.setAlignment(Qt.AlignTop)
        image_container_layout.addWidget(self.image_view.outer_frame)
        # image_container_layout.addSpacerItem(space_item)
        # image_container_layout.addWidget(self.image_view.chn_widget_wrap)

        image_panel_layout.addWidget(image_container)
        image_panel_layout.insertStretch(-1, 1)

        # ---------------------------- object panel
        object_panel_layout = QVBoxLayout(self.probecontrolpanel)
        object_panel_layout.setContentsMargins(0, 0, 0, 0)
        object_panel_layout.setSpacing(0)
        object_panel_layout.setAlignment(Qt.AlignTop)
        object_control_label = QLabel('Object View Controller')
        object_control_label.setStyleSheet(sidebar_title_label_style)

        object_btm_ctrl = QFrame()
        object_btm_ctrl.setStyleSheet('background-color:rgb(65, 65, 65);')
        object_btm_ctrl.setFixedHeight(24)
        object_btm_layout = QHBoxLayout(object_btm_ctrl)
        object_btm_layout.setContentsMargins(0, 0, 0, 0)
        object_btm_layout.setSpacing(5)
        object_btm_layout.setAlignment(Qt.AlignRight)

        object_btm_layout.addWidget(self.object_ctrl.merge_probe_btn)
        object_btm_layout.addWidget(self.object_ctrl.merge_virus_btn)
        object_btm_layout.addWidget(self.object_ctrl.merge_cell_btn)
        object_btm_layout.addWidget(self.object_ctrl.merge_line_btn)
        object_btm_layout.addWidget(self.object_ctrl.merge_bnd_btn)
        object_btm_layout.addWidget(self.object_ctrl.add_object_btn)
        object_btm_layout.addWidget(self.object_ctrl.delete_object_btn)

        object_panel_layout.addWidget(object_control_label)
        object_panel_layout.addWidget(self.object_ctrl.outer_frame)
        object_panel_layout.addWidget(object_btm_ctrl)

        # self.tool_box.segment_level_slider.valueChanged.connect(self.segment_level_changed)
        # self.toolbar.addWidget(self.tool_box.pos_label, alignment=Qt.AlignRight)
    # ------------------------------------------------------------------
    #
    #               ToolBar lasso btn related
    #
    # ------------------------------------------------------------------
    def inactive_lasso(self):
        # if self.lasso_is_closure:
        self.lasso_pnts = []
        self.image_view.img_stacks.lasso_path.clear()
        self.image_view.img_stacks.lasso_path.updateItems()

    def lasso_points_clicked(self, points, ev):
        if len(self.lasso_pnts) == 0:
            return
        clicked_ind = ev[0].index()
        if clicked_ind == 0 and len(self.lasso_pnts) >= 3:
            self.lasso_pnts.append(self.lasso_pnts[0])
            self.image_view.img_stacks.lasso_path.setData(np.asarray(self.lasso_pnts))
            self.lasso_is_closure = True
        else:
            self.lasso_pnts = []
            self.image_view.img_stacks.lasso_path.clear()
            self.image_view.img_stacks.lasso_path.updateItems()
            self.lasso_is_closure = False
        print(self.lasso_is_closure)
        print(self.lasso_pnts)
    # ------------------------------------------------------------------
    #
    #               ToolBar rotation btn related
    #
    # ------------------------------------------------------------------
    def rotate_clockwise_btn_clicked(self):
        print('moving left')

    # ------------------------------------------------------------------
    #
    #               ToolBar moving btn related
    #
    # ------------------------------------------------------------------
    def moving_left_btn_clicked(self):
        print('moving left')

    # ------------------------------------------------------------------
    #
    #               ToolBar loc btn related
    #
    # ------------------------------------------------------------------
    def cell_aim_btn_clicked(self):
        print('aim btn clicked')

    # ------------------------------------------------------------------
    #
    #               ToolBar triangle btn related
    #
    # ------------------------------------------------------------------
    def show_triangle_points(self, current_btn):
        if self.tool_box.checkable_btn_dict['{}_btn'.format(current_btn)].isChecked():
            if self.atlas_tri_data:
                if not self.atlas_view.working_atlas.tri_pnts.isVisible():
                    self.atlas_view.working_atlas.tri_pnts.setVisible(True)
            if self.histo_tri_data:
                if not self.image_view.img_stacks.tri_pnts.isVisible():
                    self.image_view.img_stacks.tri_pnts.setVisible(True)
        else:
            if self.atlas_tri_data:
                if self.atlas_view.working_atlas.tri_pnts.isVisible():
                    self.atlas_view.working_atlas.tri_pnts.setVisible(False)
            if self.histo_tri_data:
                if self.image_view.img_stacks.tri_pnts.isVisible():
                    self.image_view.img_stacks.tri_pnts.setVisible(False)

    def number_of_side_points_changed(self):
        self.np_onside = int(self.tool_box.bound_pnts_num.text())
        if self.atlas_view.atlas_data is not None:
            self.atlas_tri_onside_data = num_side_pnt_changed(self.np_onside, self.atlas_corner_points,
                                                              self.atlas_side_lines)
            self.atlas_tri_data = self.atlas_tri_onside_data + self.atlas_tri_inside_data
            self.atlas_view.working_atlas.tri_pnts.setData(pos=np.asarray(self.atlas_tri_data))
            if self.tool_box.triang_vis_btn.isChecked():
                self.update_atlas_tri_lines()
        if self.image_view.image_file is not None:
            self.histo_tri_onside_data = num_side_pnt_changed(self.np_onside, self.histo_corner_points,
                                                              self.histo_side_lines)
            self.histo_tri_data = self.histo_tri_onside_data + self.histo_tri_inside_data
            self.image_view.img_stacks.tri_pnts.setData(pos=np.asarray(self.histo_tri_data))
            if self.tool_box.triang_vis_btn.isChecked():
                self.update_histo_tri_lines()

    def remove_histo_tri_lines(self):
        if self.image_view.img_stacks.tri_lines_list:
            for da_item in self.image_view.img_stacks.tri_lines_list:
                self.image_view.img_stacks.vb.removeItem(da_item)
            self.image_view.img_stacks.tri_lines_list = []

    def update_histo_tri_lines(self):
        self.remove_histo_tri_lines()
        histo_tri_lines = get_tri_lines(self.histo_rect, self.histo_tri_data)
        for el in histo_tri_lines:
            pt1 = [el[0], el[1]]
            pt2 = [el[2], el[3]]
            self.image_view.img_stacks.tri_lines_list.append(pg.PlotDataItem(pen=self.tri_line_style))
            self.image_view.img_stacks.tri_lines_list[-1].setData(np.asarray([pt1, pt2]))
            self.image_view.img_stacks.vb.addItem(self.image_view.img_stacks.tri_lines_list[-1])

    def remove_atlas_tri_lines(self):
        if self.atlas_view.working_atlas.tri_lines_list:
            for da_item in self.atlas_view.working_atlas.tri_lines_list:
                self.atlas_view.working_atlas.vb.removeItem(da_item)
            self.atlas_view.working_atlas.tri_lines_list = []

    def update_atlas_tri_lines(self):
        self.remove_atlas_tri_lines()
        atlas_tri_lines = get_tri_lines(self.atlas_rect, self.atlas_tri_data)
        for el in atlas_tri_lines:
            pt1 = [el[0], el[1]]
            pt2 = [el[2], el[3]]
            self.atlas_view.working_atlas.tri_lines_list.append(pg.PlotDataItem(pen=self.tri_line_style))
            self.atlas_view.working_atlas.tri_lines_list[-1].setData(np.asarray([pt1, pt2]))
            self.atlas_view.working_atlas.vb.addItem(self.atlas_view.working_atlas.tri_lines_list[-1])

    def vis_tri_lines_btn_clicked(self):
        if self.tool_box.triang_vis_btn.isChecked():
            if self.atlas_tri_data:
                self.update_atlas_tri_lines()
            if self.histo_tri_data:
                self.update_histo_tri_lines()
        else:
            if self.atlas_tri_data:
                self.remove_atlas_tri_lines()
            if self.histo_tri_data:
                self.remove_histo_tri_lines()

    def matching_tri_bnd(self):
        if self.image_view.image_file is None:
            return
        if self.atlas_view.atlas_data is None:
            return
        if self.atlas_view.atlas_label is None:
            return
        if not self.histo_tri_inside_data:
            return
        print('matching bnd')
        slice_size = self.atlas_view.slice_size
        image_size = self.image_view.img_size

        histo_pnts = np.asarray(self.histo_tri_inside_data)
        rect_img = cv2.boundingRect(histo_pnts.astype(np.float32))

        if not self.atlas_tri_inside_data:
            label_img = self.atlas_view.working_atlas.label_img.image.copy()
            none_zero_label = np.where(label_img != 0)
            if len(none_zero_label) == 0:
                return
            atlas_pnts = np.vstack([none_zero_label[1], none_zero_label[0]]).T
        else:
            atlas_pnts = np.asarray(self.atlas_tri_inside_data)
        rect_atlas = cv2.boundingRect(atlas_pnts.astype(np.float32))

        self.small_atlas_rect = rect_atlas
        self.small_histo_rect = rect_img

        self.atlas_corner_points, self.atlas_side_lines, self.histo_corner_points, self.histo_side_lines = \
            match_sides_points(rect_atlas, slice_size, rect_img, image_size)

        self.atlas_tri_onside_data = num_side_pnt_changed(self.np_onside, self.atlas_corner_points, self.atlas_side_lines)
        self.atlas_tri_data = self.atlas_tri_onside_data + self.atlas_tri_inside_data
        self.atlas_view.working_atlas.tri_pnts.setData(pos=np.asarray(self.atlas_tri_data))

        self.histo_tri_onside_data = num_side_pnt_changed(self.np_onside, self.histo_corner_points, self.histo_side_lines)
        self.histo_tri_data = self.histo_tri_onside_data + self.histo_tri_inside_data
        self.image_view.img_stacks.tri_pnts.setData(pos=np.asarray(self.histo_tri_data))
        if self.tool_box.triang_vis_btn.isChecked():
            self.update_histo_tri_lines()
            self.update_atlas_tri_lines()

    # ------------------------------------------------------------------
    #
    #               ToolBar transform btn clicked
    #
    # ------------------------------------------------------------------
    def transfer_to_hist_clicked(self):
        if self.image_view.image_file is None:
            return
        if self.atlas_view.atlas_data is None:
            return
        if self.atlas_view.atlas_label is None:
            return
        print('transfer to hist')
        if not self.a2h_transferred:
            label_img = self.atlas_view.working_atlas.label_img.image.copy()
            lut = self.atlas_view.label_tree.current_lut.copy()
            da_label_img = make_label_rgb_img(label_img, lut)

            img_wrap = np.zeros((self.image_view.img_size[0], self.image_view.img_size[1], 3), np.float32)

            if self.histo_tri_inside_data and self.atlas_tri_inside_data:
                print('match triangles to hist')
                a_temp = len(self.histo_tri_data)
                b_temp = len(self.atlas_tri_data)
                if a_temp != b_temp:
                    print('number of points are not mathcing.')
                    return
                input_img = da_label_img.copy()

                # rect = (0, 0, self.image_view.img_size[1], self.image_view.img_size[0])

                subdiv = cv2.Subdiv2D(self.histo_rect)
                for p in self.histo_tri_data:
                    subdiv.insert(p)

                tri_vet_inds = get_vertex_ind_in_triangle(subdiv)
                for i in range(len(tri_vet_inds)):
                    da_inds = tri_vet_inds[i]
                    t1 = [self.atlas_tri_data[da_inds[0]], self.atlas_tri_data[da_inds[1]], self.atlas_tri_data[da_inds[2]]]
                    t2 = [self.histo_tri_data[da_inds[0]], self.histo_tri_data[da_inds[1]], self.histo_tri_data[da_inds[2]]]
                    t1 = np.reshape(t1, (3, 2))
                    t2 = np.reshape(t2, (3, 2))
                    warp_triangle(input_img, img_wrap, t1, t2, True)
            else:
                if self.small_atlas_rect is not None:
                    atlas_rect = self.small_atlas_rect
                    histo_rect = self.small_histo_rect
                else:
                    atlas_rect = self.atlas_rect
                    histo_rect = self.histo_rect
                src_xrange = (atlas_rect[0], atlas_rect[0] + atlas_rect[2])
                src_yrange = (atlas_rect[1], atlas_rect[1] + atlas_rect[3])
                src_img = da_label_img[src_yrange[0]:src_yrange[1], src_xrange[0]:src_xrange[1], :].copy()

                da_dim = (histo_rect[2], histo_rect[3])
                resized_des = cv2.resize(src_img, da_dim, interpolation=cv2.INTER_LINEAR)

                des_xrange = (histo_rect[0], histo_rect[0] + histo_rect[2])
                des_yrange = (histo_rect[1], histo_rect[1] + histo_rect[3])
                img_wrap[des_yrange[0]:des_yrange[1], des_xrange[0]:des_xrange[1]] = resized_des

            self.image_view.img_stacks.atlas_label.setImage(img_wrap)
            res = cv2.resize(img_wrap, self.image_view.tb_size, interpolation=cv2.INTER_AREA)
            self.master_layers(res, layer_type='image-overlay')
            self.init_a2h_tri_pnts = self.histo_tri_data.copy()
            self.init_a2h_overlay_img = img_wrap.copy()
            self.a2h_transferred = True
            self.tool_box.toh_btn.setIcon(self.tool_box.toh_btn_on_icon)
        else:
            self.a2h_transferred = False
            self.tool_box.toh_btn.setIcon(self.tool_box.toh_btn_off_icon)

    #
    def transfer_to_atlas_clicked(self):
        if self.image_view.image_file is None:
            return
        if self.atlas_view.atlas_data is None:
            return
        if self.atlas_view.atlas_label is None:
            return
        print('to A clicked')
        if not self.h2a_transferred:
            if self.image_view.image_file.is_rgb:
                input_img = self.image_view.current_img.copy()
            else:
                czi_img = self.image_view.current_img.copy()
                channel_hsv = self.image_view.image_file.hsv_colors
                img_temp = merge_channels_into_single_img(czi_img, channel_hsv)
                input_img = cv2.normalize(img_temp, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
                input_img = input_img.astype('uint8')

            img_wrap = np.zeros((self.atlas_view.slice_size[0], self.atlas_view.slice_size[1], 3), np.float32)

            if self.histo_tri_inside_data and self.atlas_tri_inside_data:
                print('match triangles to atlas')
                a_temp = len(self.histo_tri_data)
                b_temp = len(self.atlas_tri_data)
                if a_temp != b_temp:
                    print('number of points are not matching.')
                    return

                subdiv = cv2.Subdiv2D(self.atlas_rect)
                for p in self.atlas_tri_data:
                    subdiv.insert(p)

                tri_vet_inds = get_vertex_ind_in_triangle(subdiv)
                for i in range(len(tri_vet_inds)):
                    da_inds = tri_vet_inds[i]
                    t2 = [self.atlas_tri_data[da_inds[0]], self.atlas_tri_data[da_inds[1]],
                          self.atlas_tri_data[da_inds[2]]]
                    t1 = [self.histo_tri_data[da_inds[0]], self.histo_tri_data[da_inds[1]],
                          self.histo_tri_data[da_inds[2]]]
                    t1 = np.reshape(t1, (3, 2))
                    t2 = np.reshape(t2, (3, 2))
                    warp_triangle(input_img, img_wrap, t1, t2, True)
            else:
                if self.small_atlas_rect is not None:
                    atlas_rect = self.small_atlas_rect
                    histo_rect = self.small_histo_rect
                else:
                    atlas_rect = self.atlas_rect
                    histo_rect = self.histo_rect
                src_xrange = (histo_rect[0], histo_rect[0] + histo_rect[2])
                src_yrange = (histo_rect[1], histo_rect[1] + histo_rect[3])
                src_img = input_img[src_yrange[0]:src_yrange[1], src_xrange[0]:src_xrange[1], :].copy()

                da_dim = (atlas_rect[2], atlas_rect[3])
                resized_des = cv2.resize(src_img, da_dim, interpolation=cv2.INTER_LINEAR)

                des_xrange = (atlas_rect[0], atlas_rect[0] + atlas_rect[2])
                des_yrange = (atlas_rect[1], atlas_rect[1] + atlas_rect[3])
                img_wrap[des_yrange[0]:des_yrange[1], des_xrange[0]:des_xrange[1]] = resized_des

            self.atlas_view.working_atlas.overlay_img.setImage(img_wrap)
            res = cv2.resize(img_wrap, self.atlas_view.slice_tb_size, interpolation=cv2.INTER_AREA)
            self.master_layers(res, layer_type='atlas-overlay')
            self.init_h2a_tri_pnts = self.atlas_tri_data.copy()
            self.init_h2a_overlay_img = img_wrap.copy()
            self.h2a_transferred = True
            self.tool_box.toa_btn.setIcon(self.tool_box.toa_btn_on_icon)
        else:
            self.h2a_transferred = False
            self.tool_box.toa_btn.setIcon(self.tool_box.toa_btn_off_icon)

    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    #
    #                      Image Processing
    #
    # ------------------------------------------------------------------
    def update_histo_tri_onside_data(self):
        print('image_changed')
        self.reset_corners_hist()
        self.working_mask_data = np.ones(self.image_view.img_size).astype('uint8')

    def img_stacks_clicked(self, pos):
        x = pos[0]
        y = pos[1]
        print('image', (x, y))
        if self.image_view.image_file is None:
            return
        # ------------------------- pencil
        if self.tool_box.checkable_btn_dict['pencil_btn'].isChecked():
            self.inactive_lasso()
            self.working_img_pnts.append([x, y])
            # self.working_img_text.append(pg.TextItem(str(len(self.working_img_pnts))))
            self.image_view.img_stacks.drawing_pnts.setData(pos=np.asarray(self.working_img_pnts))
            # self.image_view.img_stacks.vb.addItem(self.working_img_text[-1])
            # self.working_img_text[-1].setPos(x, y)
        # ------------------------- eraser
        elif self.tool_box.checkable_btn_dict['eraser_btn'].isChecked():
            self.inactive_lasso()
            r = self.tool_box.eraser_size_slider.value()
            mask_img = np.zeros(self.image_view.img_size, dtype=np.uint8)
            cv2.circle(mask_img, center=(int(x), int(y)), radius=r, color=255, thickness=-1)
            mask_img = 255 - mask_img
            if not self.layer_ctrl.layer_index or len(self.layer_ctrl.current_layer_ind) > 1:
                print('check')
                return
            else:
                da_ind = np.where(np.ravel(self.layer_ctrl.layer_index) == self.layer_ctrl.current_layer_ind[0])[0]
                da_link = self.layer_ctrl.layer_link[da_ind[0]]
                if da_link == 'img-virus':
                    dst = cv2.bitwise_and(self.working_virus_data, self.working_virus_data, mask=mask_img)
                    res = cv2.resize(dst, self.image_view.tb_size, interpolation=cv2.INTER_AREA)
                    self.image_view.img_stacks.virus_img.setImage(dst)
                    self.working_virus_data = dst
                elif da_link == 'img-mask':
                    self.working_mask_data = cv2.bitwise_and(self.working_mask_data.astype(np.uint8),
                                                             self.working_mask_data.astype(np.uint8), mask=mask_img)
                    res = cv2.resize(self.working_mask_data, self.image_view.tb_size, interpolation=cv2.INTER_AREA)
                    self.image_view.img_stacks.mask_img.setImage(self.working_mask_data)
                elif da_link == 'img-boundary':
                    self.working_boundary_data = cv2.bitwise_and(self.working_boundary_data.astype(np.uint8),
                                                                 self.working_mask_data.astype(np.uint8), mask=mask_img)
                    res = cv2.resize(self.working_boundary_data, self.image_view.tb_size, interpolation=cv2.INTER_AREA)
                    self.image_view.img_stacks.boundary.setImage(self.working_boundary_data)
                else:
                    return
                self.layer_ctrl.layer_list[da_ind[0]].set_thumbnail_data(res)
        # ------------------------- magic wand -- virus
        elif self.tool_box.checkable_btn_dict['magic_wand_btn'].isChecked():
            self.inactive_lasso()
            tol_val = int(self.tool_box.magic_tol_val.text())
            if self.image_view.image_file.is_rgb:
                src_img = self.image_view.current_img.copy()
                des_img = src_img.copy()
                da_hsv_img = cv2.cvtColor(src_img, cv2.COLOR_RGB2HSV)
                da_hsv_color = da_hsv_img[int(y), int(x)]
                h_lower = da_hsv_color[0] - tol_val
                h_lower = h_lower if tol_val < da_hsv_color[0] else 0
                h_upper = da_hsv_color[0] + tol_val
                h_upper = h_upper if h_upper <= 180 else 180
                hsv_lower = (h_lower, 200, 200)
                hsv_upper = (h_upper, 255, 255)
                self.working_mask_data = cv2.inRange(src_img, hsv_lower, hsv_upper)
                # des_img = cv2.bitwise_and(des_img, des_img, mask=self.working_mask_data)
            else:
                print(self.image_view.current_img.shape[:2])
                white_img = np.ones(self.image_view.img_size).astype('uint8')
                mask_img = white_img.copy()

                # full_mask = np.ones(self.image_view.current_img.shape).astype('uint8')
                for i in range(self.image_view.image_file.n_channels):
                    if not self.image_view.channel_visible[i]:
                        continue
                    temp = self.image_view.current_img[:, :, i]
                    selected_color = temp[int(y), int(x)]
                    lower_range = selected_color - tol_val
                    upper_range = selected_color + tol_val
                    ret, thresh = cv2.threshold(temp, lower_range, upper_range, cv2.THRESH_BINARY)
                    mask_img = cv2.bitwise_and(mask_img, mask_img, mask=thresh.astype(np.uint8))
                modifiers = QApplication.keyboardModifiers()
                if modifiers == Qt.ShiftModifier:
                    self.working_mask_data = cv2.bitwise_or(self.working_mask_data, mask_img, mask=white_img)
                else:
                    self.working_mask_data = mask_img * 255

            ksize = int(self.tool_box.magic_wand_ksize.text())
            kernel_shape = self.tool_box.magic_wand_kernel.currentText()
            if ksize != 0 and kernel_shape != "Kernel":
                if kernel_shape == "Rectangular":
                    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (ksize, ksize))
                elif kernel_shape == "Elliptical":
                    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ksize, ksize))
                else:
                    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (ksize, ksize))
                temp = self.working_mask_data.copy()
                open_img = cv2.morphologyEx(temp, cv2.MORPH_OPEN, kernel)
                close_img = cv2.morphologyEx(open_img, cv2.MORPH_CLOSE, kernel)
                self.working_mask_data = 255 - close_img

            self.image_view.img_stacks.mask_img.setImage(self.working_mask_data)
            res = cv2.resize(self.working_mask_data, self.image_view.tb_size, interpolation=cv2.INTER_AREA)
            self.master_layers(res, layer_type='img-mask')
            # self.image_view.img_stacks.virus_img.setImage(self.working_virus_data)
            # res = cv2.resize(self.working_virus_data, self.image_view.tb_size, interpolation=cv2.INTER_AREA)
            # self.master_layers(res, layer_type='img-virus')

        # ------------------------- lasso
        elif self.tool_box.checkable_btn_dict['lasso_btn'].isChecked():
            if self.lasso_is_closure:
                self.lasso_pnts = []
                self.image_view.img_stacks.lasso_path.clear()
                self.image_view.img_stacks.lasso_path.updateItems()
                self.lasso_is_closure = False
                return
            new_pnt = np.array([x, y])
            if len(self.lasso_pnts) > 1:
                dists = np.sum((np.asarray(self.lasso_pnts[0]) - new_pnt) ** 2)
            else:
                dists = 1e5
            if dists < 5:
                self.lasso_pnts.append(self.lasso_pnts[0])
                self.lasso_is_closure = True
            else:
                self.lasso_pnts.append([x, y])
            drawing_pnts = np.asarray(self.lasso_pnts)
            self.image_view.img_stacks.lasso_path.setData(drawing_pnts)
        # ------------------------- triang -- triangulation pnts
        elif self.tool_box.checkable_btn_dict['triang_btn'].isChecked():
            self.inactive_lasso()
            if self.a2h_transferred or self.h2a_transferred:
                return
            self.histo_tri_inside_data.append([x, y])
            self.histo_tri_data = self.histo_tri_onside_data + self.histo_tri_inside_data
            self.image_view.img_stacks.tri_pnts.setData(pos=np.asarray(self.histo_tri_data))
            self.working_img_text.append(pg.TextItem(str(len(self.histo_tri_data) - (self.np_onside - 1) * 4)))
            self.image_view.img_stacks.vb.addItem(self.working_img_text[-1])
            self.working_img_text[-1].setPos(x, y)
            if self.tool_box.triang_vis_btn.isChecked():
                self.update_histo_tri_lines()
            # mask = np.zeros(self.image_view.current_gray_img.shape[:2], dtype="uint8")
            # for i in range(len(self.working_probe_data)):
            #     mask[self.working_probe_data[i][0], self.working_probe_data[i][1]] = 255
            # res = cv2.resize(mask.T, self.image_view.tb_size, interpolation=cv2.INTER_AREA)
            # self.master_layers(res, layer_type='img-probes')
        # ------------------------- loc -- cell
        elif self.tool_box.checkable_btn_dict['loc_btn'].isChecked():
            self.inactive_lasso()
            self.working_cell_data.append([x, y])
            self.image_view.img_stacks.cell_pnts.setData(pos=np.asarray(self.working_cell_data))
            self.cell_number += 1
            self.tool_box.cell_count_val.setText(str(self.cell_number))
            mask = np.zeros(self.image_view.current_gray_img.shape[:2], dtype="uint8")
            for i in range(len(self.working_cell_data)):
                mask[self.working_cell_data[i][0], self.working_cell_data[i][1]] = 255
            res = cv2.resize(mask.T, self.image_view.tb_size, interpolation=cv2.INTER_AREA)
            self.master_layers(res, layer_type='img-cells')
        # ------------------------- lines  -- probe
        elif self.tool_box.checkable_btn_dict['line_btn'].isChecked():
            self.inactive_lasso()
            self.working_probe_data.append([x, y])
            self.image_view.img_stacks.probe_pnts.setData(pos=np.asarray(self.working_probe_data))
            mask = np.zeros(self.image_view.current_img.shape[:2], dtype="uint8")
            for i in range(len(self.working_probe_data)):
                mask[self.working_probe_data[i][0], self.working_probe_data[i][1]] = 255
            res = cv2.resize(mask.T, self.image_view.tb_size, interpolation=cv2.INTER_AREA)
            self.master_layers(res, layer_type='img-probes')
        else:
            return

    def img_stacks_hovered(self, event):
        if event.isExit():
            return
        try:
            pos = (event.pos())
        except (IndexError, AttributeError):
            return
        y = pos.y()
        x = pos.x()
        if self.tool_box.checkable_btn_dict['eraser_btn'].isChecked():
            self.eraser_is_on = True
            r = self.tool_box.eraser_size_slider.value()
            shp = self.image_view.current_img.shape
            if x - r > 0 and x + r < shp[1] and y - r > 0 and y + r < shp[0]:
                data = self.tool_box.circle.copy()
                data[:, 0] = data[:, 0] + x
                data[:, 1] = data[:, 1] + y
                self.image_view.img_stacks.circle_follow.setData(data)
        self.statusbar.showMessage('Histological image coordinates: {}, {}'.format(x, y))

    def img_stacks_key_pressed(self, action):
        print(action)
        if not self.layer_ctrl.current_layer_ind or len(self.layer_ctrl.current_layer_ind) > 1:
            return
        da_ind = np.where(np.ravel(self.layer_ctrl.layer_index) == self.layer_ctrl.current_layer_ind[0])[0]
        da_link = self.layer_ctrl.layer_link[da_ind[0]]

        if action == 'delete':
            if self.lasso_is_closure:
                mask = np.zeros(self.image_view.img_size, dtype=np.uint8)
                pts = np.int32(self.lasso_pnts)[:, ::-1]
                cv2.fillPoly(mask, pts=[pts], color=255)
                mask = 255 - mask
                if da_link == 'img-virus':
                    dst = cv2.bitwise_and(self.working_virus_data, self.working_virus_data, mask=mask)
                    self.image_view.img_stacks.virus_img.setImage(dst)
                    self.working_virus_data = dst
                    res = cv2.resize(self.working_virus_data, self.image_view.tb_size, interpolation=cv2.INTER_AREA)
                elif da_link == 'img-boundary':
                    dst = cv2.bitwise_and(self.working_boundary_data, self.working_boundary_data, mask=mask)
                    self.image_view.img_stacks.boundary.setImage(dst)
                    self.working_boundary_data = dst
                    res = cv2.resize(self.working_boundary_data, self.image_view.tb_size, interpolation=cv2.INTER_AREA)
                elif da_link == 'img-mask':
                    dst = cv2.bitwise_and(self.working_mask_data, self.working_mask_data, mask=mask)
                    self.image_view.img_stacks.mask_img.setImage(dst)
                    self.working_mask_data = dst
                    res = cv2.resize(self.working_mask_data, self.image_view.tb_size, interpolation=cv2.INTER_AREA)
                else:
                    return
                self.layer_ctrl.layer_list[da_ind[0]].set_thumbnail_data(res)

    def hist_window_tri_pnts_moving(self, ev_obj):
        ev = ev_obj[0]
        ind = ev_obj[1]
        da_num = (self.np_onside - 1) * 4
        if ind < da_num:
            return
        if self.a2h_transferred:
            old_pnts = self.histo_tri_data.copy()
            new_pnts = self.histo_tri_data.copy()
            da_new_pnt = self.image_view.img_stacks.tri_pnts.data['pos'][ind].copy()
            new_pnts[ind] = [int(da_new_pnt[0]), int(da_new_pnt[1])]

            img_overlay = self.image_view.img_stacks.atlas_label.image.copy()
            img_wrap = img_overlay.copy()

            img_size = img_wrap.shape[:2]
            rect = (0, 0, img_size[1], img_size[0])

            subdiv = cv2.Subdiv2D(rect)
            for p in new_pnts:
                subdiv.insert(p)

            tri_vet_inds = get_vertex_ind_in_triangle(subdiv)
            for i in range(len(tri_vet_inds)):
                da_inds = tri_vet_inds[i]
                if ind not in da_inds:
                    continue
                t1 = [old_pnts[da_inds[0]], old_pnts[da_inds[1]], old_pnts[da_inds[2]]]
                t2 = [new_pnts[da_inds[0]], new_pnts[da_inds[1]], new_pnts[da_inds[2]]]
                t1 = np.reshape(t1, (3, 2))
                t2 = np.reshape(t2, (3, 2))
                warp_triangle(img_overlay, img_wrap,  t1, t2, True)
            self.image_view.img_stacks.atlas_label.setImage(img_wrap)
            self.histo_tri_data = new_pnts
        else:
            da_new_pnt = self.image_view.img_stacks.tri_pnts.data['pos'][ind].copy()
            self.histo_tri_data[ind] = [int(da_new_pnt[0]), int(da_new_pnt[1])]
        self.histo_tri_inside_data[ind - da_num] = [int(da_new_pnt[0]), int(da_new_pnt[1])]
        self.working_img_text[ind - da_num].setPos(da_new_pnt[0], da_new_pnt[1])
        if self.tool_box.triang_vis_btn.isChecked():
            self.update_histo_tri_lines()

    def segment_level_changed(self):
        print('level changed')

    def make_working_boundary(self):
        if self.working_mask_data is None:
            return
        self.inactive_lasso()
        self.working_boundary_data = cv2.Canny(self.working_mask_data.astype('uint8'), 100, 200)
        # self.image_view.img_stacks.mask_img.setVisible(False)
        self.image_view.img_stacks.boundary.setImage(self.working_boundary_data)
        res = cv2.resize(self.working_boundary_data.T, self.image_view.tb_size, interpolation=cv2.INTER_AREA)
        self.master_layers(res, layer_type='img-boundary')

    def img_drawing_pnts_clicked(self, points, ev):
        if not self.tool_box.checkable_btn_dict['eraser_btn'].isChecked() or len(self.working_img_pnts) == 0:
            return
        self.inactive_lasso()
        clicked_ind = ev[0].index()
        # self.image_view.img_stacks.vb.removeItem(self.working_img_text[-1])
        # del self.working_img_text[-1]
        del self.working_img_pnts[clicked_ind]
        self.image_view.img_stacks.drawing_pnts.setData(pos=np.asarray(self.working_img_pnts))
        # for i in range(clicked_ind, len(self.working_img_text)):
        #     self.working_img_text[i].setPos(self.working_img_pnts[i][0], self.working_img_pnts[i][1])

    def hist_window_tri_pnts_clicked(self, ev):
        if not self.tool_box.checkable_btn_dict['eraser_btn'].isChecked() or not self.histo_tri_data:
            return
        if self.a2h_transferred or self.h2a_transferred:
            return
        self.inactive_lasso()
        clicked_ind = ev[1]
        num = (self.np_onside - 1) * 4
        if clicked_ind < num:
            return
        self.image_view.img_stacks.vb.removeItem(self.working_img_text[-1])
        del self.working_img_text[-1]
        del self.histo_tri_data[clicked_ind]
        del self.histo_tri_inside_data[clicked_ind - num]
        self.image_view.img_stacks.tri_pnts.setData(pos=np.asarray(self.histo_tri_data))
        for i in range(len(self.working_img_text)):
            pnt_id = i + num
            self.working_img_text[i].setPos(self.histo_tri_data[pnt_id][0], self.histo_tri_data[pnt_id][1])
        if self.tool_box.triang_vis_btn.isChecked():
            self.update_histo_tri_lines()



    def image_move_horizon(self):
        if self.matching_img is None:
            return

        def shift_left(xy):
            return xy - np.array([-1, 0])[None, :]

        # self.overlay_img = self.overlay_img.astype(np.float32)
        # coords = warp_coords(shift_left, self.overlay_img.shape)
        # self.overlay_img = map_coordinates(self.overlay_img, coords)
        # self.overlay_img = self.overlay_img / np.max(self.overlay_img) * 255
        # if self.atlas_display == 'coronal':
        #     self.overlay_img1.setImage(self.overlay_img)
    #
    # def image_move_vertical(self):
    #     if not self.hist_overlay:
    #         return
    #     val = self.acontrols.hist_img_view.image_move_ud_slider.value()
    #
    #     def shift_up(xy):
    #         return xy - np.array([0, val])[None, :]
    #
    #     self.overlay_img = self.overlay_img.astype(np.float32)
    #     coords = warp_coords(shift_up, self.overlay_img.shape)
    #     self.overlay_img = map_coordinates(self.overlay_img, coords)
    #     self.overlay_img = self.overlay_img / np.max(self.overlay_img) * 255
    #     if self.atlas_display == 'coronal':
    #         self.overlay_img1.setImage(self.overlay_img)
    #
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    #
    #                       Atlas control
    #
    # ------------------------------------------------------------------
    def atlas_stacks_clicked(self, pos):
        print('atlas clicked')
        x = pos[0]
        y = pos[1]
        print('atlas', x, y)
        if self.atlas_view.atlas_data is None:
            return
        if self.num_windows == 4:
            return
        print('atlas clicked 1')
        if self.tool_box.checkable_btn_dict['triang_btn'].isChecked():
            self.inactive_lasso()
            if self.a2h_transferred or self.h2a_transferred:
                return
            self.atlas_tri_inside_data.append([int(x), int(y)])
            self.atlas_tri_data = self.atlas_tri_onside_data + self.atlas_tri_inside_data
            self.atlas_view.working_atlas.tri_pnts.setData(pos=np.asarray(self.atlas_tri_data))
            self.working_atlas_text.append(pg.TextItem(str(len(self.atlas_tri_inside_data))))
            self.atlas_view.working_atlas.vb.addItem(self.working_atlas_text[-1])
            self.working_atlas_text[-1].setPos(x, y)
            if self.tool_box.triang_vis_btn.isChecked():
                self.update_atlas_tri_lines()

        # if self.tool_box.pencil_btn.isChecked():
        #     self.working_atlas_pnts.append([x, y])
        #     # self.working_atlas_text.append(pg.TextItem(str(len(self.working_atlas_pnts))))
        #     # if self.atlas_display == 'coronal':
        #     # print(np.asarray(self.working_atlas_pnts))
        #     self.atlas_view.cimg.drawing_pnts.setData(pos=np.asarray(self.working_atlas_pnts))
        #     # self.atlas_view.cimg.vb.addItem(self.working_atlas_text[-1])
        #     # elif self.atlas_display == 'sagital':
        #     #     self.atlas_view.simg.drawing_pnts.setData(pos=np.asarray(self.working_atlas_pnts))
        #     #     self.atlas_view.simg.vb.addItem(self.working_atlas_text[-1])
        #     # else:
        #     #     self.atlas_view.himg.drawing_pnts.setData(pos=np.asarray(self.working_atlas_pnts))
        #     #     self.atlas_view.himg.vb.addItem(self.working_atlas_text[-1])
        #     # self.working_atlas_text[-1].setPos(x, y)
        # if self.tool_box.anchor_btn.isChecked():
        #     self.working_atlas_probe.append([x, y])
        #     da_widget.probe_pnts.setData(pos=np.asarray(self.working_atlas_probe))
        #     temp = np.zeros(self.atlas_view.slice_size, dtype=np.uint8)
        #     for i in range(len(self.working_atlas_probe)):
        #         temp[int(self.working_atlas_probe[i][1]), int(self.working_atlas_probe[i][0])] = 1
        #     res = cv2.resize(temp, self.atlas_view.slice_tb_size, interpolation=cv2.INTER_AREA)
        #     self.master_layers(res, layer_type='atlas-probes')

    def atlas_window_tri_pnts_moving(self, ev_obj):
        ev = ev_obj[0]
        ind = ev_obj[1]
        da_num = (self.np_onside - 1) * 4
        if ind < da_num:
            return
        if self.h2a_transferred:
            old_pnts = self.atlas_tri_data.copy()
            new_pnts = self.atlas_tri_data.copy()
            da_new_pnt = self.atlas_view.working_atlas.tri_pnts.data['pos'][ind].copy()
            new_pnts[ind] = [int(da_new_pnt[0]), int(da_new_pnt[1])]

            img_overlay = self.atlas_view.working_atlas.overlay_img.image.copy()
            img_wrap = img_overlay.copy()

            img_size = img_wrap.shape[:2]
            rect = (0, 0, img_size[1], img_size[0])

            subdiv = cv2.Subdiv2D(rect)
            for p in new_pnts:
                subdiv.insert(p)

            tri_vet_inds = get_vertex_ind_in_triangle(subdiv)
            for i in range(len(tri_vet_inds)):
                da_inds = tri_vet_inds[i]
                if ind not in da_inds:
                    continue
                t1 = [old_pnts[da_inds[0]], old_pnts[da_inds[1]], old_pnts[da_inds[2]]]
                t2 = [new_pnts[da_inds[0]], new_pnts[da_inds[1]], new_pnts[da_inds[2]]]
                t1 = np.reshape(t1, (3, 2))
                t2 = np.reshape(t2, (3, 2))
                warp_triangle(img_overlay, img_wrap,  t1, t2, True)
            self.atlas_view.working_atlas.overlay_img.setImage(img_wrap)
            self.atlas_tri_data = new_pnts
        else:
            da_new_pnt = self.atlas_view.working_atlas.tri_pnts.data['pos'][ind].copy()
            self.atlas_tri_data[ind] = [int(da_new_pnt[0]), int(da_new_pnt[1])]
        self.atlas_tri_inside_data[ind - da_num] = [int(da_new_pnt[0]), int(da_new_pnt[1])]
        self.working_atlas_text[ind - da_num].setPos(da_new_pnt[0], da_new_pnt[1])
        if self.tool_box.triang_vis_btn.isChecked():
            self.update_atlas_tri_lines()

    def atlas_window_tri_pnts_clicked(self, ev):
        print('atlas tri pnts clicked')
        if not self.tool_box.checkable_btn_dict['eraser_btn'].isChecked() or not self.atlas_tri_data:
            return
        if self.a2h_transferred or self.h2a_transferred:
            return
        self.inactive_lasso()
        clicked_ind = ev[1]
        print('check 1')
        num = (self.np_onside - 1) * 4
        if clicked_ind < num:
            return
        print('check 2')
        print(self.atlas_tri_data)
        self.atlas_view.working_atlas.vb.removeItem(self.working_atlas_text[-1])
        del self.working_atlas_text[-1]
        del self.atlas_tri_inside_data[clicked_ind - num]
        self.atlas_tri_data = self.atlas_tri_onside_data + self.atlas_tri_inside_data
        self.atlas_view.working_atlas.tri_pnts.setData(pos=np.asarray(self.atlas_tri_data))
        for i in range(len(self.working_atlas_text)):
            pnt_id = i + num
            self.working_atlas_text[i].setPos(self.atlas_tri_data[pnt_id][0], self.atlas_tri_data[pnt_id][1])
        if self.tool_box.triang_vis_btn.isChecked():
            self.update_atlas_tri_lines()

    def vis_atlas_boundary(self):
        if self.atlas_view.atlas_data is None:
            return
        if self.atlas_view.show_boundary_btn.isChecked():
            self.atlas_view.cimg.boundary.setVisible(True)
            self.atlas_view.simg.boundary.setVisible(True)
            self.atlas_view.himg.boundary.setVisible(True)
            # self.atlas_view.scimg.boundary.setVisible(True)
        else:
            self.atlas_view.cimg.boundary.setVisible(False)
            self.atlas_view.simg.boundary.setVisible(False)
            self.atlas_view.himg.boundary.setVisible(False)
            # self.atlas_view.scimg.boundary.setVisible(False)
            # da_page = self.atlas_view.working_page_control.page_slider.value()
            # self.atlas_view.working_atlas.boundary.setImage(self.atlas_view.atlas_bound[])

    # ------------------------------------------------------------------
    #
    #                       Atlas 3D control
    #
    # ------------------------------------------------------------------

    def show_small_area_in_3d(self):
        if self.show_child_mesh:
            self.show_child_mesh = False
        else:
            self.show_child_mesh = True

    def composition_3d_changed(self):
        if self.atlas_view.atlas_data is None:
            return
        all_keys = list(self.small_mesh_list.keys())
        for da_key in all_keys:
            self.small_mesh_list[da_key].setGLOptions(self.composition_combo.currentText())

    def sig_label_changed(self):
        if self.atlas_view.atlas_data is None or self.atlas_view.atlas_label is None:
            return
        lut = self.atlas_view.label_tree.lookup_table()

        # self.atlas_view.scimg.label_img.setLookupTable(lut=lut)
        self.atlas_view.cimg.label_img.setLookupTable(lut=lut)
        self.atlas_view.simg.label_img.setLookupTable(lut=lut)
        self.atlas_view.himg.label_img.setLookupTable(lut=lut)

        if len(self.small_mesh_list) == 0:
            return
        valid_id = list(self.small_mesh_list.keys())
        current_checked_label = list(self.atlas_view.label_tree.checked)
        n_current_label = len(current_checked_label)
        n_previous_label = len(self.previous_checked_label)
        if self.show_child_mesh:
            if n_current_label > n_previous_label:
                label_to_show = [id for id in current_checked_label if id not in self.previous_checked_label]
                label_to_show = list(np.ravel(label_to_show).astype(str))
                for id in label_to_show:
                    if id in valid_id:
                        self.small_mesh_list[id].setVisible(True)
            else:
                label_to_hide = [id for id in self.previous_checked_label if id not in current_checked_label]
                label_to_hide = list(np.ravel(label_to_hide).astype(str))
                for id in label_to_hide:
                    if id in valid_id:
                        self.small_mesh_list[id].setVisible(False)
        self.previous_checked_label = current_checked_label

        check_id = list(self.atlas_view.label_tree.checked)

        if self.show_child_mesh:
            if len(check_id) != 0:
                for id in check_id:
                    if id in valid_id:
                        if not self.small_mesh_list[id].visible():
                            self.small_mesh_list[id].setVisible(True)
            else:
                for id in valid_id:
                    if self.small_mesh_list[id].visible():
                        self.small_mesh_list[id].setVisible(False)
        #
        # # lut = self.label_tree.lookup_table()
        # lut = self.acontrols.atlas_view.label_tree.lookup_table()
        # check_id = list(self.acontrols.atlas_view.label_tree.checked)
        # check_id = np.ravel(check_id).astype(str)
        # if len(self.working_mesh) != 0:
        #     print(len(self.working_mesh))
        #     print(self.working_mesh[0])
        #     for i in range(len(self.working_mesh)):
        #         self.view3d.removeItem(self.working_mesh[i])
        #     self.working_mesh = {}
        # print(check_id)
        # valid_id = list(self.small_mesh_list.keys())
        # # valid_id = np.ravel(valid_id).astype(int)
        # print(valid_id)
        # if len(check_id) != 0:
        #     valid_mesh_count = 0
        #     for id in check_id:
        #         if id in valid_id:
        #             col_to_set = np.ravel(lut[int(id)]) / 255
        #             self.small_mesh_list[id].setColor((col_to_set[0], col_to_set[1], col_to_set[2], 0.3))
        #             self.working_mesh[valid_mesh_count] = self.small_mesh_list[id]
        #             self.view3d.addItem(self.working_mesh[valid_mesh_count])
        #             valid_mesh_count += 1



    # def coronal_window_hovered(self, pos):
    #     if self.atlas_view.navigation_btn.isChecked():




    def atlas_drawing_pnts_clicked(self, points, ev):
        if not self.tool_box.eraser_btn.isChecked() or len(self.working_atlas_pnts) == 0:
            return
        clicked_ind = ev[0].index()
        if self.atlas_display == 'coronal':
            # self.atlas_view.cimg.vb.removeItem(self.working_atlas_text[-1])
            # del self.working_atlas_text[-1]
            del self.working_atlas_pnts[clicked_ind]
            self.atlas_view.cimg.drawing_pnts.setData(pos=np.asarray(self.working_atlas_pnts))
        elif self.atlas_display == 'sagital':
            # self.atlas_view.simg.vb.removeItem(self.working_atlas_text[-1])
            # del self.working_atlas_text[-1]
            del self.working_atlas_pnts[clicked_ind]
            self.atlas_view.simg.drawing_pnts.setData(pos=np.asarray(self.working_atlas_pnts))
        else:
            # self.atlas_view.himg.vb.removeItem(self.working_atlas_text[-1])
            # del self.working_atlas_text[-1]
            del self.working_atlas_pnts[clicked_ind]
            self.atlas_view.himg.drawing_pnts.setData(pos=np.asarray(self.working_atlas_pnts))
        # for i in range(clicked_ind, len(self.working_atlas_text)):
        #     self.working_atlas_text[i].setPos(self.working_atlas_pnts[i][0], self.working_atlas_pnts[i][1])


    def coronal_slice_stacks_hovered(self, pos):
        y = int(pos.y())
        x = int(pos.x())
        da_index = self.atlas_view.current_coronal_index
        da_id = self.atlas_view.atlas_label[y, x, da_index]
        coords = np.round((np.array([pos.y(), pos.x(), da_index]) - np.ravel(
            self.atlas_view.Bregma)) * self.atlas_view.vxsize_um, 2)
        pstr = 'Atlas voxel:({}, {}, {}), ML:{}um, AP:{}um, DV:{}um) : {} '.format(
            x, da_index, y, coords[2], coords[1], coords[0],
            self.atlas_view.label_tree.describe(da_id))
        self.statusbar.showMessage(pstr)

    def sagital_slice_stacks_hovered(self, pos):
        y = int(pos.y())
        x = int(pos.x())
        da_index = self.atlas_view.current_sagital_index
        da_id = self.atlas_view.atlas_label[y, da_index,  x]
        coords = np.round((np.array([pos.y(), da_index,  pos.x()]) - np.ravel(
            self.atlas_view.Bregma)) * self.atlas_view.vxsize_um, 2)
        pstr = 'Atlas voxel:({}, {}, {}), ML:{}um, AP:{}um, DV:{}um) : {} '.format(
            da_index, x, y, coords[2], coords[1], coords[0],
            self.atlas_view.label_tree.describe(da_id))
        self.statusbar.showMessage(pstr)

    def horizontal_slice_stacks_hovered(self, pos):
        y = int(pos.y())
        x = int(pos.x())
        da_index = self.atlas_view.current_horizontal_index
        da_id = self.atlas_view.atlas_label[da_index, y, x]
        coords = np.round((np.array([da_index, pos.y(), pos.x()]) - np.ravel(
            self.atlas_view.Bregma)) * self.atlas_view.vxsize_um, 2)
        pstr = 'Atlas voxel:({}, {}, {}), ML:{}um, AP:{}um, DV:{}um) : {} '.format(
            x, da_index, y, coords[2], coords[1], coords[0],
            self.atlas_view.label_tree.describe(da_id))
        self.statusbar.showMessage(pstr)



    #
    # def view1_mouse_clicked(self, mouse_point):
    #     # point = self.getCcfPoint(mouse_point)
    #     y_pos = self.acontrols.atlas_view.c_page_slider.value()
    #     x_pos, z_pos = mouse_point
    #     if self.acontrols.hist_img_view.pencil_in_use:
    #         self.atlas_point_count += 1
    #         self.working_atlas.append([mouse_point[0], mouse_point[1]])
    #         if len(self.working_atlas_text) < len(self.working_atlas):
    #             self.working_atlas_text.append(pg.TextItem(str(self.atlas_point_count)))
    #             self.view1.addItem(self.working_atlas_text[-1])
    #             self.working_atlas_text[-1].setPos(mouse_point[0], mouse_point[1])
    #         else:
    #             for i in range(len(self.working_atlas)):
    #                 self.working_atlas_text[i].setPos(self.working_atlas[i][0], self.working_atlas[i][1])
    #         x_data = [self.working_atlas[i][0] for i in range(len(self.working_atlas))]
    #         y_data = [self.working_atlas[i][1] for i in range(len(self.working_atlas))]
    #         # pos = [{'pos': self.working_atlas[i]} for i in range(len(self.working_atlas))]
    #         self.scatter1.setData(x_data, y_data)
    #
    #     if self.pcontrols.pencil_in_use:
    #         self.prob_point_count += 1
    #
    #         z_angle = np.radians(self.acontrols.atlas_view.cz_angle_slider.value())
    #         x_angle = np.radians(self.acontrols.atlas_view.cx_angle_slider.value())
    #         page_num = self.acontrols.atlas_view.c_page_slider.value()
    #
    #         if z_angle != 0 or z_angle != 0:
    #
    #             o_corner = np.array([0, page_num, 0])
    #             o_rot = np.array([256, page_num, 256])
    #
    #             rotm = np.dot(rotation_z(z_angle), rotation_x(x_angle))
    #
    #             oz_vector = np.dot(rotm, np.array([0, 0, 1]))
    #             ox_vector = np.dot(rotm, np.array([1, 0, 0]))
    #
    #             o_corner_new = o_rot + np.dot(rotm, o_corner - o_rot)
    #
    #             pos_3d = d2td3((x_pos, z_pos), ox_vector, oz_vector, o_corner_new)
    #
    #         else:
    #             pos_3d = (x_pos, page_num, z_pos)
    #
    #         self.working_prob_2d.append([mouse_point[0], mouse_point[1]])
    #         x_data = [self.working_prob_2d[i][0] for i in range(len(self.working_prob_2d))]
    #         y_data = [self.working_prob_2d[i][1] for i in range(len(self.working_prob_2d))]
    #         # pos = [{'pos': self.working_atlas[i]} for i in range(len(self.working_atlas))]
    #         self.probe_scatter1.setData(x_data, y_data)
    #
    #         self.working_prob_3d.append(pos_3d)
    #         pdata = (np.asarray(self.working_prob_3d) - np.array([256, 512, 256])) / 4
    #         self.points_item.setData(pos=pdata)
    #         print(self.working_prob_2d[-1])
    #         print(self.working_prob_3d[-1])
    #         print(pdata[-1])
    #
    # def view1_mouse_hovered(self, mouse_info):
    #     id = mouse_info[0]
    #     x_pos, z_pos = mouse_info[1].x(), mouse_info[1].y()
    #
    #     z_angle = np.radians(self.acontrols.atlas_view.cz_angle_slider.value())
    #     x_angle = np.radians(self.acontrols.atlas_view.cx_angle_slider.value())
    #     page_num = self.acontrols.atlas_view.c_page_slider.value()
    #
    #     if z_angle != 0 or z_angle != 0:
    #         o_corner = np.array([0, page_num, 0])
    #         o_rot = np.array([256, page_num, 256])
    #         rotm = np.dot(rotation_z(z_angle), rotation_x(x_angle))
    #         oz_vector = np.dot(rotm, np.array([0, 0, 1]))
    #         ox_vector = np.dot(rotm, np.array([1, 0, 0]))
    #         o_corner_new = o_rot + np.dot(rotm, o_corner - o_rot)
    #         pos_3d = d2td3((x_pos, z_pos), ox_vector, oz_vector, o_corner_new)
    #     else:
    #         pos_3d = (x_pos, page_num, z_pos)
    #
    #     ml = np.round((pos_3d[0] - 246) * self.resolution * 1e-3, 2)
    #     ap = np.round((pos_3d[1] - 653) * self.resolution * 1e-3, 2)
    #     dv = np.round((440 - pos_3d[2]) * self.resolution * 1e-3, 2)
    #     if ml > 0:
    #         ml = 'R {}'.format(ml)
    #     elif ml < 0:
    #         ml = 'L {}'.format(-ml)
    #     else:
    #         ml = 0
    #
    #     p_pos = np.ravel(pos_3d).astype(int)
    #
    #     pstr = '({}, {}, {}), AP: {}mm, ML: {}mm, DV:{}mm, {} '.format(p_pos[0], p_pos[1], p_pos[2], ap, ml, dv,
    #                                                                    self.acontrols.atlas_view.label_tree.describe(
    #                                                                        id))
    #     # self.statusLabel.setText(id.astype(str))
    #     self.statusLabel.setText(pstr)
    #     if self.acontrols.hist_img_view.eraser_in_use:
    #         self.view1.setCursor(self.eraser_cursor)
    #     else:
    #         self.view1.setCursor(Qt.ArrowCursor)
    #

    #
    # def mouse_hovered(self, mouse_info):
    #     id = mouse_info[0]
    #     pos = (mouse_info[1].x(), mouse_info[1].y())
    #     pstr = '({}, {}), {} '.format(pos[0], pos[1], self.acontrols.atlas_view.label_tree.describe(id))
    #     # self.statusLabel.setText(id.astype(str))
    #     self.statusLabel.setText(pstr)
    #     if self.acontrols.hist_img_view.eraser_in_use:
    #         self.view1.setCursor(self.eraser_cursor)
    #     else:
    #         self.view1.setCursor(Qt.ArrowCursor)
    #
    # def mouse_hovered_hist(self, pos):
    #     if self.acontrols.hist_img_view.eraser_in_use:
    #         self.view5.setCursor(self.eraser_cursor)
    #     else:
    #         self.view5.setCursor(Qt.ArrowCursor)
    #

    # # ----------------------------------------------------------------------------
    # def auto_resize(self):
    #     if self.image_view.image_file is None:
    #         return
    #     shp = self.image_view.current_gray_img.shape[:2]
    #
    #     scale_percent = np.ceil(np.max([shp[1] / self.atlas_view.slice_size[0], shp[0] / self.atlas_view.slice_size[1]]))  # percent of original size
    #     width = int(shp[1] * scale_percent)
    #     height = int(shp[0] * scale_percent)
    #     dim = (width, height)
    #
    #     temp = []
    #     for i in range(len(self.image_view.current_color_img)):
    #         self.image_view.current_color_img[i] = cv2.resize(self.image_view.current_color_img[i], dim, interpolation=cv2.INTER_AREA)



    def match_points(self):
        a_temp = len(self.working_atlas_pnts)
        b_temp = len(self.working_img_pnts)
        if a_temp == 0 or b_temp == 0 or a_temp != b_temp:
            self.statusbar.showMessage('Please check the clicked points!')
            self.statusbar.setStyleSheet("background-color : pink")
            self.warning_status = True
            return
        self.slice_size = (512, 512)
        # tform = ProjectiveTransform()
        # tform.estimate(np.float32(np.float32(self.working_img_pnts), self.working_atlas_pnts))
        # img_warped = warp(self.image_view.current_color_img[0], tform, order=1, clip=True)  # , mode='constant',cval=float('nan'))
        print(np.float32(self.working_img_pnts)[:, ::-1])
        print(np.float32(self.working_img_pnts))
        print(np.float32(self.working_atlas_pnts))
        self.project_matrix, status = cv2.findHomography(np.float32(self.working_img_pnts)[:, ::-1], np.float32(self.working_atlas_pnts)[:, ::-1])
        print(status)
        pts = np.float32(self.working_img_pnts)[:, ::-1].reshape(-1, 1, 2)
        # pts = np.array([pts][:, ::-1], np.float32)
        dst = cv2.perspectiveTransform(pts, self.project_matrix)
        print(dst)
        # overlay histological image to atlas view
        if self.image_view.image_file.is_rgb:
            print('rgb')
        else:
            for i in range(self.image_view.image_file.n_channels):
                im_dst = cv2.warpPerspective(self.image_view.current_img[:, :, i], self.project_matrix, self.slice_size)
                self.atlas_view.cimg.overlay_img[i].setImage(im_dst)

            merged_img = np.mean(self.image_view.current_img, 2)
        res = cv2.resize(merged_img, self.atlas_view.slice_tb_size, interpolation=cv2.INTER_AREA)
        self.master_layers(res, layer_type='atlas-overlay')
        self.working_img_pnts = []
        self.working_atlas_text = []
        self.image_view.img_stacks.drawing_pnts.clear()
        self.image_view.img_stacks.drawing_pnts.updateSpots()
        self.atlas_view.working_atlas.drawing_pnts.clear()
        self.atlas_view.working_atlas.drawing_pnts.updateSpots()
        # flip_ind = np.flip(np.arange(len(self.working_atlas_text)), 0)
        # for i in flip_ind:
        #     self.working_img_text[i].setVisible(False)
        #     self.working_atlas_text[i].setVisible(False)


    def accept_projection(self):
        if self.project_matrix is None:
            return
        # translate virus
        if self.working_virus_data is not None:
            self.working_atlas_virus = cv2.warpPerspective(self.working_virus_data, self.project_matrix, self.slice_size)
            self.atlas_view.cimg.virus_img.setImage(self.working_atlas_virus)
            virus_res = cv2.resize(self.working_atlas_virus, self.atlas_view.slice_tb_size, interpolation=cv2.INTER_AREA)
            self.master_layers(virus_res, layer_type='atlas-virus')
        # translate boundary
        if self.working_boundary_data is not None:
            self.working_atlas_boundary = cv2.warpPerspective(self.working_boundary_data, self.project_matrix, self.slice_size)
            self.atlas_view.cimg.boundary.setImage(self.working_atlas_boundary)
            boundary_res = cv2.resize(self.working_atlas_boundary, self.atlas_view.slice_tb_size, interpolation=cv2.INTER_AREA)
            self.master_layers(boundary_res, layer_type='atlas-boundary')
        # translate probes
        if self.working_probe_data:
            pts = np.float32(self.working_probe_data)[:, ::-1].reshape(-1, 1, 2)
            dst = cv2.perspectiveTransform(pts, self.project_matrix)
            dst = dst.reshape(len(dst), 2)[:, ::-1]
            self.working_atlas_probe = dst
            self.atlas_view.cimg.probe_pnts.setData(pos=self.working_atlas_probe)
            probe_res = np.zeros(self.slice_size).astype('uint8')
            temp = dst.astype(int)
            for i in range(len(dst)):
                probe_res[int(dst[i][0]), int(dst[i][1])] = 255
            probe_res = cv2.resize(probe_res, self.atlas_view.slice_tb_size, interpolation=cv2.INTER_AREA)
            self.master_layers(probe_res, layer_type='atlas-probes')
        # translate cells
        if self.working_cell_data:
            pts = np.float32(self.working_cell_data)[:, ::-1].reshape(-1, 1, 2)
            dst = cv2.perspectiveTransform(pts, self.project_matrix)
            dst = dst.reshape(len(dst), 2)[:, ::-1]
            self.working_atlas_cell = dst
            self.atlas_view.cimg.cell_pnts.setData(pos=self.working_atlas_cell)
            cell_res = np.zeros(self.slice_size).astype('uint8')
            temp = dst.astype(int)
            for i in range(len(dst)):
                cell_res[int(dst[i][0]), int(dst[i][1])] = 255
            cell_res = cv2.resize(cell_res, self.atlas_view.slice_tb_size, interpolation=cv2.INTER_AREA)
            self.master_layers(cell_res, layer_type='atlas-cells')









        # translate cells

        # translate lines

        # translate boundary



    #     print(img_warped.shape)
    #     # tform = estimate_transform('projective', np.array(self.working_img), np.array(self.working_atlas))
    #     # tf_img_warp = warp(self.da_pstep_data, tform.inverse, mode='constant')
    #     # print(tf_img_warp)
    #     # print(np.max(tf_img_warp))
    #     img_warp = img_warped * (255. / np.max(img_warped))
    #     self.image_data[page_number] = img_warp
    #     self.acontrols.hist_img_view.img1.setImage(img_warp)
    #     self.working_atlas = []
    #     self.working_image = []
    #     self.img_point_count = 0
    #     self.img_point_count = 0
    #     self.scatter1.setData(None, None)
    #     self.scatter5.setData(None, None)
    #     for i in range(len(self.working_atlas_text)):
    #         self.working_atlas_text[i].setPos(self.faraway_place, self.faraway_place)
    #     for i in range(len(self.working_img_text)):
    #         self.working_img_text[i].setPos(self.faraway_place, self.faraway_place)
    #
    # def overlay_image(self):
    #     # if len(self.working_atlas) == 0 or len(self.working_img) == 0:
    #     #     return
    #     page_number = self.acontrols.hist_img_view.page_slider.value()
    #     if self.atlas_display == 'coronal':
    #         da_show_image = rotate(self.image_data[page_number], 90, preserve_range=True)
    #         # da_show_image = da_show_image[::-1,:]
    #         self.overlay_img1.setImage(da_show_image)
    #     self.overlay_img = da_show_image
    #     self.hist_overlay = True
    #
    # def register_image(self):
    #     self.overlay_img1.clear()
    #     self.hist_overlay = False
    #
    # def image_size_changed(self):
    #     val = self.acontrols.hist_img_view.rescale_slider.value()
    #     page_number = self.acontrols.hist_img_view.page_slider.value()
    #     da_image_data = self.image_data[page_number]
    #     da_image_data = resize(da_image_data, (da_image_data.shape[0] // val, da_image_data.shape[1] // val),
    #                            anti_aliasing=True)
    #     if self.hist_overlay:
    #         if self.atlas_display == 'coronal':
    #             self.overlay_img1.setImage(da_image_data)
    #     else:
    #         self.image_data[page_number] = da_image_data
    #         self.acontrols.hist_img_view.img1.setImage(self.image_data[page_number])
    #
    # def image_rotation_changed(self):
    #     val = self.acontrols.hist_img_view.image_rt_slider.value()
    #     page_number = self.acontrols.hist_img_view.page_slider.value()
    #     da_image_data = rotate(self.image_data[page_number], val, preserve_range=True)
    #     if self.hist_overlay:
    #         if self.atlas_display == 'coronal':
    #             self.overlay_img1.setImage(da_image_data)
    #     else:
    #         self.image_data[page_number] = da_image_data
    #         self.acontrols.hist_img_view.img1.setImage(self.image_data[page_number])
    #
    # def image_opacity_changed(self):
    #     val = self.acontrols.hist_img_view.image_op_slider.value()
    #     if self.atlas_display == 'coronal':
    #         self.overlay_img1.setOpts(opacity=float(val / 10))
    #

    # ------------------------------------------------------------------
    #
    #                      layers control
    #
    # ------------------------------------------------------------------
    def master_layers(self, res, layer_type):
        if not self.layer_ctrl.layer_link or layer_type not in self.layer_ctrl.layer_link:
            self.layer_ctrl.add_layer(layer_type)
            self.layer_ctrl.layer_list[-1].set_thumbnail_data(res)
        else:
            print(self.layer_ctrl.layer_link)
            print(layer_type)
            da_ind = np.where(np.ravel(self.layer_ctrl.layer_link) == layer_type)[0]
            self.layer_ctrl.layer_list[da_ind[0]].set_thumbnail_data(res)

    def layers_opacity_changed(self, val):
        if not self.layer_ctrl.current_layer_ind or len(self.layer_ctrl.current_layer_ind) > 1:
            return
        da_ind = np.where(np.ravel(self.layer_ctrl.layer_index) == self.layer_ctrl.current_layer_ind[0])[0]
        if len(da_ind) == 0:
            return
        da_link = self.layer_ctrl.layer_list[da_ind[0]].get_link()
        if 'img' in da_link:
            respond_widget = self.image_view.img_stacks
        elif 'atlas' in da_link:
            respond_widget = self.atlas_view.working_atlas
        else:
            return
        if 'virus' in da_link:
            respond_widget.virus_img.setOpts(opacity=val * 0.01)
        elif 'boundary' in da_link:
            respond_widget.boundary.setOpts(opacity=val * 0.01)
        elif 'mask' in da_link:
            respond_widget.mask_img.setOpts(opacity=val * 0.01)
        elif 'overlay' in da_link:
            respond_widget.overlay_img.setOpts(opacity=val * 0.01)
        elif 'cells' in da_link:
            respond_widget.cell_pnts.setPen((0, 0, 255, int(val * 255 * 0.01)))
        elif 'probes' in da_link:
            respond_widget.probe_pnts.setPen((0, 255, 0, int(val * 255 * 0.01)))
        elif 'lines' in da_link:
            respond_widget.lines.setPen((0, 255, 0, int(val * 255 * 0.01)))
        else:
            return

        # if da_link == 'img-virus':
        #     self.image_view.img_stacks.virus_img.setOpts(opacity=val * 0.01)
        # elif da_link == 'img-boundary':
        #     self.image_view.img_stacks.contours_img.setOpts(opacity=val * 0.01)
        # elif da_link == 'img-mask':
        #     self.image_view.img_stacks.mask_img.setOpts(opacity=val * 0.01)
        # else:
        #     return

    def layers_visible_changed(self, event):
        da_link = event[1]
        vis = event[2]
        if vis:
            val = self.layer_ctrl.layer_opacity_slider.value() * 0.01
        else:
            val = 0
        if 'img' in da_link:
            respond_widget = self.image_view.img_stacks
        elif 'atlas' in da_link:
            respond_widget = self.atlas_view.working_atlas
        else:
            return
        if 'virus' in da_link:
            respond_widget.virus_img.setOpts(opacity=val)
        elif 'boundary' in da_link:
            respond_widget.boundary.setOpts(opacity=val)
        elif 'mask' in da_link:
            respond_widget.mask_img.setOpts(opacity=val)
        elif 'overlay' in da_link:
            respond_widget.overlay_img.setOpts(opacity=val)
        elif 'cells' in da_link:
            respond_widget.cell_pnts.setPen((0, 0, 255, int(val * 255)))
        elif 'probes' in da_link:
            respond_widget.probe_pnts.setPen((0, 255, 0, int(val * 255)))
        elif 'lines' in da_link:
            respond_widget.lines.setPen((0, 255, 0, int(val * 255)))
        else:
            return
        # if da_link == 'img-virus':
        #     self.image_view.img_stacks.virus_img.setOpts(opacity=val)
        # elif da_link == 'img-boundary':
        #     self.image_view.img_stacks.contours_img.setOpts(opacity=val)
        # elif da_link == 'img-mask':
        #     self.image_view.img_stacks.mask_img.setOpts(opacity=val)
        # elif da_link == 'img-cells':
        #     self.image_view.img_stacks.cell_pnts.setOpts(opacity=val)
        # elif da_link == 'img-lines':
        #     self.image_view.img_stacks.lines.setOpts(opacity=val)
        # elif da_link == 'img-probes':
        #     self.image_view.img_stacks.probe_pnts.setOpts(opacity=val)
        # elif da_link == 'atlas-virus':
        #     self.atlas_view.img_stacks.virus_img.setOpts(opacity=val)
        # elif da_link == 'atlas-boundary':
        #     self.image_view.img_stacks.contours_img.setOpts(opacity=val)
        # elif da_link == 'atlas-cells':
        #     self.image_view.img_stacks.cell_pnts.setOpts(opacity=val)
        # elif da_link == 'atlas-lines':
        #     self.image_view.img_stacks.lines.setOpts(opacity=val)
        # elif da_link == 'atlas-probes':
        #     self.image_view.img_stacks.probe_pnts.setOpts(opacity=val)
        # else:
        #     return
    #
    # ------------------------------------------------------------------
    #
    #              objects (probe, virus, ....) control
    #
    # ------------------------------------------------------------------
    def make_object_pieces(self):
        if self.working_atlas_probe:
            probe_data = np.asarray(self.working_atlas_probe)
            if self.atlas_display == 'coronal':
                da_vec = np.ones(len(self.working_atlas_probe)) * self.atlas_view.current_coronal_index
                da_vec.reshape(len(self.working_atlas_probe), 1)
                data = np.vstack((probe_data[:, 0], da_vec, probe_data[:, 1]))
            elif self.atlas_display == 'sagital':
                da_vec = np.ones(len(self.working_atlas_probe)) * self.atlas_view.current_sagital_index
                da_vec.reshape(len(self.working_atlas_probe), 1)
                data = np.vstack((da_vec, probe_data[:, 0], probe_data[:, 1]))
            else:
                da_vec = np.ones(len(self.working_atlas_probe)) * self.atlas_view.current_horizontal_index
                da_vec.reshape(len(self.working_atlas_probe), 1)
                data = np.vstack((probe_data[:, 0], probe_data[:, 1], da_vec))
            print(data.T.shape)
            self.object_ctrl.add_object_piece(object_name='probe', object_icon=self.object_ctrl.probe_icon, object_data=data.T)
            self.working_atlas_probe = []
            self.atlas_view.working_atlas.probe_pnts.clear()
            self.atlas_view.working_atlas.probe_pnts.updateSpots()
        if self.working_atlas_virus is not None:
            self.object_ctrl.add_object_piece(object_name='virus', object_icon=self.object_ctrl.virus_icon, object_data=self.working_atlas_virus)
        if self.working_atlas_cell:
            self.object_ctrl.add_object_piece(object_name='cell', object_icon=self.object_ctrl.cell_icon,
                                        object_data=self.working_atlas_cell)
        if self.working_atlas_lines:
            self.object_ctrl.add_object_piece(object_name='line', object_icon=self.object_ctrl.line_icon,
                                        object_data=self.working_atlas_lines)
        if self.working_atlas_boundary:
            self.object_ctrl.add_object_piece(object_name='boundary', object_icon=self.object_ctrl.bnd_icon,
                                        object_data=self.working_atlas_boundary)




    def merge_probes(self):
        if self.object_ctrl.probe_piece_count == 0:
            return
        cind = [ind for ind in range(len(self.object_ctrl.obj_name)) if 'probe' in self.object_ctrl.obj_name[ind]]
        probe_names = np.unique(np.ravel(self.object_ctrl.obj_name)[cind])
        n_probes = len(probe_names)
        for i in range(n_probes):
            single_probe_ind = [ind for ind in range(len(self.object_ctrl.obj_name)) if probe_names[i] in self.object_ctrl.obj_name[ind]]
            data = self.object_ctrl.obj_data[single_probe_ind[0]]
            if len(single_probe_ind) > 1:
                for j in range(1, len(single_probe_ind)):
                    data = data + self.object_ctrl.obj_data[single_probe_ind[j]]
            print(data)
            info_dict = self.calculate_probe_info(np.asarray(data))

            new_obj = RegisteredObject(index=self.object_ctrl.obj_count, object_name='probe',
                                         object_icon=self.object_ctrl.probe_icon, group_index=self.registered_probe_count)
            info_dict['prob_color'] = new_obj.color.name()
            self.registered_prob_list.append(info_dict)

            new_obj.text_btn.setText('probe{}'.format(i+1))
            new_obj.set_checked(True)
            new_obj.sig_clicked.connect(self.probe_info_on_click)
            new_obj.sig_object_color_changed.connect(self.obj_color_changed)
            # new_obj.eye_clicked.connect(self.obj_piece_name_changed)
            self.object_ctrl.obj_data.append([])
            self.object_ctrl.obj_list.append(new_obj)
            self.object_ctrl.obj_index.append(self.object_ctrl.obj_count)
            self.object_ctrl.obj_name.append('registered probe {}'.format(i+1))

            if self.object_ctrl.current_obj_ind is None:
                self.object_ctrl.current_obj_ind = self.object_ctrl.obj_count
            else:
                ind2unactive = np.where(np.ravel(self.object_ctrl.obj_index) == self.object_ctrl.current_obj_ind)[0][0]
                self.object_ctrl.obj_list[ind2unactive].set_checked(False)
                self.object_ctrl.current_obj_ind = self.object_ctrl.obj_count
            self.object_ctrl.layer_layout.addWidget(self.object_ctrl.obj_list[-1])
            self.object_ctrl.obj_count += 1
            self.registered_probe_count += 1

            # draw 3d
            pos = (np.array([info_dict['sp'], info_dict['new_ep'], info_dict['ep']]) - np.array([self.atlas_view.atlas_info[3]['Bregma'][0], self.atlas_view.atlas_info[3]['Bregma'][1], self.atlas_view.atlas_info[3]['Bregma'][2]])) / 2.
            pos_color = new_obj.color
            probe_line = gl.GLLinePlotItem(pos=pos, color=pos_color, width=3, mode='line_strip')
            probe_line.setGLOptions('opaque')
            self.probe_lines_3d.append(probe_line)
            self.view3d.addItem(self.probe_lines_3d[-1])


        self.cut_section = ['None' for i in range(n_probes)]
        for i in range(n_probes):
            if len(np.unique(data[:, 0])) == 1:
                self.cut_section[i] = 'sagital'
            if len(np.unique(data[:, 1])) == 1:
                self.cut_section[i] = 'coronal'
            if len(np.unique(data[:, 2])) == 1:
                self.cut_section[i] = 'horizontal'

        for i in range(n_probes):
            if self.cut_section[i] == 'None':
                continue
            if self.cut_section[i] == 'coronal':
                data2d = np.vstack([self.registered_prob_list[i]['sp'], self.registered_prob_list[i]['ep']])
                data2d = data2d[:, [0, 2]]
                print(data2d)
                da_ind = np.where(np.ravel(self.object_ctrl.obj_name) == 'registered probe {}'.format(i+1))[0]
                da_color = self.object_ctrl.obj_list[da_ind[0]].color
                line2d = pg.PlotDataItem(data2d, pen=pg.mkPen(da_color, width=2))
                self.probe_lines_2d.append(line2d)
                self.atlas_view.cimg.vb.addItem(self.probe_lines_2d[-1])

        self.object_ctrl.probe_piece_count = 0

    def calculate_probe_info(self, data):
        start_pnt, end_pnt, avg, direction = line_fit(data)
        theta, phi = get_angles(direction)
        unique_label, region_length, channels, new_ep = get_probe_length(self.atlas_view.atlas_label, start_pnt, end_pnt, avg, direction)
        label_names, label_acronym, label_color = get_label_name(self.atlas_view.label_info, unique_label)
        da_dict = {'sp': start_pnt, 'ep': end_pnt, 'data': data,
                   'new_ep': new_ep, 'theta': theta, 'phi': phi,
                   'label': unique_label, 'label_name': label_names,
                   'label_acronym': label_acronym, 'region_length': region_length,
                   'label_color': label_color, 'channels': channels}
        return da_dict

    def probe_info_on_click(self, ev):
        print(ev)
        index = ev[0]
        num = ev[-1]
        print(('obj clicked', index))
        if self.object_ctrl.current_obj_ind != index:
            id2unactive = np.where(np.ravel(self.object_ctrl.obj_index) == self.object_ctrl.current_obj_ind)[0][0]
            self.object_ctrl.obj_list[id2unactive].set_checked(False)
            id2active = np.where(np.ravel(self.object_ctrl.obj_index) == index)[0][0]
            self.object_ctrl.obj_list[id2active].set_checked(True)
            self.object_ctrl.current_obj_ind = index

        da_data = self.registered_prob_list[num]
        sp = da_data['sp']
        theta = da_data['theta']
        phi = da_data['phi']

        region_length = da_data['region_length']
        r = np.sum(region_length)
        label_name = da_data['label_name']
        abbrev = da_data['label_acronym']
        probe_color = da_data['prob_color']
        label_color = da_data['label_color']
        channels = da_data['channels'].astype(int)

        vals = region_length / r * 2

        self.probe_window = ProbeInfoWindow(num+1, probe_color, theta, phi, r, label_name, abbrev, vals, channels,
                                            label_color)
        self.probe_window.show()

    def obj_color_changed(self, ev):
        id = ev[0]
        color = ev[1]
        object_name = ev[2]
        group_id = ev[3]
        self.probe_lines_3d[group_id].setData(color=color)
        self.probe_lines_2d[group_id].setPen(color)
        self.registered_prob_list[group_id]['prob_color'] = color.name()

    def obj_line_width_changed(self):
        val = self.object_ctrl.line_width_slider.value()
        for i in range(len(self.probe_lines_3d)):
            self.probe_lines_3d[i].setData(width=val)

    # ------------------------------------------------------------------
    #
    #                  Menu Bar ---- File ----- related
    #
    # ------------------------------------------------------------------
    def file_save(self):
        file_name = QtGui.QFileDialog.getSaveFileName(self, 'Save File')
        if file_name != '':
            file = open(file_name, 'w')
            text = self.textEdit.toPlainText()
            file.write(text)
            file.close()



    # def render_volume(self, atlas_folder):
    #
    #
    #

    #
    #     # temp_atlas = self.atlas_data.copy()
    #     # temp_atlas[self.segmentation_data != id] = 0
    #     self.mesh_shape = np.ravel(self.atlas_data.shape) / 4
    #
    #     # pimg = np.ascontiguousarray(temp_atlas[::4, ::4, ::4])
    #     for id in np.unique(self.segmentation_data):
    #         if id == 0:
    #             continue
    #         if id in self.label_data['index']:
    #             color_to_set = self.label_data['color'][(self.label_data['index'] == id)][0] / 255
    #             md = gl.MeshData(vertexes=small_verts_list[str(id)], faces=small_faces_list[str(id)])
    #             mesh = gl.GLMeshItem(meshdata=md, smooth=True,
    #                                  color=(color_to_set[0], color_to_set[1], color_to_set[2], 0.3), shader='balloon')
    #             mesh.setGLOptions('opaque')
    #             mesh.translate(-self.mesh_shape[0] / 2., -self.mesh_shape[1] / 2., -self.mesh_shape[2] / 2.)
    #             # mesh.setVisible(False)
    #             self.small_mesh_list[str(id)] = mesh
    #             self.small_mesh_list[str(id)].setVisible(False)
    #
    #     print(len(self.small_mesh_list))
    #
    #
    #
    #         verts, faces = pg.isosurface(ndi.gaussian_filter(img.astype('float32'), (2, 2, 2)), 0.5)

            # outfile = open(os.path.join(atlas_folder, 'WHS_atlas_verts.pkl'), 'wb')
            # pickle.dump(verts, outfile)
            # outfile.close()
            #
            # outfile = open(os.path.join(atlas_folder, 'WHS_atlas_faces.pkl'), 'wb')
            # pickle.dump(faces, outfile)
            # outfile.close()

        # img = np.ascontiguousarray(self.atlas_data[::4, ::4, ::4])
        # md = gl.MeshData(vertexes=verts, faces=faces)
        # mesh = gl.GLMeshItem(meshdata=md, smooth=True, color=[0.5, 0.5, 0.5, 0.2], shader='balloon')
        # mesh.setGLOptions('additive')
        # mesh.translate(-self.mesh_shape[0] / 2., -self.mesh_shape[1] / 2., -self.mesh_shape[2] / 2.)
        #
        # self.view3d.addItem(mesh)
        #
        # self.view3d.addItem(self.ap_plate_mesh)
        # self.view3d.addItem(self.ml_plate_mesh)
        # self.view3d.addItem(self.dv_plate_mesh)
        #
        # mesh_keys = list(self.small_mesh_list.keys())
        # for i in range(len(self.small_mesh_list)):
        #     self.view3d.addItem(self.small_mesh_list[mesh_keys[i]])
        #
        # ax = gl.GLAxisItem()
        # ax.setSize(2, 2, 2)
        #
        # g = gl.GLGridItem()
        # g.scale(2, 2, 1)
        # self.view3d.addItem(ax)
        # self.view3d.addItem(g)
        #
        # self.points_item = gl.GLScatterPlotItem(color=(48 / 255, 21 / 255, 253 / 255, 1), size=10, pxMode=False)
        # self.view3d.addItem(self.points_item)

        # self.view3d.show()

    # def sliceChanged(self):
    #     self.view2.autoRange(items=[self.img2.atlas_img])
    # self.target.setVisible(False)

    # ------------------------------------------------------------------
    #
    #                       Atlas Loader
    #
    # ------------------------------------------------------------------



    def render_small_volume(self, factor=2, level=0.1):
        self.small_verts_list = {}
        self.small_faces_list = {}
        # small_pimg_list = {}

        for id in np.unique(self.atlas_view.atlas_label):
            if id == 0:
                continue
            temp_atlas = self.atlas_view.atlas_data.copy()
            temp_atlas[self.atlas_view.atlas_label != id] = 0
            pimg = np.ascontiguousarray(temp_atlas[::factor, ::factor, ::factor])
            verts, faces = pg.isosurface(ndi.gaussian_filter(pimg.astype('float64'), (2, 2, 2)), np.max(temp_atlas) * level)

            # small_pimg_list[str(id)] = pimg
            self.small_verts_list[str(id)] = verts
            self.small_faces_list[str(id)] = faces

        outfile = open(os.path.join(self.atlas_folder, 'WHS_atlas_small_verts.pkl'), 'wb')
        pickle.dump(self.small_verts_list, outfile)
        outfile.close()

        outfile = open(os.path.join(self.atlas_folder, 'WHS_atlas_small_faces.pkl'), 'wb')
        pickle.dump(self.small_faces_list, outfile)
        outfile.close()

    # render volume
    # vol = np.empty(img.shape + (4,), dtype='ubyte')
    # vol[:] = img[..., None]
    # vol = np.ascontiguousarray(vol.transpose(1, 2, 0, 3))
    # vi = pgl.GLVolumeItem(vol)
    # self.glView.addItem(vi)
    # vi.translate(-vol.shape[0]/2., -vol.shape[1]/2., -vol.shape[2]/2.)

    def load_waxholm_rat_atlas(self):
        atlas_folder = '/Users/jingyig/Work/Kavli/WaxholmRat/'
        # infile = open(atlas_folder + '/WHS_atlas_labels.pkl', 'rb')
        # label_data = pickle.load(infile)
        # infile.close()
        # atlas_folder = str(QFileDialog.getExistingDirectory(self, "Select Atlas Folder"))
        if atlas_folder != '':
            self.statusbar.showMessage('Loading Atlas...')
            self.atlas_folder = atlas_folder
            with pg.BusyCursor():
                da_atlas = AtlasLoader(atlas_folder)
                atlas_data = np.transpose(da_atlas.atlas_data, [2, 0, 1])[::-1, :, :]
                segmentation_data = np.transpose(da_atlas.segmentation_data, [2, 0, 1])[::-1, :, :]

                s_boundary = np.transpose(da_atlas.boundary['s_contour'], [2, 0, 1])[::-1, :, :]
                c_boundary = np.transpose(da_atlas.boundary['c_contour'], [2, 0, 1])[::-1, :, :]
                h_boundary = np.transpose(da_atlas.boundary['h_contour'], [2, 0, 1])[::-1, :, :]

                boundary = {'s_contour': s_boundary, 'c_contour': c_boundary, 'h_contour': h_boundary}

                self.atlas_view.set_data(atlas_data, segmentation_data, da_atlas.atlas_info,
                                         da_atlas.label_info, boundary)
                self.atlas_view.working_cut_changed(self.atlas_display)
                self.reset_corners_atlas()

            self.statusbar.showMessage('Atlas Loaded.')

            pre_made_verts_path = os.path.join(atlas_folder, 'WHS_atlas_verts.pkl')
            pre_made_faces_path = os.path.join(atlas_folder, 'WHS_atlas_faces.pkl')

            if os.path.exists(pre_made_verts_path) and os.path.exists(pre_made_faces_path):

                infile = open(pre_made_verts_path, 'rb')
                self.verts = pickle.load(infile)
                infile.close()

                infile = open(pre_made_faces_path, 'rb')
                self.faces = pickle.load(infile)
                infile.close()

            else:
                self.statusbar.showMessage('Brain mesh is not found! Mesh is constructing in 3D view....')
                with pg.BusyCursor():
                    # rotm = np.dot(rotation_x(np.radians(90)), rotation_z(np.radians(90)))
                    self.verts, self.faces = render_volume(da_atlas.atlas_data, self.atlas_folder, factor=2, level=0.1)
                    # self.verts = np.dot(rotm, self.verts.T).T

            md = gl.MeshData(vertexes=self.verts, faces=self.faces)

            self.atlas_view.mesh.setMeshData(meshdata=md)
            self.mesh_origin = np.ravel(da_atlas.atlas_info[3]['Bregma']) / 2
            self.atlas_view.mesh.translate(-self.mesh_origin[0], -self.mesh_origin[1], -self.mesh_origin[2])

            self.statusbar.showMessage('Brain mesh is Loaded.')

            return

            pre_made_small_verts_path = os.path.join(atlas_folder, 'WHS_atlas_small_verts.pkl')
            pre_made_small_faces_path = os.path.join(atlas_folder, 'WHS_atlas_small_faces.pkl')
            if os.path.exists(pre_made_small_verts_path) and os.path.exists(pre_made_small_faces_path):

                infile = open(pre_made_small_verts_path, 'rb')
                self.small_verts_list = pickle.load(infile)
                infile.close()

                infile = open(pre_made_small_faces_path, 'rb')
                self.small_faces_list = pickle.load(infile)
                infile.close()
            else:
                self.statusbar.showMessage('Brain region mesh is not found! Rendering in 3D view....')
                with pg.BusyCursor():
                    self.render_small_volume(factor=2, level=0.1)

            for id in np.unique(self.atlas_view.atlas_label):
                if id == 0:
                    continue
                if id in self.atlas_view.label_info['index']:
                    id = int(id)
                    color_to_set = self.atlas_view.label_info['color'][(self.atlas_view.label_info['index'] == id)][0] / 255
                    md = gl.MeshData(vertexes=self.small_verts_list[str(id)], faces=self.small_faces_list[str(id)])
                    mesh = gl.GLMeshItem(meshdata=md, smooth=True,
                                         color=(color_to_set[0], color_to_set[1], color_to_set[2], 0.8), shader='balloon')
                    mesh.setGLOptions('opaque')
                    mesh.translate(-self.mesh_shape[0], -self.mesh_shape[1], -self.mesh_shape[2])
                    # mesh.setVisible(False)
                    self.small_mesh_list[str(id)] = mesh
                    self.small_mesh_list[str(id)].setVisible(False)

            mesh_keys = list(self.small_mesh_list.keys())
            for i in range(len(self.small_mesh_list)):
                self.view3d.addItem(self.small_mesh_list[mesh_keys[i]])

            self.sidebar.setCurrentIndex(0)

            self.statusbar.showMessage('Brain region mesh is Loaded.')






            # self.view1.autoRange(items=[self.coronal_img.atlas_img])
            # self.view2.autoRange(items=[self.sagital_img.atlas_img])
            # self.view3.autoRange(items=[self.horizon_img.atlas_img])
            # self.view4.autoRange(items=[self.sagital_img_copy.atlas_img])
            # # self.statusLabel.setText('')
            #
            # self.renderVolume(atlas_folder)
            self.statusbar.showMessage('Atlas loaded successfully.')

    # ------------------------------------------------------------------
    #
    #                       Image Loader
    #
    # ------------------------------------------------------------------

    def load_image(self):

        # path = "/Users/jingyig/Work/Kavli/PyCode/herrbs/test.jpeg"
        # image = cv2.imread(path)
        # window_name = 'image'
        # cv2.imshow(window_name, image)
        # cv2.waitKey(0)
        if self.image_view.image_file is not None:
            print('need to clean everything')


        # image_file = ImageReader("/Users/jingyig/Work/Kavli/PyCode/herrbs/test.jpeg")
        # self.image_view.set_data(image_file)

        image_file = CZIReader("/Users/jingyig/Work/Kavli/Data/HERBS_DATA/26455 S2 Sld5 RFG GFP Ida.czi")
        image_file.read_data(0.1, scene_index=0)
        self.image_view.set_data(image_file)
        self.reset_corners_hist()
        if self.atlas_view.atlas_data is None:
            self.show_only_image_window()
        else:
            self.show_2_windows()


        # self.hist_lut.setImageItem(self.image_view.current_color_img)

        # filter = "CZI (*.czi);;JPEG (*.jpg;*.jpeg);;PNG (*.png);;TIFF (*.tif)"
        # dlg = QFileDialog()
        # dlg.setFileMode(QFileDialog.ExistingFiles)
        # image_file_path = dlg.getOpenFileName(self, "Select Histological Image File", str(Path.home()), filter)

        # self.image_file_type = image_file_path[0][-4:].lower()
        # if image_file_path[0] != '':
        #     self.statusbar.showMessage('Image file loading ...')
        #     with pg.BusyCursor():
        #         with warnings.catch_warnings():
        #             warnings.filterwarnings("error")
        #             if self.image_file_type == '.czi':
        #                 image_file = CZIReader(image_file_path[0])
        #                 scale = self.image_view.scale_slider.value()
        #                 scale = 0.01 if scale == 0 else scale * 0.01
        #                 if self.image_view.check_scenes.isChecked():
        #                     image_file.read_data(scale, scene_index=None)
        #                 else:
        #                     image_file.read_data(scale, scene_index=0)
        #             else:
        #                 image_file = ImageReader(image_file_path[0])
        #         self.image_view.set_data(image_file)
        #     self.layerpanel.setEnabled(True)
        #     self.statusbar.showMessage('Image file loaded.')
        #     # change sidebar focus
        #     self.sidebar.setCurrentIndex(2)
        #     if self.atlas_view.atlas_data is None:
        #         self.show_only_image_window()
        #     else:
        #         self.histview.setVisible(True)
        # else:
        #     return

    def load_images(self):
        images_folder = str(QFileDialog.getExistingDirectory(self, "Select Images Folder"))
        print(images_folder)
        # histology_images_folder = '/Users/jingyig/Work/Kavli/PyCode/vitlab/racer/image/Jacopo 26504 S2 Sld1 NeuN DiI/'
        if images_folder != '':
            image_files_list = os.listdir(images_folder)
            image_files_list = natsorted(image_files_list)
            self.statusbar.showMessage('Image files loading ...')
            with pg.BusyCursor():
                with warnings.catch_warnings():
                    warnings.filterwarnings("error")
                    image_file = ImagesReader(images_folder, image_files_list)
                    self.image_view.set_data(image_file)

            self.sidebar.setCurrentIndex(3)
            self.statusbar.showMessage('Image files loaded.')
        else:
            return



def main():
    app = QApplication(argv)
    app.setStyleSheet(herrbs_style)
    # if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    #     app.instance().exec_()
    window = HERBS()
    window.show()

    exit(app.exec_())
    # app.exec_()


if __name__ == '__main__':
    main()



