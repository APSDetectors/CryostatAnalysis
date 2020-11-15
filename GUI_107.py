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
    
class PlotWindow(QMainWindow):

    def __init__(self):
        super(PlotWindow, self).__init__()
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        toolbar = NavigationToolbar(self.canvas, self)
        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.canvas)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
       
class SinglePhasePlot(QGroupBox):
    
    def __init__(self):
        super(SinglePhasePlot, self).__init__()
        
        self.setTitle("Single Phase Plots")
        
        self.filebutton = QPushButton("Choose File")
        self.filelabel = QLabel("")
        
        filelayout = QHBoxLayout()
        filelayout.addWidget(self.filebutton)
        filelayout.addWidget(self.filelabel) 
    
        self.coolbutton = QRadioButton("Cooldown/Warmup Phase")
        self.regenbutton = QRadioButton("Regeneration Phase")
        self.regbutton = QRadioButton("Regulation Phase")
        
        buttonlayout = QVBoxLayout()
        buttonlayout.addWidget(self.coolbutton)
        buttonlayout.addWidget(self.regenbutton)
        buttonlayout.addWidget(self.regbutton)
        
        self.chooselabel = QLabel("Choose phase: ")
        self.choosephase = QComboBox()
        
        chooselayout = QHBoxLayout()
        chooselayout.addWidget(self.chooselabel)
        chooselayout.addWidget(self.choosephase)
        
        self.plot = QPushButton("Plot")
        
        layout = QVBoxLayout()
        layout.addLayout(filelayout)
        layout.addLayout(buttonlayout)
        layout.addLayout(chooselayout)
        layout.addWidget(self.plot)
        self.setLayout(layout)
        
        self.filebutton.clicked.connect(self.open_file)
        self.coolbutton.pressed.connect(self.press_cool)
        self.regenbutton.pressed.connect(self.press_regen)
        self.regbutton.pressed.connect(self.press_reg) 
        self.choosephase.activated.connect(self.choose_phase)
        self.plot.clicked.connect(self.show_plot)
    
    def open_file(self):
        path = QFileDialog.getOpenFileName(self, "Open")[0]
        if path:
            self.logs = cryo.split_107(cryo.load_107(path))
            self.filelabel.setText(str(self.logs[0]['log1'].iloc[0,0])[:10] + ' log') 
            
    def press_cool(self):
        options = ["cooldown", "warmup"]
        self.choosephase.clear()
        self.choosephase.addItems(options)
        self.phasetype = 0
        
    def press_regen(self):
        options = list(self.logs[1].keys())
        self.choosephase.clear()
        self.choosephase.addItems(options)
        self.phasetype = 1 
            
    def press_reg(self):
        options = list(self.logs[2].keys())
        self.choosephase.clear()
        self.choosephase.addItems(options)
        self.phasetype = 2
        
    def choose_phase(self):
        self.phaseindex = self.choosephase.currentIndex()
        print(self.phaseindex)
            
    def show_plot(self):
        self.plotwindow = PlotWindow()
        if self.phasetype == 0: 
            if self.phaseindex == 0:
                cryo.cooldown_plot(self.logs[0]['log1'],self.plotwindow)
            elif self.phaseindex == 1: 
                cryo.cooldown_plot(self.logs[0]['log{}'.format(len(self.logs[0]))],self.plotwindow)
        if self.phasetype ==1: 
            cryo.regen_plot(self.logs[1]['regen{}'.format(self.phaseindex+1)],self.plotwindow)
        if self.phasetype ==2: 
            cryo.reg_plot(self.logs[2]['reg{}'.format(self.phaseindex+1)],self.plotwindow)
        self.plotwindow.show()
        
class MultiplePhasePlot(QGroupBox):
    def __init__(self):
        super(MultiplePhasePlot, self).__init__()
        
        self.setTitle("Multiple Phase Plots")
        
        self.filebutton = QPushButton("Choose File")
        self.filelabel = QLabel("")
        
        filelayout = QHBoxLayout()
        filelayout.addWidget(self.filebutton)
        filelayout.addWidget(self.filelabel) 
        
        self.regentempbutton = QRadioButton("Mag cycle 50 mK temp")
        self.regenmagbutton = QRadioButton("Mag cycle current")
        self.regtempbutton = QRadioButton("Temp hold 50 mK temp")
        self.regmagbutton = QRadioButton("Temp hold current")
        self.reg3kbutton = QRadioButton("Temp hold 3K temp")
        
        buttonlayout = QVBoxLayout()
        buttonlayout.addWidget(self.regentempbutton)
        buttonlayout.addWidget(self.regenmagbutton)
        buttonlayout.addWidget(self.regtempbutton)
        buttonlayout.addWidget(self.regmagbutton)
        buttonlayout.addWidget(self.reg3kbutton)
    
        self.plotbutton = QPushButton("Plot")
        
        layout = QVBoxLayout()
        layout.addLayout(filelayout)
        layout.addLayout(buttonlayout)
        layout.addWidget(self.plotbutton)
        self.setLayout(layout)
        
        self.filebutton.clicked.connect(self.open_file)
        self.regentempbutton.pressed.connect(self.chooseplottype)
        self.regenmagbutton.pressed.connect(self.chooseplottype)
        self.regtempbutton.pressed.connect(self.chooseplottype)
        self.regmagbutton.pressed.connect(self.chooseplottype)
        self.reg3kbutton.pressed.connect(self.chooseplottype)
        
    def open_file(self):
        path = QFileDialog.getOpenFileName(self, "Open")[0]
        if path:
            self.logs = cryo.split_107(cryo.load_107(path))
            self.filelabel.setText(str(self.logs[0]['log1'].iloc[0,0])[:10] + ' log') 
            cryo.temp_hold(self.logs[2])
    
    def chooseplottype(self): 
        sender = self.sender()
        plottype = sender.text()
        print(plottype)
    
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
        self.maxcurrentbutton.pressed.connect(self.chooseplottype)
        self.stddevbutton.pressed.connect(self.chooseplottype)
        self.tempqtysbutton.pressed.connect(self.chooseplottype)
        
    def open_files(self):
        paths = QFileDialog.getOpenFileNames(self, "Open")[0]
        if paths: 
            dates = ""
            for i in paths: 
                firstrows = pd.read_csv(r'{}'.format(i), nrows = 3)
                print(firstrows)
                dates += str(firstrows.iloc[2,0][:10] + ' log')  + '\n'
            self.filelabel.setText(dates) 
    
    def chooseplottype(self): 
        sender = self.sender()
        plottype = sender.text()
        print(plottype)
        
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.Q1 = SinglePhasePlot()
        self.Q2 = MultiplePhasePlot()
        self.Q3 = SummaryPlot()
        
        layout = QGridLayout()
        layout.addWidget(self.Q1, 0, 0)
        layout.addWidget(self.Q2, 0, 1)
        layout.addWidget(self.Q3, 1, 0)
        
        widget = QWidget()
        widget.setLayout(layout)
        
        self.setCentralWidget(widget)
        
        
        
app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec_() 







