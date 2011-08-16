//AJAX CALL
function XHRRequest(url, callback, params) {
  var xhr = new XMLHttpRequest();
  var methode = 'POST';
 
  if(xhr) {    
    xhr.open(methode, url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.send(params);
    
    xhr.onreadystatechange = function() {
      if (xhr.readyState == 4) {
        if (xhr.status == 200) {
          console.log("RESPONSE is " + typeof(xhr.responseText) + " " + xhr.responseText);

          switch(callback) {
            case 'index':
              renderIndex(xhr.responseText);
              break;
            default:
              console.error('Unknown type: ');
              return xhr.responseText;
          }
          
        return xhr.responseText
        
        } else {
          console.error ("Invocation Errors Occured");
          return "Invocation Errors Occured";
        }

      } else {
        return xhr.readyState;
      }
    }
  }
}

function CORS(url) {
  $.ajax({
    type: "POST",
    url: url,
    dataType: "json",
    async: false,
    
    success: function(data) {
      renderIndex(data);
      save(data);
      $('.play').click();
    },
    
    complete: function(data) {
      //IMPORTANT
      $('#matches').listview('refresh');
    } 
});

}





