

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
function loadImageRequest(){
    var image_selected = $("#imageSelect").val();
    if (image_selected != "All_R") {
        var image_path = "/static/images_requêtes/" + image_selected + ".jpg"
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
        data.forEach(function(image){
            images_html += '<img class="image px-2 py-2" src="' + image + '" alt="Image" style="width:20%">';
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
        $('#metricTable tbody').empty();
        $.each(data, function(index, item){
            $('#metricTable tbody').append('<tr><td>' + item.Requete + '</td><td>' + item.R50 + '</td><td>' + item.R100 + '</td><td>' + item.P50 + '</td><td>' + item.P100 + '</td><td>' + item.AP50 + '</td><td>' + item.AP100  + '</td></tr>');
        });
        $('#metricContainer').show();
    })
    $.get('/get_moy', function(moy){
        var contenuElement = document.getElementById("MAP50");
        contenuElement.textContent = "MaP top 50 : " + moy[0];
        var contenuElement = document.getElementById("MAP100");
        contenuElement.textContent = "MaP top 100 : " + moy[1];
    });
}

$(document).ready(function(){


    $("#imageSelect").change( function( event ) {
        loadImageRequest();
      });

    loadImageRequest();    
    get_time();
    var image_selected = $("#imageSelect").val();
    if (image_selected != "All_R") {
        get_top();
        get_RP(); 
    }
    else {
        get_metrics();
    }
    
});