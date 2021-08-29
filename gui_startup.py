from PyQt5 import QtCore, QtGui, QtWidgets
from driver_config_macros import *
import os
import sys
from math import gcd

app_ = QtWidgets.QApplication(sys.argv)
w, h = app_.primaryScreen().size().width(), app_.primaryScreen().size().height()
#Screen Ratio Corrections
gcd_ = gcd(w, h)
resRatio = w/h
baseRatio = 16/9
wR = w/(gcd_*16) #Ratio Correction
hR = h/(gcd_*9) #Ratio Correction
widthRatio = 1#w/1920 #Full Width Ratio Correction
heightRatio = 1#h/1080 #Full Height Ratio Correction
print(wR, hR)
app_.exit()

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(250*widthRatio, 90*heightRatio)
        MainWindow.setMinimumSize(QtCore.QSize(250*widthRatio, 90*heightRatio))
        MainWindow.setMaximumSize(QtCore.QSize(250*widthRatio, 90*heightRatio))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(".\\icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.driverLabel = QtWidgets.QLabel(self.centralwidget)
        self.driverLabel.setGeometry(QtCore.QRect(20*widthRatio, 20*heightRatio, 41*widthRatio, 21*heightRatio))
        self.driverLabel.setObjectName("driverLabel")
        self.driverComboBox = QtWidgets.QComboBox(self.centralwidget)
        self.driverComboBox.setGeometry(QtCore.QRect(60*widthRatio, 20*heightRatio, 71*widthRatio, 21*heightRatio))
        self.driverComboBox.setEditable(True)
        self.driverComboBox.setObjectName("driverComboBox")
        self.driverComboBox.addItem("")
        self.driverComboBox.addItem("")
        self.autoDetectButton = QtWidgets.QPushButton(self.centralwidget)
        self.autoDetectButton.setGeometry(QtCore.QRect(140*widthRatio, 20*heightRatio, 75*widthRatio, 23*heightRatio))
        self.autoDetectButton.setObjectName("autoDetectButton")
        self.doneButton = QtWidgets.QPushButton(self.centralwidget)
        self.doneButton.setGeometry(QtCore.QRect(80*widthRatio, 50*heightRatio, 75*widthRatio, 23*heightRatio))
        self.doneButton.setObjectName("doneButton")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Driver Selection"))
        self.driverLabel.setText(_translate("MainWindow", "Driver"))
        self.driverComboBox.setItemText(0, _translate("MainWindow", "ps2000a"))
        self.driverComboBox.setItemText(1, _translate("MainWindow", "ps3000a"))
        self.autoDetectButton.setText(_translate("MainWindow", "Autodetect"))
        self.doneButton.setText(_translate("MainWindow", "Done"))

        self.autoDetectButton.clicked.connect(self.autodetect)
        self.driverComboBox.currentTextChanged.connect(self.driverCheck)
        self.doneButton.clicked.connect(self.done)

    def autodetect(self):
        self.driverComboBox.setCurrentText(driver_autodetect())

    def driverCheck(self):
        driver_replacement(self.driverComboBox.currentText())

    def done(self):
        app.exit()
        driver_replacement(self.driverComboBox.currentText())
        os.system('python gui.py')

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
