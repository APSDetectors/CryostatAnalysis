from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import cryostat_functions as cryo

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar

import sys 

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = plt.figure()
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)
    def figure(self,grid): 
        pass
    
class PlotWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(PlotWindow, self).__init__(*args, **kwargs)
        
    def new_canvas(self):
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        toolbar = NavigationToolbar(self.canvas, self)
        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.canvas)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
    


log=cryo.load_107(r"C:\Users\Goldfishy\Documents\Argonne 2020\Cyrostat Scrips\2019_08_23_09;43snout_swissx_M-451.csv")
dicts = cryo.split_107(log)
app= QApplication([])
window = PlotWindow()
window.new_canvas()
cryo.cooldown_plot(dicts[0]['log1'],window)
window.show()
app.exec_()


       
class SinglePhasePlot(QGroupBox):
    
    def __init__(self, *args, **kwargs):
        super(SinglePhasePlot, self).__init__(*args, **kwargs)
        
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
        path = QFileDialog.getOpenFileName(window, "Open")[0]
        if path:
            global logs
            self.filelabel.setText(path[0:15] + '...' + path[-25:]) 
            logs = cryo.split_107(cryo.load_107(path))
        
        #the following 3 functions are repetitive. is there a way to connect all three buttons to the same function
        #which then uses a conditional statement based on which button is pressed? is there a way to tell which button is pressed?
    def press_cool(self):
        options = ["cooldown", "warmup"]
        self.choosephase.clear()
        self.choosephase.addItems(options)
        #self.phasetype = 0?
        
    def press_regen(self):
        options = list(logs[1].keys())
        self.choosephase.clear()
        self.choosephase.addItems(options)
        phasetype = 1 
            
    def press_reg(self):
        options = list(logs[2].keys())
        self.choosephase.clear()
        self.choosephase.addItems(options)
        phasetype = 2
        
    def choose_phase(self):
        phaseindex = self.choosephase.currentIndex()
        print(phaseindex)
            
    def show_plot(self):
        self.plotwindow = TestPlot()
        self.plotwindow.show()
        
        
'''   

app = QApplication(sys.argv)

window = SinglePhasePlot()
window.show()

app.exec_() 

'''





