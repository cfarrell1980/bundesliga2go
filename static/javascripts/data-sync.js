// var teamsURL = 'http://paddy.suse.de:8080/getTeams';
// var indexURL = 'http://paddy.suse.de:8080/v2';

var teamsURL = 'http://10.10.100.148:8080/getTeams';
var indexURL = 'http://10.10.100.148:8080/v2';
// 
// var teamsURL = 'http://dell:8080/getTeams';
// var indexURL = 'http://dell:8080/v2';

function firstRun(mday) {
//   localStorage.clear();
//   log("Param " + mday)
  
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
      
//       var worker = chrome.extension.getURL("web_worker.js"); 
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
  
  
//   if(typeof(Worker) == 'undefined') {
    console.log("GET INDEX: AJAX call in main thread");
    console.log("Call url " + indexURL + " with param " + matchday);
    XHRRequest('index', indexURL, matchday);
//   } else {
//     console.log("GET INDEX: AJAX call through Web Workers");
//     console.log("Call url " + indexURL + " with param " + matchday);
//     
//     var worker = new Worker("/static/javascripts/worker.js");
//     worker.postMessage({'get': 'index', 'url':indexURL, 'params': matchday});
//     
//     worker.onmessage = function(event) {
//       if(event.data != "wait") {
//         console.log("Got from Paddy");
//         console.log(event.data)
//         saveIndex(event.data);
//       }
//     };
//   }
}

