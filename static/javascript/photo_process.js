var photo_input = document.getElementById('add_photo');
photo_input.addEventListener("change", e =>{
  var imageFile = photo_input.files[0];
  var reader = new FileReader();

  console.log(imageFile);
  console.log(imageFile['name']);

  reader.addEventListener("load", e=> {
    console.log(reader.result);
    var base64String = (reader.result).replace(/^.+?;base64,/, '')


    const byteCharacters = atob(base64String);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], {type: "image/*"});

    console.log("blobbbbb")
    console.log(blob)

    var newImageFile = new File([blob],imageFile['name'])
    console.log(newImageFile);

  });

  reader.readAsDataURL(imageFile);
});
