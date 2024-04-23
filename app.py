from flask import Flask, render_template, session, request, flash, redirect, url_for
from PyQt5 import QtCore, QtGui, QtWidgets
import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QFileDialog
import cv2
import numpy as np
from skimage.transform import resize
from skimage.io import imread
from skimage.feature import hog
from skimage import exposure
from matplotlib import pyplot as plt
from functions import extractReqFeatures, showDialog, concatenate
from distances import *
import time
import hashlib
import json

app = Flask(__name__)

app.secret_key = 'secret'
config = dict()
config['descripteur'] = dict()
config['image_url'] = ''
config['to_concatenate'] = list()
config['features'] = list()
config['distance'] = ''
config['images_proches'] = list()
config['RP'] = list()

@app.route('/', methods=['GET', 'POST'])
def index():
    
    if not session.get('logged_in'):
        return render_template('login.html')
    
    if request.method == "POST" and "confirmation" in request.form:

        concatenate = request.form.get("mix")
        config['distance'] = request.form.get("distance")
        update_descripteur_config(request.form)
        if not is_descripteur_selected():
            flash('Pas de descripteur sélectionné', 'params')
            return redirect(request.url)
        
        for k, desc in enumerate(config['descripteur']):
            if config['descripteur'][desc] == 'on':
                folder_model = "static/" + desc.upper()

        config['features'] = loadFeatures(concatenate, folder_model)
        flash('chargement des descripteurs terminé')  

        session['descripteur_selected'] = True

        return redirect('/')
        
    if request.method == "POST" and "affichage" in request.form:

        name = request.form.get('imageSelect')
        config['image_url'] = "static/images_requêtes/" + name +".jpg"

        return redirect('/')

    if request.method == "POST" and "indexation" in request.form:
         # On vérifie que les descripteurs ont bien été chargés
         if not session.get('descripteur_selected'):
             flash("Veuillez confirmer vos options de recherches d'abord")
         else:
            concatenate = request.form.get("mix")
            config['images_proches'], noms_proches = Recherche(concatenate, config['descripteur'], config['distance'], 100)
            config['RP'] = [rappel_precision(100, noms_proches)]

            session['indexation_done'] = True

            return redirect('/')

    return render_template('index.html', config=config)


def update_descripteur_config(form):
    config['descripteur'] = {
        'bgr': form.get('BGR'),
        'hsv': form.get('HSV'),
        'sift': form.get('SIFT'),
        'orb': form.get('ORB'),
        'glcm': form.get('GLCM'),
        'hog': form.get('HOG'),
        'lbp': form.get('LBP'),
        'VGG16': form.get('VGG16'),
        'Xception': form.get('Xception'),     
    }

def is_descripteur_selected():
    descripteurs = config['descripteur']
    return any(value for value in descripteurs.values())

@app.route('/login', methods=['POST'])
def login():
    salt = "gz42"
    if request.method == 'POST' and 'register' in request.form:
        return render_template('register.html')
    if request.method == 'POST' and 'form_login' in request.form:
        pwd = request.form.get('password') + salt
        hash_pwd = hashlib.md5(pwd.encode())
        collection = []
        with open ("static/mdp.txt", "r") as fout:
            for ligne in fout:
                [name, pswd] = ligne.rstrip('\n').split(", ")
                collection.append((name, pswd))
        print(collection)
        if (request.form.get('username'), hash_pwd.hexdigest()) in collection:
            session['logged_in'] = True
        else:
            flash('Accès refusé, mauvais identifiants', 'login')
    return redirect(url_for('index'))

@app.route('/register', methods=['POST'])
def register():
    salt = "gz42"
    if request.method == 'POST' and 'login' in request.form:
        return render_template('login.html')
    if request.method == 'POST' and 'form_register' in request.form:
        pwd = request.form.get('password') + salt
        if len(pwd) < 10:
            flash('Mot de passe trop court, entrez au moins 6 caractères', 'register')
            return render_template('register.html')
        hash_pwd = hashlib.md5(pwd.encode())
        collection = []
        with open ("static/mdp.txt", "r") as fout:
            for ligne in fout:
                [name, _] = ligne.rstrip('\n').split(", ")
                collection.append(name)
        if request.form.get('username') in collection:
            flash('Nom d\'utilisateur déjà utilisé', 'register')
            return render_template('register.html')
        else:
            with open ("static/mdp.txt", "a") as fout:
                fout.write(f"{request.form.get('username')}, {hash_pwd.hexdigest()}\n")
            session['logged_in'] = True
    return redirect(url_for('index'))

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return index()

def loadFeatures(concatenate, folder_model):
    t1 = time.time()
    
    if concatenate == 'oui':
        folder_model = concatenate('static/dataset', config['to_concatenate'][0], config['to_concatenate'][1])

    ##Charger les features de la base de données.
    print("chargement de descripteurs en cours ...")
    file = folder_model + ".json"
    with open(file, "r") as fichier:
        features1 = json.load(fichier)

    t2 = time.time()
    flash(f'temps de chargement : {t2-t1} s')

    return features1


def Recherche(concatenate, desc, dist, sortie):
    t1 = time.time()
    fileName = config['image_url']

    #Remise à 0 de la grille des voisins 
    voisins=""

    ##Generer les features de l'images requete
    if concatenate == 'oui':
        req1 = extractReqFeatures(fileName,config['to_concatenate'][0])
        req2 = extractReqFeatures(fileName, config['to_concatenate'][1])
        if(config['to_concatenate'] == 1 or config['to_concatenate'] == 2):
            req1 = req1.ravel()
        if(config['to_concatenate'] == 1 or config['to_concatenate'] == 2):
            req2 = req2.ravel()
        req =  np.concatenate([req1,req2])
    
    else:
        req = extractReqFeatures(fileName, config['descripteur'])

    #Aller chercher dans la liste de l'interface la distance choisie
    distanceName=dist
    #Générer les voisins
    voisins=getkVoisins(config['features'], req, sortie, distanceName)
    path_image_plus_proches = []
    nom_image_plus_proches = []
    for k in range(sortie):
        path_image_plus_proches.append(voisins[k][0])
        nom_image_plus_proches.append(os.path.basename(voisins[k][0]))

    t2 = time.time()
    print('temps de recherche :', t2-t1)
    
    return path_image_plus_proches, nom_image_plus_proches

@app.route("/get_top50")
def get_top50():
    if not session.get('indexation_done'):
        flash("Veuillez effectuer la recherche en indexant l'image d'abord")
    else:
        return config['images_proches'][:50]


@app.route("/get_top100")
def get_top100():
    if not session.get('indexation_done'):
        flash("Veuillez effectuer la recherche en indexant l'image d'abord")
    else:
        return config['images_proches'][:100]


def rappel_precision(sortie, nom_image_plus_proches):
    fileName = config['image_url']
    size = 1000
    rappel_precision=[]
    rappels=[]
    precisions=[]
    filename_req=os.path.basename(fileName)
    name_image, _ = filename_req.split(".")
    name_image = name_image.split('_')
    num_image = name_image[-1]
    classe_image_requete = name_image[0]
    sous_classe_image_requete = name_image[1]
    val =0
    
    for j in range(sortie):
        name_image_proche = nom_image_plus_proches[j].split('_')
        print(name_image_proche)
        classe_image_proche = name_image_proche[0]
        classe_image_requete = int(classe_image_requete)
        classe_image_proche = int(classe_image_proche)
        if classe_image_requete==classe_image_proche:
            rappel_precision.append(True) #Bonne classe (pertinant)
            val += 1
        else:
            rappel_precision.append(False) #Mauvaise classe (non pertinant)
    for i in range(sortie):
        j=i
        val=0
        while(j>=0):
            if rappel_precision[j]:
                val+=1
            j-=1 
        precision = val/(i+1) * 100
        rappel = val/sortie * 100
        rappels.append(rappel)
        precisions.append(precision)

    #Création de la courbe R/P
    plt.plot(rappels,precisions)
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("R/P"+str(sortie)+" voisins de l'image n°"+num_image)
    print(rappels, precisions)

    average_P = 0
    deno = 0
    for i in range(sortie):
        if rappel_precision[i]:
            average_P += precisions[i]
            deno += 1
    average_P/=deno
    flash(average_P)

    #Enregistrement de la courbe RP
    save_folder="static/RP/"
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    save_name=os.path.join(save_folder, num_image+'.png')
    plt.savefig(save_name,format='png',dpi=600)
    plt.close()
    return save_name


@app.route("/get_RP")
def get_RP():
    if not session.get('indexation_done'):
        flash("Veuillez effectuer la recherche en indexant l'image d'abord")
        return []
    else:
        return config['RP']

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)