var imagerApiEndpoint = 'https://ej7ryesphb.execute-api.us-east-1.amazonaws.com/dev/';
var bucketName = 'hpf-imager-houessou-com-files';
var awsRegion = 'us-east-1';
var identityPoolId = 'us-east-1:1d4efcf7-f995-4331-bd94-c3ed6111f246';

var gridScope;
var descriptionScope;
var filesScope;

//Timer
const FULL_DASH_ARRAY = 283;
const WARNING_THRESHOLD = 10;
const ALERT_THRESHOLD = 5;

const COLOR_CODES = {
  info: {
    color: "green"
  },
  warning: {
    color: "orange",
    threshold: WARNING_THRESHOLD
  },
  alert: {
    color: "red",
    threshold: ALERT_THRESHOLD
  }
};

const TIME_LIMIT = 10;
let timePassed = 0;
let timeLeft = TIME_LIMIT;
let timerInterval = null;
let remainingPathColor = COLOR_CODES.info.color;

document.getElementById("timerApp").innerHTML = `
<div class="base-timer">
  <svg class="base-timer__svg" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <g class="base-timer__circle">
      <circle class="base-timer__path-elapsed" cx="50" cy="50" r="45"></circle>
      <path
        id="base-timer-path-remaining"
        stroke-dasharray="283"
        class="base-timer__path-remaining ${remainingPathColor}"
        d="
          M 50, 50
          m -45, 0
          a 45,45 0 1,0 90,0
          a 45,45 0 1,0 -90,0
        "
      ></path>
    </g>
  </svg>
  <span id="base-timer-label" class="base-timer__label">${formatTime(
    timeLeft
  )}</span>
</div>
`;

function onTimesUp() {
  clearInterval(timerInterval);
  showGetAnalysisButton();
}

function startTimer() {
  timerInterval = setInterval(() => {
    timePassed = timePassed += 1;
    timeLeft = TIME_LIMIT - timePassed;
    document.getElementById("base-timer-label").innerHTML = formatTime(
      timeLeft
    );
    setCircleDasharray();
    setRemainingPathColor(timeLeft);

    if (timeLeft === 0) {
      onTimesUp();
    }
  }, 1000);
}

function formatTime(time) {
  const minutes = Math.floor(time / 60);
  let seconds = time % 60;

  if (seconds < 10) {
    seconds = `0${seconds}`;
  }

  return `${minutes}:${seconds}`;
}

function setRemainingPathColor(timeLeft) {
  const { alert, warning, info } = COLOR_CODES;
  if (timeLeft <= alert.threshold) {
    document
      .getElementById("base-timer-path-remaining")
      .classList.remove(warning.color);
    document
      .getElementById("base-timer-path-remaining")
      .classList.add(alert.color);
  } else if (timeLeft <= warning.threshold) {
    document
      .getElementById("base-timer-path-remaining")
      .classList.remove(info.color);
    document
      .getElementById("base-timer-path-remaining")
      .classList.add(warning.color);
  }
}

function calculateTimeFraction() {
  const rawTimeFraction = timeLeft / TIME_LIMIT;
  return rawTimeFraction - (1 / TIME_LIMIT) * (1 - rawTimeFraction);
}

function setCircleDasharray() {
  const circleDasharray = `${(
    calculateTimeFraction() * FULL_DASH_ARRAY
  ).toFixed(0)} 283`;
  document
    .getElementById("base-timer-path-remaining")
    .setAttribute("stroke-dasharray", circleDasharray);
}
// End Timer

function createUuid(){
    var dt = new Date().getTime();
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (dt + Math.random()*16)%16 | 0;
        dt = Math.floor(dt/16);
        return (c=='x' ? r :(r&0x3|0x8)).toString(16);
    });
    return uuid;
}

function showTimerForm(){
    $("#timerForm").removeClass("d-none");
    startTimer();
} 

function showAnalysisForm(){
    var fileKey = localStorage.getItem('fileKey');
    getAnalysis(fileKey, applyAnalysisScope);
    $("#analysisForm").removeClass("d-none");
} 

function hideAddFilesForm(){
    $("#addFilesForm").addClass("d-none");
    $("#fileinput").replaceWith($("#fileinput").val('').clone(true));
}

function showGetAnalysisButton(){
    $("#getAnalysisButton").removeClass("d-none");
}

function resetForms(){
    $("#addFilesForm").removeClass("d-none");
    $("#getAnalysisButton").addClass("d-none");
    $("#analysisForm").addClass("d-none");
    $("#timerForm").addClass("d-none");
}

function addFileName () {
    var fileName = document.getElementById('fileinput').files[0].name;
    document.getElementById('fileName').innerHTML = fileName;
}      

function getAnalysis(fileKey, callback) {
    var todoApi = imagerApiEndpoint + fileKey +'/analysis'

    $.ajax({
    url : todoApi,
    type : 'GET',
    //headers : {'Authorization' : idJwt },
    success : function(response) {
        console.log('fileKey: ' + fileKey);
        callback(response);
    },
    error : function(response) {
        console.log("could not retrieve analysis report.");
        if (response.status == "401") {
        }
    }
    });
}

function uploadImage(){
    var filesToUp = document.getElementById('fileinput').files;

    if (!filesToUp.length) {
        alert("You need to choose a file to upload.");   
    }
    else{
        var file = filesToUp[0];
        var legacyFileName = file.name;
        var fileExtension = legacyFileName.split(".")[1];
        var fileKey = createUuid() + "." + fileExtension

        var sizeInKB = file.size/1024;
        console.log('uploading a file of ' +  sizeInKB)
        if (sizeInKB > 10240) {
            alert("File size exceeds the limit of 10MB.");
        }
        else{
            AWS.config.update({
                region: awsRegion,
                credentials: new AWS.CognitoIdentityCredentials({
                    IdentityPoolId: identityPoolId
                })
            });
            var s3 = new AWS.S3({
                apiVersion: '2006-03-01',
                params: {Bucket: bucketName}
            });
            var params = {
                Key: fileKey,
                Body: file,
                ACL: 'public-read'
            };
            s3.upload(params, function(err, data) {
                if (err) {
                    console.log(err, err.stack);
                    alert("Failed to upload file ");
                } else {
                    console.log('file uploaded');
                    localStorage.setItem('fileKey', fileKey);
                    showTimerForm();
                    hideAddFilesForm();
                }
            })
        } 
    }    
}

function applyAnalysisScope(imageData) {
    analysisScope.imageData = imageData;
    analysisScope.$apply();
}

