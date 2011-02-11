var DEBUG = true;
var teamsURL = 'http://paddy.suse.de:8080/getTeams'
var dataURL= 'http://paddy.suse.de:8080/getData'

//var cmd = '20'

//localStorage.clear();



jQuery(document).ready(function() {
 //     jQuery('#clear').click(function(){
//	console.log("RESET LS")
//	localStorage.clear();
  //    });

      console.time('rebder')
      getTeams(teamsURL);
      getRemoteData(dataURL);
      console.log("Getting cmd from localstorage");
      var cmd = localStorage.getItem('cmd');
      console.log("Done... cmd is"+cmd+"!");
      renderMatchDay(cmd, getMatchesByMatchdayID(cmd));
      console.timeEnd('rebder')
    });
