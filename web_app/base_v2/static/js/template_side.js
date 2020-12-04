function openNav() {
    document.getElementById("mySidenav").style.width = "250px";
}

window.addEventListener('click', function(e){
  if (!document.getElementById('mySidenav').contains(e.target) && !document.getElementById('myMenu').contains(e.target)){
    // Clicked in box
   document.getElementById("mySidenav").style.width = "0px";
  } else{

 // document.getElementById("mySidenav").style.width = "0px";
  }
});
