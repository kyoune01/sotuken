# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'design.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1051, 605)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.result = QtWidgets.QLabel(self.centralwidget)
        self.result.setGeometry(QtCore.QRect(750, 80, 281, 91))
        self.result.setStyleSheet("font: 20pt \"Sans Serif\";\n"
"text-align: center;\n"
"")
        self.result.setLineWidth(1)
        self.result.setAlignment(QtCore.Qt.AlignCenter)
        self.result.setObjectName("result")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(950, 210, 21, 31))
        self.label_3.setStyleSheet("font: 14pt \"Sans Serif\";")
        self.label_3.setObjectName("label_3")
        self.timer = QtWidgets.QLabel(self.centralwidget)
        self.timer.setGeometry(QtCore.QRect(780, 170, 221, 71))
        self.timer.setStyleSheet("font: 20pt \"Sans Serif\";\n"
"text-align: center;\n"
"")
        self.timer.setText("")
        self.timer.setAlignment(QtCore.Qt.AlignCenter)
        self.timer.setObjectName("timer")
        self.caputureImg = QtWidgets.QGraphicsView(self.centralwidget)
        self.caputureImg.setGeometry(QtCore.QRect(10, 80, 660, 500))
        self.caputureImg.setObjectName("caputureImg")
        self.StartButton = QtWidgets.QPushButton(self.centralwidget)
        self.StartButton.setGeometry(QtCore.QRect(820, 280, 141, 81))
        self.StartButton.setStyleSheet("font: 20pt \"Sans Serif\";")
        self.StartButton.setObjectName("StartButton")
        self.Question = QtWidgets.QLineEdit(self.centralwidget)
        self.Question.setGeometry(QtCore.QRect(10, 30, 661, 41))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.Question.setFont(font)
        self.Question.setObjectName("Question")
        self.Question.raise_()
        self.timer.raise_()
        self.result.raise_()
        self.label_3.raise_()
        self.caputureImg.raise_()
        self.StartButton.raise_()
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Window"))
        self.result.setText(_translate("MainWindow", "Result"))
        self.label_3.setText(_translate("MainWindow", "秒"))
        self.StartButton.setText(_translate("MainWindow", "Start"))
        self.Question.setText(_translate("MainWindow", "input Quetion"))

