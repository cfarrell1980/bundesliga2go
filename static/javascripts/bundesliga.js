var DEBUG = true;
var teamsURL = 'http://paddy.suse.de:8080/getTeams'
var dataURL= 'http://paddy.suse.de:8080/getData'

// localStorage.clear();

jQuery(document).ready(function() {
  initNavbar();  
  if(localStorage['lastKnownMatchday']) {
    log("Safari LS")
    var cmd = localStorage['lastKnownMatchday'];
    renderMatchDay(cmd, getMatchesByMatchdayID(cmd));
  } else {
    log("Safari GD")
    getTeamsData();
  }
});
