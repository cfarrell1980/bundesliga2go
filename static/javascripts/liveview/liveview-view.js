//INIT FUNCTION
jQuery(document).ready(function() {
  //CHECK ONLINE/OFFLINE
  index();
 
  
  jQuery('#reset').click(function () {
    sessionStorage.removeItem("matches");
    location.reload();
  });
 
  var timer = null; 
  var active = false;
  
  jQuery('#ticker').live('click', function () {
    var button = jQuery(this).parent().find('span.ui-btn-text');
    var header = jQuery('#header');
    
    if(active == false) {
      button.text("Stop auto mode");
//      header.css('background', 'green');
      header.addClass('green');

      timer = setInterval(update, 5000);
      active = true;
      
    } else {
      button.text("Auto");
//      header.css('background', '#252525');
      header.removeClass('green');
      jQuery(this).removeClass('ui-btn-active');
      clearInterval(timer);
      active = false;
    }
  });
  
  $('a.play').click(function(){
    console.log("click")
    $('embed').remove();
    $('body').append('<embed src="/static/sound/goal.ogg" autostart="true" hidden="true" loop="false">');
  });


//  var audioElement = document.createElement('audio');
//	audioElement.setAttribute('src', '../sound/goal.wav');
//	audioElement.load()
//	audioElement.addEventListener("load", function() { 
//		audioElement.play(); 
//		$(".duration span").html(audioElement.duration);
//		$(".filename span").html(audioElement.src);
//	}, true);
  
});

function renderIndex(data) {
  console.log("**** VIEW: INDEX " + data + " ****");

  var list = $("#matches");
  list.empty();
  
  matches = data;

  for(i=0; i< data.length; i++) {
    var icon1 = "<span class='icon icon-" + data[i].team1shortcut + "'></span>";
    var icon2 = "<span class='icon icon-" + data[i].team2shortcut + "'></span>";
    
    list.append("<li class='match container_12' style='text-align:center;'>" + 
      "<span class='grid_5'>" + icon1 + data[i].team1shortcut + "</span>" + 
      "<span class='grid_2 text20'>" + data[i].team1score + " : " +  data[i].team2score + "</span> " + 
      "<span class='grid_5'>" + data[i].team2shortcut + icon2 + "</span>" + 
    "</li>");
  }
}



