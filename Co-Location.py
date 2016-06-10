# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 15:47:06 2016

@author: yash

TODO
1) Use super for setupUi
2)
"""
from __future__ import print_function

from PyQt4 import QtCore, QtGui
from PyQt4.uic import loadUiType
from PyQt4.QtGui import QGraphicsScene, QFileDialog, QPixmap

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
    
import numpy as np
    
Ui_MainWindow, QMainWindow = loadUiType('GUI.ui')


class Main(QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super(Main, self).__init__()
        self.setupUi(self)
        self.setupUi_custom()

    def setupUi_custom(self,):
        self.flag = True
        self.scene = QGraphicsScene()
        self.scene2 = QGraphicsScene()
        self.scene3 = QGraphicsScene()
        self.pushButton.clicked.connect(self.selectFile)
        
        fig1 = Figure()            
        ax1f1 = fig1.add_subplot(111)
        ax1f1.plot(np.random.rand(5))
        self.addmpl(fig1)

    def selectFile(self):                  
        self.scene.clear()
        self.scene2.clear()
        self.scene3.clear()
        
        filename = QFileDialog.getOpenFileName()
        self.lineEdit.setText(filename)
        
        #DO this step before calling tensorflow
        self.scene.addPixmap(QPixmap(filename).scaled(self.graphicsView.size(), QtCore.Qt.KeepAspectRatio))
        self.graphicsView.setScene(self.scene)
        
        #importing TensorFlow on top causes segmentation fault (official bug #2034)
        #importing here helps in working around the problem
        #Python modules could be considered as singletons... so no matter how many times they are imported, they get initialized only once
        import Yolo_module as yolo
        import graph_module as gm
        
        if(self.flag):
            #initialise the model, only once
            self.classifier = yolo.YOLO_TF()
            self.flag = False
            

        self.rmmpl()                                    #remove previous graph
        self.classifier.detect_from_file(filename)      #execute Yolo on the image     
        
        #Dislplay tagged image        
        image = self.classifier.tagged_image        
        image = QtGui.QImage(image, image.shape[1],\
                            image.shape[0], image.shape[1] * 3,QtGui.QImage.Format_RGB888)        
        self.scene2.addPixmap(QPixmap(image).scaled(self.graphicsView_3.size(), QtCore.Qt.KeepAspectRatio))
        self.graphicsView_3.setScene(self.scene2)        
        
        fig = Figure()
        axf = fig.add_subplot(111)
        gm.co_location(self.classifier.objects, axf)
        self.addmpl(fig)
        
    def addmpl(self, fig):
        #Add figure to canvas and widget
        self.canvas = FigureCanvas(fig)
        self.mplvl.addWidget(self.canvas)
        self.canvas.draw()
 
    def rmmpl(self,):
        #remove the canvas and widget
        self.mplvl.removeWidget(self.canvas)
        self.canvas.close()



if __name__ == '__main__':
    import sys
 
    app = QtGui.QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(app.exec_())
