from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtCore, QtGui, QtWidgets

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

class TableModel(QtCore.QAbstractTableModel):

    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, x, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[x]
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return self._data.index[x]
        return None
    
class TableWindow(QMainWindow):
    def __init__(self, data):
        super().__init__()
        
        self.data = data
        self.table = QtWidgets.QTableView()
        self.model = TableModel(self.data)
        self.table.setModel(self.model)
        self.setCentralWidget(self.table)
        
class CoolWarmWindow(QWidget):
    def __init__(self,coollog,warmlog):
        super(CoolWarmWindow, self).__init__()
        
        self.coollog = coollog
        self.warmlog = warmlog
        
        self.coolbutton = QRadioButton("Cooldown time")
        self.warmbutton= QRadioButton("Warmup time")
        self.time = QLabel("")
        
        buttonlayout = QVBoxLayout()
        buttonlayout.addWidget(self.coolbutton)
        buttonlayout.addWidget(self.warmbutton)
        
        layout = QHBoxLayout()
        layout.addLayout(buttonlayout)
        layout.addWidget(self.time)
        self.setLayout(layout)
        
        self.coolbutton.pressed.connect(self.cooltime)
        self.warmbutton.pressed.connect(self.warmtime)

    def cooltime(self):
        text = str(round(cryo.coolwarm_time(self.coollog),3))
        self.time.setText(text + ' hours')
        
    def warmtime(self):
        text = str(round(cryo.coolwarm_time(self.warmlog),3))
        self.time.setText(text + ' hours')
       
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
        self.plotbutton.pressed.connect(self.show_plot)
        
    def open_file(self):
        path = QFileDialog.getOpenFileName(self, "Open")[0]
        if path:
            self.logs = cryo.split_107(cryo.load_107(path))
            self.filelabel.setText(str(self.logs[0]['log1'].iloc[0,0])[:10] + ' log') 
            cryo.temp_hold(self.logs[2])
    
    def chooseplottype(self): 
        sender = self.sender()
        self.plottype = sender.text()
        
    def show_plot(self):
        self.plotwindow = PlotWindow()
        typefunc = {"Mag cycle 50 mK temp":cryo.regen_temp_plots, "Mag cycle current":cryo.regen_mag_plots, "Temp hold 50 mK temp": cryo.reg_temp_plots, "Temp hold current": cryo.reg_mag_plots, "Temp hold 3K temp":cryo.reg_3K_plots}
        if 'Mag cycle' in self.plottype:
            typefunc[self.plottype](self.logs[1],self.plotwindow)
        elif "Temp hold" in self.plottype:
            typefunc[self.plottype](self.logs[2],self.plotwindow)
        
        
    
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
        self.tempqtysbutton = QRadioButton("Temperature qtys vs. date")
        
        self.setpoint = QLineEdit("Enter 50 mK setpoint (e.g. 0.06)")
        self.temp = QLineEdit("Enter temperature stage of interest (e.g. 3 K)") 
        
        currentlayout = QHBoxLayout()
        currentlayout.addWidget(self.maxcurrentbutton)
        currentlayout.addWidget(self.setpoint)
        
        templayout = QHBoxLayout()
        templayout.addWidget(self.tempqtysbutton)
        templayout.addWidget(self.temp)
        
        buttonlayout = QVBoxLayout()
        buttonlayout.addLayout(currentlayout)
        buttonlayout.addWidget(self.stddevbutton)
        buttonlayout.addLayout(templayout)
        
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
        self.plotbutton.pressed.connect(self.show_plot)
        
    def open_files(self):
        self.paths = QFileDialog.getOpenFileNames(self, "Open")[0]
        if self.paths: 
            dates = ""
            for i in self.paths: 
                firstrows = pd.read_csv(r'{}'.format(i), nrows = 3)
                dates += str(firstrows.iloc[2,0][:10] + ' log')  + '\n'
            self.filelabel.setText(dates) 
    
    def chooseplottype(self): 
        sender = self.sender()
        self.plottype = sender.text()
    
    def show_plot(self): 
        self.plotwindow = PlotWindow()
        typefunc = {"Max current vs. hold time":cryo.maxcurrent_holdtime, "50 mK std dev vs. date":cryo.stddev_time, "Temperature qtys vs. date":cryo.temp_minmaxmean}
        if self.plottype == "Max current vs. hold time":
            typefunc[self.plottype](self.paths,float(self.setpoint.text()), self.plotwindow)
        elif self.plottype == "Temperature qtys vs. date":
            typefunc[self.plottype](self.paths, self.temp.text(), self.plotwindow)
        else:
            typefunc[self.plottype](self.paths,self.plotwindow)
        
class SummaryData(QGroupBox):
    def __init__(self):
        super(SummaryData, self).__init__()
        
        self.setTitle("Summary Quantity Data")
        
        self.filebutton = QPushButton("Choose File")
        self.filelabel = QLabel("")
        
        filelayout = QHBoxLayout()
        filelayout.addWidget(self.filebutton)
        filelayout.addWidget(self.filelabel) 
        
        self.tempdatabutton = QRadioButton("Temperature summary qtys")
        self.magdatabutton = QRadioButton("Magnet summary qtys")
        self.regendatabutton = QRadioButton("Regen summary qtys")
        self.coolwarmbutton = QRadioButton("Cooldown/warmup time")
    
        buttonlayout = QVBoxLayout()
        buttonlayout.addWidget(self.tempdatabutton)
        buttonlayout.addWidget(self.magdatabutton)
        buttonlayout.addWidget(self.regendatabutton)
        buttonlayout.addWidget(self.coolwarmbutton)
        
        self.viewbutton = QPushButton("View data")
        self.savebutton = QPushButton("Save data")
        
        actionlayout = QHBoxLayout()
        actionlayout.addWidget(self.viewbutton)
        actionlayout.addWidget(self.savebutton)

        layout = QVBoxLayout()
        layout.addLayout(filelayout)
        layout.addLayout(buttonlayout)
        layout.addLayout(actionlayout)
        self.setLayout(layout)
        
        self.filebutton.clicked.connect(self.open_file)
        self.tempdatabutton.pressed.connect(self.choosecsvtype)
        self.magdatabutton.pressed.connect(self.choosecsvtype)
        self.regendatabutton.pressed.connect(self.choosecsvtype)
        self.coolwarmbutton.pressed.connect(self.choosecsvtype)
        self.viewbutton.clicked.connect(self.viewdata)
        self.savebutton.clicked.connect(self.save_file)
    
    def open_file(self):
        path = QFileDialog.getOpenFileName(self, "Open")[0]
        if path:
            self.logs = cryo.split_107(cryo.load_107(path))
            self.filelabel.setText(str(self.logs[0]['log1'].iloc[0,0])[:10] + ' log') 
            cryo.temp_hold(self.logs[2])
    
    def choosecsvtype(self): 
        sender = self.sender()
        self.csvtype = sender.text()
        if self.csvtype == "Temperature summary qtys":
            tempqtys = cryo.temp_summary(self.logs[2], 107)
            self.data = cryo.temp_summary_combine(tempqtys, 107)
        elif self.csvtype == "Magnet summary qtys":
            self.data = cryo.hold_summary(self.logs[2])
        elif self.csvtype == "Regen summary qtys":
            self.data = cryo.regen_summary(self.logs[1])
        elif self.csvtype == "Cooldown/warmup time":
            self.coollog = self.logs[0]['log1']
            self.warmlog = self.logs[0]['log{}'.format(str(len(self.logs[0])))]

    def viewdata(self):
        if self.csvtype != "Cooldown/warmup time":
            self.tablewindow = TableWindow(self.data)
            self.tablewindow.show() 
        elif self.csvtype == "Cooldown/warmup time":
            self.coolwarmdialog = CoolWarmWindow(self.coollog,self.warmlog) 
            self.coolwarmdialog.show()    
    
    def save_file(self):
        path = QFileDialog.getSaveFileName(self, "Save As",  '', "Excel (*.csv)")[0]
        if path:
            self.data.to_csv(path)
    
        
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.Q1 = SinglePhasePlot()
        self.Q2 = MultiplePhasePlot()
        self.Q3 = SummaryPlot()
        self.Q4 = SummaryData()
        
        layout = QGridLayout()
        layout.addWidget(self.Q1, 0, 0)
        layout.addWidget(self.Q2, 0, 1)
        layout.addWidget(self.Q3, 1, 0)
        layout.addWidget(self.Q4, 1, 1)
        
        widget = QWidget()
        widget.setLayout(layout)
        
        self.setCentralWidget(widget)


if __name__ == "__main__": 
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec_() 








