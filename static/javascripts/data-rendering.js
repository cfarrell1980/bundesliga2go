function indexPage(matchday) {
  log("Render Index for: " + matchday);
  
  //var activeMatches = getActive();
  
  if(matchday == '#') matchday = localStorage.getItem('cmd');
  jQuery('#cmd').text('Spieltag ' + matchday);
  
  matches = getMatches(matchday);

  if(matches !== null) {
    var content = '';
    for(var i=0; i<matches.length; i++) {
      match = getMatchByID(matches[i]);
      team1 = getTeamByID(match.idt1);
      team2 = getTeamByID(match.idt2);
      
      initMatchPage(matches[i], match, team1, team2);
      
      content += '<li data-icon="false"><a href="' + matches[i] + '" id=' + matches[i] + ' data-theme="c" class="match">';
        content += '<span class="container_12" style="vertical-align:middle;">';
        content += '<span class="grid_5 text-left">' + 
//          '<span class="icon icon-' + team1.icon.split('/').pop().split('.').shift() + '"></span>' + team1.short +'</span>';
          '<span class="icon icon-' + team1.short + '"></span>' + team1.short +'</span>';
        content += '<span class="grid_2 text-center points">' + match.gt1.length + ':' + match.gt2.length + '</span>';
        content += '<span class="grid_5 text-right">' + 
//          team2.short +  '<span class="icon icon-' + team2.icon.split('/').pop().split('.').shift() + '"></span></span>';
          team2.short +  '<span class="icon icon-' + team2.short + '"></span></span>';
        content += '</span>';
      content += '</a></li>';  
    }
    
    jQuery('#list').html(content).page();
    jQuery('#list').listview('refresh', true);
    
    jQuery('#list').find('img.ui-li-thumb').removeClass('ui-li-thumb');
    jQuery('#list').find('span.ui-icon-arrow-r').remove();
  } else {
    jQuery('#list').html('<li>Can not render Index page for ' + matchday +' </li>');
      
  }
}

function initMatchPage(matchID, match, team1, team2) {
  matchPage =  '<div class="matchPage" data-role="page" id="' + matchID + '">';
  matchPage += '<div data-role="header"><h1>' + team1.short + ' vs ' + team2.short +'</h1></div>';
  matchPage += '<div data-role="content">';
    matchPage += '<ul data-role="listview">';
    matchPage += '<li>Datum: ' + match.st.split('T')[0] + ' ' + match.st.split('T')[1] + '</li>';
      matchPage += '<li class="container_12">';
        matchPage += '<span class="grid_5 left text-left">' + team1.short /*+ '<span class="right">' +  match.gt1.length + '</span>'*/ + '</span>';
	matchPage += '<span class="grid_2 text-center points-big">' + '<span>' +  match.gt1.length + '</span>' + ':' + '<span>' +  match.gt2.length + '</span>' + '</span>';
        matchPage += '<span class="grid_5 right text-right">' + team2.short/* + '<span class="left">:' +  match.gt2.length + '</span>'*/ + '</span>';
      matchPage +='</li>';
      matchPage += '<li class="container_12">';
      
      if(match.gt1.length == match.gt2.length) {
        for(var i=0; i<match.gt1.length; i++) {
          matchPage += '<span class="grid_6 left text-left">';
            matchPage += '<span class="left">' + match.gt1[i].s + '</span>';
            matchPage += '<span class="right margin-right10">' +  match.gt1[i].m + '\"</span>';
          matchPage += '</span>';
          
          matchPage += '<span class="grid_6 right text-right">';
            matchPage += '<span class="left margin-left10">' +  match.gt2[i].m + '\"</span>';
            matchPage += '<span class="right">' + match.gt2[i].s + '</span>';
          matchPage += '</span>';
        }
      } else {
        var counter=0;
        match.gt1.length < match.gt2.length? counter = match.gt2.length : counter = match.gt1.length

        var tmp = 0;
        for(var j=0; j<counter; j++) {
          match.gt1? tmp = match.gt1: tmp=0;
          
          if(match.gt1[j]) {
            matchPage += '<span class="grid_6 left text-left">';
              matchPage += '<span class="left">' + match.gt1[j].s + '</span>';
              matchPage += '<span class="right margin-right10">' +  match.gt1[j].m + '\"</span>';
            matchPage += '</span>';
          } else {
            matchPage += '<span class="grid_6 left text-left">';
              matchPage += '<span class="left">--</span>';
              matchPage += '<span class="right margin-right10">--</span>';
            matchPage += '</span>';
          }
          
          if(match.gt2[j]) {
            matchPage += '<span class="grid_6 right text-right">';
              matchPage += '<span class="left margin-left10">' +  match.gt2[j].m + '\"</span>';
              matchPage += '<span class="right">' + match.gt2[j].s + '</span>';
            matchPage += '</span>';
          } else {
            matchPage += '<span class="grid_6 right text-right">';
              matchPage += '<span class="left margin-left10">--</span>';
              matchPage += '<span class="right">--</span>';
            matchPage += '</span>';
          }
        }
      }
      
      matchPage +='</li>';
      matchPage +='<li style="text-align:center;">&nbsp;</li>';
//       matchPage +='<hr/>';
//       matchPage +='<li style="text-align:center;"><hr/>/*</li>*/';
    matchPage += '</ul>';
  matchPage += '</div>';
  matchPage += '<div data-role="footer">Footer</div>';
  $(matchPage).insertAfter('#home').page();
}



hideSpinner = function(){
  jQuery.mobile.pageLoading(true);
}
  
jQuery(document).ready(function() {
  jQuery('li.ui-btn').bind("click", function(){
    
  });
//   document.ontouchmove = function(event) {
//     event.preventDefault();
//   };

  
  jQuery('#prev').bind("click", function(){
    var $cmd = jQuery('#cmd').text().split(' ')[1];
    $cmd = parseInt($cmd)-1;
//     jQuery('#cmd').text('Spieltag ' + $cmd);
    console.log("Switch to " + $cmd)
    
    jQuery.mobile.pageLoading();
    setTimeout(hideSpinner,500);
    firstRun($cmd);
    return false;
  });
  
  jQuery('#next').bind("click", function(){
    var $cmd = jQuery('#cmd').text().split(' ')[1];
    $cmd = parseInt($cmd)+1;
//     jQuery('#cmd').text('Spielzag ' + $cmd);
    console.log("Switch to " + $cmd)
    
    jQuery.mobile.pageLoading();
    setTimeout(hideSpinner,500);
    firstRun($cmd);
    return false;
  }); 
  
  jQuery('#home').bind("swiperight", function(){
    var $cmd = jQuery('#cmd').text().split(' ')[1];
    $cmd = parseInt($cmd)-1;
//     jQuery('#cmd').text('Spielzag ' + $cmd);
    console.log("Switch to " + $cmd)
    
    jQuery.mobile.pageLoading();
    setTimeout(hideSpinner,500);
    firstRun($cmd);
    return false;
  });
  
  jQuery('#home').bind("swipeleft", function(){
    var $cmd = jQuery('#cmd').text().split(' ')[1];
    $cmd = parseInt($cmd)+1;
//     jQuery('#cmd').text('Spielzag ' + $cmd);
    console.log("Switch to " + $cmd)
    
    jQuery.mobile.pageLoading();
    setTimeout(hideSpinner,500);
    firstRun($cmd);
    return false;
  });
});


// function hideLoading(){
//   jQuery.mobile.pageLoading(true);
// }

// //TODO: Investigate page loading issue --> jQuery.mobile.pageLoading(true);
// function initNavbar() {
//   var id = ['#prevMatchday', '#nextMatchday'];
//   var matchday;
//   
//   for (var i in id) {
//     jQuery(id[i]).live('click tap', function(event) {
//       matchday = parseInt(jQuery('#navbar>h2').text());
//       //TODO: if matchday > 34 switch to next season
//       (jQuery(this).attr('id') == 'nextMatchday') ? matchday++ : matchday--;
//       renderMatchDay(matchday, getMatchesByMatchdayID(matchday));
//       jQuery.mobile.pageLoading();
//       setTimeout("hideLoading()",500);
//       return false;
//     });
//   }
// }
