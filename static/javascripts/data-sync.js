//DON'T FORGET TO CHANGE THE URL!!!
var dataURL= 'http://paddy.suse.de:8080/getData';
var teamsURL = 'http://paddy.suse.de:8080/getTeams';
var goalsURL= 'http://paddy.suse.de:8080/getGoals';

// var teamsURL = 'http://192.168.178.35:8080/getTeams';
// var dataURL= 'http://192.168.178.35:8080/getData';
// var goalsURL= 'http://192.168.178.35:8080/getGoals';

//AJAX Cross Origin Ressource Sharing
function XHRRequest(url, params) {
  var xhr = new XMLHttpRequest();
  params == '#'? data = ' ' : data = params
  
  if(xhr) {    
    xhr.open('POST', url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.send(data);
    xhr.onreadystatechange = function() {
      if (xhr.readyState == 4) {
	if (xhr.status == 200) {
	  saveData(JSON.parse(xhr.responseText));
	} else {
	  return "Invocation Errors Occured";
	}
      } else {
	return xhr.readyState;
      }
    }
  }
}

//GET TEAMS DATA FROM SERVER
function getTeamsData() {
  console.log("DON'T FORGET TO CHANGE THE URL!!!");
  log("DEBUG: GET TEAMS FROM");
  $.ajax({
    url: teamsURL,
    cache: false,
    async: false,
    dataType: 'jsonp',
    success: getMatchdaysData
  });
}

function getMatchdaysData(data) {
  //TODO: remove inline CSS!!!
  $('#list').html('<li style="display:block; padding:50px 0px; text-align:center;"><img src="static/css/images/ajax-loader.png" style="vertical-align:middle"><span style=" vertical-align:middle; font-size:22px;"> loading data, please wait ...</span></li>');
  saveTeams(data)
  log("DEBUG: GET ALL DATA FROM");
  
  if(typeof(Worker) == 'undefined') {
    log("AJAX call in main thread");
    XHRRequest(dataURL, '#');
  } else {
    log("AJAX call in separate thread (Web Workers)");
    var worker = new Worker("/static/javascripts/worker.js");
    worker.postMessage({'get': 'data', 'params': '#'});
    
    worker.onmessage = function(event) {
      if(event.data != "wait") {
	log("save data from worker")
	saveData(JSON.parse(event.data));
      } else {
	log("worker said " + event.data)
      }
    };
  }
}

//GET UPDATES FROM SERVER
function getGoals(url, tstamp) {
  typeof(tstamp) != "undefined"? tstamp = tstamp : tstamp = '#';
  
  log("DEBUG: GET UPDATES FROM " + url + " FOR TIMESTAMP " + tstamp);
  if(typeof(Worker) == 'undefined') {
    log("AJAX call in main thread");
    XHRRequest(goalsURL, tstamp);
  } else {
    log("AJAX call in separate thread (Web Workers)");
    var worker = new Worker("/static/javascripts/worker.js");
    worker.postMessage({'get': 'goals', 'params': tstamp});
    
    worker.onmessage = function(event) {
      if(event.data != "wait") {
	log("save data from worker")
	saveGoals(JSON.parse(event.data));
      } else {
	log("worker said " + event.data)
      }
    };
  }
}
