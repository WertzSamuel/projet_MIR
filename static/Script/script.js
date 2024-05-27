

// Déconnexion si page fermée
$(window).on('beforeunload', function() {
    var form = $('<form action="{{ url_for("logout") }}" method="post"></form>');
    $('body').append(form);
    form.submit();
});

// Ajout de listenner sur les cases à cocher pour gérer leur accès
document.addEventListener("DOMContentLoaded", function() {
    toggleCheckboxes();
    var checkboxes = document.querySelectorAll(".single");

    // On lie le listenner à toutes les cases
    checkboxes.forEach(function(checkbox) {
        checkbox.addEventListener("change", function() {
            toggleCheckboxes();
            toggleDistances();
        });
    });
});

// Fonction empéchant certaines combinaisons de descripteurs
function toggleCheckboxes() {
    var mix = document.getElementById("mix");
    var checkboxes = document.querySelectorAll(".single");
    var checkedCount = 0;
    var selectedCheckboxes = [];

    checkboxes.forEach(function(checkbox) {
        checkbox.disabled = false;

        if (checkbox.checked) {
            checkedCount++;
            selectedCheckboxes.push(checkbox);
        }
    });

    // Si on ne veut pas concaténer -> un seul descripteur à la fois
    if (mix.checked == false && checkedCount >= 1) {
        checkboxes.forEach(function(checkbox) {
            checkbox.checked = false;
            checkbox.disabled = true;
        });
        selectedCheckboxes.slice(0, 1).forEach(function(checkbox) {
            checkbox.checked = true;
            checkbox.disabled = false;
        });
    }
    else if (mix.checked){

        // Si on veut concaténer -> pas de SIFT ou ORB
        checkboxes.forEach(function(checkbox) {
            if ((checkbox.name === "SIFT" || checkbox.name === "ORB")) {
                checkbox.disabled = true;
                checkbox.checked = false;
            }
        })

        // Si on veut concaténer -> deux descripteurs à la fois
        if(checkedCount >= 2){
            checkboxes.forEach(function(checkbox) {
                checkbox.checked = false;
                checkbox.disabled = true;
            });
            selectedCheckboxes.slice(0, 2).forEach(function(checkbox) {
                checkbox.checked = true;
                checkbox.disabled = false;
            });
        }
    }
}

// Fonction gérant l'affichage des options de distance
function toggleDistances() {
    var distanceSelect = document.getElementById("distanceSelect");
    var siftOrbSelected = false;

    // Vérifie si SIFT ou ORB est sélectionné
    document.querySelectorAll(".single").forEach(function(checkbox) {
        if (checkbox.checked && (checkbox.name === "SIFT" || checkbox.name === "ORB")) {
            siftOrbSelected = true;
        }
    });

    if (siftOrbSelected) {
        distanceSelect.innerHTML = '<option value="Brute_force">Brute-force</option>';
        distanceSelect.innerHTML += '<option value="Flann">Flann</option>';

    }
    else {
        distanceSelect.innerHTML = '<option value="Euclidienne">Euclidienne</option>';
        distanceSelect.innerHTML += '<option value="Correlation">Correlation</option>';
        distanceSelect.innerHTML += '<option value="Chi_Carre">Chi carré</option>';
        distanceSelect.innerHTML += '<option value="Intersection">Intersection</option>';
        distanceSelect.innerHTML += '<option value="Bhattacharyya">Bhattacharyya</option>';
    }
}

// Charge l'image requête
function loadImageRequest(data){
    var image_selected = $("#imageSelect").val();
    var marque_selected = $("#marque").val();
    var modele_selected = $("#modele").val();
    var numero_selected = $("#numeroImage").val();
    if (image_selected != "Autres") {
        $("#AutreImage").hide();
    }
    if (image_selected != "All_R" && image_selected != "Autres") {
        var image_path = "/static/images_requêtes/" + image_selected + ".jpg"
        $("#image_requete").attr("src",image_path);
    }
    else if (image_selected == "Autres") {
        $("#AutreImage").show();
        var image_path = "/static/dataset/" 
        + marque_selected 
        + "_" + modele_selected 
        + "_" + data[marque_selected].marque 
        + "_" + data[marque_selected][modele_selected].modele 
        + "_" + numero_selected + ".jpg"
        $("#image_requete").attr("src",image_path);
    }
    else {
        $("#image_requete").attr("src","");
        $("#top").val("100");
    }
}

// Récupère les images les + proches
function get_top() {
    $.get('/get_top', function(data){
        var images_html = '';
        var image_req = data[0];
        var classe_req = image_req.split("/").pop().split("_")[0];
        data.forEach(function(image){
            var nom_image = image.split("/").pop();
            var classe = nom_image.split("_")[0];
            if (classe == classe_req) {
                images_html += '<img class="image my-2 mx-2 " src="' + image + '" alt="' +nom_image+ '" title="' +nom_image+ '" style="width:18%; border: 0.3rem solid green;">';
            } else {
                images_html += '<img class="image my-2 mx-2" src="' + image + '" alt="' +nom_image+ '" title="' +nom_image+ '" style="width:18%; border: 0.3rem solid red;">';
            }
            
        });
        $("#conteneur_images").html(images_html);
    });
}

// Récupère le graphe RP
function get_RP(){
    $.get('/get_RP', function(data){
        var images_html = '';
        data.forEach(function(image){
            images_html += '<img  src="' + image + '" alt="Image" width="600" height="450">';
            $("#conteneur_RP").show();
        });
        $("#conteneur_RP").html(images_html);
        
    });
}

// Récupère les temps d'exécution
function get_time() {
    $.get('/get_time_data', function(data){
        $('#timeTable tbody').empty();
        $.each(data, function(index, item){
            $('#timeTable tbody').append('<tr><td>' + item.Descripteur + '</td><td>' + item.Recherche + '</td><td>' + item.Moyen + '</td></tr>');
        });
        $('#timeContainer').show();
    });
}

// Affiche le tableau des métriques
function get_metrics() {
    
    $.get('/get_metric_data', function(data){
        const top = data[data.length - 1].top;
        const metrics = data.slice(0, -1); 
        for (let i = 0; i < 3; i++) {
            $('#thead').append('<th> Top '+ String(top/2) + '</th>')    
            $('#thead').append('<th> Top '+ String(top) + '</th>')    
        }
        $('#metricTable tbody').empty();
        $.each(metrics, function(index, item){
            $('#metricTable tbody').append('<tr><td>' + item.Requete + '</td><td>' + item.R50 + '</td><td>' + item.R100 + '</td><td>' + item.P50 + '</td><td>' + item.P100 + '</td><td>' + item.AP50 + '</td><td>' + item.AP100  + '</td><td>' + item.R_Precision + '</td></tr>');
        });
        

    })
    $.get('/get_moy', function(data){
        const top = data[data.length - 1].top;
        const moy = data.slice(0, -1); 
        var contenuElement = document.getElementById("MAP50");
        contenuElement.textContent = "MaP top "+ String(top/2) + " : "  + moy[0] + " %";
        var contenuElement = document.getElementById("MAP100");
        contenuElement.textContent = "MaP top "+ String(top) + " : " + moy[1] + " %";
        $('#metricContainer').show();
        $('#metricTable').show();
    });

    
}

$(document).ready(function(){

    $("#Recherche").click(function(event) {
        $('#modal-loading').modal('show');
    });
    $("#imageSelect").change( function( event ) {
        fetch('static/data.json')
        .then(response => response.json())
        .then(data => {
            loadImageRequest(data);
        });
      });

    fetch('static/data.json')
    .then(response => response.json())
    .then(data => {
        loadImageRequest(data);
    });
    get_time();
    get_top();
    get_RP(); 
    get_metrics();
    
    
});

// Charger le fichier JSON
fetch('static/data.json')
.then(response => response.json())
.then(data => {
    initializeSelectors(data);
});

function initializeSelectors(data) {
    const marqueSelect = document.getElementById('marque');
    const modeleSelect = document.getElementById('modele');
    const numeroImageSelect = document.getElementById('numeroImage');

    // Remplir la liste déroulante des marques
    for (const marqueId in data) {
        const marque = data[marqueId].marque;
        const option = document.createElement('option');
        option.value = marqueId;
        option.textContent = marque;
        marqueSelect.appendChild(option);
    }

    // Mettre à jour les modèles et numéros d'image lorsque la marque change
    marqueSelect.addEventListener('change', () => {
        const selectedMarqueId = marqueSelect.value;
        modeleSelect.innerHTML = '';
        numeroImageSelect.innerHTML = '';

        const marqueData = data[selectedMarqueId];
        for (const modeleId in marqueData) {
            if (modeleId !== 'marque') {
                const modele = marqueData[modeleId].modele;
                const option = document.createElement('option');
                option.value = modeleId;
                option.textContent = modele;
                modeleSelect.appendChild(option);
            }
        }

        // Simuler un changement pour remplir les numéros d'image pour le premier modèle par défaut
        modeleSelect.dispatchEvent(new Event('change'));
        loadImageRequest(data);
    });

    // Mettre à jour les numéros d'image lorsque le modèle change
    modeleSelect.addEventListener('change', () => {
        const selectedMarqueId = marqueSelect.value;
        const selectedModeleId = modeleSelect.value;
        numeroImageSelect.innerHTML = '';

        const numeroImages = data[selectedMarqueId][selectedModeleId].numero;
        for (const numero of numeroImages) {
            const option = document.createElement('option');
            option.value = numero;
            option.textContent = numero;
            numeroImageSelect.appendChild(option);
        }
        loadImageRequest(data);
    });

    // Déclencher le changement initial pour remplir les modèles et numéros d'image
    marqueSelect.dispatchEvent(new Event('change'));

    numeroImageSelect.addEventListener('change', () => {
        loadImageRequest(data);
    });
    }