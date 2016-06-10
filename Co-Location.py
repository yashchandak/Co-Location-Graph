# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 15:47:06 2016

@author: yash

TODO
1) Use super for setupUi
2) Batch Process feature

Helpful references:
1) For integrating matplotlib with PyQt4 (http://blog.rcnelson.com/building-a-matplotlib-gui-with-qt-designer-part-1/)

"""
from __future__ import print_function

from PyQt4 import QtCore, QtGui
from PyQt4.uic import loadUiType
from PyQt4.QtGui import QGraphicsScene, QFileDialog, QPixmap

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

Ui_MainWindow, QMainWindow = loadUiType('GUI.ui')


class Main(QMainWindow, Ui_MainWindow):
    flag = True
    categories = {}
    
    def __init__(self, ):
        super(Main, self).__init__()
        self.setupUi(self)
        self.setupUi_custom()

    def update_categories(self):
        #update selected categories
        for radiobox in self.findChildren(QtGui.QRadioButton):
            self.categories[radiobox.text()] = radiobox.isChecked()
        
    def setupUi_custom(self,): 
        self.update_categories()    
        self.scene = QGraphicsScene()
        self.scene2 = QGraphicsScene()
        self.pushButton.clicked.connect(self.selectFile)
        
        #Add blank canvas initially
        fig1 = Figure()            
        self.addmpl(fig1)

    def selectFile(self):  
        #Clear previous image displays        
        self.scene.clear()
        self.scene2.clear()
        self.update_categories()
                
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
        self.classifier.categories = self.categories
        self.classifier.detect_from_file(filename)      #execute Yolo on the image     
        
        #Dislplay tagged image        
        image = self.classifier.tagged_image        
        image = QtGui.QImage(image, image.shape[1], image.shape[0], image.shape[1] * 3,QtGui.QImage.Format_RGB888)        
        self.scene2.addPixmap(QPixmap(image).scaled(self.graphicsView_3.size(), QtCore.Qt.KeepAspectRatio))
        self.graphicsView_3.setScene(self.scene2)        
        
        #Display graph
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
