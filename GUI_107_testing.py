# -*- coding: utf-8 -*-
"""
Created on Sun Nov  8 22:07:14 2020

@author: Goldfishy
"""
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import cryostat_functions as cryo

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar

import sys 

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = plt.figure()
        super(MplCanvas, self).__init__(self.fig)
    def figure(self,grid): 
        self.axes = self.fig.add_subplot(111)
        pass
    
class PlotWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(PlotWindow, self).__init__(*args, **kwargs)
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        toolbar = NavigationToolbar(self.canvas, self)
        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.canvas)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        
'''
app= QApplication([])
window = PlotWindow() 
ax = window.canvas.fig.add_subplot(111)
ax.plot([1,2,3],[5,8,2])
window.show()
app.exec_()
'''

log=cryo.load_107(r"C:\Users\Goldfishy\Documents\Argonne 2020\Cyrostat Scrips\2019_08_23_09;43snout_swissx_M-451.csv")
dicts = cryo.split_107(log)
app= QApplication([])
window = PlotWindow()
cryo.reg_plot(dicts[2]['reg1'],window)
window.show()
app.exec_()

