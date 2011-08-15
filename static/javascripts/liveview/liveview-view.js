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
      button.text("Stop");
      header.css('background', 'green');

      timer = setInterval(update, 1000);
      active = true;
      
    } else {
      button.text("Start");
      header.css('background', '#252525');

      clearInterval(timer);
      active = false;
    }
  });
  
});

function renderIndex(data) {
  console.log("**** VIEW: INDEX " + data + " ****");

  var list = $("#matches");
  list.empty();
  
  matches = data;

  for(i=0; i< matches.length; i++) {
    console.log(match.find(matches[i]));
    list.append("<li>"+ matches[i] +"</li>");
  }
}
