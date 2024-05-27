from flask import Flask, render_template, session, request, flash, redirect, url_for, jsonify
from functions import update_descripteur_config, is_descripteur_selected
from functions import loadFeatures, Recherche, rappel_precision
from distances import *
import hashlib
import json

app = Flask(__name__)

app.secret_key = 'secret'
config = dict()
config['descripteur'] = dict()
config['image_url'] = ''
config['folder_model'] = list()
config['old_folder_model'] = []
config['features'] = list()
config['distance'] = ''
config['images_proches'] = list()
config['RP'] = list()
config['concatenate'] = ''
config['time'] = [0]*3
config['metrics'] = [['R'+str(i), 0, 0, 0, 0, 0, 0, 0] for i in range(1, 16)]
config['metrics'].append(['Autre', 0, 0, 0, 0, 0, 0, 0])
config['top'] = 50

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

with open("static/data.json", 'r') as f:
    data = json.load(f)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST" and "search" in request.form:
        
        return redirect(url_for('search'))  
    
    return render_template('index.html', config=config)
    

@app.route('/search', methods=['GET', 'POST'])
def search():
    if not session.get('logged_in'):
        return render_template('login.html')  

    if request.method == "POST" and "recherche" in request.form:

        session['indexation_done'] = False

        # Récupération des options de recherche
        config['concatenate'] = request.form.get("mix")
        config['distance'] = request.form.get("distance")
        config['top'] = int(request.form.get("top"))
        image_name = request.form.get('imageSelect')
        classe = request.form.get('marque')
        marque = data[classe]["marque"]
        sousclasse = request.form.get('modele')
        modele = data[classe][sousclasse]["modele"]
        numero = request.form.get('numeroImage')
        config['descripteur'] = update_descripteur_config(request.form)

        # Message d'erreur si pas de descripteur sélectionné
        if not is_descripteur_selected(config['descripteur']):
            flash('Pas de descripteur sélectionné', 'danger')
            return redirect(url_for('search'))
        
        # On récupère le chemin des descripteurs sélectionnés
        config['folder_model'].clear()
        for desc in config['descripteur']:
            if config['descripteur'][desc] == 'on':
                folder_model = "static/" + desc.upper() + ".json"
                config['folder_model'].append(folder_model)

        # Chargement des descripteurs
        config['features'] = loadFeatures(config['concatenate'], config['folder_model'])

        
        # On vérifie si on doit exécuter les requêtes ou une seule
        session['autre'] = False
        if image_name == "All_R":
            requests = requete
            session['all'] = True
        elif image_name == "Autres":
            session['autre'] = True
            image_search = classe + "_" + sousclasse + "_" + marque + "_" + modele + "_" + numero
            requests = [image_search]
            session['all'] = False
        else:
            requests = [image_name]
            session['all'] = False

        if config['old_folder_model'] != config['folder_model']:
            config['old_folder_model'] = config['folder_model'].copy()
            config['metrics'] = [['R'+str(i), 0, 0, 0, 0, 0, 0, 0] for i in range(1, 16)]
            config['metrics'].append(['Autre', 0, 0, 0, 0, 0, 0, 0])

        # On effectue la recherche 
        total_time = 0
        if not session['autre']:
            for i, req in enumerate(requete):
                if req in requests:
                    config['image_url'] = "static/images_requêtes/" + req +".jpg"
                    config['images_proches'], noms_proches, search_time = Recherche(config['image_url'], config['features'], config['distance'], config['top'])
                    config['RP'], config['metrics'][i] = rappel_precision(config['top'], noms_proches, config['image_url'], config['metrics'][i][0])
                    session['indexation_done'] = True
                    total_time += search_time
            config['time'] = [total_time, total_time/len(requests)]
            flash('Recherche terminée', 'success')  
        else:
            config['image_url'] = "static/images_requêtes/" + image_search +".jpg"
            config['images_proches'], noms_proches, search_time = Recherche(config['image_url'], config['features'], config['distance'], config['top'])
            config['RP'], config['metrics'][15] = rappel_precision(config['top'], noms_proches, config['image_url'], "Autre")
            session['indexation_done'] = True
            total_time += search_time
            config['time'] = [total_time, total_time/len(requests)]
            flash('Recherche terminée', 'success')  


        return redirect(url_for('search'))

    return render_template('search.html', config=config)


@app.route("/get_top")
def get_top():
    if session.get('indexation_done') and not session.get('all'):
        images = config['images_proches'][:config['top']]
        return jsonify(images)
    

@app.route("/get_RP")
def get_RP():
    if not session.get('indexation_done') or session.get('all'):
        #flash("Veuillez effectuer la recherche en indexant l'image d'abord")
        return []
    else:
        return config['RP']
    
@app.route("/get_time_data")
def get_time_data():

    if session.get('indexation_done'):
        for d in config['descripteur']:
            if config['descripteur'][d] == 'on':
                desc = d.upper()
        data = [
            {'Descripteur' : desc, 
            'Recherche': round(config['time'][0], 2), 
            'Moyen': round(config['time'][1], 2)},
        ]
        return jsonify(data)

@app.route("/get_metric_data")
def get_metric_data():

    if session.get('indexation_done'):
        data = [
            {'Requete' : config['metrics'][i][0], 
            'R50': round(config['metrics'][i][1], 2), 
            'R100': round(config['metrics'][i][2], 2),
            'P50': round(config['metrics'][i][3], 2),
            'P100': round(config['metrics'][i][4], 2), 
            'AP50': round(config['metrics'][i][5], 2),
            'AP100': round(config['metrics'][i][6], 2),
            'R_Precision': round(config['metrics'][i][7], 2)
            }
        for i in range(16)]
        data.append({'top': config['top']})

        return jsonify(data)
    
@app.route("/get_moy")
def get_moy():

    if session.get('indexation_done'):
        data = config['metrics']
       
        s_AP50, s_AP100, c = 0, 0, 0
        for element in data:
            if element[5] != 0:
                s_AP50 += element[5]
                s_AP100 += element[6]
                c += 1
        moy = [str(round(s_AP50/c, 3)), str(round(s_AP100/c, 3))]
        moy.append({'top': config['top']})

        return jsonify(moy)
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    salt = "hs21"
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
            flash('Accès refusé, mauvais identifiants', 'danger')
    return redirect(url_for('search'))

@app.route('/register', methods=['POST'])
def register():
    salt = "hs21"
    if request.method == 'POST' and 'login' in request.form:
        return render_template('login.html')
    if request.method == 'POST' and 'form_register' in request.form:
        pwd = request.form.get('password') + salt
        if len(pwd) < 10:
            flash('Mot de passe trop court, entrez au moins 6 caractères', 'danger')
            return render_template('login.html')
        hash_pwd = hashlib.md5(pwd.encode())
        collection = []
        with open ("static/mdp.txt", "r") as fout:
            for ligne in fout:
                [name, _] = ligne.rstrip('\n').split(", ")
                collection.append(name)
        if request.form.get('username') in collection:
            flash('Nom d\'utilisateur déjà utilisé', 'danger')
            return render_template('login.html')
        else:
            with open ("static/mdp.txt", "a") as fout:
                fout.write(f"{request.form.get('username')}, {hash_pwd.hexdigest()}\n")
            session['logged_in'] = True
    return redirect(url_for('search'))

@app.route("/logout")
def logout():
    config['descripteur'] = dict()
    config['image_url'] = ''
    config['folder_model'] = list()
    config['features'] = list()
    config['distance'] = ''
    config['images_proches'] = list()
    config['RP'] = list()
    config['concatenate'] = ''
    config['time'] = [0]*3
    config['metrics'] = [['R'+str(i), 0, 0, 0, 0, 0, 0] for i in range(1, 16)]
    session['logged_in'] = False
    session['all'] = False
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
