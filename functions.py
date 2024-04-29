#Defintion de toute les fonctions à appeller dans l'interface
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox
import os
import cv2
import numpy as np
from skimage.transform import resize
from skimage.feature import hog
from skimage import exposure
from skimage import io, color, img_as_ubyte
from matplotlib import pyplot as plt
from skimage.feature import hog, greycomatrix, greycoprops, local_binary_pattern
import json

def generate_HSV(img):
    
    histH = cv2.calcHist([img],[0],None,[180],[0,180])
    histS = cv2.calcHist([img],[1],None,[256],[0,256])
    histV = cv2.calcHist([img],[2],None,[256],[0,256])
    feature = np.concatenate((histH, np.concatenate((histS,histV),axis=None)),axis=None)

    return feature
        
def generate_BGR(img):
    
    histB = cv2.calcHist([img],[0],None,[256],[0,256])
    histG = cv2.calcHist([img],[1],None,[256],[0,256])
    histR = cv2.calcHist([img],[2],None,[256],[0,256])
    feature = np.concatenate((histB, np.concatenate((histG,histR),axis=None)),axis=None)

    return feature

def generate_SIFT(img):
    
    sift = cv2.SIFT_create()  #cv2.xfeatures2d.SIFT_create() pour py < 3.4 
    kps , feature = sift.detectAndCompute(img,None)

    return feature    

def generate_ORB(img):
        
    orb = cv2.ORB_create()
    key_point1,feature = orb.detectAndCompute(img,None)
    
    return feature


def generate_GLCM(img):

    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    gray = img_as_ubyte(gray)
    distances=[1,-1]
    angles=[0, np.pi/4, np.pi/2, 3*np.pi/4]
    glcmMatrix = greycomatrix(gray, distances=distances, angles=angles,normed=True)
    glcmProperties1 = greycoprops(glcmMatrix,'contrast').ravel()
    glcmProperties2 = greycoprops(glcmMatrix,'dissimilarity').ravel()
    glcmProperties3 = greycoprops(glcmMatrix,'homogeneity').ravel()
    glcmProperties4 = greycoprops(glcmMatrix,'energy').ravel()
    glcmProperties5 = greycoprops(glcmMatrix,'correlation').ravel()
    glcmProperties6 = greycoprops(glcmMatrix,'ASM').ravel()
    feature = np.array([glcmProperties1,glcmProperties2,glcmProperties3,glcmProperties4,glcmProperties5,glcmProperties6]).ravel()

    return feature
	

def generate_LBP(img):
    
    points=8
    radius=1
    method='default'
    subSize=(70,70)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.resize(img,(350,350))
    fullLBPmatrix = local_binary_pattern(img,points,radius,method)
    histograms = []
    for k in range(int(fullLBPmatrix.shape[0]/subSize[0])):
        for j in range(int(fullLBPmatrix.shape[1]/subSize[1])):
            subVector =fullLBPmatrix[k*subSize[0]:(k+1)*subSize[0],j*subSize[1]:(j+1)*subSize[1]].ravel()
            subHist,edges =np.histogram(subVector,bins=int(2**points),range=(0,2**points))
            histograms = np.concatenate((histograms,subHist),axis=None)
    feature = histograms

    return feature


def generate_HOG(img):
    
    cellSize = (25,25)
    blockSize = (50,50)
    blockStride = (25,25)
    nBins = 9
    winSize = (350,350)
    image = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    image = cv2.resize(image,winSize)
    hog = cv2.HOGDescriptor(winSize,blockSize,blockStride,cellSize,nBins)
    feature = hog.compute(image)

    return feature



def concatenation(filenames, folders, descripteurs):
    algo_choix1 = None
    algo_choix2 = None
    for desc in descripteurs:
        if descripteurs[desc] == 'on' and not algo_choix1:
            algo_choix1 = desc
        elif descripteurs[desc] == 'on':
            algo_choix2 = desc

    pas=0
    feat=[] 
    folder_model1 = folders[0]
    folder_model2 = folders[1]
    _,nom1 = folder_model1.split('/')
    _,nom2 = folder_model2.split('/')
    folder_name = "static/" + nom1.rstrip(".json") + "_" + nom2
    print(folder_name)
    if not os.path.exists(folder_name):

        with open(folder_model1, "r") as fichier:
            feature1 = json.load(fichier)
        with open(folder_model2, "r") as fichier:
            feature2 = json.load(fichier)
        
        features = {}
        for k in feature1:
            features[k] = list(np.concatenate([feature1[k], feature2[k]]))

        with open(folder_name, "w") as fichier:
            json.dump(features, fichier)

    return folder_name


def search_feature(filename, features):
    image_name = os.path.basename(filename).rstrip('.jpg')
    return features[image_name]


def extractReqFeatures(fileName, algo_choice, features):  

    if fileName : 

        if features:
            return search_feature(fileName, features)
        
        img = cv2.imread(fileName)
        resized_img = resize(img, (128*4, 64*4))
            
        if algo_choice=="bgr": #Couleurs
            vect_features = generate_BGR(img)
        
        elif algo_choice=="hsv": # Histo HSV
            vect_features = generate_HSV(img)

        elif algo_choice=="sift": #SIFT
            vect_features = generate_SIFT(img)
    
        elif algo_choice=="orb": #ORB
            vect_features = generate_ORB(img)

        elif algo_choice=="glcm": #GLCM
            vect_features = generate_GLCM(img)

        elif algo_choice=="lbp": #LBP
            vect_features = generate_LBP(img)

        elif algo_choice=="hog": #HOG
            vect_features = generate_HOG(img)
			
        print("saved")
        return vect_features