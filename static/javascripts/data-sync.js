var teamsURL = 'http://foxhall.de:8081/getTeams';
var indexURL = 'http://foxhall.de:8081/v2';

function firstRun(mday) {
  mday == '#'? matchday=localStorage.getItem('cmd') : matchday=localStorage.getItem(mday);

  if(matchday == null || typeof(matchday) === 'undefined') {
    log("Performe init sync, LS is empty!")
    prepareIndex(mday);
  } else {
    log("Read matchday " + mday + " from LS!")
    indexPage(mday);
  }
}

//GET TEAMS DATA FROM SERVER
function prepareIndex(matchday) {
  console.log("Send request with param " + matchday)
  if(localStorage.getItem('teams-synced')) {
    log("TEAMS already synced! continue with index(" + matchday + ")");
    index('#', matchday)
  } else {
    if(typeof(Worker) == 'undefined') {
      console.log("GET TEAMS: AJAX call in main thread");
      XHRRequest('teams', teamsURL, '#');
    } else {
      console.log("GET TEAMS: AJAX call through Web Workers");
      var worker = new Worker("/static/javascripts/worker.js");
      worker.postMessage({'get': 'teams', 'url':teamsURL, 'params': '#'});
      
      worker.onmessage = function(event) {
        if(event.data != "wait") {
          index(event.data, matchday);
        } 
      };
    }
  }
}

function index(data, matchday) {
  if(data!='#') { saveTeams(data) }

  if(typeof(Worker) == 'undefined') {
    console.log("GET INDEX: AJAX call in main thread");
    console.log("Call url " + indexURL + " with param " + matchday);
    XHRRequest('index', indexURL, matchday);
  } else {
    console.log("GET INDEX: AJAX call through Web Workers");
    console.log("Call url " + indexURL + " with param " + matchday);
    
    var worker = new Worker("/static/javascripts/worker.js");
    worker.postMessage({'get': 'index', 'url':indexURL, 'params': matchday});
    
    worker.onmessage = function(event) {
      if(event.data != "wait") {
        saveIndex(event.data);
      }
    };
  }
}

var activeURL = "http://foxhall.de:8081/active?tester=2011-08-06-16-00"

function getActive() {
  if(typeof(Worker) == 'undefined') {
    console.log("GET ACTIVE MATCHES: AJAX call in main thread");
    console.log("Call url " + activeURL);
    XHRRequest('', activeURL, 'active');
  } else {
    console.log("GET ACTIVE MATCHES: AJAX call through Web Workers");
    console.log("Call url " + activeURL);
    
    var worker = new Worker("/static/javascripts/worker.js");
    worker.postMessage({'params' : 'active', 'url':activeURL});
    
    worker.onmessage = function(event) {
      if(event.data != "wait") {
        saveIndex(event.data);
      }
    };
  }
}

