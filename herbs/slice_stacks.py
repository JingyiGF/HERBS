import os
import sys
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph.functions as fn
import pyqtgraph.functions as fn
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from movable_points import TriangulationPoints


class ClickableSlice(pg.ImageItem):
    class SignalProxy(QObject):
        mouseHovered = pyqtSignal(object)  # id
        mouseClicked = pyqtSignal(object)  # id

    def __init__(self):
        self._sigprox = ClickableSlice.SignalProxy()
        self.mouseHovered = self._sigprox.mouseHovered
        self.mouseClicked = self._sigprox.mouseClicked

        pg.ImageItem.__init__(self)

        self.setAcceptHoverEvents(True)
        self.setLevels((0, 1))
        self.setOpts(axisOrder='row-major')

    def set_data(self, atlas_data, scale=None):
        # self.label_data = label
        # self.atlas_data = atlas_data
        if scale is not None:
            self.resetTransform()
            self.scale(*scale)
        self.setImage(atlas_data, autoLevels=False)
        # self.label_img.setImage(self.label_data, autoLevels=False)

    def hoverEvent(self, event):
        if event.isExit():
            return
        try:
            pos = (event.pos())
        except (IndexError, AttributeError):
            return
        self.mouseHovered.emit(event)

    def mouseClickEvent(self, event):
        pos = (event.pos().x(), event.pos().y())
        # id = self.label_data[int(event.pos().x()), int(event.pos().y())]
        self.mouseClicked.emit(pos)
        # self.mouseClicked.emit([event, id])


# class SliceStack(QGraphicsItemGroup):
#     class SignalProxy(QtCore.QObject):
#         mouseHovered = QtCore.Signal(object)  # id
#         mouseClicked = QtCore.Signal(object)  # id
#
#     def __init__(self):
#         self._sigprox = SliceStack.SignalProxy()
#         self.mouseHovered = self._sigprox.mouseHovered
#         self.mouseClicked = self._sigprox.mouseClicked
#
#         QGraphicsItemGroup.__init__(self)
#         self.atlas_img = pg.ImageItem(levels=[0, 1])
#         self.label_img = pg.ImageItem()
#         self.atlas_img.setParentItem(self)
#         self.label_img.setParentItem(self)
#         self.label_img.setZValue(10)
#         self.label_img.setOpacity(0.5)
#         self.set_overlay('Multiply')
#
#         self.label_colors = {}
#         self.setAcceptHoverEvents(True)
#
#     def set_data(self, atlas, label, scale=None):
#         self.label_data = label
#         self.atlas_data = atlas
#         if scale is not None:
#             self.resetTransform()
#             self.scale(*scale)
#         self.atlas_img.setImage(self.atlas_data, autoLevels=False)
#         self.label_img.setImage(self.label_data, autoLevels=False)
#
#     def set_lut(self, lut):
#         self.label_img.setLookupTable(lut)
#
#     def set_overlay(self, overlay):
#         mode = getattr(QtGui.QPainter, 'CompositionMode_' + overlay)
#         self.label_img.setCompositionMode(mode)
#
#     def set_label_opacity(self, o):
#         self.label_img.setOpacity(o)
#
#     def setLabelColors(self, colors):
#         self.label_colors = colors
#
#     def hoverEvent(self, event):
#         if event.isExit():
#             return
#         try:
#             pos = (event.pos())
#             id = self.label_data[int(event.pos().x()), int(event.pos().y())]
#             # print(('pos', pos))
#         except (IndexError, AttributeError):
#             return
#         self.mouseHovered.emit([id, pos])
#
#     def mouseClickEvent(self, event):
#         pos = (event.pos().x(), event.pos().y())
#         # id = self.label_data[int(event.pos().x()), int(event.pos().y())]
#         self.mouseClicked.emit(pos)
#         # self.mouseClicked.emit([event, id])
#
#     def boundingRect(self):
#         return self.label_img.boundingRect()
#
#     def shape(self):
#         return self.label_img.shape


class SliceStacks(pg.GraphicsLayoutWidget):
    class SignalProxy(QObject):
        mouseHovered = pyqtSignal(object)  # id
        mouseClicked = pyqtSignal(object)  # id

    def __init__(self):
        self._sigprox = SliceStacks.SignalProxy()
        self.sig_mouse_hovered = self._sigprox.mouseHovered
        self.sig_mouse_clicked = self._sigprox.mouseClicked

        pg.GraphicsLayoutWidget.__init__(self)
        self.vb = self.addViewBox()
        self.setBackground('k')
        self.vb.setAspectLocked()
        self.vb.invertY(True)
        self.vb.setAcceptHoverEvents(True)

        # self.img = SliceStack()
        self.img = ClickableSlice()
        self.img.mouseClicked.connect(self.mouse_clicked)
        self.img.mouseHovered.connect(self.mouse_hovered)
        self.label_img = pg.ImageItem()
        self.label_img.setCompositionMode(QPainter.CompositionMode.CompositionMode_Multiply)
        self.boundary = pg.ImageItem()
        self.boundary.setCompositionMode(QPainter.CompositionMode.CompositionMode_Plus)
        self.boundary.setVisible(False)

        self.tri_pnts = TriangulationPoints()
        self.tri_lines_list = []

        self.circle_follow = pg.PlotDataItem(pen=pg.mkPen('r', width=2, style=Qt.DashLine))
        self.lasso_path = pg.PlotDataItem(pen=pg.mkPen(color='r', width=3, style=Qt.DashLine),
                                          symbolPen='r', symbol='o', symbolSize=4)

        self.overlay_img = pg.ImageItem()

        self.overlay_contour = pg.ImageItem()
        self.overlay_contour.setLevels(levels=(0, 1))

        self.mask_img = pg.ImageItem()
        # self.mask_img.setLevels(levels=(0, 1))

        self.virus_pnts = pg.ScatterPlotItem(pen=(133, 255, 117), symbolBrush=(133, 255, 117), symbolPen=(55, 55, 55),
                                             symbol='s', symbolSize=1)

        self.probe_pnts = pg.ScatterPlotItem(pen=pg.mkPen(color=(128, 128, 128)), symbol='+', symbolSize=2, brush=None)
        self.cell_pnts = pg.ScatterPlotItem(pen=QColor(238, 130, 238), symbol='d', symbolSize=2, brush=None)
        self.drawing_pnts = pg.ScatterPlotItem(pen='b', symbol='o', symbolSize=2, brush=None)
        self.contour_pnts = pg.ScatterPlotItem(pen='b', symbol='o', symbolSize=2, brush=None)

        self.temp_probe_line = pg.PlotDataItem(pen=pg.mkPen(color='r', width=1, style=Qt.DashLine))

        self.v_line = pg.InfiniteLine(angle=90, movable=False)
        self.h_line = pg.InfiniteLine(angle=0, movable=False)
        self.v_line.setVisible(False)
        self.h_line.setVisible(False)

        # self.overlay_img = []
        # for i in range(4):
        #     self.overlay_img.append(pg.ImageItem())

        self.vb.addItem(self.img)
        self.vb.addItem(self.label_img)
        self.vb.addItem(self.boundary)
        # for i in range(4):
        #     self.vb.addItem(self.overlay_img[i])
        self.vb.addItem(self.tri_pnts)
        self.vb.addItem(self.circle_follow)
        self.vb.addItem(self.lasso_path)

        self.vb.addItem(self.overlay_img)
        self.vb.addItem(self.overlay_contour)

        self.vb.addItem(self.mask_img)
        self.vb.addItem(self.virus_pnts)
        self.vb.addItem(self.temp_probe_line)
        self.vb.addItem(self.probe_pnts)
        self.vb.addItem(self.cell_pnts)
        self.vb.addItem(self.drawing_pnts)
        self.vb.addItem(self.contour_pnts)

        self.vb.addItem(self.v_line, ignoreBounds=True)
        self.vb.addItem(self.h_line, ignoreBounds=True)

    def set_data(self, atlas, label, contour, scale=None):
        self.img.set_data(atlas)
        self.label_img.setImage(label, autoLevels=False)
        self.boundary.setImage(contour, atutoLevels=False)


    def boundingRect(self):
        return self.label_img.boundingRect()

    def set_lut(self, lut):
        self.label_img.setLookupTable(lut)

    def set_overlay(self, overlay):
        mode = getattr(QtGui.QPainter, 'CompositionMode_' + overlay)
        self.label_img.setCompositionMode(mode)

    def set_label_opacity(self, o):
        self.label_img.setOpacity(o)

    def setLabelColors(self, colors):
        self.label_colors = colors

    def mouse_hovered(self, event):
        if event.isExit():
            return
        try:
            pos = (event.pos())
        except (IndexError, AttributeError):
            return
        self.sig_mouse_hovered.emit(pos)

    def mouse_clicked(self, pos):
        self.sig_mouse_clicked.emit(pos)

