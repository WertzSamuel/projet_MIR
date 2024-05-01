window.addEventListener("load", (event) => {
    CheckTheme();
    });
function ChangeTheme() {
    let ThemeElements = document.querySelectorAll(".theme");        
    
    if (checkSession("Theme", "light")==false) {
        ThemeElements.forEach(element => {
            element.style.transition="all 0.5s"
            element.classList.add("light");
            
        });
        document.getElementById("moonandsun").href.baseVal="#sun-fill" ;
        document.getElementById("moonandsun").href.animVal="#sun-fill" ;
        setSession("Theme", "light")
    }
    else {
        ThemeElements.forEach(element => {
            element.style.transition="all 0.5s"
            element.classList.remove("light");
        });
        document.getElementById("moonandsun").href.baseVal="#moon-stars-fill";
        document.getElementById("moonandsun").href.animVal="#moon-stars-fill";
        setSession("Theme", "dark")
    }
}

function CheckTheme() {
    let ThemeElements = document.querySelectorAll(".theme");    
    if (checkSession("Theme", "light")==true) {
        ThemeElements.forEach(element => {
            element.classList.add("light");
            document.getElementById("moonandsun").href.baseVal="#sun-fill" ;
            document.getElementById("moonandsun").href.animVal="#sun-fill" ;
        });
    }
}


function CloseNav(){
    if (document.getElementById("nav-button").getAttribute("aria-expanded")=="true"){
      document.getElementById("nav-button").click();
    }
    
  
  }
document.addEventListener("click", function(event) {
// If user clicks inside the element, do nothing
if (event.target.closest("#MainNavbar")) return
// If user clicks outside the element, hide it!
CloseNav();
})