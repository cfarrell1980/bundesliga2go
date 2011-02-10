var DEBUG = true;
//LOGGER
function log(object, inspect) {
  if(DEBUG) { 
    var now = new Date();
    if(typeof(object) === 'string') {
      console.log(now.getHours() + ':' + now.getMinutes() + ':' + now.getSeconds() + ' '+ object);
    } else {
      console.log(now.getHours() + ':' + now.getMinutes() + ':' + now.getSeconds() + ' ' + 'RETURNS: ' + object);
      console.log('------------------------------------------');
    }
  }
}

//TODO: Replace the jsonp call with CORS ajax call

//DON'T FORGET TO CHANGE THE URL!!!

var teamsURL = 'http://192.168.178.35:8080/getTeams'
var dataURL= 'http://192.168.178.35:8080/getData'

//GET TEAMS DATA FROM SERVER
function getTeamsData() {
  console.log("DON'T FORGET TO CHANGE THE URL!!!");
  log("DEBUG: GET TEAMS FROM");
  $.ajax({
    url: teamsURL,
    cache: false,
    async: false,
    dataType: 'jsonp',
    success: getAllData
  });
}

//GET ALL DATA FROM SERVER
function getAllData(data) {
  saveTeams(data)
  log("DEBUG: GET ALL DATA FROM");
  $.ajax({
    url: dataURL,
//     cache: false,
//     async: false,
    dataType: 'jsonp',
    success: saveData
  });
}

//SAVE TEAMS DATA FROM SERVER
function saveTeams(data) {
  log("DEBUG: SAVE TEAMS DATA");
  var teams = new Array();
  for(var id in data) {
    teams.push(id);
    for(var value in data[id]) {
      localStorage.setItem('team'+id, JSON.stringify(data[id]));
    }
  }  
  localStorage.setItem('teams', JSON.stringify(teams));
}

//SAVE ALL DATA FROM SERVER
function saveData(data) {
  log("DEBUG: SAVE ALL DATA");
  if(data.cmd) {
    for(var matchdayID in data.matchdays) {
      localStorage.setItem('lastKnownMatchday', JSON.stringify(data.cmd));
    }
  }
  
  if(data.matchdays) {
    for(var matchdayID in data.matchdays) {
      localStorage.setItem('matchday'+matchdayID, JSON.stringify(data.matchdays[matchdayID]));
    }
  }
  
  if(data.matches) {
    for(var matchID in data.matches) {
      localStorage.setItem('match'+matchID, JSON.stringify(data.matches[matchID]));
    }
  }
  
  if(data.goalindex) {
    for(var matchID in data.goalindex) {
      localStorage.setItem('goal'+matchID, JSON.stringify(data.goalindex[matchID]));
    }
  }
  
  if(data.goalobjects) {
    for(var goalID in data.goalobjects) {
      localStorage.setItem('goalobject'+goalID, JSON.stringify(data.goalobjects[goalID]));
    }
  }

  renderMatchDay(data.cmd, getMatchesByMatchdayID(data.cmd));
}

//GET UPDATES FROM SERVER
function getUpdates(url, tstamp) {
  log("DEBUG: GET UPDATES FROM " + url + " FOR TIMESTAMP " + tstamp);
  $.ajax({
    url: url,
	 dataType: 'jsonp',
	 data: 'tstamp=' + tstamp,
	 success: saveUpdates
  });
}

//SAVE UPDATES FROM SERVER
function saveUpdates(data) {
  log("DEBUG: SAVE UPDATES");
}

function getMatchesByMatchdayID(id) {
  log("INFO: GET TEAMS BY MATCHDAYID " + id);
  return JSON.parse(localStorage.getItem('matchday'+id));
}

function getMatchByID(id) {
  log("INFO: GET TEAMS BY MATCH ID " + id);
  return JSON.parse(localStorage.getItem('match'+id));
}
 
function getTeamsForMatch(id) {
  log("INFO: GET TEAMS BY MATCHDAYID " + id);
  try {
    var temp = JSON.parse(localStorage.getItem('match' + id));
    var teams  = [];
    teams.push(temp.t1);
    teams.push(temp.t2);
    return teams;
  } catch(err) {
    log("ERROR: " + err);
  }
}

function getTeamDataByTeamID(id) {
  log("INFO: GET TEAM DATA BY TEAM ID " + id);
  return JSON.parse(localStorage.getItem('team' + id));
}