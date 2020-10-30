# -*- coding: utf-8 -*-
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from cryostat_functions import load_107, split_107

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import sys 

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class TestPlot(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(TestPlot, self).__init__(*args, **kwargs)
        
        global sc
        sc = MplCanvas(self, width=5, height=4, dpi=100)
        sc.axes.plot([0,1,2,3,4], [1,2,3,2,5])
        
        # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
        toolbar = NavigationToolbar(sc, self)

        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(sc)

        # Create a placeholder widget to hold our toolbar and canvas.
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
    
# hello test comment for git

class SinglePhasePlot(QGroupBox):
    
    def __init__(self, *args, **kwargs):
        super(SinglePhasePlot, self).__init__(*args, **kwargs)
        
        self.setTitle("Single Phase Plots")
        
        filebutton = QPushButton("Choose File")
        filelabel = QLabel("")
        
        filelayout = QHBoxLayout()
        filelayout.addWidget(filebutton)
        filelayout.addWidget(filelabel) 
    
        coolbutton = QRadioButton("Cooldown/Warmup Phase")
        regenbutton = QRadioButton("Regeneration Phase")
        regbutton = QRadioButton("Regulation Phase")
        coolbutton.setChecked(True)
        
        buttonlayout = QVBoxLayout()
        buttonlayout.addWidget(coolbutton)
        buttonlayout.addWidget(regenbutton)
        buttonlayout.addWidget(regbutton)
        
        chooselabel = QLabel("Choose phase: ")
        choosephase = QComboBox()
        
        chooselayout = QHBoxLayout()
        chooselayout.addWidget(chooselabel)
        chooselayout.addWidget(choosephase)
        
        plot = QPushButton("Plot")
        
        layout = QVBoxLayout()
        layout.addLayout(filelayout)
        layout.addLayout(buttonlayout)
        layout.addLayout(chooselayout)
        layout.addWidget(plot)
        self.setLayout(layout)
        
        def open_file():
            path = QFileDialog.getOpenFileName(window, "Open")[0]
            if path:
                global logs
                filelabel.setText(path[0:15] + '...' + path[-25:]) 
                logs = split_107(load_107(path))
        
        #the following 3 functions are repetitive. is there a way to connect all three buttons to the same function
        #which then uses a conditional statement based on which button is pressed? is there a way to tell which button is pressed?
        def press_cool():
            options = ["cooldown", "warmup"]
            choosephase.clear()
            choosephase.addItems(options)
            global phasetype
            phasetype = 0
        
        def press_regen():
            options = list(logs[1].keys())
            choosephase.clear()
            choosephase.addItems(options)
            phasetype = 1 
            
        def press_reg():
            options = list(logs[2].keys())
            choosephase.clear()
            choosephase.addItems(options)
            phasetype = 2
        
        def choose_phase():
            phaseindex = choosephase.currentIndex()
            print(phaseindex)
            
        def show_plot():
            self.plot = TestPlot()
            self.plot.show()
        
        filebutton.clicked.connect(open_file)
        coolbutton.pressed.connect(press_cool)
        regenbutton.pressed.connect(press_regen)
        regbutton.pressed.connect(press_reg) 
        choosephase.activated.connect(choose_phase)
        plot.clicked.connect(show_plot)
        

app = QApplication(sys.argv)

window = SinglePhasePlot()
window.show()

app.exec_() 







