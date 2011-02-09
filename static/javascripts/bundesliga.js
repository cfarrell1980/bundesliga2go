var DEBUG = true;
var teamsURL = 'http://paddy.suse.de:8080/getTeams'
var dataURL= 'http://paddy.suse.de:8080/getData'

var cmd = '20'

//localStorage.clear();



jQuery(document).ready(function() {
 //     jQuery('#clear').click(function(){
//	console.log("RESET LS")
//	localStorage.clear();
  //    });

      console.time('rebder')
      getTeams(teamsURL);
      getRemoteData(dataURL);
      renderMatchDay('20', getMatchesByMatchdayID('20'));
      console.timeEnd('rebder')
    });
