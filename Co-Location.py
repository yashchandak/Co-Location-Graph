# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 15:47:06 2016

@author: yash

Helpful references:
1) For integrating matplotlib with PyQt4 (http://blog.rcnelson.com/building-a-matplotlib-gui-with-qt-designer-part-1/)

TODO
1) Use super for setupUi
2) Batch Process feature

"""
from __future__ import print_function

import os

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
        super(Main, self).__init__()        #initialise from the ui designed by Designer App
        self.setupUi(self)
        self.setupUi_custom()
        self.edge_threshold = 100
        self.to_disp = []

    def update_categories(self):
        #update selected categories
        for radiobox in self.findChildren(QtGui.QRadioButton):
            self.categories[radiobox.text()] = radiobox.isChecked()
    
     
    def setupUi_custom(self,):    
        self.scene = QGraphicsScene()
        self.scene2 = QGraphicsScene()
        self.pushButton.clicked.connect(self.selectFile)        
        self.horizontalSlider.valueChanged.connect(self.updateLCD)
        self.pushButton_2.clicked.connect(self.disp_graph)
        self.pushButton_3.clicked.connect(self.selectFile_from_folder)
        
        #TODO [WEIRD PROBLEM] QPixmap needs to be called at least once with JPG image before tensorFlow, otherwise program crashes
        self.scene.addPixmap(QPixmap(os.getcwd()+"/demo.jpg").scaled(self.graphicsView.size(), QtCore.Qt.KeepAspectRatio))
        self.graphicsView.setScene(self.scene)  
        
        #Add blank canvas initially
        fig1 = Figure()            
        self.addmpl(fig1)

    def updateLCD(self):
        #update edge_threshold variable based on slider
        self.edge_threshold = self.horizontalSlider.value()
        self.lcdNumber.display(self.edge_threshold)        
        
    def tag_image(self, filename, batch = False):
        #importing TensorFlow on top causes segmentation fault (official bug #2034)
        #importing here helps in working around the problem
        #Python modules could be considered as singletons... so no matter how many times they are imported, they get initialized only once
        import Yolo_module as yolo
        
        if(self.flag):
            #initialise the model, only once
            self.classifier = yolo.YOLO_TF()
            self.flag = False            
            
        self.classifier.batch = batch

        self.classifier.detect_from_file(filename)      #execute Yolo on the image 
        return self.classifier.tagged_image 
        
    def disp_img(self, filename):
        #DO this step before calling tensorflow
        self.scene.addPixmap(QPixmap(filename).scaled(self.graphicsView.size(), QtCore.Qt.KeepAspectRatio))
        self.graphicsView.setScene(self.scene)   
        
        #Dislplay tagged image        
        image = self.tag_image(filename)      
        
        image = QtGui.QImage(image, image.shape[1], image.shape[0], image.shape[1] * 3,QtGui.QImage.Format_RGB888)  #convert to Qt image format      
        self.scene2.addPixmap(QPixmap(image).scaled(self.graphicsView_3.size(), QtCore.Qt.KeepAspectRatio))
        self.graphicsView_3.setScene(self.scene2)        
        
        
    def disp_graph(self, result = []):    
        import graph_module as gm
        
        self.update_categories()
        self.rmmpl()                                    #remove previous graph
        if result != [] and result != False:
            self.to_disp = result
        
        print(self.to_disp)        
        #Display graph
        fig = Figure()
        axf = fig.add_subplot(111)
        gm.co_location(self.to_disp, axf, self.edge_threshold, self.categories) #get updated graph
        self.addmpl(fig)
    
    def selectFile(self):  
        #Clear previous image displays        
        self.scene.clear()
        self.scene2.clear()
        self.update_categories()
             
        filename = QFileDialog.getOpenFileName(directory = '/home/yash/Downloads/Pascal VOC 2012/samples')
        self.lineEdit.setText(filename)
        
        self.disp_img(filename)
        self.disp_graph([self.classifier.result]) #list of 1 resultant list
        
    def selectFile_from_folder(self):
        #Read all the images in the folder
        path = QFileDialog.getExistingDirectory(None, 'Select a folder:', '/home/yash/Downloads/Pascal VOC 2012', QtGui.QFileDialog.ShowDirsOnly)
        self.lineEdit_2.setText(path)
        
        valid_images = [".jpg",".png",".tga", ".pgm", ".jpeg"]
        self.batch_results = []
        for f in os.listdir(path):              #list all the files in the folder
            ext = os.path.splitext(f)[1]        #get the file extension
            if ext.lower() not in valid_images: #check if the extension is valid for the image
                continue
            filename = path+'/'+f               #create the path of the image
            print(filename)
            
            self.tag_image(filename, batch = True)
            self.batch_results.append( self.classifier.result) #list of all resultant lists
        
        #clear the image regions during batch upload
        self.scene.clear()
        self.scene2.clear()    
        
        self.disp_graph(self.batch_results)
        
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
