//INIT FUNCTION
jQuery(document).ready(function() {
  //CHECK ONLINE/OFFLINE
  if(navigator.onLine) {
    index();
  } else {
    jQuery('#matches').html("SORRY YOU ARE OFFLINE !!!");
  }
  
  jQuery('#reset').click(function () {
    sessionStorage.removeItem("matches");
    location.reload();
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
  
// list.listview('refresh');
  
//  if(!synced) { save(matches); }
}
