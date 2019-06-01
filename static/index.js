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

// WEBCAM FUNCTIONS

let v = document.getElementById("myVideo");
//create a canvas to grab an image for upload
let imageCanvas = document.createElement('canvas');
let imageCtx = imageCanvas.getContext("2d");

//Add file blob to a form and post
function postFile(file) {
    let formdata = new FormData();
    formdata.append("file", file);
    let xhr = new XMLHttpRequest();
    xhr.open('POST', 'http://www.mugshotpy.com/results', true);
    xhr.onload = function () {
        if (this.status === 200) {
            console.log(this.response);
            document.open();
            document.write(this.response);
            document.close();
            history.replaceState('data to be passed', 'Title of the page', '/results');
        }
        else
            console.error(xhr);
    };
    // xhr.responseType = "document";
    xhr.send(formdata);
}

//Get the image from the canvas
function sendImagefromCanvas() {
    //Make sure the canvas is set to the current video size
    imageCanvas.width = v.videoWidth;
    imageCanvas.height = v.videoHeight;

    imageCtx.drawImage(v, 0, 0, v.videoWidth, v.videoHeight);

    //Convert the canvas to blob and post the file
    imageCanvas.toBlob(postFile, 'image/jpeg');
}

//Take a picture on click
v.onclick = function() {
    console.log('click');
    sendImagefromCanvas();
};

window.onload = function () {

    //Get camera video
    navigator.mediaDevices.getUserMedia({video: {width: 640, height: 360}, audio: false})
        .then(stream => {
            v.srcObject = stream;
        })
        .catch(err => {
            console.log('navigator.getUserMedia error: ', err)
        });

};
