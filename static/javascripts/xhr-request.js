function XHRRequest(type, url, params) {
  var xhr = new XMLHttpRequest();
  
  if(type == 'index') {
    url = url + '?md='+params;
  } else{
    params = '#';
  }
 
  if(xhr) {    
    xhr.open('POST', url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.send(params);
    
    xhr.onreadystatechange = function() {
      if (xhr.readyState == 4) {
        if (xhr.status == 200) {
          switch(type) {
            case 'index':
              saveIndex(xhr.responseText, params);
              break;
            case 'teams':
              index(xhr.responseText, params);
              break;
            default:
              console.error('Unknown type: ' + type);
          }
        } else {
          return "Invocation Errors Occured";
        }
      } else {
        return xhr.readyState;
      }
    }
  }
}