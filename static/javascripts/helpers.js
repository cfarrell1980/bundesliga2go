function navbarMatchDay(matchdayID) {
  if(typeof matchdayID == 'undefined')  {
    $('#navbar').html('<p class="error">ERROR: Can not render nav bar</p>');  
  } else {
    var content =  '<h2 class="ui-title" tabindex="0" role="heading" aria-level="1"><span>' + matchdayID + '</span>. Spieltag' + '</h2>' +
    '<a href="#" id="prevMatchday" class="ui-btn-left ui-btn ui-btn-corner-all ui-shadow ui-btn-up-c">' +
    '<span class="ui-btn-inner ui-btn-corner-all">' +
    '<span class="ui-btn-text">' +
    '<img class="" src="static/css/images/arrow-left.png" style="height:16px; vertical-align:middle;">' +
    '</span>' +
    '</span>' +
    '</a>' +
    '<a href="#" id="nextMatchday" class="ui-btn-right ui-btn ui-btn-corner-all ui-shadow ui-btn-up-c">' +
    '<span class="ui-btn-inner ui-btn-corner-all">' +
    '<span class="ui-btn-text">' +
    '<img class="" src="static/css/images/arrow-right.png" style="height:16px; vertical-align:middle;">' +
    '</span>' +
    '</span>' + 
    '</a>' ;
    
    $('#navbar').html(content);
  }
}

function checkPoints(finished, points, team) {
  if(finished) { 
    if(team == 'team1') {
      return '<span class="right">' + points + '</span>';
    } else {
      return '<span class="left">:' + points + '</span>';
    }
  } else { 
    if(team == 'team2') {
      return '<span class="left color-grey">:0</span>'; 
    } else {
      return '<span class="right color-grey">0</span>'; 
    }
    
  }
}

function renderMatchDay(matchdayID, matches) {
  navbarMatchDay(matchdayID);
  var list = '';
  var t1, t2, match;
  
  for (var i=0; i<matches.length; i++) {
    t1 = getTeamDataByTeamID(getTeamsForMatch(matches[i])[0]);
    t2 = getTeamDataByTeamID(getTeamsForMatch(matches[i])[1]);
    match = getMatchByID(matches[i]);
    
    list += '<li>' +
    '<a class="match_link" href="' + matches[i] + '">' +
    '<span class="leftSpan">' +
    '<img class="game" src="static/logos/' + t1.icon.split('/').pop() + '">' +
    '&nbsp;<span class="game_text">'+ t1.short + '</span>' +	
      checkPoints(match.fin, match.pt1, 'team1') +
    '</span>' + 
    '<span class="rightSpan">' +
      checkPoints(match.fin, match.pt2, 'team2') +
    '<span class="game_text">'+ t2.short + '</span>' + 
    '<img class="game" src="static/logos/' + t2.icon.split('/').pop() + '">' +
    '</span>' +
    '</a>' +
    '</li>';
    
    renderGames(matches[i], match, t1, t2);        
  }
  
  $('#list').html(list).listview('refresh');    
  $('#list').find('img.ui-li-thumb').removeClass('ui-li-thumb');
  $('#list').find('span.ui-icon-arrow-r').remove();
  $('#list' + matches[i]).listview('refresh');    
}

function renderGames(matchID, match, t1, t2) {
  var games='';
  games +='<div data-role="page" id="' + matchID + '">' +
	    '<div data-role="header">' +
	      '<h2>' + t1.short + ' vs ' + t2.short +'</h2>' +
	      '<a href="#home" class="ui-btn-left" data-icon="arrow-l">zuück</a>' +
	    '</div>' +
	    
	    '<div data-role="content" class="ui-body">' +
	      '<ul id="list' + matchID + '" data-role="listview" role="listbox" data-theme="c" ata-dividertheme="b" data-inset="true">' +
	      '<li>POINTS:</li>' +
	      '<li>' +
	      '<img class="game" src="static/logos/' + t1.icon.split('/').pop() + '">' + t1.short + 
	      '<span style="float:right;">' + match.pt1 + '</span>' +
	      '</li>' +
	      '<li>' +
	      '<img class="game" src="static/logos/' + t2.icon.split('/').pop() + '">' + t2.short + 
	      '<span style="float:right;">' + match.pt2 + '</span>' +
	      '</li>' +
	      '</ul>' +
	    '</div>' +
	    '<div id="homeFooter" data-role="footer"><h2>FOOTER</h2></div>' +
	  '</div>';

  $(games).insertAfter('#home');
  $('#'+matchID).hide();
}

function loading(){
  jQuery.mobile.pageLoading(true);
}

//TODO: Investigate page loading issue --> jQuery.mobile.pageLoading(true);
function initNavbar() {
  var id = ['#prevMatchday', '#nextMatchday'];
  var matchday;
  
  for (var i in id) {
    jQuery(id[i]).live('click tap', function(event) {
    matchday = parseInt(jQuery('#navbar>h2').text());
    //TODO: if matchday > 34 switch to next season
    (jQuery(this).attr('id') == 'nextMatchday') ? matchday++ : matchday--;
    renderMatchDay(matchday, getMatchesByMatchdayID(matchday));
    return false;
    });
  }
}