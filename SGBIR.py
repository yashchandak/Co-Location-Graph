# -*- coding: utf-8 -*-
"""
Created on Mon Jul  4 14:05:06 2016

@author: yash
"""

from __future__ import print_function

import os

from PyQt4 import QtCore, QtGui
from PyQt4.uic import loadUiType
from PyQt4.QtGui import QGraphicsScene, QFileDialog, QPixmap,  QMessageBox#, QWidget, QPushButton

from heapq import nsmallest
import pickle
import cv2
import numpy as np
from graph_module import apx_distance

Ui_MainWindow, QMainWindow = loadUiType('SGBIR_gui.ui')

class ImgWidget(QtGui.QLabel):
    ##IMP: IF using QtDesigner to make tables, make sure to set default row, column to non zero values
    ##otherwise it doesn't seem to work [Weird Bug]
    def __init__(self, parent=None, imagePath = '', size = 50):
        super(ImgWidget, self).__init__(parent)       
        pic = QtGui.QPixmap(imagePath)                              #Get the pic from it's path
        if pic.height()>pic.width(): pic=pic.scaledToWidth(size)    #resize the picture to fit the table cell
        else: pic=pic.scaledToHeight(size)
        self.setAlignment(QtCore.Qt.AlignCenter)                    #centre align the picture
        self.setPixmap(pic)


class CBIR(QMainWindow, Ui_MainWindow):
    #class variables
    flag = True
    categories = {}
    classes =  ["Aeroplane", "Bicycle", "Bird", "Boat", "Bottle", "Bus", "Car", "Cat", "Chair", "Cow", "Dining Table", "Dog", "Horse", "Motorbike", "Person", "Potted plant", "Sheep", "Sofa", "Train","Tv"]
    mask = np.zeros(len(classes))    
    class2idx = {item:i  for i,item in enumerate(classes)}
    valid_images = ["jpg","png","tga", "pgm", "jpeg"]
    valid_videos = ["mp4", "avi"]
    edge_threshold = 100
    topk = 10
    to_disp = [] 
    stop = False
    database_path = ''
    thumbnail_size = 256
    spacing = 40
    images_per_row = 2 
    cached_db = {}
    cached_db_path = ''
    alpha = 16 
    beta = 0.8
    
    def __init__(self, ):
        super(CBIR, self).__init__()        #initialise from the ui designed by Designer App
        self.setupUi(self)
        self.setupUi_custom()
   
    def setupUi_custom(self,): 
        self.setWindowTitle('CBIR') 
        
        #setup space to display selected image and it's tagged version
        self.scene = QGraphicsScene()
        self.scene2 = QGraphicsScene()
        
        #connect the buttons to their respective functions
        self.pushButton.clicked.connect(self.select_image)
        self.pushButton_2.clicked.connect(self.find_similar)
        self.pushButton_3.clicked.connect(self.select_database)
        self.horizontalSlider.valueChanged.connect(self.update_LCD)
        
        #TODO [WEIRD PROBLEM] QPixmap needs to be called at least once with JPG image before tensorFlow, otherwise program crashes
        self.scene.addPixmap(QPixmap(os.getcwd()+"/images/demo.jpg").scaled(self.graphicsView.size(), QtCore.Qt.KeepAspectRatio))
        self.graphicsView.setScene(self.scene)          
        
        #set-up toolbar items and link them to respective functions
        Help = QtGui.QAction(QtGui.QIcon('images/info.png'), 'Help', self)
        Help.triggered.connect(self.show_help)
        
        Settings = QtGui.QAction(QtGui.QIcon('images/settings.png'), 'Settings', self)
        Settings.triggered.connect(self.show_settings)
        
        Export = QtGui.QAction(QtGui.QIcon('images/export.png'), 'Export', self)
        Export.triggered.connect(self.show_export)
        
        ##To set up the toolbar
        self.toolbar = self.addToolBar('Help')
        self.toolbar.addAction(Help)
        self.toolbar = self.addToolBar('Settings')
        self.toolbar.addAction(Settings)
        self.toolbar = self.addToolBar('Export')
        self.toolbar.addAction(Export)
        
    def show_help(self):
       msg = QMessageBox()
       #setup title, main heading, about us info
       msg.setIcon(QMessageBox.Information) 
       msg.setWindowTitle("About Us")
       msg.setText("Semantic Graph based Image matching")       
       msg.setInformativeText("Developed by Yash Chandak, under supervision of Prof. Babiga Birregah, University of Technology, Troyes")
       #Section for further details on how to use the software
       f = open('How-To/how-to-SGBIR.txt', 'r')
       msg.setDetailedText(f.read())
       
       #setup return buttons
       msg.setStandardButtons(QMessageBox.Ok )    	
       msg.exec_()

    def show_settings(self):
        topk, ok = QtGui.QInputDialog.getInt(self, 'Settings', 'Number of results to display')
        self.topk = topk
        
    def show_export(self):
        #TODO gephi export
        name, ok = QtGui.QInputDialog.getText(self, 'Export to Gephi format', 'Enter file name :')
        self.exportname = name

    def select_database(self):
        #Read all the images in the folder
        path = QFileDialog.getExistingDirectory(None, 'Select a folder:', '/home/yash/Project/dataset/Pascal VOC 2012/', QtGui.QFileDialog.ShowDirsOnly)
        self.lineEdit_2.setText(path)   
        self.database_path = path
    
    def update_categories(self):
        #update selected categories
        self.mask.fill(0)
        for radiobox in self.findChildren(QtGui.QRadioButton):
            self.categories[radiobox.text()] = radiobox.isChecked()
            if not radiobox.text() == 'All': self.mask[self.class2idx[radiobox.text()]] = radiobox.isChecked()
            
        if self.categories.get('All',0) == 1: self.mask.fill(1)

    def update_LCD(self):
        #update edge_threshold variable based on slider
        self.edge_threshold = self.horizontalSlider.value()
        self.lcdNumber.display(self.edge_threshold)  
        
    def show_similar(self, pictures, base_dir=''):
        #set the table layout spacing
        self.tableWidget.setMinimumWidth((self.thumbnail_size+self.spacing)*self.images_per_row+(self.spacing*2))
        #set table row and column count based on similar images received
        rowCount=len(pictures)//self.images_per_row
        if len(pictures)%self.images_per_row: rowCount+=1
        self.tableWidget.setRowCount(rowCount)
    
        row=-1
        #set the pictures in the table cells
        for i,picture in enumerate(pictures):
            col=i%self.images_per_row
            if not col: row+=1
            #self.tableWidget.setCellWidget(row, col,  ImgWidget(imagePath = self.cached_db[picture][0], size=self.thumbnail_size))            
            self.tableWidget.setCellWidget(row, col,  ImgWidget(imagePath = base_dir+'/'+picture, size=self.thumbnail_size))            

    def read_database(self):
        #Option to select database
        if self.database_path == '':
            print("Database file not selected")
            self.select_database()        
        
        found = False        
        if self.cached_db_path == self.database_path:
            #No need to re-read from cPickle if it's re-run on the same db
            found = True
        
        #Search for any pre-existing db file
        else:
            self.cached_db_path = self.database_path
            for file in os.listdir(self.database_path):              #list all the files in the folder
                extension = file.split('.')[1]        #get the file extension
                if extension.lower() == 'db':      #check for pickled cached_db file
                    self.cached_db = pickle.load(open(self.database_path+'/'+file, 'rb'))
                    print("Cached database found!")
                    found = True
                    break
                
        #Create a new db if no exiting db is found
        if not found:   self.cached_db = self.make_db(self.database_path)

        
    def count_diff(self, v1, v2):       
        w = [self.alpha if i==0 else 1 for i in v1 ]
        return  np.sum(self.mask*w*np.power((v1 - v2), 2)) #sum of weighted Squared error, masked by selected classes        
    
    def loc_diff(self, w1, w2):
        #more the difference, the less the score
        return 1
        #TODO: add the details
        return 1/np.exp(np.abs(w1-w2))
        
    def score(self, edges, vec, db_img):
        #weighted score of location deifference and count difference
        return self.beta*self.count_diff(vec, self.cached_db['vec'][db_img]) \
                + (1-self.beta)*self.loc_diff(edges, self.cached_db['edges'][db_img])        
        
    def get_vec_and_classes(self, results):
        #returns vector and all unique classes for the given image result.
        vec = np.zeros(len(self.classifier.classes))
        classes_present = []
        for result in results:
            vec[self.class2idx[result[0]]] += 1
            classes_present.append(result[0])
        return vec, set(classes_present)      
        
    def order(self, c1, c2):
        #edge nodes concatenated in alphabetical order to create edge name
        if self.class2idx[c1]< self.class2idx[c2]: return c1+c2
        else: return c2+c1
        
    def get_edges_with_weights(self, results):
        #returns a list of (edge, weight)
        return [(self.order(results[i][0], results[j][0]), apx_distance(results[i], results[j])) \
                for i in range(len(results)) for j in range(i, len(results))]  
                
    def make_db(self, path):
        print("caching database..")
        inv_map = {c:[] for c in self.classes}
        edges = {}
        vec = {}
        for file in os.listdir(path):              #list all the fileiles in the folder
            ext = file.split('.')[1]        #get the file extension
            if ext.lower() in self.valid_images:
                print(file)
                full_path = path+'/'+file
                self.tag_image(filename = full_path)

                #store the all the edges and weights for the image
                edges[file] = self.get_edges_with_weights(self.classifier.result)
                
                #create the inverse map( class -> images )
                v, classes_present = self.get_vec_and_classes(self.classifier.result)
                vec[file] = v
                for c in classes_present:
                    inv_map[c].append(file)
        
        #Storage format = {dir, inv_map[class]->images, vectors[image]->vec, edges[image]->edges}        
        cached_db = {'dir': path, 'inv_map': inv_map, 'vec': vec, 'edges':edges}        
        pickle.dump(cached_db, open(path+'/cache.db', 'wb'))
        return cached_db
        
    def find_similar(self, results):
        #do pattern matching on the images in retrieved cached_db
        #keep top 10 and display on right
        self.read_database()
        
        #get the edges, vector, classes_present in the query image
        edges = self.get_edges_with_weights(results)
        vec, classes_present = self.get_vec_and_classes(results)
        
        #get all the images having at least one occurence of the class present in query image
        imgs = set([img for c in classes_present for img in self.cached_db['inv_map'][c]]) 

        #choose the topK similar images from the images retrieved from database
        best_matches = nsmallest(self.topk, imgs, key = lambda e: self.score(edges, vec, e))
           
        self.show_similar(best_matches, self.cached_db['dir'])

        
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
            #convert image to PyQt display format
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

    
    def select_image(self):  
        #Clear previous image displays        
        self.scene.clear()
        self.scene2.clear()
        self.tableWidget.clearContents()
        self.update_categories() #update categories to incorporate any changes made
        
        #Change the file path to any default directory, as per need.             
        filename = QFileDialog.getOpenFileName(directory = '/home/yash/Project/dataset/Pascal VOC 2012/')
        self.lineEdit.setText(filename)
        
        if filename.split('.')[1] in self.valid_images:
            self.disp_img(filename = filename) 
            self.find_similar(self.classifier.result)
            #self.find_similar_using_vector(self.classifier.result)
        else:
            print("Invalid file format")


if __name__ == '__main__':
    import sys 
    app = QtGui.QApplication(sys.argv)
    cbir = CBIR()
    cbir.show()
    app.exec()
