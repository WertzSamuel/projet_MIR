from flask import Flask, render_template, session, request, flash, redirect, url_for, jsonify
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
from functions import extractReqFeatures, showDialog, concatenation
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
config['concatenate'] = ''
config['time'] = [0]*3
config['metrics'] = [['R'+str(i), 0, 0, 0, 0, 0, 0] for i in range(1, 16)]

@app.route('/', methods=['GET', 'POST'])
def index():

    if config['distance'] == '' :
        session['descripteur_selected'] = False
        session['image_selected'] = False
        session['indexation_done'] = False
    
    if not session.get('logged_in'):
        return render_template('login.html')
    
    if request.method == "POST" and "confirmation" in request.form:
        config['descripteur'] = dict()

        config['concatenate'] = request.form.get("mix")
        config['distance'] = request.form.get("distance")
        update_descripteur_config(request.form)
        if not is_descripteur_selected():
            flash('Pas de descripteur sélectionné', 'params')
            return redirect(request.url)
        
        for desc in config['descripteur']:
            if config['descripteur'][desc] == 'on':
                folder_model = "static/" + desc.upper() + ".json"
                config['to_concatenate'].append(folder_model)

        config['features'] = loadFeatures(config['concatenate'], folder_model)
        flash('chargement des descripteurs terminé')  

        session['descripteur_selected'] = True

        return redirect('/')
        
    if request.method == "POST" and "affichage" in request.form:

        name = request.form.get('imageSelect')
        config['image_url'] = "static/images_requêtes/" + name +".jpg"

        session['image_selected'] = True

        return redirect('/')

    if request.method == "POST" and "indexation" in request.form:
        # On vérifie que les descripteurs ont bien été chargés
        if not session.get('descripteur_selected'):
            flash("Veuillez confirmer vos options de recherches d'abord")
        elif not session.get('image_selected'):
            flash("Veuillez choisir une image d'abord")
        else:
            concatenate = request.form.get("mix")
            config['images_proches'], noms_proches = Recherche(config['concatenate'], config['descripteur'], config['distance'], 100)
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
        folder_model = concatenation('static/dataset', config['to_concatenate'], config['descripteur'])
        print(folder_model)

    ##Charger les features de la base de données.
    file = folder_model
    with open(file, "r") as fichier:
        features1 = json.load(fichier)

    t2 = time.time()

    config['time'][0] = t2-t1

    return features1


def Recherche(concatenate, desc, dist, sortie):
    t1 = time.time()
    fileName = config['image_url']
    descripteurs = config['descripteur']

    #Remise à 0 de la grille des voisins 
    voisins=""

    ##Generer les features de l'images requete
    if concatenate == 'oui':
        algo_choix1 = 0
        algo_choix2 = 0
        for k, desc in enumerate(descripteurs):
            if descripteurs[desc] == 'on' and algo_choix1 == 0:
                algo_choix1 = k+1
            elif descripteurs[desc] == 'on':
                algo_choix2 = k+1
        req1 = extractReqFeatures(fileName, algo_choix1)
        req2 = extractReqFeatures(fileName, algo_choix2)
        '''
        if(algo_choix1 == 1 or algo_choix1 == 2):
            req1 = req1.ravel()
        if(algo_choix2 == 1 or algo_choix2 == 2):
            req2 = req2.ravel()
        '''
        req =  np.concatenate([req1,req2])
    
    else:
        algo_choice = 0
        for k, desc in enumerate(descripteurs):
            if descripteurs[desc] == 'on':
                algo_choice = k+1
        req = extractReqFeatures(fileName, algo_choice)

    #Générer les voisins
    voisins=getkVoisins(config['features'], req, sortie, dist)
    path_image_plus_proches = []
    nom_image_plus_proches = []
    for k in range(sortie):
        path_image_plus_proches.append(voisins[k][0])
        nom_image_plus_proches.append(os.path.basename(voisins[k][0]))

    t2 = time.time()
    search_time = t2-t1
    config['time'][1], config['time'][2] = search_time, search_time/len(config['features'])
    
    return path_image_plus_proches, nom_image_plus_proches

@app.route("/get_top50")
def get_top50():
    if not session.get('indexation_done'):
        flash("Veuillez effectuer la recherche en indexant l'image d'abord")
    else:
        images = config['images_proches'][:50]
        return jsonify(images)


@app.route("/get_top100")
def get_top100():
    if not session.get('indexation_done'):
        flash("Veuillez effectuer la recherche en indexant l'image d'abord")
    else:
        images = config['images_proches'][:100]
        return jsonify(images)


def rappel_precision(sortie, nom_image_plus_proches):
    t1 = time.time()

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
        classe_image_proche = name_image_proche[0]
        classe_image_requete = int(classe_image_requete)
        classe_image_proche = int(classe_image_proche.lstrip('dataset\\'))
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

    requete = {"1_4_Kia_stinger_1944": 0,
                "1_2_Kia_sorento_1675": 1,
                "1_9_Kia_stonic_2629": 2,
                "3_1_Renault_Twingo_4491": 3,
                "3_0_Renault_grandscenic_4372": 4,
                "3_5_Renault_clio_5101": 5,
                "5_0_Mercedes_ClasseCLS_7059": 6,
                "5_3_Mercedes_classeC_7403": 7,
                "5_8_Mercedes_CLA_7992": 8,
                "7_0_Peugeot_508break_9642": 9,
                "7_3_Peugeot_Rifter_10091": 10,
                "7_6_Peugeot_3008_10530": 11,
                "9_0_Audi_A6_12288": 12,
                "9_3_Audi_Q7_12722": 13,
                "9_4_Audi_A1_12833": 14}
    req = requete[fileName.lstrip("static/images_requêtes/").rstrip(".jpg")]

    config['metrics'][req][1] = rappels[49]
    config['metrics'][req][3] = precisions[49]
    config['metrics'][req][2] = rappels[99]
    config['metrics'][req][4] = precisions[99]

    #Création de la courbe R/P
    plt.plot(rappels,precisions)
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("R/P"+str(sortie)+" voisins de l'image n°"+num_image)

    average_P = 0
    deno = 0
    for i in range(sortie):
        if rappel_precision[i]:
            average_P += precisions[i]
            deno += 1
        if i == sortie//2:
            config['metrics'][req][5] = average_P/deno

    config['metrics'][req][6] = average_P/deno

    #Enregistrement de la courbe RP
    save_folder="static/RP/"
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    save_name=os.path.join(save_folder, num_image+'.png')
    plt.savefig(save_name,format='png',dpi=600)
    plt.close()

    t2 = time.time()

    return save_name


@app.route("/get_RP")
def get_RP():
    if not session.get('indexation_done'):
        flash("Veuillez effectuer la recherche en indexant l'image d'abord")
        return []
    else:
        return config['RP']
    
@app.route("/get_time_data")
def get_time_data():

    if not session.get('indexation_done'):
        flash("Veuillez effectuer la recherche en indexant l'image d'abord")

    else:
        for d in config['descripteur']:
            if config['descripteur'][d] == 'on':
                desc = d.upper()
        data = [
            {'Descripteur' : desc, 
            'Indexation': round(config['time'][0], 2), 
            'Recherche': round(config['time'][1], 2), 
            'Moyen': round(config['time'][2], 2)},
        ]
        return jsonify(data)

@app.route("/get_metric_data")
def get_metric_data():

    if not session.get('indexation_done'):
        flash("Veuillez effectuer la recherche en indexant l'image d'abord")

    else:
        data = [
            {'Requete' : config['metrics'][i][0], 
            'R50': round(config['metrics'][i][1], 2), 
            'R100': round(config['metrics'][i][2], 2),
            'P50': round(config['metrics'][i][3], 2),
            'P100': round(config['metrics'][i][4], 2), 
            'AP50': round(config['metrics'][i][5], 2),
            'AP100': round(config['metrics'][i][6], 2)}
        for i in range(15)]

        return jsonify(data)
    
@app.route("/get_moy")
def get_moy():

    if not session.get('indexation_done'):
        flash("Veuillez effectuer la recherche en indexant l'image d'abord")

    else:
        data = config['metrics']
       
        s_AP50, s_AP100, c = 0, 0, 0
        for element in data:
            print(element)
            if element[5] != 0:
                s_AP50 += element[5]
                s_AP100 += element[6]
                c += 1
        moy = [str(round(s_AP50/c, 3)), str(round(s_AP100/c, 3))]

        return jsonify(moy)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)