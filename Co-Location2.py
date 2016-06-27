# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 15:47:06 2016

@author: yash

Helpful references:
1) For integrating matplotlib with PyQt4 (http://blog.rcnelson.com/building-a-matplotlib-gui-with-qt-designer-part-1/)
2) Threading in PyQt (https://nikolak.com/pyqt-threading-tutorial/)

TODO
1) 

"""
from __future__ import print_function

import os

from PyQt4 import QtCore, QtGui
from PyQt4.uic import loadUiType
from PyQt4.QtGui import QGraphicsScene, QFileDialog, QPixmap
from PyQt4.QtCore import QThread, SIGNAL

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

import cv2

Ui_MainWindow, QMainWindow = loadUiType('GUI.ui')


class CoLocation(QMainWindow, Ui_MainWindow):
    flag = True
    categories = {}
    valid_images = ["jpg","png","tga", "pgm", "jpeg"]
    valid_videos = ["mp4", "avi"]
    edge_threshold = 100
    to_disp = [] 
    
    def __init__(self, ):
        super(CoLocation, self).__init__()        #initialise from the ui designed by Designer App
        self.setupUi(self)
        self.setupUi_custom()
        
    def update_categories(self):
        #update selected categories
        for radiobox in self.findChildren(QtGui.QRadioButton):
            self.categories[radiobox.text()] = radiobox.isChecked()
    
    def setupUi_custom(self,):    
        
        self.scene = QGraphicsScene()
        self.scene2 = QGraphicsScene()
        #TODO [WEIRD PROBLEM] QPixmap needs to be called at least once with JPG image before tensorFlow, otherwise program crashes
        self.scene.addPixmap(QPixmap(os.getcwd()+"/demo.jpg").scaled(self.graphicsView.size(), QtCore.Qt.KeepAspectRatio))
        self.graphicsView.setScene(self.scene)  
        
        import Yolo_module as yolo
        self.classifier = yolo.YOLO_TF()
        #Create thread for heavy processing and tensorflow, pass the instance of itself to modify GUI
        self.image_thread = ImageThread(self, self.classifier)
        #add connect SIGNAL here 
                
        self.pushButton.clicked.connect(self.selectFile)        
        self.horizontalSlider.valueChanged.connect(self.updateLCD)
        self.pushButton_2.clicked.connect(self.image_thread.disp_graph)
        self.pushButton_3.clicked.connect(self.selectFile_from_folder)
        
        #Add blank canvas initially
        fig1 = Figure()            
        self.addmpl(fig1)

    def updateLCD(self):
        #update edge_threshold variable based on slider
        self.edge_threshold = self.horizontalSlider.value()
        self.lcdNumber.display(self.edge_threshold)        
        
    def selectFile(self):  
        #Clear previous image displays        
        self.scene.clear()
        self.scene2.clear()
        self.update_categories()
             
        filename = QFileDialog.getOpenFileName(directory = '/home/yash/Downloads/Pascal VOC 2012/samples')
        self.lineEdit.setText(filename)
        
        if filename.split('.')[1] in self.valid_videos:
            self.image_thread.temp = filename #disp_video(filename)
            self.image_thread.start()
        
        elif filename.split('.')[1] in self.valid_images:
            self.image_thread.disp_img(filename = filename)
            self.image_thread.disp_graph()
            
        else:
            print("Invalid file format")
        
    def selectFile_from_folder(self):
        #Read all the images in the folder
        path = QFileDialog.getExistingDirectory(None, 'Select a folder:', '/home/yash/Downloads/Pascal VOC 2012', QtGui.QFileDialog.ShowDirsOnly)
        self.lineEdit_2.setText(path)
        
        for f in os.listdir(path):              #list all the files in the folder
            ext = f.split('.')[1]        #get the file extension
            if ext.lower() not in self.valid_images: #check if the extension is valid for the image
                continue
            filename = path+'/'+f               #create the path of the image
            print(filename)
            
            self.image_thread.tag_image(filename, batch = True)
        
        #clear the image regions during batch upload
        self.scene.clear()
        self.scene2.clear()    
        
        self.image_thread.disp_graph(batch = True)
        
    def addmpl(self, fig):
        #Add figure to canvas and widget
        self.canvas = FigureCanvas(fig)
        self.mplvl.addWidget(self.canvas)
        self.canvas.draw()
 
    def rmmpl(self,):
        #remove the canvas and widget
        self.mplvl.removeWidget(self.canvas)
        self.canvas.close()


class ImageThread(QThread):
    
    def __init__(self, GUI, classifier):
        QThread.__init__(self)

        #importing TensorFlow on top causes segmentation fault (official bug #2034)
        #importing here helps in working around the problem
        #Python modules could be con)sidered as singletons... so no matter how many times they are imported, they get initialized only once
        #import Yolo_module as yolo

        #self.classifier = yolo.YOLO_TF()
        self.classifier=  classifier
        self.GUI = GUI
        self.counter = 1
        self.batch_result = []
        self.temp = ""
        
    def tag_image(self, filename = None, batch = False, image = None ):
        self.classifier.batch = batch
        
        if not image == None:
            self.classifier.detect_from_cvmat(image)
        else:
            self.classifier.detect_from_file(filename)      #execute Yolo on the image 
        
        if batch:
            self.batch_result.append(self.classifier.result)
        
        return self.classifier.tagged_image
        
    def disp_img(self, filename = None, img = None):
        if not img == None:
            img_rgb = img.copy()
            cv2.cvtColor(img, cv2.COLOR_BGR2RGB, img_rgb)
            img_rgb = QtGui.QImage(img_rgb, img_rgb.shape[1], img_rgb.shape[0], img_rgb.shape[1] * 3,QtGui.QImage.Format_RGB888) 
            self.GUI.scene.addPixmap(QPixmap(img_rgb).scaled(self.GUI.graphicsView.size(), QtCore.Qt.KeepAspectRatio))
            image = self.tag_image(image = img)
        
        else:
            self.GUI.scene.addPixmap(QPixmap(filename).scaled(self.GUI.graphicsView.size(), QtCore.Qt.KeepAspectRatio))
            #Dislplay tagged image        
            image = self.tag_image(filename = filename)      
            
        image = QtGui.QImage(image, image.shape[1], image.shape[0], image.shape[1] * 3,QtGui.QImage.Format_RGB888)  #convert to Qt image format      
        self.GUI.scene2.addPixmap(QPixmap(image).scaled(self.GUI.graphicsView_3.size(), QtCore.Qt.KeepAspectRatio))

        self.GUI.graphicsView.setScene(self.GUI.scene) 
        self.GUI.graphicsView_3.setScene(self.GUI.scene2)        
        
        
    def disp_graph(self, batch = False):    
        import graph_module as gm
        
        if batch:
            result = self.batch_result
        else:
            result = [self.classifier.result]           #list of lists
        
        self.GUI.update_categories()
        self.GUI.rmmpl()                                    #remove previous graph
        if result != [] and result != False:
            return
            
        #Display graph
        fig = Figure()
        axf = fig.add_subplot(111)
        axf.set_axis_off()
        gm.co_location(result, axf, self.GUI.edge_threshold, self.GUI.categories) #get updated graph
        self.GUI.addmpl(fig)
        print("graph added")
    
    def disp_video(self, filename, skip = 20):
        
        cap = cv2.VideoCapture(filename)
        count = 0
        while True:
            #TODO: Better method - https://nikolak.com/pyqt-threading-tutorial/
            #QtCore.QCoreApplication.processEvents()
            
            ret, img = cap.read()
            if not ret:
                break
            if count % skip == 0 :
                img = cv2.resize(img, (640, 480))
                self.disp_img(img = img)
                self.disp_graph()
                count = 0            
            count +=1


    def __del__(self):
        self.wait()
    
    
    def modify(self):
        self.emit(SIGNAL("modified"))
        
    def run(self):
        self.disp_video(self.temp)


def kill_proc_tree(pid, including_parent=True):    
    import psutil
    parent = psutil.Process(pid)
    for child in parent.children(recursive=True):
        child.kill()
    if including_parent:
        parent.kill()


if __name__ == '__main__':
    import sys 
    app = QtGui.QApplication(sys.argv)
    coLoc = CoLocation()
    coLoc.show()
    app.exec()
    
    print("DEBUG1")
    kill_proc_tree(os.getpid())
    print("DEBUG2")
    sys.exit(0)
    print("DEBUG3")
    
    