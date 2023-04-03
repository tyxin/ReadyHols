var photo_input = document.getElementById('add_photo');
var photo_upload_form = document.getElementById('photo_upload_form');

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

