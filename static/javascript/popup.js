//function openPopUp(elementID) {
//    console.log(elementID)
//    var popup = document.getElementById(elementID);
//    popup.classList.toggle("show");
//}

$ = function(id) {
  return document.getElementById(id);
}

var show = function(id,id_button,type_show) {
	$(id).style.display ='block';
    $(id_button).innerHTML = type_show;
}


var hide = function(id) {
	$(id).style.display ='none';
}

var show_error = function(id){
    $(id).style.display = "block"
};
  
var highlight_row = function(id) {
    var index = -1;
    for (var i = 0; i < $(id).rows.length;i++){
        $(id).rows[i].onclick = function(){
            console.log(index);
            if (index != -1 ){
                $(id).rows[index].classList.toggle("selected");
            };
            index = this.rowIndex;
            this.classList.toggle("selected");
            console.log(index);
        };
        
    };
};

highlight_row('vacation_tbl');

//var update_row = function(id, data, ...display_ids){
//    var indexSelected = -1;
//	console.log(data[0])
//    for (var i = 0; i < $(id).rows.length;i++){
//        if ($(id).rows[i].classList.length>0){
//            indexSelected = i;
//        };
//    };
//    // show_with_data(id, indexSelected, data, display_ids);
//};



