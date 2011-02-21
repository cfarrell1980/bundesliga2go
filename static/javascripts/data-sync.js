//DON'T FORGET TO CHANGE THE URL!!!
var teamsURL = 'http://paddy.suse.de:8080/getTeams';


// var teamsURL = 'http://192.168.178.35:8080/getTeams';
// var dataURL= 'http://192.168.178.35:8080/getData';
// var goalsURL= 'http://192.168.178.35:8080/getGoals';

//AJAX Cross Origin Ressource Sharing
function XHRRequest(type, params) {
  var url, params;

  var xhr = new XMLHttpRequest();
  params == '#'? data = ' ' : data = params
  
  switch (type) {
    case 'data':
      url = 'http://paddy.suse.de:8080/getData';
      break;
    case 'goals':
      url = 'http://paddy.suse.de:8080/getGoals';
      break;
    default:
      console.error('Unknown type: ' + type);
  }
  
  if(xhr) {    
    xhr.open('POST', url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.send(data);
    xhr.onreadystatechange = function() {
      if (xhr.readyState == 4) {
	if (xhr.status == 200) {
	  switch (type) {
	    case 'data':
	      saveData(JSON.parse(xhr.responseText));
	      break;
	    case 'goals':
	      saveGoals(JSON.parse(xhr.responseText));
	      break;
	    default:
	      console.error('Unknown type: ' + type);
	  }
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
    XHRRequest('data', '#');
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
function getGoals(tstamp) {
  typeof(tstamp) != "undefined"? tstamp = tstamp : tstamp = '#';
  log("DEBUG: GET GOALS FOR TIMESTAMP " + tstamp);
  
  if(typeof(Worker) == 'undefined') {
    log("AJAX call in main thread");
    XHRRequest('goals', tstamp);
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
