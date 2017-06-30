# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created: Fri Jun 30 11:25:35 2017
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(600, 400)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.saveToLabel = QtGui.QLabel(self.centralwidget)
        self.saveToLabel.setObjectName("saveToLabel")
        self.gridLayout.addWidget(self.saveToLabel, 1, 0, 1, 1)
        self.saveToPushButton = QtGui.QPushButton(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.saveToPushButton.sizePolicy().hasHeightForWidth())
        self.saveToPushButton.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/newPrefix/icon-folder-128.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.saveToPushButton.setIcon(icon)
        self.saveToPushButton.setObjectName("saveToPushButton")
        self.gridLayout.addWidget(self.saveToPushButton, 1, 1, 1, 1)
        self.acquirePushButton = QtGui.QPushButton(self.centralwidget)
        self.acquirePushButton.setCheckable(True)
        self.acquirePushButton.setChecked(True)
        self.acquirePushButton.setObjectName("acquirePushButton")
        self.gridLayout.addWidget(self.acquirePushButton, 0, 0, 1, 2)
        self.counterLabel = QtGui.QLabel(self.centralwidget)
        self.counterLabel.setObjectName("counterLabel")
        self.gridLayout.addWidget(self.counterLabel, 0, 2, 1, 1)
        self.counterSpinBox = QtGui.QSpinBox(self.centralwidget)
        self.counterSpinBox.setStyleSheet("QSpinBox{background: none}")
        self.counterSpinBox.setFrame(False)
        self.counterSpinBox.setReadOnly(False)
        self.counterSpinBox.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.counterSpinBox.setMinimum(-1)
        self.counterSpinBox.setObjectName("counterSpinBox")
        self.gridLayout.addWidget(self.counterSpinBox, 0, 3, 1, 1)
        self.saveToLineEdit = QtGui.QLineEdit(self.centralwidget)
        self.saveToLineEdit.setObjectName("saveToLineEdit")
        self.gridLayout.addWidget(self.saveToLineEdit, 1, 2, 1, 2)
        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(1, 1)
        self.gridLayout.setColumnStretch(2, 1)
        self.gridLayout.setColumnStretch(3, 4)
        self.verticalLayout.addLayout(self.gridLayout)
        self.imageView = ImageView(self.centralwidget)
        self.imageView.setObjectName("imageView")
        self.verticalLayout.addWidget(self.imageView)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 600, 25))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "pyCAM", None, QtGui.QApplication.UnicodeUTF8))
        self.saveToLabel.setText(QtGui.QApplication.translate("MainWindow", "Save to:", None, QtGui.QApplication.UnicodeUTF8))
        self.acquirePushButton.setText(QtGui.QApplication.translate("MainWindow", "Acquire", None, QtGui.QApplication.UnicodeUTF8))
        self.counterLabel.setText(QtGui.QApplication.translate("MainWindow", "Counter", None, QtGui.QApplication.UnicodeUTF8))

from pyqtgraph import ImageView
import resources_rc
