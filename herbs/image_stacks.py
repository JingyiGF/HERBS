import colorsys
import os
import sys
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph.functions as fn
from .movable_points import TriangulationPoints


class ClickableImage(pg.ImageItem):
    class SignalProxy(QObject):
        mouseHovered = pyqtSignal(object)  # id
        mouseClicked = pyqtSignal(object)  # id

    def __init__(self):
        self._sigprox = ClickableImage.SignalProxy()
        self.mouseHovered = self._sigprox.mouseHovered
        self.mouseClicked = self._sigprox.mouseClicked

        pg.ImageItem.__init__(self)

        self.setAcceptHoverEvents(True)
        self.setOpts(axisOrder='row-major')

    def set_data(self, hist_image_data, scale=None):
        # self.label_data = label
        self.hist_data = hist_image_data
        if scale is not None:
            self.resetTransform()
            self.scale(*scale)
        self.setImage(self.hist_data, autoLevels=False)
        # self.label_img.setImage(self.label_data, autoLevels=False)

    def hoverEvent(self, event):
        if event.isExit():
            return
        try:
            pos = (event.pos())
            id = 1  # self.label_data[int(event.pos().x()), int(event.pos().y())]
        except (IndexError, AttributeError):
            return
        self.mouseHovered.emit(event)

    def mouseClickEvent(self, event):
        pos = (event.pos().x(), event.pos().y())
        # print(pos)
        # id = self.label_data[int(event.pos().x()), int(event.pos().y())]
        self.mouseClicked.emit(pos)
        # self.mouseClicked.emit([event, id])


class ImageStacks(pg.GraphicsLayoutWidget):
    class SignalProxy(QtCore.QObject):
        sigMouseHovered = QtCore.Signal(object)  # id
        sigMouseClicked = QtCore.Signal(object)  # id
        sigKeyPressed = QtCore.Signal(object)  # event

    def __init__(self):
        self._sigprox = ImageStacks.SignalProxy()
        self.sig_mouse_hovered = self._sigprox.sigMouseHovered
        self.sig_mouse_clicked = self._sigprox.sigMouseClicked
        self.sig_key_pressed = self._sigprox.sigKeyPressed

        pg.GraphicsLayoutWidget.__init__(self)

        self.data = None
        self.vb = self.addViewBox()
        self.setBackground('k')
        self.vb.setAspectLocked()
        self.vb.invertY(True)
        self.vb.setAcceptHoverEvents(True)

        self.img1 = ClickableImage()
        self.img1.mouseClicked.connect(self.mouse_clicked)
        self.img1.mouseHovered.connect(self.mouse_hovered)
        self.img2 = pg.ImageItem()
        self.img2.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_Plus)
        self.img3 = pg.ImageItem()
        self.img3.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_Plus)
        self.img4 = pg.ImageItem()
        self.img4.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_Plus)

        self.boundary = pg.ImageItem()
        self.lasso_path = pg.PlotDataItem(pen=pg.mkPen(color='r', width=3, style=Qt.DashLine),
                                          symbolPen='r', symbol='o', symbolSize=4)
        self.drawing_pnts = pg.ScatterPlotItem(pen='b', symbol='o', symbolSize=2, brush=None)
        self.probe_pnts = pg.ScatterPlotItem(pen='g', symbol='s', symbolSize=2, brush=None)
        self.cell_pnts = pg.ScatterPlotItem(pen=QColor(238, 130, 238), symbol='d', symbolSize=2, brush=None)
        self.circle_follow = pg.PlotDataItem(pen=pg.mkPen('r', width=2, style=Qt.DashLine))
        self.virus_img = pg.ImageItem()  # for virus injection
        self.mask_img = pg.ImageItem()  # for virus injection
        self.lines = pg.PlotDataItem()
        self.atlas_label = pg.ImageItem()
        self.atlas_label.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_Plus)
        self.atlas_contour = pg.ImageItem()
        self.atlas_contour.setLevels(levels=(0, 1))
        self.atlas_contour.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_Plus)
        self.tri_pnts = TriangulationPoints()
        self.tri_pnts.setVisible(False)
        self.tri_lines_list = []

        self.image_list = [self.img1, self.img2, self.img3, self.img4]

        for i in range(4):
            self.vb.addItem(self.image_list[i])
            self.image_list[i].setVisible(False)

        self.vb.addItem(self.boundary)
        self.vb.addItem(self.virus_img)
        self.vb.addItem(self.mask_img)
        self.vb.addItem(self.lasso_path)
        self.vb.addItem(self.drawing_pnts)
        self.vb.addItem(self.circle_follow)
        self.vb.addItem(self.probe_pnts)
        self.vb.addItem(self.cell_pnts)
        self.vb.addItem(self.lines)
        self.vb.addItem(self.atlas_label)
        self.vb.addItem(self.atlas_contour)
        self.vb.addItem(self.tri_pnts)

    def set_data(self, data, is_rgb=False, scale=None):
        self.data = data
        if scale is not None:
            self.resetTransform()
            self.scale(*scale)
        # for i in range(len(self.data)):
        if is_rgb:
            self.image_list[0].setImage(self.data, autoLevels=False)
            self.image_list[0].setVisible(True)
        else:
            for i in range(self.data.shape[2]):
                self.image_list[i].setImage(self.data[:, :, i], autoLevels=False)
                self.image_list[i].setVisible(True)
        # self.hist_lut.setLevels(0, 65535)

    def set_lut(self, lut_list):
        for i in range(self.data.shape[2]):
            self.image_list[i].setLevels(levels=(0, 65535))
            self.image_list[i].setLookupTable(lut_list[i])

    def set_opacity(self, is_rgb):
        if is_rgb:
            self.image_list[0].setOpts(opacity=1)
        else:
            for i in range(len(self.data)):
                self.image_list[i].setOpts(opacity=0)

    def boundingRect(self):
        return self.image_list[0].boundingRect()


    def mouse_hovered(self, event):
        if event.isExit():
            return
        try:
            pos = (event.pos())
            id = 1  # self.label_data[int(event.pos().x()), int(event.pos().y())]
        except (IndexError, AttributeError):
            return
        self.sig_mouse_hovered.emit(event)

    def mouse_clicked(self, pos):
        self.sig_mouse_clicked.emit(pos)

    def change_background_color(self, color: tuple):
        self.setBackground(color)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Backspace:
            print("Killing")
            self.sig_key_pressed.emit('delete')



