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
from .movable_points import TriangulationPoints


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

        tri_pnts = TriangulationPoints()
        self.tri_lines_list = []

        circle_follow = pg.PlotDataItem(pen=pg.mkPen('r', width=2, style=Qt.DashLine))
        lasso_path = pg.PlotDataItem(pen=pg.mkPen(color=(0, 255, 255), width=3, style=Qt.DashLine),
                                     symbolPen=(0, 255, 255), symbol='o', symbolSize=4)
        ruler_path = pg.PlotDataItem(pen=pg.mkPen(color='y', width=3, style=Qt.DashLine),
                                     symbolPen='y', symbolBrush='y', symbol='s', symbolSize=3)

        overlay_img = pg.ImageItem()

        overlay_contour = pg.ImageItem()
        overlay_contour.setLevels(levels=(0, 1))

        mask_img = pg.ImageItem()
        mask_img.setLevels(levels=(0, 1))

        grid_lines = pg.GridItem(pen=(128, 128, 128))
        grid_lines.setVisible(False)

        virus_pnts = pg.ScatterPlotItem(pen=(133, 255, 117), brush=(133, 255, 117), symbol='s', size=5, hoverSize=8)
        probe_pnts = pg.ScatterPlotItem(pen=(0, 0, 255), brush=(0, 0, 255), symbol='s', size=5, hoverSize=8)
        cell_pnts = pg.ScatterPlotItem(pen=(0, 255, 0), brush=(0, 255, 0), size=5, hoverSize=8)
        drawing_pnts = pg.PlotDataItem(pen=pg.mkPen(color=(255, 102, 0), width=2), brush=None)
        contour_pnts = pg.PlotDataItem(pen=pg.mkPen(color=(255, 0, 255), width=3), brush=None)

        self.pre_trajectory_list = []
        for i in range(4):
            self.pre_trajectory_list.append(pg.PlotDataItem(pen=pg.mkPen(color=(0, 0, 255), width=2), brush=None))

        self.image_dict = {'atlas-overlay': overlay_img,
                           'atlas-mask': mask_img,
                           'grid_lines': grid_lines,
                           'tri_pnts': tri_pnts,
                           'circle_follow': circle_follow,
                           'lasso_path': lasso_path,
                           'atlas-virus': virus_pnts,
                           'atlas-contour': contour_pnts,
                           'atlas-probe': probe_pnts,
                           'atlas-cells': cell_pnts,
                           'ruler_path': ruler_path,
                           'atlas-drawing': drawing_pnts}
        self.image_dict_keys = list(self.image_dict.keys())

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

        for i in range(len(self.image_dict)):
            self.vb.addItem(self.image_dict[self.image_dict_keys[i]])

        for i in range(4):
            self.vb.addItem(self.pre_trajectory_list[i])

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

