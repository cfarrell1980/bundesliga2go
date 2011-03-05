function indexPage(cmd) {
  matches = getMatches(cmd);
  
  var content = '';
  for(var i=0; i<matches.length; i++) {
    match = getMatchByID(matches[i]);
    team1 = getTeamByID(match.idt1);
    team2 = getTeamByID(match.idt2);
    
    initMatchPage(matches[i], match, team1, team2);
    
    content += '<li data-icon="false"><a href="' + matches[i] + '" id=' + matches[i] + ' data-theme="c" class="match">';
      content += '<div class="container_12">';
      content += '<div class="grid_5 text-left">' + 
        '<span class="icon icon-' + team1.icon.split('/').pop().split('.').shift() + '"></span>' + team1.short +'</div>';
      content += '<div class="grid_2 text-center">' + match.gt1.length + ':' + match.gt2.length + '</div>';
      content += '<div class="grid_5 text-right">' + 
        team2.short +  '<span class="icon icon-' + team2.icon.split('/').pop().split('.').shift() + '"></span></div>';
      content += '</div>';
    content += '</a></li>';  
  }
  
  jQuery('#cmd').text('Spieltag ' + cmd);
  jQuery('#list').html(content).page();
  jQuery('#list').listview('refresh', true);
  
  jQuery('#list').find('img.ui-li-thumb').removeClass('ui-li-thumb');
  jQuery('#list').find('span.ui-icon-arrow-r').remove();
  
      
}

function initMatchPage(matchID, match, team1, team2) {
 
//   matchPage =  '<div data-role="page" data-theme="c" id="' + matchID + '">';
//     matchPage += '<div data-role="header"><h2>Spiel: ' + matchID + '</h2></div>';  
//     
//     matchPage += '<div id="list' + matchID + '" data-role="content" class="ui-body">';
//       matchPage += '<div>Datum: ' + match.st.split('T')[0] + ' Zeit: ' +  match.st.split('T')[1] + '</div>';
// 
//       matchPage += '<div class="container_12">';
//         matchPage += '<div class="grid_12 text-center">' + team1.name + ' vs ' + team2.name + '</div>';
//         
//         matchPage += '<div class="grid_6 text-left">';
//           matchPage += '<span class="grid_2 left">ICON</span>';
//           matchPage += '<span class="grid_4 right text-right margin-right5">' + team1.short + '</span>';
//         matchPage += '</div>';
//       
//         matchPage += '<div class="grid_6 text-right">';
//           matchPage += '<span class="grid_4 left text-left margin-left5">' + team2.short + '</span>';
//           matchPage += '<span class="grid_2 right margin-left5" style="float:right">ICON</span>';
//         matchPage += '</div>'
//       
//         matchPage += '<div class="grid_6 text-left">';
//           matchPage += '<span class="grid_4 left text-left ">Scorer</span>';
//           matchPage += '<span class="grid_2 right text-right margin-right5">Goal</span>';
//         matchPage += '</div>';
//       
//         matchPage += '<div class="grid_6 text-left">';
//           matchPage += '<span class="grid_2 left text-left margin-left5">Goal</span>';
//           matchPage += '<span class="grid_4 right text-right">Scorer</span>';
//         matchPage += '</div>';
//         
//     matchPage += '</div>';
//   matchPage += '</div>';
  
  matchPage =  '<div data-role="page" data-theme="c" id="' + matchID + '">';
  matchPage += '<div data-role="header"><h1>' + team1.short + ' vs ' + team2.short +'</h1></div>';
  matchPage += '<div data-role="content">';
    matchPage += '<ul data-role="listview">';
    matchPage += '<li>Datum: ' + match.st.split('T')[0] + ' ' + match.st.split('T')[1] + '</li>';
      matchPage += '<li class="container_12">';
        matchPage += '<span class="grid_6 left text-left">' + team1.short + '</span>';
        matchPage += '<span class="grid_6 right text-right">' + team2.short +'</span>';
      matchPage +='</li>';
      matchPage += '<li class="container_12">';
      
      if(match.gt1.length == match.gt2.length) {
        for(var i=0; i<match.gt1.length; i++) {
//           matchPage += '<span class="grid_6 left text-left">' + match.gt1[i].s + '</span>';
//           matchPage += '<span class="grid_6 right text-right">' + match.gt2[i].s + '</span>';
          
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
    matchPage += '</ul>';
  matchPage += '</div>';
  matchPage += '<div data-role="footer">Header</div>';
  $(matchPage).insertAfter('#home').page();
}



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
