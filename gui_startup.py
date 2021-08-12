from PyQt5 import QtCore, QtGui, QtWidgets
from driver_config_macros import *
import os

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(250, 90)
        MainWindow.setMinimumSize(QtCore.QSize(250, 90))
        MainWindow.setMaximumSize(QtCore.QSize(250, 90))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(".\\icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.driverLabel = QtWidgets.QLabel(self.centralwidget)
        self.driverLabel.setGeometry(QtCore.QRect(20, 20, 41, 21))
        self.driverLabel.setObjectName("driverLabel")
        self.driverComboBox = QtWidgets.QComboBox(self.centralwidget)
        self.driverComboBox.setGeometry(QtCore.QRect(60, 20, 71, 21))
        self.driverComboBox.setEditable(True)
        self.driverComboBox.setObjectName("driverComboBox")
        self.driverComboBox.addItem("")
        self.driverComboBox.addItem("")
        self.autoDetectButton = QtWidgets.QPushButton(self.centralwidget)
        self.autoDetectButton.setGeometry(QtCore.QRect(140, 20, 75, 23))
        self.autoDetectButton.setObjectName("autoDetectButton")
        self.doneButton = QtWidgets.QPushButton(self.centralwidget)
        self.doneButton.setGeometry(QtCore.QRect(80, 50, 75, 23))
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
