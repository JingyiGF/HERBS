import os
import sys
import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import *
from pyqtgraph.Qt import QtGui, QtCore


class MovablePoints(pg.GraphItem):
    mouseHovered = pyqtSignal(object)
    mouseDragged = pyqtSignal(object)
    mouseClicked = pyqtSignal(object)

    def __init__(self):
        self.dragPoint = None
        self.dragOffset = None
        pg.GraphItem.__init__(self)
        self.data = None
        self.y_range = None

    def setData(self, **kwds):
        self.data = kwds
        if 'pos' in self.data:
            if self.y_range is None:
                self.y_range = self.data['pos'][-1, 1]
            self.npts = self.data['pos'].shape[0]
            self.data['data'] = np.empty(self.npts, dtype=[('index', int)])
            self.data['data']['index'] = np.arange(self.npts)
        self.updateGraph()

    def updateGraph(self):
        pg.GraphItem.setData(self, **self.data)

    def mouseDragEvent(self, ev):
        if ev.button() != QtCore.Qt.LeftButton:
            ev.ignore()
            return

        if ev.isStart():
            pos = ev.buttonDownPos()
            pts = self.scatter.pointsAt(pos)
            if len(pts) == 0:
                # self.mouseClicked.emit(ev)
                ev.ignore()
                return
            self.dragPoint = pts[0]
            ind = pts[0].data()[0]
            if ind in [0, self.npts-1]:
                return
            self.dragOffset = self.data['pos'][ind] - pos
        elif ev.isFinish():
            self.dragPoint = None
            return
        else:
            if self.dragPoint is None:
                ev.ignore()
                return

        ind = self.dragPoint.data()[0]
        temp_pos = ev.pos()
        if temp_pos[0] <= self.data['pos'][ind - 1, 0]:
            temp_pos[0] = self.data['pos'][ind - 1, 0] + 1
        if temp_pos[0] >= self.data['pos'][ind + 1, 0]:
            temp_pos[0] = self.data['pos'][ind + 1, 0] - 1

        self.data['pos'][ind] = temp_pos + self.dragOffset
        self.data['pos'][self.data['pos'][:, 1] > self.y_range, 1] = self.y_range
        self.data['pos'][self.data['pos'][:, 1] < 0, 1] = 0
        self.updateGraph()
        self.mouseDragged.emit((ev, ind))
        ev.accept()

    def clear(self):
        self.scatter.clear()



class TriangulationPoints(pg.GraphItem):
    mouseHovered = pyqtSignal(object)
    mouseDragged = pyqtSignal(object)
    mouseClicked = pyqtSignal(object)

    def __init__(self):
        self.dragPoint = None
        self.dragOffset = None
        pg.GraphItem.__init__(self)
        self.scatter.sigClicked.connect(self.onclick)
        self.data = None
        self.y_range = None
        self.x_range = None

    def setData(self, **kwds):
        self.data = kwds
        if 'pos' in self.data:
            self.npts = self.data['pos'].shape[0]
            self.data['data'] = np.empty(self.npts, dtype=[('index', int)])
            self.data['data']['index'] = np.arange(self.npts)
        self.update_graph()

    def set_range(self, x_range, y_range):
        self.x_range = x_range
        self.y_range = y_range

    def mouseDragEvent(self, ev):
        if ev.button() != Qt.LeftButton:
            ev.ignore()
            return

        if ev.isStart():
            pos = ev.buttonDownPos()
            pts = self.scatter.pointsAt(pos)
            if len(pts) == 0:
                # self.mouseClicked.emit(ev)
                ev.ignore()
                return
            self.dragPoint = pts[0]
            ind = pts[0].data()[0]

            self.dragOffset = self.data['pos'][ind] - pos
        elif ev.isFinish():
            self.dragPoint = None
            return
        else:
            if self.dragPoint is None:
                ev.ignore()
                return

        ind = self.dragPoint.data()[0]
        temp_pos = ev.pos()
        if temp_pos[0] <= 0:
            temp_pos[0] = 0
        if temp_pos[0] >= self.x_range:
            temp_pos[0] = self.x_range
        if temp_pos[1] <= 0:
            temp_pos[1] = 0
        if temp_pos[1] >= self.y_range:
            temp_pos[1] = self.y_range

        self.data['pos'][ind] = temp_pos + self.dragOffset

        self.update_graph()
        self.mouseDragged.emit((ev, ind))
        ev.accept()

    def update_graph(self):
        pg.GraphItem.setData(self, **self.data)

    def onclick(self, ev, point):
        ind = point[0].data()[0]
        print(ind)
        self.mouseClicked.emit((ev, ind))





class TriangulationPointsTest(pg.ScatterPlotItem):
    mouseHovered = pyqtSignal(object)
    mouseDragged = pyqtSignal(object)
    mouseClicked = pyqtSignal(object)

    def __init__(self):

        pg.ScatterPlotItem.__init__(self)
        self.sigClicked.connect(self.onclick)

        self.data = None

        self.y_range = None
        self.x_range = None

        self.drag_point = None
        self.drag_offset = None

        dtype = [
            ('x', float),
            ('y', float),
            ('size', float),
            ('symbol', object),
            ('pen', object),
            ('brush', object),
            ('visible', bool),
            ('data', object),
            ('hovered', bool),
            ('item', object),
            ('index', int),
            ('sourceRect', [
                ('x', int),
                ('y', int),
                ('w', int),
                ('h', int)
            ])
        ]

        self.data = np.empty(0, dtype=dtype)

    def setData(self, **kwds):
        self.data = kwds
        if 'pos' in self.data:
            self.npts = self.data['pos'].shape[0]
            self.data['data'] = np.empty(self.npts, dtype=[('index', int)])
            self.data['data']['index'] = np.arange(self.npts)
        # self.update_graph()

    def set_range(self, x_range, y_range):
        self.x_range = x_range
        self.y_range = y_range

    def mouseDragEvent(self, ev):
        if ev.button() != Qt.LeftButton:
            ev.ignore()
            return

        if ev.isStart():
            pos = ev.buttonDownPos()
            pts = self.pointsAt(pos)
            if len(pts) == 0:
                # self.mouseClicked.emit(ev)
                ev.ignore()
                return
            self.dragPoint = pts[0]
            ind = pts[0].data()[0]

            self.drag_offset = self.data['pos'][ind] - pos
        elif ev.isFinish():
            self.drag_point = None
            return
        else:
            if self.drag_point is None:
                ev.ignore()
                return

        ind = self.dragPoint.data()[0]
        temp_pos = ev.pos()
        if temp_pos[0] <= 0:
            temp_pos[0] = 0
        if temp_pos[0] >= self.x_range:
            temp_pos[0] = self.x_range
        if temp_pos[1] <= 0:
            temp_pos[1] = 0
        if temp_pos[1] >= self.y_range:
            temp_pos[1] = self.y_range

        self.data['pos'][ind] = temp_pos + self.dragOffset

        self.setData(pos=self.data['pos'])
        self.mouseDragged.emit((ev, ind))
        ev.accept()

    # def update_graph(self):
    #     pg.ScatterPlotItem.setData(self, **self.data)

    def onclick(self, ev, point):
        ind = point[0].data()[0]
        print(ind)
        self.mouseClicked.emit((ev, ind))

