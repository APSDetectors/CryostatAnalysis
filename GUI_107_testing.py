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

import pandas as pd

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
        
class SummaryPlot(QGroupBox):
    def __init__(self):
        super(SummaryPlot, self).__init__()
        
        self.setTitle("Summary Quantity Plots")
        
        self.filebutton = QPushButton("Choose Files")
        self.filelabel = QLabel("")
        
        filelayout = QHBoxLayout()
        filelayout.addWidget(self.filebutton)
        filelayout.addWidget(self.filelabel) 
        
        self.maxcurrentbutton = QRadioButton("Max current vs. hold time")
        self.stddevbutton = QRadioButton("50 mK std dev vs. date")
        self.tempqtysbutton = QRadioButton("50 mK temperature qtys vs. date")
    
        buttonlayout = QVBoxLayout()
        buttonlayout.addWidget(self.maxcurrentbutton)
        buttonlayout.addWidget(self.stddevbutton)
        buttonlayout.addWidget(self.tempqtysbutton)
        
        self.plotbutton = QPushButton("Plot")
        
        layout = QVBoxLayout()
        layout.addLayout(filelayout)
        layout.addLayout(buttonlayout)
        layout.addWidget(self.plotbutton)
        self.setLayout(layout)
        
        self.filebutton.clicked.connect(self.open_files)
        
    def open_files(self):
        paths = QFileDialog.getOpenFileNames(self, "Open")[0]
        if paths: 
            dates = ""
            for i in paths: 
                firstrows = pd.read_csv(r'{}'.format(i), nrows = 3)
                print(firstrows)
                dates += str(firstrows.iloc[2,0][:10] + ' log')  + '\n'
            self.filelabel.setText(dates) 
        
        print(type(paths))
        print(paths)
    
    
app = QApplication(sys.argv)

window = SummaryPlot()
window.show()

app.exec_()