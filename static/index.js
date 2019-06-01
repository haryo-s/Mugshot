/**
 * Open and close the menu
 * @param name Element's ID to be opened or closed
 */
function openForm(name) {
    var i;
    var x = document.getElementsByClassName("forms");
    for (i = 0; i < x.length; i++) {
        x[i].style.display = "none";
    }
    document.getElementById(name).style.display = "block";
}

/**
 * Spawn the camera and show it
 */
function ShowCam() {
    Webcam.set({
        width: 320,
        height: 240,
        image_format: 'jpeg',
        jpeg_quality: 100
    });
    Webcam.attach('#my_camera');
}
window.onload = ShowCam;

/**
 * Takes a still of the image, display it and upload it to the server
 */
function snap() {
    Webcam.snap(function (data_uri) {
        // display results in page
        document.getElementById('results').innerHTML =
            '<img id="image" src="' + data_uri + '"/>';
    });

    console.log("Uploading...")
    var image = document.getElementById('image').src;

    postFile(image);
}

function postFile(file) {
    let formdata = new FormData();
    formdata.append("file", file);
    let xhr = new XMLHttpRequest();
    xhr.open('POST', 'http://localhost:5001/results', true);
    xhr.onload = function () {
        if (this.status === 200)
            console.log(this.response);
        else
            console.error(xhr);
    };
    xhr.send(formdata);
    console.log(formdata);
}
