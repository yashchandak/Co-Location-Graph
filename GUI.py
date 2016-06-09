# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'GUI.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!
import numpy

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QGraphicsScene, QFileDialog, QPixmap
import YOLO_tiny_tf

#import cv2



try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(737, 483)
        
        self.radioButton = QtGui.QRadioButton(Dialog)
        self.radioButton.setGeometry(QtCore.QRect(20, 20, 117, 22))
        self.radioButton.setChecked(True)
        self.radioButton.setObjectName(_fromUtf8("radioButton"))
        self.radioButton_2 = QtGui.QRadioButton(Dialog)
        self.radioButton_2.setGeometry(QtCore.QRect(20, 60, 117, 22))
        self.radioButton_2.setAutoExclusive(False)
        self.radioButton_2.setObjectName(_fromUtf8("radioButton_2"))
        self.radioButton_3 = QtGui.QRadioButton(Dialog)
        self.radioButton_3.setGeometry(QtCore.QRect(20, 240, 117, 22))
        self.radioButton_3.setAutoExclusive(False)
        self.radioButton_3.setObjectName(_fromUtf8("radioButton_3"))
        self.radioButton_4 = QtGui.QRadioButton(Dialog)
        self.radioButton_4.setGeometry(QtCore.QRect(20, 260, 117, 22))
        self.radioButton_4.setAutoExclusive(False)
        self.radioButton_4.setObjectName(_fromUtf8("radioButton_4"))
        self.radioButton_5 = QtGui.QRadioButton(Dialog)
        self.radioButton_5.setGeometry(QtCore.QRect(20, 280, 117, 22))
        self.radioButton_5.setAutoExclusive(False)
        self.radioButton_5.setObjectName(_fromUtf8("radioButton_5"))
        self.radioButton_6 = QtGui.QRadioButton(Dialog)
        self.radioButton_6.setGeometry(QtCore.QRect(20, 300, 117, 22))
        self.radioButton_6.setAutoExclusive(False)
        self.radioButton_6.setObjectName(_fromUtf8("radioButton_6"))
        self.radioButton_7 = QtGui.QRadioButton(Dialog)
        self.radioButton_7.setGeometry(QtCore.QRect(20, 320, 117, 22))
        self.radioButton_7.setAutoExclusive(False)
        self.radioButton_7.setObjectName(_fromUtf8("radioButton_7"))
        self.radioButton_8 = QtGui.QRadioButton(Dialog)
        self.radioButton_8.setGeometry(QtCore.QRect(20, 340, 117, 22))
        self.radioButton_8.setAutoExclusive(False)
        self.radioButton_8.setObjectName(_fromUtf8("radioButton_8"))
        self.radioButton_9 = QtGui.QRadioButton(Dialog)
        self.radioButton_9.setGeometry(QtCore.QRect(20, 360, 117, 22))
        self.radioButton_9.setAutoExclusive(False)
        self.radioButton_9.setObjectName(_fromUtf8("radioButton_9"))
        self.radioButton_10 = QtGui.QRadioButton(Dialog)
        self.radioButton_10.setGeometry(QtCore.QRect(20, 380, 117, 22))
        self.radioButton_10.setAutoExclusive(False)
        self.radioButton_10.setObjectName(_fromUtf8("radioButton_10"))
        self.radioButton_11 = QtGui.QRadioButton(Dialog)
        self.radioButton_11.setEnabled(True)
        self.radioButton_11.setGeometry(QtCore.QRect(20, 400, 117, 22))
        self.radioButton_11.setAutoExclusive(False)
        self.radioButton_11.setObjectName(_fromUtf8("radioButton_11"))
        self.radioButton_13 = QtGui.QRadioButton(Dialog)
        self.radioButton_13.setGeometry(QtCore.QRect(20, 80, 117, 22))
        self.radioButton_13.setAutoExclusive(False)
        self.radioButton_13.setObjectName(_fromUtf8("radioButton_13"))
        self.radioButton_14 = QtGui.QRadioButton(Dialog)
        self.radioButton_14.setGeometry(QtCore.QRect(20, 100, 117, 22))
        self.radioButton_14.setAutoExclusive(False)
        self.radioButton_14.setObjectName(_fromUtf8("radioButton_14"))
        self.radioButton_15 = QtGui.QRadioButton(Dialog)
        self.radioButton_15.setGeometry(QtCore.QRect(20, 120, 117, 22))
        self.radioButton_15.setAutoExclusive(False)
        self.radioButton_15.setObjectName(_fromUtf8("radioButton_15"))
        self.radioButton_16 = QtGui.QRadioButton(Dialog)
        self.radioButton_16.setGeometry(QtCore.QRect(20, 140, 117, 22))
        self.radioButton_16.setAutoExclusive(False)
        self.radioButton_16.setObjectName(_fromUtf8("radioButton_16"))
        self.radioButton_17 = QtGui.QRadioButton(Dialog)
        self.radioButton_17.setGeometry(QtCore.QRect(20, 160, 117, 22))
        self.radioButton_17.setAutoExclusive(False)
        self.radioButton_17.setObjectName(_fromUtf8("radioButton_17"))
        self.radioButton_18 = QtGui.QRadioButton(Dialog)
        self.radioButton_18.setGeometry(QtCore.QRect(20, 180, 117, 22))
        self.radioButton_18.setAutoExclusive(False)
        self.radioButton_18.setObjectName(_fromUtf8("radioButton_18"))
        self.radioButton_19 = QtGui.QRadioButton(Dialog)
        self.radioButton_19.setGeometry(QtCore.QRect(20, 220, 117, 22))
        self.radioButton_19.setAutoExclusive(False)
        self.radioButton_19.setObjectName(_fromUtf8("radioButton_19"))
        self.radioButton_20 = QtGui.QRadioButton(Dialog)
        self.radioButton_20.setGeometry(QtCore.QRect(20, 200, 117, 22))
        self.radioButton_20.setAutoExclusive(False)
        self.radioButton_20.setObjectName(_fromUtf8("radioButton_20"))
        self.radioButton_12 = QtGui.QRadioButton(Dialog)
        self.radioButton_12.setGeometry(QtCore.QRect(20, 420, 117, 22))
        self.radioButton_12.setAutoExclusive(False)
        self.radioButton_12.setObjectName(_fromUtf8("radioButton_12"))
        self.radioButton_21 = QtGui.QRadioButton(Dialog)
        self.radioButton_21.setGeometry(QtCore.QRect(20, 440, 117, 22))
        self.radioButton_21.setAutoExclusive(False)
        self.radioButton_21.setObjectName(_fromUtf8("radioButton_21"))
        
        
        self.scene = QGraphicsScene()
        self.graphicsView = QtGui.QGraphicsView(Dialog)
        self.graphicsView.setGeometry(QtCore.QRect(180, 80, 231, 161))
        self.graphicsView.setObjectName(_fromUtf8("graphicsView"))
        self.graphicsView_2 = QtGui.QGraphicsView(Dialog)
        self.graphicsView_2.setGeometry(QtCore.QRect(430, 80, 281, 351))
        self.graphicsView_2.setObjectName(_fromUtf8("graphicsView_2"))
        self.graphicsView_3 = QtGui.QGraphicsView(Dialog)
        self.graphicsView_3.setGeometry(QtCore.QRect(180, 270, 231, 171))
        self.graphicsView_3.setObjectName(_fromUtf8("graphicsView_3"))
        
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(240, 240, 121, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(250, 440, 101, 21))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(510, 440, 131, 21))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        
        self.lineEdit = QtGui.QLineEdit(Dialog)
        self.lineEdit.setGeometry(QtCore.QRect(250, 20, 351, 27))
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        
        self.pushButton = QtGui.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(610, 20, 99, 27))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.pushButton.clicked.connect(self.selectFile)
        
        self.label_4 = QtGui.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(200, 20, 51, 31))
        self.label_4.setObjectName(_fromUtf8("label_4"))

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)


    def selectFile(self):            
        self.scene.clear()
        filename = '/home/yash/fish.jpg'#QFileDialog.getOpenFileName()
        self.lineEdit.setText(filename)
        
        self.scene.addPixmap(QPixmap(filename).scaled(self.graphicsView.size(), QtCore.Qt.KeepAspectRatio))
        #myPixmap = QtGui.QPixmap(_fromUtf8(filename))
        #myScaledPixmap = myPixmap.scaled(self.graphicsView.size(), Qt.KeepAspectRatio)
        print("here")   
        self.graphicsView.setScene(self.scene)
    
    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.radioButton.setText(_translate("Dialog", "All", None))
        self.radioButton_2.setText(_translate("Dialog", "Aeroplane", None))
        self.radioButton_3.setText(_translate("Dialog", "Cow", None))
        self.radioButton_4.setText(_translate("Dialog", "Dining Table", None))
        self.radioButton_5.setText(_translate("Dialog", "Dog", None))
        self.radioButton_6.setText(_translate("Dialog", "Horse", None))
        self.radioButton_7.setText(_translate("Dialog", "Motorbike", None))
        self.radioButton_8.setText(_translate("Dialog", "Person", None))
        self.radioButton_9.setText(_translate("Dialog", "Potted plant", None))
        self.radioButton_10.setText(_translate("Dialog", "sheep", None))
        self.radioButton_11.setText(_translate("Dialog", "Sofa", None))
        self.radioButton_13.setText(_translate("Dialog", "Bicycle", None))
        self.radioButton_14.setText(_translate("Dialog", "Bird", None))
        self.radioButton_15.setText(_translate("Dialog", "Boat", None))
        self.radioButton_16.setText(_translate("Dialog", "Bottle", None))
        self.radioButton_17.setText(_translate("Dialog", "Bus", None))
        self.radioButton_18.setText(_translate("Dialog", "Car", None))
        self.radioButton_19.setText(_translate("Dialog", "Chair", None))
        self.radioButton_20.setText(_translate("Dialog", "Cat", None))
        self.radioButton_12.setText(_translate("Dialog", "Train", None))
        self.radioButton_21.setText(_translate("Dialog", "Tv", None))
        self.label.setText(_translate("Dialog", "Uplaoded Image", None))
        self.label_2.setText(_translate("Dialog", "Tagged Image", None))
        self.label_3.setText(_translate("Dialog", "Co-Location Graph", None))
        self.pushButton.setText(_translate("Dialog", "Upload", None))
        self.label_4.setText(_translate("Dialog", "Image", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

