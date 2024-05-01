function setCookie(cname, cvalue, exdays) {
  const d = new Date();
  d.setTime(d.getTime() + (exdays*24*60*60*1000));
  let expires = "expires="+ d.toUTCString();
  document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
  //document.cookie = cname + "=" + cvalue + ";path=/";
}

function setSession(name, value) {
  sessionStorage.setItem(name, value);
}

function checkSession(name, value) {
  if (sessionStorage.getItem(name) == value) {
    return true;
  }
  else {
    return false;
  }
}

function getCookie(cname) {
  let name = cname + "=";
  let decodedCookie = decodeURIComponent(document.cookie);
  let ca = decodedCookie.split(';');
  for(let i = 0; i <ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

function checkCookie(cname) {
  let cookie = getCookie(cname);
  if (cookie != "") {
   return true;
  } else {
    return false;
  }
}