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

def showDialog():
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Information)
    msgBox.setText("Merci de sélectionner un descripteur via le menu ci-dessus")
    msgBox.setWindowTitle("Pas de Descripteur sélectionné")
    msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    returnValue = msgBox.exec()

def generateHistogramme_HSV(filenames, progressBar):
    if not os.path.isdir("HSV"):
        os.mkdir("HSV")
    i=0
    for path in os.listdir(filenames):
        img = cv2.imread(filenames+"/"+path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        histH = cv2.calcHist([img],[0],None,[180],[0,180])
        histS = cv2.calcHist([img],[1],None,[256],[0,256])
        histV = cv2.calcHist([img],[2],None,[256],[0,256])
        feature = np.concatenate((histH, np.concatenate((histS,histV),axis=None)),axis=None)

        num_image, _ = path.split(".")
        np.savetxt("HSV/"+str(num_image)+".txt" ,feature)
        
        progressBar.setValue(100*((i+1)/len(os.listdir(filenames))))
        i+=1
    print("indexation Hist HSV terminée !!!!")
        
def generateHistogramme_Color(filenames, progressBar):
    if not os.path.isdir("BGR"):
        os.mkdir("BGR")
    i=0
    for path in os.listdir(filenames):
        img = cv2.imread(filenames+"/"+path)
        histB = cv2.calcHist([img],[0],None,[256],[0,256])
        histG = cv2.calcHist([img],[1],None,[256],[0,256])
        histR = cv2.calcHist([img],[2],None,[256],[0,256])
        feature = np.concatenate((histB, np.concatenate((histG,histR),axis=None)),axis=None)

        num_image, _ = path.split(".")
        np.savetxt("BGR/"+str(num_image)+".txt" ,feature)
        progressBar.setValue(100*((i+1)/len(os.listdir(filenames))))
        i+=1
    print("indexation Hist Couleur terminée !!!!")

def generateSIFT(filenames, progressBar):
    if not os.path.isdir("SIFT"):
        os.mkdir("SIFT")
    i=0
    for path in os.listdir(filenames):
        img = cv2.imread(filenames+"/"+path)
        featureSum = 0
        sift = cv2.SIFT_create()  
        kps , des = sift.detectAndCompute(img,None)

        num_image, _ = path.split(".")
        np.savetxt("SIFT/"+str(num_image)+".txt" ,des)
        progressBar.setValue(100*((i+1)/len(os.listdir(filenames))))
        
        featureSum += len(kps)
        i+=1
    print("Indexation SIFT terminée !!!!")    


def generateORB(filenames, progressBar):
    if not os.path.isdir("ORB"):
        os.mkdir("ORB")
    i=0
    for path in os.listdir(filenames):
        img = cv2.imread(filenames+"/"+path)
        orb = cv2.ORB_create()
        key_point1,descrip1 = orb.detectAndCompute(img,None)
        
        num_image, _ = path.split(".")
        np.savetxt("ORB/"+str(num_image)+".txt" ,descrip1 )
        progressBar.setValue(100*((i+1)/len(os.listdir(filenames))))
        i+=1
    print("indexation ORB terminée !!!!")


def generateGLCM(filenames, progressBar):
    if not os.path.isdir("GLCM"):
        os.mkdir("GLCM")
    distances=[1,-1]
    angles=[0, np.pi/4, np.pi/2, 3*np.pi/4]
    i=0
    for path in os.listdir(filenames):
        image = cv2.imread(filenames+"/"+path)
        gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        gray = img_as_ubyte(gray)
        glcmMatrix = greycomatrix(gray, distances=distances, angles=angles,normed=True)
        glcmProperties1 = greycoprops(glcmMatrix,'contrast').ravel()
        glcmProperties2 = greycoprops(glcmMatrix,'dissimilarity').ravel()
        glcmProperties3 = greycoprops(glcmMatrix,'homogeneity').ravel()
        glcmProperties4 = greycoprops(glcmMatrix,'energy').ravel()
        glcmProperties5 = greycoprops(glcmMatrix,'correlation').ravel()
        glcmProperties6 = greycoprops(glcmMatrix,'ASM').ravel()
        feature = np.array([glcmProperties1,glcmProperties2,glcmProperties3,glcmProperties4,glcmProperties5,glcmProperties6]).ravel()
        num_image, _ = path.split(".")
        np.savetxt("GLCM/"+str(num_image)+".txt" ,feature)
        progressBar.setValue(100*((i+1)/len(os.listdir(filenames))))
        i+=1
    print("indexation GLCM terminée !!!!")
	

def generateLBP(filenames, progressBar):
    if not os.path.isdir("LBP"):
        os.mkdir("LBP")
    i=0
    for path in os.listdir(filenames):
        img = cv2.imread(filenames+"/"+path)
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
        num_image, _ = path.split(".")
        np.savetxt("LBP/"+str(num_image)+".txt" ,histograms)
        progressBar.setValue(100*((i+1)/len(os.listdir(filenames)))) 
        i+=1
    print("indexation LBP terminé !!!!")


def generateHOG(filenames, progressBar):
    if not os.path.isdir("HOG"):
        os.mkdir("HOG")
    i=0
    cellSize = (25,25)
    blockSize = (50,50)
    blockStride = (25,25)
    nBins = 9
    winSize = (350,350)
    for path in os.listdir(filenames):
        img = cv2.imread(filenames+"/"+path)
        image = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        image = cv2.resize(image,winSize)
        hog = cv2.HOGDescriptor(winSize,blockSize,blockStride,cellSize,nBins)
        feature = hog.compute(image)
        num_image, _ = path.split(".")
        np.savetxt("HOG/"+str(num_image)+".txt" ,feature )
        progressBar.setValue(100*((i+1)/len(os.listdir(filenames))))
        i+=1
    print("indexation HOG terminée !!!!")


def concatenate(filenames, models,folders, progressbar):
    algo_choix1=''
    algo_choix2=''
    nom=''
    folder_name1=''
    folder_name2=''
    pas=0
    feat=[] 
    algo_choix1 =models[0]
    folder_model1 = folders[0]
    algo_choix2 = models[1]
    folder_model2 = folders[1]
    _,nom1 = folder_model1.split('/')
    _,nom2 = folder_model2.split('/')
    folder_name=nom1+"_"+nom2
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
        features=''
        data=''
        feature=''
        featureTOT=''
        for j in os.listdir(str(folder_model1)):
            data1=os.path.join(folder_model1,j)
            data2=os.path.join(folder_model2,j)
            feature1 = np.loadtxt(data1)
            feature2 = np.loadtxt(data2)
            if(algo_choix1 == 1 or algo_choix1 == 2):
                feature1 = feature1.ravel()
            if(algo_choix2 == 1 or algo_choix2 == 2):
                feature2 = feature2.ravel()
            featureTOT = np.concatenate([feature1,feature2])
            feat.append((os.path.join(filenames,os.path.basename(data1).split('.')[0]+'.jpg'),featureTOT))
            pas += 1
            progressbar.setValue(int(100*((pas+1)/10000))) 
        saveFeaturesToFiles(feat, folder_name, progressbar)
    return folder_name


def saveFeaturesToFiles(features, folderName, progressBar):
    if not os.path.exists(folderName):
        os.makedirs(folderName)
    i=1
    progressBar.setValue(0)
    print(len(features))
    for name,feature in features:
        print(i,"Writing",name)
        _, numero = name.split('/')
        num_unique = numero.split('.')[0]
        print(num_unique)
        np.savetxt(folderName+"/"+num_unique+".txt",feature)
        i+=1
        progressBar.setValue(100*((i+1)/len(features)))


def extractReqFeatures(fileName, descripteurs):  
    algo_choice = 0
    for k, desc in enumerate(descripteurs):
        if descripteurs[desc] == 'on':
            algo_choice = k+1

    if fileName : 
        img = cv2.imread(fileName)
        resized_img = resize(img, (128*4, 64*4))
            
        if algo_choice==1: #Couleurs
            histB = cv2.calcHist([img],[0],None,[256],[0,256])
            histG = cv2.calcHist([img],[1],None,[256],[0,256])
            histR = cv2.calcHist([img],[2],None,[256],[0,256])
            vect_features = np.concatenate((histB, np.concatenate((histG,histR),axis=None)),axis=None)
        
        elif algo_choice==2: # Histo HSV
            hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
            histH = cv2.calcHist([hsv],[0],None,[180],[0,180])
            histS = cv2.calcHist([hsv],[1],None,[256],[0,256])
            histV = cv2.calcHist([hsv],[2],None,[256],[0,256])
            vect_features = np.concatenate((histH, np.concatenate((histS,histV),axis=None)),axis=None)

        elif algo_choice==3: #SIFT
            sift = cv2.SIFT_create() #cv2.xfeatures2d.SIFT_create() pour py < 3.4 
            # Find the key point
            kps , vect_features = sift.detectAndCompute(img,None)
    
        elif algo_choice==4: #ORB
            orb = cv2.ORB_create()
            # finding key points and descriptors of both images using detectAndCompute() function
            key_point1,vect_features = orb.detectAndCompute(img,None)

        elif algo_choice==5: #GLCM
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
            vect_features = np.array([glcmProperties1,glcmProperties2,glcmProperties3,glcmProperties4,glcmProperties5,glcmProperties6]).ravel()

        elif algo_choice==6: #LBP
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
            vect_features = histograms

        elif algo_choice==7: #HOG
            cellSize = (25,25)
            blockSize = (50,50)
            blockStride = (25,25)
            nBins = 9
            winSize = (350,350)
            image = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            image = cv2.resize(image,winSize)
            hog = cv2.HOGDescriptor(winSize,blockSize,blockStride,cellSize,nBins)
            vect_features = hog.compute(image)
			
        np.savetxt("Methode_"+str(algo_choice)+"_requete.txt" ,vect_features)
        print("saved")
        #print("vect_features", vect_features)
        return vect_features