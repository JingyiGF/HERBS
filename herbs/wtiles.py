from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from .uuuuuu import read_qss_file

dialog_style = '''
QDialog {
    background-color: rgb(50, 50, 50);
    color: white;
    font-size: 12px;
    width: 50px;
}

QLabel {
    color: white;
    width: 50px;
}
'''


class LayerSettingDialog(QDialog):
    def __init__(self, window_name, min_val, max_val, val):
        super().__init__()

        self.setWindowTitle(window_name)
        self.setStyleSheet(dialog_style)

        self.val = val

        self.val_slider = QSlider(Qt.Horizontal)
        self.val_slider.setValue(val)
        self.val_slider.setMinimum(min_val)
        self.val_slider.setMaximum(max_val)
        self.val_slider.setSingleStep(1)
        self.val_slider.sliderMoved.connect(self.val_spinbox_changed)

        self.val_spinbox = QSpinBox()
        self.val_spinbox.setValue(val)
        self.val_spinbox.setMaximum(max_val)
        self.val_spinbox.setMinimum(min_val)
        self.val_spinbox.setSingleStep(1)
        self.val_spinbox.valueChanged.connect(self.value_changed)

        # ok button, used to close window
        ok_btn = QDialogButtonBox(QDialogButtonBox.Ok)
        ok_btn.accepted.connect(self.accept)

        # add widget to layout
        layout = QHBoxLayout()
        layout.addWidget(self.val_slider)
        layout.addWidget(self.val_spinbox)
        layout.addSpacing(10)
        layout.addWidget(ok_btn)
        self.setLayout(layout)

    def accept(self) -> None:
        self.close()

    def val_spinbox_changed(self):
        val = self.val_slider.value()
        self.val = val
        self.val_spinbox.setValue(val)

    def value_changed(self):
        val = self.val_spinbox.value()
        self.val = val
        self.val_slider.setValue(val)


class SliceSettingDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Current Slice Settings')
        self.setStyleSheet(dialog_style)

        self.cut = 'Coronal'
        self.width = 0
        self.height = 0
        self.distance = 0

        self.cut_combo = QComboBox()
        self.cut_combo.addItems(['Coronal', 'Sagittal', 'Horizontal'])
        self.cut_combo.currentIndexChanged.connect(self.cut_changed)

        width_label = QLabel('Width (mm):')
        height_label = QLabel('Height (mm):')
        distance_label = QLabel('Distance w.r.t. Bregma (mm):')

        self.width_val = QDoubleSpinBox()
        self.width_val.setValue(0)
        self.width_val.setRange(-50, 50)
        self.width_val.valueChanged.connect(self.width_val_changed)
        self.height_val = QDoubleSpinBox()
        self.height_val.setValue(0)
        self.height_val.setRange(-50, 50)
        self.height_val.valueChanged.connect(self.height_val_changed)
        self.distance_val = QDoubleSpinBox()
        self.distance_val.setValue(0)
        self.distance_val.setRange(-50, 50)
        self.distance_val.valueChanged.connect(self.distance_val_changed)

        # ok button, used to close window
        ok_btn = QDialogButtonBox(QDialogButtonBox.Ok)
        ok_btn.accepted.connect(self.accept)

        # add widget to layout
        content_frame = QFrame()
        content_layout = QGridLayout(content_frame)
        content_layout.addWidget(self.cut_combo, 0, 0, 1, 2)
        content_layout.addWidget(width_label, 1, 0, 1, 1)
        content_layout.addWidget(self.width_val, 1, 1, 1, 1)
        content_layout.addWidget(height_label, 2, 0, 1, 1)
        content_layout.addWidget(self.height_val, 2, 1, 1, 1)
        content_layout.addWidget(distance_label, 3, 0, 1, 1)
        content_layout.addWidget(self.distance_val, 3, 1, 1, 1)

        layout = QVBoxLayout()
        layout.addWidget(content_frame)
        layout.addWidget(ok_btn)
        self.setLayout(layout)

    def accept(self) -> None:
        self.close()

    def cut_changed(self):
        self.cut = self.cut_combo.currentText()

    def width_val_changed(self):
        self.width = self.width_val.value()

    def height_val_changed(self):
        self.height = self.height_val.value()

    def distance_val_changed(self):
        self.distance = self.distance_val.value()


class QDoubleButton(QPushButton):
    right_clicked = pyqtSignal()
    left_clicked = pyqtSignal()
    double_clicked = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(QDoubleButton, self).__init__(*args, **kwargs)

        btn_style = read_qss_file('qss/object_text_button.qss')
        self.setStyleSheet(btn_style)

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.setInterval(150)
        self.timer.timeout.connect(self.timeout)

        self.is_double = False
        self.is_left_click = True

        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if not self.timer.isActive():
                self.timer.start()

            self.is_left_click = False
            if event.button() == Qt.LeftButton:
                self.is_left_click = True

            return True

        elif event.type() == QEvent.MouseButtonDblClick:
            self.is_double = True
            return True

        return False

    def timeout(self):
        if self.is_double:
            self.double_clicked.emit()
        else:
            if self.is_left_click:
                self.left_clicked.emit()
            else:
                self.right_clicked.emit()

        self.is_double = False


class QLabelClickable(QLabel):
    # doubleClicked = pyqtSignal(object)
    clicked = pyqtSignal(object)

    def __init__(self, parent=None):
        super(QLabelClickable, self).__init__(parent)

    def mousePressEvent(self, event):
        self.ultimo = 'Click'

    def mouseReleaseEvent(self, event):
        if self.ultimo == 'Click':
            QTimer.singleShot(QApplication.instance().doubleClickInterval(),
                              self.performSingleClickAction)
        else:
            self.ultimo = 'doubleClick'
            self.clicked.emit(self.ultimo)

    def mouseDoubleClickEvent(self, event):
        self.ultimo = 'doubleClick'

    def performSingleClickAction(self):
        if self.ultimo == 'Click':
            self.clicked.emit(self.ultimo)
            self.update()


class QFrameClickable(QFrame):
    clicked = pyqtSignal(object)

    def __init__(self, parent=None):
        super(QFrameClickable, self).__init__(parent)

    # def mousePressEvent(self, QMouseEvent):
    #     if QMouseEvent.button() == Qt.LeftButton:
    #         self.clicked.emit()
    #     elif QMouseEvent.button() == Qt.RightButton:
    #         self.clicked.emit()
    #     self.update()

    def mousePressEvent(self, event):
        self.ultimo = 'Click'

    def mouseReleaseEvent(self, event):
        if self.ultimo == 'Click':
            QTimer.singleShot(QApplication.instance().doubleClickInterval(),
                              self.performSingleClickAction)
        else:
            self.ultimo = 'doubleClick'
            self.clicked.emit(self.ultimo)

    def mouseDoubleClickEvent(self, event):
        self.ultimo = 'doubleClick'

    def performSingleClickAction(self):
        if self.ultimo == 'Click':
            self.clicked.emit(self.ultimo)
            self.update()


class LineEditEntered(QLineEdit):
    sig_return_pressed = pyqtSignal()

    def __init__(self):
        QLineEdit.__init__(self)

    def keyPressEvent(self, event):
        super(LineEditEntered, self).keyPressEvent(event)

        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.sig_return_pressed.emit()

