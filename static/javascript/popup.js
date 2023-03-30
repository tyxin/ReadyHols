//function openPopUp(elementID) {
//    console.log(elementID)
//    var popup = document.getElementById(elementID);
//    popup.classList.toggle("show");
//}

$ = function(id) {
  return document.getElementById(id);
}

var show = function(id) {
	$(id).style.display ='block';
}
var hide = function(id) {
	$(id).style.display ='none';
}