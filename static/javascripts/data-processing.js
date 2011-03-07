var DEBUG = true;
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
  console.log("SAVE TEAMS DATA FROM SERVER")
  
  var teams = new Array();
  objects = JSON.parse(data);
  
  for(var id in objects.teams) {
    teams.push(id);
    localStorage.setItem('team'+id, JSON.stringify(objects.teams[id]));
  }  
  
  localStorage.setItem('teams', JSON.stringify(teams));
  localStorage.setItem('teams-synced', 'true');
}


//SAVE ALL DATA FROM SERVER
function saveIndex(data) {
  console.log("DEBUG: SAVE INDEX DATA");
  var matchday = JSON.parse(data);
  
  localStorage.setItem('cmd', matchday.cmd);
  localStorage.setItem(matchday.cmd, JSON.stringify(matchday.meta.idx));
  
  for(var id in matchday.md) {
    localStorage.setItem(id, JSON.stringify(matchday.md[id]));
  }
  
//   jQuery('#cmd').text('Spieltag ' + matchday.cmd);
  indexPage(matchday.cmd);
}


function getMatches(cmd) {
  return JSON.parse(localStorage.getItem(cmd));
}

function getMatchByID(id) {
  return JSON.parse(localStorage.getItem(id));
}

function getTeamByID(id) {
  return JSON.parse(localStorage.getItem('team' + id));
}
