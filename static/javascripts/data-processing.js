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

//SAVE TEAMS DATA FROM SERVER
function saveTeams(data) {
  log("DEBUG: SAVE TEAMS DATA");
  console.log(data.cmd);
  
  var teams = new Array();
  localStorage.setItem('cmd',data['cmd']);
  
  for(var id in data['teams']) {
    teams.push(data['teams'][id]);
    localStorage.setItem('team'+id,JSON.stringify(data['teams'][id]));
  }  
  
//   localStorage.setItem('teams-synced', 'true');
  localStorage.setItem('teams', JSON.stringify(teams));
}

//SAVE ALL DATA FROM SERVER
function saveData(data) {
  log("DEBUG: SAVE ALL DATA");
  if(data.cmd) {
    for(var matchdayID in data.matchdays) {
      localStorage.setItem('lastKnownMatchday', JSON.stringify(data.cmd));
//       localStorage.setItem('data-synced', 'true');
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
  
  log("DEBUG: RENDER MACTH DAY");
  renderMatchDay(data.cmd, getMatchesByMatchdayID(data.cmd));
}

function saveGoals(data) {
  log("DEBUG: SAVE GOALS DATA");
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
  
  log("Set goals to synced and perform page reload!");
  localStorage.setItem('goals-synced', 'true');
  jQuery.mobile.pageLoading();
  setTimeout("hideLoading()",1000);
  location.reload();
}

function getMatchesByMatchdayID(id) {
  //log("INFO: GET TEAMS BY MATCHDAYID " + id);
  return JSON.parse(localStorage.getItem('matchday'+id));
}

function getMatchByID(id) {
  //log("INFO: GET TEAMS BY MATCH ID " + id);
  return JSON.parse(localStorage.getItem('match'+id));
}
 
function getTeamsForMatch(id) {
    var temp = JSON.parse(localStorage.getItem('match' + id));
    var teams  = [];
    teams.push(temp.t1);
    teams.push(temp.t2);
    return teams;
}

function getTeamDataByTeamID(id) {
  //log("INFO: GET TEAM DATA BY TEAM ID " + id);
  return JSON.parse(localStorage.getItem('team' + id));
}

function getGoalsByMatchID(id) {
//   log("INFO: GET GOALS DATA BY MATCH ID " + 'goal' + id);
  if('goal' + id in localStorage) {
    return JSON.parse(localStorage.getItem('goal' + id));
  } else {
    return false;
  }
}

function getGoalObjectByID(id) {
//   log("INFO: GET GOAL BY ID " + 'goalobject' + id);
  return JSON.parse(localStorage.getItem('goalobject' + id));
}
