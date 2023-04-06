var file_process = function(id_input,id_upload_form){

  var photo_input = document.getElementById(id_input);
  var photo_upload_form = document.getElementById(id_upload_form);

  var dataURL, dataFile;
  photo_input.addEventListener("change", e =>{
    var imageFile = photo_input.files[0];
    var reader = new FileReader();
    var dataFile = imageFile['name'];

    console.log(imageFile);
    console.log(imageFile['name']);

    reader.addEventListener("load", e=> {
      console.log(reader.result);
      dataURL = reader.result;

    });

    reader.readAsDataURL(imageFile);
  });


};



