jQuery(document).ready(function() {
  //localStorage.clear();
//   console.log("ss")
  initNavbar();
//   jQuery('a.back').live('click', function() {
//     console.log("GO BACK");
    //jQuery.mobile.changePage(jQuery('#home'));
//   });      
  
  if(localStorage['lastKnownMatchday']) {
    log("Safari LS")
    var cmd = localStorage['lastKnownMatchday'];
    renderMatchDay(cmd, getMatchesByMatchdayID(cmd));
  } else {
    log("Safari GD")
    getTeamsData();
  }
});
