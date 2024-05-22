#Defintion de toute les fonctions à appeller dans l'interface
import os
import numpy as np
import json
import time
import matplotlib.pyplot as plt
from distances import getkVoisins

def concatenation(folders):
   
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


def extractReqFeatures(fileName, features):  
    image_name = os.path.basename(fileName).rstrip('.jpg')
    return features[image_name]
        

def update_descripteur_config(form):
    descripteurs = {
        'bgr': form.get('BGR'),
        'hsv': form.get('HSV'),
        'sift': form.get('SIFT'),
        'orb': form.get('ORB'),
        'glcm': form.get('GLCM'),
        'hog': form.get('HOG'),
        'lbp': form.get('LBP'),
        'VGG16': form.get('VGG16'),
        'VGG16_2': form.get('VGG16_2'),
        'VGG19': form.get('VGG19'),
        'VGG19_2': form.get('VGG19_2'),
        'ResNet50': form.get('ResNet50'),
        'ResNet50_2': form.get('ResNet50_2'),
        'Xception': form.get('Xception'),     
        'Xception_2': form.get('Xception_2'),     
        'InceptionV3': form.get('InceptionV3'),     
        'InceptionV3_2': form.get('InceptionV3_2'), 
        'ResNet50Tune': form.get('ResNet50Tune')
    }
    return descripteurs

def is_descripteur_selected(descripteurs):
    return any(value for value in descripteurs.values())

def loadFeatures(concatenate, folder_model):
    
    if concatenate: 
        file = concatenation(folder_model)
    else: 
        file = folder_model[0]
    with open(file, "r") as fichier:
        features = json.load(fichier)

    return features

def Recherche(fileName,features, dist, top):
    t1 = time.time()

    #Remise à 0 de la grille des voisins 
    voisins=""

    # Récupérer les features de l'images requete
    req = extractReqFeatures(fileName, features)

    #Générer les voisins
    voisins=getkVoisins(features, req, top, dist)
    path_image_plus_proches = []
    nom_image_plus_proches = []
    for k in range(top):
        path_image_plus_proches.append("static/dataset/"+voisins[k][0]+".jpg")
        nom_image_plus_proches.append(voisins[k][0])

    t2 = time.time()
    search_time = t2-t1
    
    return path_image_plus_proches, nom_image_plus_proches, search_time


def rappel_precision(top, nom_image_plus_proches, fileName, R):

    # Initialisation
    size = 1000
    val = 0
    rappels, precisions, rappel_precision = [], [], []
    
    # Récupération du nom et de la classe de l'image
    filename_req=os.path.basename(fileName)
    name_image, _ = filename_req.split(".")
    name_image = name_image.split('_')
    num_image = name_image[-1]
    classe_image_requete = int(name_image[0])
    sous_classe_image_requete = int(name_image[1])

    # On parcourt les images proches pour vérifier si elles sont de la même classe
    for j in range(top):
        name_image_proche = nom_image_plus_proches[j].split('_')
        classe_image_proche = name_image_proche[0]
        classe_image_proche = int(classe_image_proche.lstrip('dataset\\'))
        if classe_image_requete==classe_image_proche:
            rappel_precision.append(True) #Bonne classe (pertinant)
            val += 1
        else:
            rappel_precision.append(False) #Mauvaise classe (non pertinant)

        # Calul du rappel et de la précision
        precision = (val/(j+1)) * 100
        rappel = (val/top) * 100
        rappels.append(rappel)
        precisions.append(precision)
    
    print(rappels)
    print(precisions)

        

    metrics = [R, rappels[(top//2)-1], rappels[(top)-1], precisions[(top//2)-1], precisions[(top)-1]]

    #Création de la courbe R/P
    plt.plot(rappels,precisions)
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("R/P "+str(top)+" voisins de l'image n°"+num_image)

    average_P = 0
    deno = 0
    for i in range(top):
        if rappel_precision[i]:
            average_P += precisions[i]
            deno += 1
        if i == (top//2)-1:
            metrics.append(average_P/deno)

    metrics.append(average_P/deno)

    print(metrics[-2])

    #Enregistrement de la courbe RP
    save_folder="static/RP/"
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    save_name=os.path.join(save_folder, num_image+'.png')
    plt.savefig(save_name,format='png',dpi=600)
    plt.close()

    return [save_name], metrics

