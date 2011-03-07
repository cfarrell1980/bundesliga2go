var teamsURL = 'http://paddy.suse.de:8080/getTeams';
var indexURL = 'http://paddy.suse.de:8080/v2';
// 
// var teamsURL = 'http://dell:8080/getTeams';
// var indexURL = 'http://dell:8080/v2';

function firstRun(matchday) {
  if(localStorage.getItem(matchday) === null || typeof(localStorage.getItem(matchday)) == 'undefined') {
    log("Performe init sync!")
//     jQuery('#cmd').text('Spieltag ' + matchday);
    matchday? prepareIndex(matchday) : prepareIndex('#');
  } else {
    log("Read from LS! " + localStorage.getItem("cmd"))
    jQuery('#cmd').text('Spieltag ' + localStorage.getItem("cmd"));
    matchday? indexPage(matchday) : indexPage(localStorage.getItem("cmd"));
  }
}

//GET TEAMS DATA FROM SERVER
function prepareIndex(matchday) {
  if(typeof(Worker) == 'undefined') {
    log("TEAMS: AJAX call in main thread");
    XHRRequest('teams', teamsURL, '#');
  } else {
    log("TEAMS: AJAX call through Web Workers");
    var worker = new Worker("/static/javascripts/worker.js");
    worker.postMessage({'get': 'teams', 'url':teamsURL, 'params': '#'});
    
    worker.onmessage = function(event) {
      if(event.data != "wait") {
        index(event.data, matchday);
      } 
    };
  }
}

function index(data, matchday) {
  saveTeams(data);
  
  if(typeof(Worker) == 'undefined') {
    log("INDEX: AJAX call in main thread");
//     console.log("Set matchday " + matchday)
//     jQuery('#cmd').text('Spieltag ' + matchday);
    XHRRequest('index', indexURL, matchday);
  } else {
    log("INDEX: Web Workers)");
    var worker = new Worker("/static/javascripts/worker.js");
    worker.postMessage({'get': 'index', 'url':indexURL, 'params': matchday});
    
    worker.onmessage = function(event) {
      if(event.data != "wait") {
//         jQuery('#cmd').text('Spieltag ' + matchday);
        saveIndex(event.data);
      }
    };
  }
}

