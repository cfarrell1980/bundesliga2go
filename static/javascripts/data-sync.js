var teamsURL = 'http://paddy.suse.de:8080/getTeams';
var indexURL = 'http://paddy.suse.de:8080/v2?md=22';

function firstRun() {
  if (localStorage.getItem('cmd') === null || typeof(localStorage.getItem('cmd')) == 'undefined') {
    log("Performe init sync!")
    prepareIndex();
  } else {
    log("Read from LS! " + localStorage.getItem("cmd"))
    indexPage(localStorage.getItem("cmd"));
  }
}

//GET TEAMS DATA FROM SERVER
function prepareIndex() {
  if(typeof(Worker) == 'undefined') {
    log("TEAMS: AJAX call in main thread");
    XHRRequest('teams', teamsURL, '#');
  } else {
    log("TEAMS: AJAX call through Web Workers");
    var worker = new Worker("/static/javascripts/worker.js");
    worker.postMessage({'get': 'teams', 'url':teamsURL, 'params': '#'});
    
    worker.onmessage = function(event) {
      if(event.data != "wait") {
        index(event.data);
      } 
    };
  }
}

function index(data) {
  saveTeams(data);
  
  if(typeof(Worker) == 'undefined') {
    log("INDEX: AJAX call in main thread");
    XHRRequest('index', indexURL, '#');
  } else {
    log("INDEX: Web Workers)");
    var worker = new Worker("/static/javascripts/worker.js");
    worker.postMessage({'get': 'index', 'url':indexURL, 'params': '#'});
    
    worker.onmessage = function(event) {
      if(event.data != "wait") {
        saveIndex(event.data);
      }
    };
  }
}

