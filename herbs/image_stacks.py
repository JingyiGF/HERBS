import colorsys
import os
import sys
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
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

        self.hist_data = None

        self.setAcceptHoverEvents(True)
        # self.setOpts(axisOrder='row-major')

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


class SliceStack(pg.GraphicsLayoutWidget):
    class SignalProxy(QObject):
        mouseHovered = pyqtSignal(object)  # id
        mouseClicked = pyqtSignal(object)  # id
        sigKeyPressed = pyqtSignal(object)  # event

    def __init__(self):
        self._sigprox = SliceStack.SignalProxy()
        self.sig_mouse_hovered = self._sigprox.mouseHovered
        self.sig_mouse_clicked = self._sigprox.mouseClicked
        self.sig_key_pressed = self._sigprox.sigKeyPressed

        pg.GraphicsLayoutWidget.__init__(self)

        self.data = None
        self.vb = self.addViewBox()
        self.setBackground('k')
        self.vb.setAspectLocked()
        self.vb.invertY(True)
        self.vb.setAcceptHoverEvents(True)
        # self.vb.enableAutoRange(enable=False)

        self.base_layer = ClickableImage()
        self.base_layer.mouseClicked.connect(self.mouse_clicked)
        self.base_layer.mouseHovered.connect(self.mouse_hovered)

        self.img_layer = pg.ImageItem()
        self.img_layer.setCompositionMode(QPainter.CompositionMode_Plus)

        circle_follow = pg.PlotDataItem(pen=pg.mkPen('r', width=2, style=Qt.DashLine))
        lasso_path = pg.PlotDataItem(pen=pg.mkPen(color=(0, 255, 255), width=3, style=Qt.DashLine),
                                     symbolPen=(0, 255, 255), symbol='o', symbolSize=4)

        ruler_path = pg.PlotDataItem(pen=pg.mkPen(color='y', width=3, style=Qt.DashLine),
                                     symbolPen='y', symbolBrush='y', symbol='s', symbolSize=4)

        overlay_img = pg.ImageItem()
        overlay_img.setCompositionMode(QPainter.CompositionMode_Plus)
        overlay_contour = pg.ImageItem()
        overlay_contour.setLevels(levels=(0, 1))

        mask_img = pg.ImageItem()
        mask_img.setLevels(levels=(0, 1))

        tri_pnts = TriangulationPoints()
        tri_pnts.setVisible(False)
        self.tri_lines_list = []

        grid_lines = pg.GridItem(pen=(128, 128, 128))
        grid_lines.setVisible(False)

        cell_pnts = pg.ScatterPlotItem(pen=(0, 255, 0), brush=(0, 255, 0), size=5, hoverSize=8)
        probe_pnts = pg.ScatterPlotItem(pen=(0, 0, 255), brush=(0, 0, 255), symbol='s', size=5, hoverSize=8)
        bregma_pnt = pg.ScatterPlotItem(pen=(180, 112, 57), brush=(180, 112, 57), symbol='star', size=10, hoverSize=15)

        drawing_pnts = pg.PlotDataItem(pen=pg.mkPen(color=(255, 102, 0), width=2), brush=None)
        contour_pnts = pg.PlotDataItem(pen=pg.mkPen(color=(255, 0, 255), width=3), brush=None)

        probe_trajectory = pg.PlotDataItem(pen=pg.mkPen(color=(0, 0, 255), width=2), brush=None)

        self.pre_trajectory_list = [pg.PlotDataItem(pen=pg.mkPen(color=(0, 0, 255), width=2), brush=None)]

        self.image_dict = {'atlas-overlay': overlay_img,
                           'overlay_contour': overlay_contour,
                           'atlas-drawing': drawing_pnts,
                           'atlas-contour': contour_pnts,
                           'atlas-mask': mask_img,
                           'grid_lines': grid_lines,
                           'tri_pnts': tri_pnts,
                           'circle_follow': circle_follow,
                           'lasso_path': lasso_path,
                           'atlas-probe': probe_pnts,
                           'bregma_pnt': bregma_pnt,
                           'ruler_path': ruler_path,
                           'atlas-cells': cell_pnts,
                           'atlas-trajectory': probe_trajectory}
        self.image_dict_keys = list(self.image_dict.keys())

        self.vb.addItem(self.base_layer)
        self.vb.addItem(self.img_layer)

        for i in range(len(self.image_dict)):
            self.vb.addItem(self.image_dict[self.image_dict_keys[i]])

        self.vb.addItem(self.pre_trajectory_list[0])

    def set_data(self, data, scale=None):
        self.data = data
        if scale is not None:
            self.resetTransform()
            self.scale(*scale)
        base_img = np.zeros(data.shape[:2], 'uint8')
        self.base_layer.setImage(base_img)
        self.img_layer.setImage(data)

    def set_pre_design_vis_data(self, data):
        n_probe = len(data)
        exist_n_probes = len(self.pre_trajectory_list)
        if n_probe < exist_n_probes:
            del_ind = np.arange(n_probe, exist_n_probes)[::-1]
            for i in del_ind:
                self.vb.removeItem(self.pre_trajectory_list[i])
                self.pre_trajectory_list[i].deleteLater()
                del self.pre_trajectory_list[i]
        elif n_probe > exist_n_probes:
            for i in range(exist_n_probes, n_probe):
                self.pre_trajectory_list.append(pg.PlotDataItem(pen=pg.mkPen(color=(0, 0, 255), width=2), brush=None))
                self.vb.addItem(self.pre_trajectory_list[-1])

        for i in range(n_probe):
            self.pre_trajectory_list[i].setData(data[i])

    def pre_trajectory_color_changed(self, col, lw):
        for i in range(len(self.pre_trajectory_list)):
            self.pre_trajectory_list[i].setPen(pg.mkPen(color=col, width=lw))

    def remove_pre_trajectories_vis_lines(self):
        del_ind = np.arange(len(self.pre_trajectory_list))[::-1]
        for i in del_ind:
            self.vb.removeItem(self.pre_trajectory_list[i])
            self.pre_trajectory_list[i].deleteLater()
            del self.pre_trajectory_list[i]
            # self.pre_trajectory_list[i].updateItems(True)
        self.pre_trajectory_list.clear()

    def boundingRect(self):
        return self.base_layer.boundingRect()

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

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Backspace:
            print("Killing")
            self.sig_key_pressed.emit('delete')


class ImageStacks(pg.GraphicsLayoutWidget):
    class SignalProxy(QObject):
        sigMouseHovered = pyqtSignal(object)  # id
        sigMouseClicked = pyqtSignal(object)  # id
        sigKeyPressed = pyqtSignal(object)  # event

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
        # self.vb.enableAutoRange(enable=False)

        self.base_layer = ClickableImage()
        self.base_layer.mouseClicked.connect(self.mouse_clicked)
        self.base_layer.mouseHovered.connect(self.mouse_hovered)

        img1 = pg.ImageItem()
        img1.setCompositionMode(QPainter.CompositionMode_Plus)
        img2 = pg.ImageItem()
        img2.setCompositionMode(QPainter.CompositionMode_Plus)
        img3 = pg.ImageItem()
        img3.setCompositionMode(QPainter.CompositionMode_Plus)
        img4 = pg.ImageItem()
        img4.setCompositionMode(QPainter.CompositionMode_Plus)

        circle_follow = pg.PlotDataItem(pen=pg.mkPen('r', width=2, style=Qt.DashLine))
        lasso_path = pg.PlotDataItem(pen=pg.mkPen(color=(0, 255, 255), width=3, style=Qt.DashLine),
                                     symbolPen=(0, 255, 255), symbol='o', symbolSize=4)
        ruler_path = pg.PlotDataItem(pen=pg.mkPen(color='y', width=3, style=Qt.DashLine),
                                     symbolPen='y', symbolBrush='y', symbol='s', symbolSize=4)

        overlay_img = pg.ImageItem()
        overlay_img.setCompositionMode(QPainter.CompositionMode_Plus)
        overlay_contour = pg.ImageItem()
        overlay_contour.setLevels(levels=(0, 1))

        mask_img = pg.ImageItem()
        mask_img.setLevels(levels=(0, 1))

        tri_pnts = TriangulationPoints()
        tri_pnts.setVisible(False)
        self.tri_lines_list = []

        grid_lines = pg.GridItem(pen=(128, 128, 128))
        grid_lines.setVisible(False)

        probe_pnts = pg.ScatterPlotItem(pen=(0, 0, 255), brush=(0, 0, 255), symbol='s', size=5, hoverSize=8)
        cell_pnts = pg.ScatterPlotItem(pen=(0, 255, 0), brush=(0, 255, 0), size=5, hoverSize=8)
        blob_pnts = pg.ScatterPlotItem(pen=(55, 55, 55), brush=(55, 55, 55), symbol='s', size=5)
        drawing_pnts = pg.PlotDataItem(pen=pg.mkPen(color=(255, 102, 0), width=2), brush=None)
        contour_pnts = pg.PlotDataItem(pen=pg.mkPen(color=(255, 0, 255), width=3), brush=None)

        probe_trajectory = pg.PlotDataItem(pen=pg.mkPen(color=(0, 0, 255), width=2), brush=None)

        virus_img = pg.ImageItem()
        virus_img.setLevels(levels=(0, 1))

        self.image_list = [img1, img2, img3, img4]
        self.image_dict = {'img-overlay': overlay_img,
                           'overlay_contour': overlay_contour,
                           'img-virus': virus_img,
                           'img-contour': contour_pnts,
                           'img-mask': mask_img,
                           'grid_lines': grid_lines,
                           'tri_pnts': tri_pnts,
                           'circle_follow': circle_follow,
                           'lasso_path': lasso_path,
                           'ruler_path': ruler_path,
                           'img-probe': probe_pnts,
                           'img-cells': cell_pnts,
                           'img-blob': blob_pnts,
                           'img-drawing': drawing_pnts,
                           'img-trajectory': probe_trajectory}
        self.image_dict_keys = list(self.image_dict.keys())

        self.vb.addItem(self.base_layer)
        for i in range(4):
            self.vb.addItem(self.image_list[i])
            self.image_list[i].setVisible(False)

        for i in range(len(self.image_dict)):
            self.vb.addItem(self.image_dict[self.image_dict_keys[i]])

    def set_data(self, data, scale=None):
        self.data = data
        if scale is not None:
            self.resetTransform()
            self.scale(*scale)
        base_img = np.zeros(data.shape[:2], 'uint8')
        self.base_layer.setImage(base_img)
        for i in range(self.data.shape[2]):
            self.image_list[i].setImage(self.data[:, :, i], autoLevels=False)
            self.image_list[i].setVisible(True)

    def set_lut(self, lut_list, bit_level):
        for i in range(self.data.shape[2]):
            self.image_list[i].setLevels(levels=(0, bit_level))
            self.image_list[i].setLookupTable(lut_list[i])

    def set_opacity(self, val):
        for i in range(len(self.data)):
            self.image_list[i].setOpts(opacity=val)

    def boundingRect(self):
        return self.base_layer.boundingRect()

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
        if event.key() == Qt.Key_Backspace or event.key() == Qt.Key_Delete:
            print("Killing")
            self.sig_key_pressed.emit('delete')
        # elif event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
        #     print('enter')
        #     self.sig_key_pressed.emit('enter')



