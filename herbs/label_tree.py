import os
import sys
import numpy as np
from PyQt5.QtWidgets import *
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph.functions as fn
from PyQt5.QtGui import QIcon, QPixmap, QColor
from PyQt5.QtCore import Qt, QSize



class SignalBlock(object):
    """Class used to temporarily block a Qt signal connection::

        with SignalBlock(signal, slot):
            # do something that emits a signal; it will
            # not be delivered to slot
    """
    def __init__(self, signal, slot):
        self.signal = signal
        self.slot = slot

    def __enter__(self):
        self.signal.disconnect(self.slot)
        return self

    def __exit__(self, *args):
        self.signal.connect(self.slot)
        

class LabelTree(QWidget):
    labels_changed = QtCore.Signal()
    
    def __init__(self, parent=None):
        self._block_signals = False
        QWidget.__init__(self, parent)
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.label_level = None
        self.current_lut = None
        
        self.tree = QTreeWidget(self)
        self.layout.addWidget(self.tree, 0, 0)
        self.tree.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.tree.headerItem().setText(0, "id")
        self.tree.headerItem().setText(1, "name")
        self.tree.headerItem().setText(2, "color")
        self.labels_by_id = {}
        self.labels_by_acronym = {}
        self.checked = set()
        self.tree.itemChanged.connect(self.item_change)
        
        self.reset_btn = QtGui.QPushButton('Reset colors')
        self.layout.addWidget(self.reset_btn, 1, 0)
        self.reset_btn.clicked.connect(self.reset_colors)
    
    def set_labels(self, label_data):
        self._block_signals = True
        try:
            n_labels = len(label_data['index'])
            self.label_level = np.max([ind for ind in label_data['index'] if ind not in label_data['parent']])
            self.current_lut = np.zeros((self.label_level + 1, 3), 'i')
            for i in range(n_labels):
                id = label_data['index'][i]
                parent = label_data['parent'][i]
                if parent < 0:
                    parent = -1
                color = label_data['color'][i]
                if id <= self.label_level:
                    self.current_lut[id] = np.array([color[0], color[1], color[2]])
                da_color = QColor(color[0], color[1], color[2]).name(QColor.HexRgb)
                da_color = da_color.split('#')[1]
                name = label_data['label'][i]
                acronym = label_data['abbrev'][i]
                rec = (id, parent, name.encode(), acronym.encode(), da_color.encode())
                self.add_label(*rec)
        finally:
            self._block_signals = False
        self.labels_changed.emit()

    def add_label(self, id, parent, name, acronym, color):
        item = QtGui.QTreeWidgetItem([acronym.decode(), name.decode(), ''])
        item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
        item.setCheckState(0, QtCore.Qt.Unchecked)
        if parent in self.labels_by_id:
            root = self.labels_by_id[parent]['item']
        else:
            root = self.tree.invisibleRootItem()
    
        root.addChild(item)
        btn = pg.ColorButton(color=pg.mkColor(color.decode()))
        btn.defaultColor = color.decode()
        btn.id = id
        self.tree.setItemWidget(item, 2, btn)
    
        self.labels_by_id[id] = {'item': item, 'btn': btn}
        item.id = id
        self.labels_by_acronym[acronym] = self.labels_by_id[id]
    
        btn.sigColorChanged.connect(self.item_color_changed)

    def item_change(self, item, col):
        checked = item.checkState(0) == QtCore.Qt.Checked
        with SignalBlock(self.tree.itemChanged, self.item_change):
            self.check_recursive(item, checked)
    
        if not self._block_signals:
            self.labels_changed.emit()

    def check_recursive(self, item, checked):
        if checked:
            self.checked.add(item.id)
            item.setCheckState(0, QtCore.Qt.Checked)
        else:
            if item.id in self.checked:
                self.checked.remove(item.id)
            item.setCheckState(0, QtCore.Qt.Unchecked)
    
        for i in range(item.childCount()):
            self.check_recursive(item.child(i), checked)

    def item_color_changed(self, btn):
        color = btn.color()
        self.set_label_color(btn.id, color)

    def set_label_color(self, label_id, color, recursive=True, emit=True):
        item = self.labels_by_id[label_id]['item']
        btn = self.labels_by_id[label_id]['btn']
        rgb_color = color.getRgb()
        self.current_lut[label_id] = np.array([rgb_color[0], rgb_color[1], rgb_color[2]])
        with SignalBlock(btn.sigColorChanged, self.item_color_changed):
            btn.setColor(color)
        if recursive:
            for i in range(item.childCount()):
                ch = item.child(i)
                self.set_label_color(ch.id, color, recursive=recursive, emit=False)
        if emit:
            self.labels_changed.emit()
    
    def lookup_table(self):
        lut = np.zeros((self.label_level + 1, 4), dtype=np.ubyte)
        # print(lut.shape)
        for id in self.checked:
            if id >= lut.shape[0]:
                continue
            lut[id] = self.labels_by_id[id]['btn'].color(mode='byte')
        return lut

    def reset_colors(self):
        try:
            self.blockSignals(True)
            for k, v in self.labels_by_id.items():
                self.set_label_color(k, v['btn'].defaultColor, recursive=False, emit=False)
        finally:
            self.blockSignals(False)
            self.labels_changed.emit()
    
    def describe(self, id):
        if id == 0:
            return ''
        else:
            if id not in self.labels_by_id:
                return "Unknown label: %d" % id
        descr = []
        item = self.labels_by_id[id]['item']
        name = str(item.text(1))
        while item not in [self.labels_by_acronym[b'Brain']['item'], self.labels_by_acronym[b'SpC']['item'], self.labels_by_acronym[b'IE']['item']]:
            descr.insert(0, str(item.text(0)))
            item = item.parent()
        return '[%d]' % id + ' > '.join(descr) + "  :  " + name