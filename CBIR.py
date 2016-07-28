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

from heapq import nsmallest, nlargest
import pickle
import cv2
import numpy as np
from graph_module import get_edges_with_weights

Ui_MainWindow, QMainWindow = loadUiType('CBIR_gui.ui')

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
       msg.setText("Semantic Entity graph based Image matching")       
       msg.setInformativeText("Developed by Yash Chandak, under supervision of Prof. Babiga Birregah, University of Technology, Troyes")
       
       #Section for further details on how to use the software
       f = open('HowTo.txt', 'r')
       msg.setDetailedText(f.read())
       
       #setup return buttons
       msg.setStandardButtons(QMessageBox.Ok )    	
       msg.exec_()

    def show_settings(self):
        framerate, ok = QtGui.QInputDialog.getInt(self, 'Settings', 'Enter Frame Rate for Videos:')
        self.framerate = framerate
        
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
        for radiobox in self.findChildren(QtGui.QRadioButton):
            self.categories[radiobox.text()] = radiobox.isChecked()

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

    def read_database(self, ext):
        #Option to select database
        if self.database_path == '':
            print("Database file not selected")
            self.select_database()        
        
        found = False        
        if self.cached_db_path == self.database_path and self.cached_db_ext == ext:
            #No need to re-read from cPickle if it's re-run on the same db
            found = True
        
        #Search for any pre-existing db file
        else:
            self.cached_db_path = self.database_path
            self.cached_db_ext = ext
            for file in os.listdir(self.database_path):              #list all the files in the folder
                extension = file.split('.')[1]        #get the file extension
                if extension.lower() == ext:      #check for pickled cached_db file
                    self.cached_db = pickle.load(open(self.database_path+'/'+file, 'rb'))
                    print("Cached database found!")
                    found = True
                    break
                
        #Create a new db if no exiting db is found
        if not found:
            if ext == 'db_vec': self.cached_db = self.make_db_vectorised(self.database_path)
            else: self.cached_db = self.make_db(self.database_path)

    def make_db_vectorised(self, path):
        #right now storing full paths, just for convenience, can be removed later
        #store the other results also, including the graph edge weights
        print("caching database..")
        
        cached_db = {}             
        for file in os.listdir(path):              #list all the fileiles in the folder
            ext = file.split('.')[1]        #get the file extension
            if ext.lower() in self.valid_images:
                print(file)
                full_path = path+'/'+file
                self.tag_image(filename = full_path)
                #Storage format = {name : [path, vec, full_results]}
                cached_db[file] = [full_path, self.get_vec(self.classifier.result), self.classifier.result]
                
        pickle.dump(cached_db, open(path+'/cache.db_vec', 'wb'))
        return cached_db

    def get_vec(self, results):
        vec = np.zeros(len(self.classifier.classes))
        for result in results:
            vec[self.classifier.class2idx[result[0]]] += 1
        return vec
        
    def difference(self, g1, g2):
        
        if sum(g1*g2) == 0: return 99999
        alpha = 16        
        w = [alpha if i==0 else 1 for i in g1 ]
        diff = np.power(w*(g1 - g2), 2).sum() #Squared error
        self.not_completely_diff += 1
        return diff
            
    def find_similar_using_vector(self, results):
        #do pattern matching on the images in retrieved cached_db
        #keep top 10
        #display the top 10 images on right
        self.read_database(ext = 'db_vec')
        
        #check if database atleast has more images than k.
        if len(self.cached_db.keys()) < self.topk: best_matches = self.cached_db.keys()
        else:
            self.not_completely_diff = 0
            best_matches = nsmallest(self.topk, self.cached_db.keys(), \
                            key = lambda e: self.difference(self.get_vec(results), self.cached_db[e][1] ))
        
        if self.not_completely_diff < self.topk: 
            best_matches = best_matches[:self.not_completely_diff]
            
        self.show_similar(best_matches)
    
    
    def make_db(self, path):
        print("caching database..")
        classes =  ["Aeroplane", "Bicycle", "Bird", "Boat", "Bottle", "Bus", "Car", "Cat", "Chair", "Cow", "Dining Table", "Dog", "Horse", "Motorbike", "Person", "Potted plant", "Sheep", "Sofa", "Train","Tv"]   
        tag2idx = {}
        counter = 0
        idx2tag = []
        data = {}
        for i in range(len(classes)):
            for j in range(i, len(classes)):
                tag2idx[classes[i]+classes[j]] = counter
                counter += 1
                idx2tag.append(classes[i]+classes[j])
                #TODO: [IMPROVE] make the edges non-directional!!
                data[classes[i]+classes[j]] = []
                data[classes[j]+classes[i]] = [] #workaround solution
                
        #Storage format = {dir, tag2idx, idx2tag, data : {edge : [(file1, weight1), .. , (fileN, weightN)]}}        
        cached_db = {'dir': path, 'tag2idx': tag2idx,'idx2tag': idx2tag, 'data': data}
        print(cached_db)
        #cached_db['data'] = {classes[i]+classes[j] : [] for i in range(len(classes)) for j in range(i, len(classes))}
        
                     
        for file in os.listdir(path):              #list all the fileiles in the folder
            ext = file.split('.')[1]        #get the file extension
            if ext.lower() in self.valid_images:
                print(file)
                full_path = path+'/'+file
                self.tag_image(filename = full_path)
                
                for edge, weight in get_edges_with_weights(self.classifier.result):
                    cached_db['data'][edge].append((file, weight))
                
        pickle.dump(cached_db, open(path+'/cache.db', 'wb'))
        return cached_db
        
    def find_similar(self, results):
        #TODO : [PROBLEM] No penalty accounted for extra/irrelevant objects
        #do pattern matching on the images in retrieved cached_db
        #keep top 10 and display on right
        self.read_database(ext = 'db')
        edges = get_edges_with_weights(results)
        files = {}
        for edge, e_weight in edges:
            for img, i_weight in self.cached_db['data'][edge]:
                #cummulatively update the scores of files
                files[img] = files.get(img, 0) +  self.get_match_score(e_weight, i_weight)        

        best_matches = nlargest(self.topk, files.keys(), key = lambda e: files[e] )            
        self.show_similar(best_matches, self.cached_db['dir'])
    
    def get_match_score(self, w1, w2):
        #more the difference, the less the score
        return 1/np.exp(np.abs(w1-w2))
        
      
        
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

    
    def select_image(self):  
        #Clear previous image displays        
        self.scene.clear()
        self.scene2.clear()
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
