# -*- coding: utf-8 -*-
"""
Created on Mon Jul  4 14:05:06 2016

@author: yash
"""

from __future__ import print_function

import os

from PyQt4 import QtCore, QtGui
from PyQt4.uic import loadUiType
from PyQt4.QtGui import QGraphicsScene, QFileDialog, QPixmap, QTableWidgetItem, QIcon, QLabel, QWidget

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

import cv2

Ui_MainWindow, QMainWindow = loadUiType('CBIR_gui.ui')

class ImgWidget(QtGui.QLabel):

    def __init__(self, parent=None, imagePath = ''):
        super(ImgWidget, self).__init__(parent)
        pic = QtGui.QPixmap(imagePath)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setPixmap(pic)


class CBIR(QMainWindow, Ui_MainWindow, QWidget):
    flag = True
    categories = {}
    valid_images = ["jpg","png","tga", "pgm", "jpeg"]
    valid_videos = ["mp4", "avi"]
    edge_threshold = 100
    to_disp = [] 
    stop = False

    THUMBNAIL_SIZE = 48
    SPACING = 10
    IMAGES_PER_ROW = 1 
    
    def __init__(self, ):
        super(CBIR, self).__init__()        #initialise from the ui designed by Designer App
        self.setupUi(self)
        #self.setupUi_custom()
        
        self.tableWidget.setMinimumWidth((self.THUMBNAIL_SIZE+self.SPACING)*self.IMAGES_PER_ROW+(self.SPACING*2))
        path = '/home/yash/Project/dataset/Pascal VOC 2012/samples'
        pictures = []
        for f in os.listdir(path):              #list all the files in the folder
            ext = f.split('.')[1]        #get the file extension
            if ext.lower() not in self.valid_images: continue#check if the extension is valid for the image
            pictures.append(path+'/'+f )
        
        #self.tableWidget2 = QtGui.QTableWidget(2, 1, self)
        #self.tableWidget2.setGeometry(QtCore.QRect(570, 20, 741, 611))
        #self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        #self.tableWidget.setColumnCount(0)
        
        #pictures = ['2007_001627.jpg', '2007_001630.jpg']
        rowCount=len(pictures)//self.IMAGES_PER_ROW
        if len(pictures)%self.IMAGES_PER_ROW: rowCount+=1
        self.tableWidget.setRowCount(rowCount)
    
        row=-1
        for i,picture in enumerate(pictures):
            col=i%self.IMAGES_PER_ROW
            if not col: row+=1
            self.tableWidget.setCellWidget(row, 0,  ImgWidget(imagePath = picture))

###########################            
#            item=QTableWidgetItem()
#        
#            # Scale the image by either height or width and then 'crop' it to the
#            # desired size, this prevents distortion of the image.
#            p=QPixmap(picture)
#            if p.height()>p.width(): p=p.scaledToWidth(self.THUMBNAIL_SIZE)
#            else: p=p.scaledToHeight(self.THUMBNAIL_SIZE)
#            p=p.copy(0,0,self.THUMBNAIL_SIZE,self.THUMBNAIL_SIZE)
#            item.setIcon(QIcon(p))
#        
#            self.tableWidget.setItem(row,col,item)

    
    def addPicture(self, row, col, picturePath):
        item=QTableWidgetItem()
    
        # Scale the image by either height or width and then 'crop' it to the
        # desired size, this prevents distortion of the image.
        p=QPixmap(picturePath)
        if p.height()>p.width(): p=p.scaledToWidth(self.THUMBNAIL_SIZE)
        else: p=p.scaledToHeight(self.THUMBNAIL_SIZE)
        p=p.copy(0,0,self.THUMBNAIL_SIZE,self.THUMBNAIL_SIZE)
        item.setIcon(QIcon(p))
    
        self.tableWidget.setItem(row,col,item)    
    
    
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
        self.stop_button.clicked.connect(self.set_stop)
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
        
    def tag_image(self, filename = None, batch = False, image = None ):
        #importing TensorFlow on top causes segmentation fault (official bug #2034)
        #importing here helps in working around the problem
        #Python modules could be con)sidered as singletons... so no matter how many times they are imported, they get initialized only once
        import Yolo_module as yolo
        
        if(self.flag):
            #initialise the model, only once
            self.classifier = yolo.YOLO_TF()
            self.flag = False            
            
        self.classifier.batch = batch
        
        if not image == None:
            self.classifier.detect_from_cvmat(image)
        else:
            self.classifier.detect_from_file(filename)      #execute Yolo on the image 
        
        return self.classifier.tagged_image
        
    def disp_img(self, filename = None, img = None):
        if not img == None:
            img_rgb = img.copy()
            cv2.cvtColor(img, cv2.COLOR_BGR2RGB, img_rgb)
            img_rgb = QtGui.QImage(img_rgb, img_rgb.shape[1], img_rgb.shape[0], img_rgb.shape[1] * 3,QtGui.QImage.Format_RGB888) 
            self.scene.addPixmap(QPixmap(img_rgb).scaled(self.graphicsView.size(), QtCore.Qt.KeepAspectRatio))
            image = self.tag_image(image = img)
        
        else:
            #DO this step before calling tensorflow
            self.scene.addPixmap(QPixmap(filename).scaled(self.graphicsView.size(), QtCore.Qt.KeepAspectRatio))
                          
            #Dislplay tagged image        
            image = self.tag_image(filename = filename)      
            
        image = QtGui.QImage(image, image.shape[1], image.shape[0], image.shape[1] * 3,QtGui.QImage.Format_RGB888)  #convert to Qt image format      
        self.scene2.addPixmap(QPixmap(image).scaled(self.graphicsView_3.size(), QtCore.Qt.KeepAspectRatio))

        self.graphicsView.setScene(self.scene) 
        self.graphicsView_3.setScene(self.scene2)        

    
    def selectFile(self):  
        #Clear previous image displays        
        self.scene.clear()
        self.scene2.clear()
        self.update_categories()
             
        filename = QFileDialog.getOpenFileName(directory = '/home/yash/Downloads/Pascal VOC 2012/samples')
        self.lineEdit.setText(filename)
        
        if filename.split('.')[1] in self.valid_videos:
            self.disp_video(filename)
        
        elif filename.split('.')[1] in self.valid_images:
            self.disp_img(filename = filename)
            self.disp_graph([self.classifier.result]) #list of 1 resultant list
            
        else:
            print("Invalid file format")
        
    def selectFile_from_folder(self):
        #Read all the images in the folder
        path = QFileDialog.getExistingDirectory(None, 'Select a folder:', '/home/yash/Downloads/Pascal VOC 2012', QtGui.QFileDialog.ShowDirsOnly)
        self.lineEdit_2.setText(path)
        
        
        self.batch_results = []
        for f in os.listdir(path):              #list all the files in the folder
            ext = f.split('.')[1]        #get the file extension
            if ext.lower() not in self.valid_images: #check if the extension is valid for the image
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
    cbir = CBIR()
    cbir.show()
    app.exec()
    
#    print("DEBUG1")
#    kill_proc_tree(os.getpid())
#    print("DEBUG2")
#    sys.exit(0)
#    print("DEBUG3")

###################################################################

#
#from PyQt4.QtCore import *
#from PyQt4.QtGui import *
#from PyQt4 import QtGui
#
#THUMBNAIL_SIZE = 128
#SPACING = 10
#IMAGES_PER_ROW = 5
#
#class TableWidget(QTableWidget):
#    def init(self, parent=None, **kwargs):
#        QTableWidget.init(self, parent, **kwargs)
#        self.setMinimumWidth((THUMBNAIL_SIZE+SPACING)*IMAGES_PER_ROW+(SPACING*2))
#    
#    def addPicture(self, row, col, picturePath):
#        item=QTableWidgetItem()
#    
#        # Scale the image by either height or width and then 'crop' it to the
#        # desired size, this prevents distortion of the image.
#        p=QPixmap(picturePath)
#        if p.height()>p.width(): p=p.scaledToWidth(THUMBNAIL_SIZE)
#        else: p=p.scaledToHeight(THUMBNAIL_SIZE)
#        p=p.copy(0,0,THUMBNAIL_SIZE,THUMBNAIL_SIZE)
#        item.setIcon(QIcon(p))
#    
#        self.setItem(row,col,item)
#        
#
#class MainWindow(QMainWindow):
#    def init(self, ):
#        print("here")
#        QMainWindow.init(self, parent, **kwargs)
#        centralWidget=QWidget(self)
#        l=QVBoxLayout(centralWidget)
#    
#        self.tableWidget=TableWidget(self)
#        l.addWidget(self.tableWidget)
#    
#        self.setCentralWidget(centralWidget)
#        
#        print("here!")#'/home/yash/Project/dataset/Pascal VOC 2012/samples'
#        picturesPath=QDesktopServices.storageLocation(QDesktopServices.PicturesLocation)
#        pictureDir=QDir(picturesPath)
#        pictures=pictureDir.entryList(['*.jpg','*.png','*.gif'])
#        print(len(pictures))
#    
#        rowCount=len(pictures)//IMAGES_PER_ROW
#        if len(pictures)%IMAGES_PER_ROW: rowCount+=1
#        self.tableWidget.setRowCount(rowCount)
#    
#        row=-1
#        for i,picture in enumerate(pictures):
#            col=i%IMAGES_PER_ROW
#            if not col: row+=1
#            self.tableWidget.addPicture(row, col, pictureDir.absoluteFilePath(picture))    
#            
#
#from sys import argv, exit
#
#a=QApplication(argv)
#m=MainWindow()
#m.show()
##m.raise_()
#exit(a.exec_())

###################################################################

#app = QtGui.QApplication([])
#widget = QdContactSheet()
#
#filenames = []
#path = '/home/yash/Project/dataset/Pascal VOC 2012/samples'
#for f in os.listdir(path):              #list all the files in the folder
#    ext = f.split('.')[1]        #get the file extension
#    if ext.lower() not in  ["jpg","png","tga", "pgm", "jpeg"]: continue#check if the extension is valid for the image
#    filenames.append(path+'/'+f )
#
#images = filenames# list of images you want to view as thumbnails
#images.sort()
#widget.load(images)
#
#widget.setWindowTitle("Contact Sheet")
#widget.resize(1000, 800)
#widget.show()
#exit(app.exec_())
